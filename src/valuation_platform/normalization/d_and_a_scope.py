"""Exact reviewed D&A acceptance; no generic fallback or component arithmetic."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
from typing import Mapping

from valuation_platform.sec.annual_period import ResolvedAnnualPeriod
from valuation_platform.sec.filing_xbrl import (
    FilingXBRLDimension, FilingXBRLQName, SECFilingXBRL,
    parse_filing_xbrl_instance,
)
from .concepts import FinancialMetric
from .models import (
    AmbiguityReason, AmbiguousHistoricalMetric, DAndAOccurrenceAudit,
    DAndAScopeAudit, EvidenceSourceKind, FactEvidence, FilingXBRLEvidence,
    HistoricalPeriod, HistoricalPolicyProvenance, MissingHistoricalMetric, MissingReason,
    NormalizedHistoricalValue, ReviewedPolicyEvidence,
)

D_AND_A_SCOPE_POLICY_ID = "d_and_a_scope_equivalence"
D_AND_A_SCOPE_POLICY_VERSION = "1"
D_AND_A_SCOPE_CLASSIFICATION = "OPERATING_D_AND_A_EQUIVALENT"
_CONCEPT = "DepreciationAndAmortization"
_ISO = "http://www.xbrl.org/2003/iso4217"
_RESEARCH = "docs/depreciation-amortization-scope-evidence-design.md"
_LOCATIONS = (
    "Depreciation and amortization annual add-back row",
    "current annual property/equipment/technology expense paragraph",
    "current annual finite-lived intangible amortization expense paragraph",
    "Consolidation; Property/equipment/technology; Intangibles; Leases; Client incentives",
    "operating lease cost and ROU presentation paragraphs",
)


class DAndAScopePolicyError(ValueError):
    """Structurally invalid curated policy or supplied filing evidence."""


@dataclass(frozen=True)
class DAndASupportDefinition:
    """A separately reviewed supporting expense, never a derived operand."""

    namespace: str
    concept: str
    dimensions: tuple[FilingXBRLDimension, ...]
    expected_value: Decimal
    decimals: str


@dataclass(frozen=True)
class DAndAScopePolicyEntry:
    """Full exact identity plus immutable reviewed source/relationship snapshot."""

    company_cik: int
    accession_number: str
    form: str
    filed: date
    primary_document: str
    report_date: date
    annual_start: date
    annual_end: date
    namespace: str
    taxonomy: str
    concept: str
    unit: str
    economic_scope: str
    expected_value: Decimal
    instance_url: str
    instance_digest: str
    reviewed_evidence: tuple[ReviewedPolicyEvidence, ...]
    support: tuple[DAndASupportDefinition, ...]
    artifact_digests: tuple[tuple[str, str], ...]
    reviewed_entry_json: str
    metric: FinancialMetric = FinancialMetric.D_AND_A

    @property
    def key(self):
        return (
            self.metric, self.company_cik, self.accession_number, self.form,
            self.filed, self.primary_document, self.report_date,
            self.annual_start, self.annual_end, self.namespace, self.taxonomy,
            self.concept, (), self.unit, self.economic_scope,
        )

    def __post_init__(self):
        try:
            record = json.loads(self.reviewed_entry_json)
            filing = record["filing"]
            prefix = (
                "https://www.sec.gov/Archives/edgar/data/"
                f"{self.company_cik}/{self.accession_number.replace('-', '')}/"
            )
            valid = (
                self.metric is FinancialMetric.D_AND_A
                and type(self.company_cik) is int and self.company_cik == 1403161
                and re.fullmatch(r"[0-9]{10}-[0-9]{2}-[0-9]{6}", self.accession_number)
                and self.form == filing["form"] == "10-K"
                and self.accession_number == filing["accession_number"]
                and self.filed.isoformat() == filing["filing_date"]
                and self.primary_document == filing["primary_document"]
                and self.report_date.isoformat() == filing["report_date"]
                and self.annual_start.isoformat() == record["annual_start"]
                and self.annual_end.isoformat() == record["annual_end"]
                and self.annual_start < self.annual_end == self.report_date
                and self.namespace == record["namespace"]
                and self.taxonomy == "us-gaap" and self.concept == _CONCEPT
                and self.unit == "USD"
                and self.economic_scope == D_AND_A_SCOPE_CLASSIFICATION
                and isinstance(self.expected_value, Decimal)
                and self.expected_value.is_finite()
                and self.instance_url == record["artifacts"][0]["url"]
                and self.instance_digest == record["artifacts"][0]["sha256"]
                and self.expected_value == Decimal(next(
                    f["numeric_value"] for f in record["facts"]
                    if f["concept_key"] == self.namespace + "#" + _CONCEPT
                    and not f["context"]["dimensions"]
                ))
                and type(self.reviewed_evidence) is tuple
                and len(self.reviewed_evidence) == 5
                and len({e.evidence_id for e in self.reviewed_evidence}) == 5
                and tuple((e.source_url, e.content_digest) for e in self.reviewed_evidence)
                    == tuple((n["url"], n["sha256"]) for n in record["notes"])
                and all(e.review_status == "approved" and e.research_artifact == _RESEARCH
                        for e in self.reviewed_evidence)
                and tuple(e.filing_location for e in self.reviewed_evidence)
                    == tuple(n["location"] + " — " + detail
                             for n, detail in zip(record["notes"], _LOCATIONS))
                and type(self.support) is tuple and len(self.support) == 2
                and self.support == _support_definitions(record)
                and type(self.artifact_digests) is tuple
                and self.artifact_digests == tuple(
                    (a["url"], a["sha256"])
                    for a in (*record["artifacts"], *record["notes"])
                )
                and len({u for u, _ in self.artifact_digests}) == 9
                and all(u.startswith(prefix) and re.fullmatch(r"[0-9a-f]{64}", h)
                        for u, h in self.artifact_digests)
                and any(p["role_uri"].endswith("/CONSOLIDATEDSTATEMENTSOFOPERATIONS")
                        and p["definition"] and p["reports"] for p in record["presentation"])
                and any(c["parent"] == "CostsAndExpenses"
                        and c["child"] == _CONCEPT and Decimal(c["weight"]) == 1
                        for c in record["calculation"])
            )
        except (KeyError, TypeError, ValueError, StopIteration):
            valid = False
        if not valid:
            raise DAndAScopePolicyError("Incomplete or inconsistent D&A reviewed entry")


@dataclass(frozen=True)
class DAndAScopePolicy:
    policy_id: str
    version: str
    entries: tuple[DAndAScopePolicyEntry, ...]

    def __post_init__(self):
        if (self.policy_id != D_AND_A_SCOPE_POLICY_ID
                or self.version != D_AND_A_SCOPE_POLICY_VERSION
                or type(self.entries) is not tuple or len(self.entries) != 5
                or any(not isinstance(e, DAndAScopePolicyEntry) for e in self.entries)
                or len({e.key for e in self.entries}) != 5):
            raise DAndAScopePolicyError("Invalid immutable D&A policy/version/entry set")


@dataclass(frozen=True)
class VerifiedDAndAArtifacts:
    accession_number: str
    digests: tuple[tuple[str, str], ...]

    def __post_init__(self):
        if (type(self.digests) is not tuple or not self.digests
                or len({u for u, _ in self.digests}) != len(self.digests)
                or any(not re.fullmatch(r"[0-9a-f]{64}", h) for _, h in self.digests)):
            raise DAndAScopePolicyError("Invalid reviewed artifact attestation")


def _dimensions(items):
    def qname(q):
        return FilingXBRLQName(q["namespace"], q["local_name"])
    return tuple(FilingXBRLDimension(
        qname(d["dimension"]),
        qname(d["explicit_member"]) if d["explicit_member"] else None,
        d["typed_member_xml"],
    ) for d in items)


def _support_definitions(record):
    return tuple(DAndASupportDefinition(
        f["concept_key"].split("#")[0], f["concept_key"].split("#")[1],
        _dimensions(f["context"]["dimensions"]), Decimal(f["numeric_value"]),
        f["decimals"],
    ) for f in record["facts"] if f["context"]["dimensions"]
       or f["concept_key"].endswith("#AmortizationOfIntangibleAssets"))


def _entry(record):
    filing = record["filing"]
    return DAndAScopePolicyEntry(
        1403161, filing["accession_number"], filing["form"],
        date.fromisoformat(filing["filing_date"]), filing["primary_document"],
        date.fromisoformat(filing["report_date"]),
        date.fromisoformat(record["annual_start"]), date.fromisoformat(record["annual_end"]),
        record["namespace"], "us-gaap", _CONCEPT, "USD", D_AND_A_SCOPE_CLASSIFICATION,
        Decimal(next(f["numeric_value"] for f in record["facts"]
                     if not f["context"]["dimensions"]
                     and f["concept_key"].endswith("#" + _CONCEPT))),
        record["artifacts"][0]["url"], record["artifacts"][0]["sha256"],
        tuple(ReviewedPolicyEvidence(
            f"v-{record['annual_end']}-{i}", n["url"],
            n["location"] + " — " + _LOCATIONS[i - 1], _RESEARCH,
            date(2026, 10, 10), "approved",
            "Selected consolidated operating asset expense; separate finite-lived "
            "amortization, incentives, impairment and lease scope. 2025 property "
            "precision corroborates scope only; no residual/tolerance/lease adjustment.",
            n["sha256"],
        ) for i, n in enumerate(record["notes"], 1)),
        _support_definitions(record),
        tuple((a["url"], a["sha256"]) for a in (*record["artifacts"], *record["notes"])),
        json.dumps(record, sort_keys=True, separators=(",", ":")),
    )


D_AND_A_SCOPE_EQUIVALENCE_POLICY = DAndAScopePolicy(
    D_AND_A_SCOPE_POLICY_ID, D_AND_A_SCOPE_POLICY_VERSION,
    tuple(_entry(r) for r in json.loads(
        Path(__file__).with_name("d_and_a_scope_registry.json").read_text()
    )),
)


def d_and_a_scope_entry_for(company_cik, filing, annual_period,
                          policy=D_AND_A_SCOPE_EQUIVALENCE_POLICY):
    if policy != D_AND_A_SCOPE_EQUIVALENCE_POLICY:
        raise DAndAScopePolicyError("Unpublished D&A version or reviewed evidence")
    if not isinstance(annual_period, ResolvedAnnualPeriod):
        return None
    entry = next((e for e in policy.entries if (
        e.company_cik == company_cik and e.accession_number == filing.accession_number
        and e.form == filing.form and e.filed == filing.filing_date
        and e.primary_document == filing.primary_document
        and e.report_date == filing.report_date
        and e.annual_start == annual_period.start and e.annual_end == annual_period.end
    )), None)
    if entry is not None:
        f, a = annual_period.filing, annual_period.evidence
        if (f.registrant_cik != company_cik or f.accession_number != filing.accession_number
                or f.form != filing.form or f.filing_date != filing.filing_date
                or f.report_date != filing.report_date or f.primary_document != filing.primary_document
                or f.source_url != entry.instance_url
                or a.registrant_cik != company_cik or a.entity_identifier_scheme != "http://www.sec.gov/CIK"
                or a.dimensions):
            raise DAndAScopePolicyError("Inconsistent authoritative D&A annual evidence")
    return entry


def verify_d_and_a_artifacts(entry, artifacts: Mapping[str, bytes],
                            filing_xbrl: SECFilingXBRL):
    """Check retrieved bytes, including binding the parsed instance to those bytes."""
    digests = tuple((u, hashlib.sha256(artifacts[u]).hexdigest())
                    for u, _ in entry.artifact_digests if u in artifacts)
    if digests != entry.artifact_digests:
        raise DAndAScopePolicyError("Missing or changed selected D&A reviewed artifact")
    parsed = parse_filing_xbrl_instance(
        artifacts[entry.instance_url], company=filing_xbrl.company,
        filing=filing_xbrl.filing, source_url=entry.instance_url,
        retrieved_at=filing_xbrl.retrieved_at,
    )
    if (parsed.facts != filing_xbrl.facts or parsed.contexts != filing_xbrl.contexts
            or parsed.units != filing_xbrl.units):
        raise DAndAScopePolicyError("Parsed D&A instance is not the verified source")
    return VerifiedDAndAArtifacts(entry.accession_number, digests)


def _usd(fact):
    return (fact.unit is not None and not fact.unit.denominator_measures
            and fact.unit.numerator_measures == (FilingXBRLQName(_ISO, "USD"),))


def _evidence(fact, context, filing_xbrl, ordinal):
    return FilingXBRLEvidence(
        EvidenceSourceKind.FILING_XBRL, fact.source_url, fact.namespace, fact.concept,
        fact.raw_value, fact.numeric_value, "USD", fact.start, fact.end,
        fact.accession_number, filing_xbrl.filing.form, filing_xbrl.filing.filing_date,
        filing_xbrl.filing.report_date, filing_xbrl.filing.primary_document,
        filing_xbrl.retrieved_at, fact.context_id, fact.dimensions, fact.decimals,
        fact.is_nil, fact.unit_ref, ordinal, context.entity_identifier_scheme,
        context.entity_identifier,
    )


def _compact(evidence):
    return FactEvidence(
        evidence.source_kind, evidence.source_url, "us-gaap", evidence.concept,
        evidence.value, evidence.unit, evidence.start, evidence.end,
        evidence.accession_number, evidence.observation_form, evidence.observation_filed,
        None, None, None,
    )


def apply_curated_d_and_a_scope_policy(
    bucket, direct_result, company_cik, annual_period, filing_xbrl,
    artifacts=None, policy=D_AND_A_SCOPE_EQUIVALENCE_POLICY,
):
    """Accept one exact semantic signature, keeping all original occurrences."""
    if direct_result.metric is not FinancialMetric.D_AND_A:
        raise DAndAScopePolicyError("D&A policy received another metric")
    if isinstance(direct_result, AmbiguousHistoricalMetric):
        return direct_result
    entry = d_and_a_scope_entry_for(company_cik, bucket.filing, annual_period, policy)
    if entry is None or filing_xbrl is None or artifacts is None:
        return direct_result
    if (artifacts.accession_number != entry.accession_number
            or artifacts.digests != entry.artifact_digests):
        raise DAndAScopePolicyError("Incomplete or mismatched D&A reviewed evidence")
    if (filing_xbrl.company.cik != company_cik or filing_xbrl.filing != bucket.filing
            or filing_xbrl.source_url != entry.instance_url):
        raise DAndAScopePolicyError("Inconsistent D&A instance source/accession metadata")
    contexts = {c.context_id: c for c in filing_xbrl.contexts}
    units = {u.unit_id: u for u in filing_xbrl.units}
    if len(contexts) != len(filing_xbrl.contexts) or len(units) != len(filing_xbrl.units):
        raise DAndAScopePolicyError("Duplicate D&A context or unit definition")
    eligible, audit, support = [], [], []
    nil_statuses = {}
    support_matches = {s: [] for s in entry.support}
    for ordinal, f in enumerate(filing_xbrl.facts):
        if not re.search(r"depreci|amorti|deplet|accreti", f.concept, re.I):
            continue
        c = contexts.get(f.context_id)
        if c is None:
            raise DAndAScopePolicyError("Missing D&A fact context")
        if (f.start != c.start or f.end != c.end or f.dimensions != c.dimensions
                or f.source_url != filing_xbrl.source_url
                or f.accession_number != entry.accession_number):
            raise DAndAScopePolicyError("Broken D&A context/source/accession linkage")
        if ((f.unit_ref is not None and (f.unit != units.get(f.unit_ref) or f.unit is None))
                or (f.unit_ref is None and f.unit is not None)):
            raise DAndAScopePolicyError("Broken D&A unit linkage")
        entity = (c.entity_identifier_scheme == "http://www.sec.gov/CIK"
                  and c.entity_identifier.isdigit() and int(c.entity_identifier) == company_cik)
        period = f.start == entry.annual_start and f.end == entry.annual_end
        concept = f.namespace == entry.namespace and f.concept == entry.concept
        reason = ("EXCLUDED_ENTITY" if not entity else "EXCLUDED_PERIOD" if not period
                  else "EXCLUDED_CONCEPT" if not concept else "EXCLUDED_DIMENSIONS"
                  if f.dimensions else "EXCLUDED_UNIT" if not _usd(f)
                  else "EXCLUDED_NIL" if f.is_nil else "ELIGIBLE")
        relevant_support = any(f.namespace == s.namespace and f.concept == s.concept
                               and f.dimensions == s.dimensions for s in entry.support)
        if entity and period and (concept or relevant_support):
            if not f.is_nil and (f.unit_ref is None or f.unit is None):
                raise DAndAScopePolicyError("Missing D&A numeric unit linkage")
            signature = (f.namespace, f.concept, f.start, f.end, f.dimensions,
                         f.unit.numerator_measures if f.unit else None,
                         f.unit.denominator_measures if f.unit else None)
            nil_statuses.setdefault(signature, set()).add(f.is_nil)
            if not f.is_nil and (not isinstance(f.numeric_value, Decimal)
                               or not f.numeric_value.is_finite()):
                raise DAndAScopePolicyError("Malformed D&A numeric evidence")
        for s in entry.support:
            if (entity and period and f.namespace == s.namespace and f.concept == s.concept
                    and f.dimensions == s.dimensions and _usd(f) and not f.is_nil):
                support_matches[s].append((ordinal, f, c))
                reason = "REVIEWED_SCOPE_SUPPORT"
        if reason == "ELIGIBLE":
            eligible.append((ordinal, f, c))
        audit.append(DAndAOccurrenceAudit(ordinal, f, c, reason))
    if any(len(statuses) > 1 for statuses in nil_statuses.values()):
        raise DAndAScopePolicyError("D&A nil/numeric collision")
    candidates = tuple(_compact(_evidence(f, c, filing_xbrl, i))
                       for i, (_, f, c) in enumerate(eligible, 1))
    values = {f.numeric_value for _, f, _ in eligible}
    if len(values) > 1:
        return AmbiguousHistoricalMetric(FinancialMetric.D_AND_A,
                                        AmbiguityReason.CONFLICTING_CONCEPT_VALUES, candidates)
    if not values:
        return direct_result
    if values != {entry.expected_value}:
        return (replace(direct_result, reason=MissingReason.CURATED_D_AND_A_EVIDENCE_MISMATCH)
                if isinstance(direct_result, MissingHistoricalMetric) else direct_result)
    for s, matches in support_matches.items():
        if not matches:
            return direct_result
        if any(f.numeric_value != s.expected_value or f.decimals != s.decimals
               for _, f, _ in matches):
            return (replace(direct_result, reason=MissingReason.CURATED_D_AND_A_EVIDENCE_MISMATCH)
                    if isinstance(direct_result, MissingHistoricalMetric) else direct_result)
        support.extend(_evidence(f, c, filing_xbrl, i)
                       for i, (_, f, c) in enumerate(matches, 1))
    provenance = HistoricalPolicyProvenance(
        policy.policy_id, policy.version, entry.economic_scope, company_cik,
        entry.accession_number, entry.report_date, entry.annual_start, entry.annual_end,
        entry.taxonomy, entry.concept, entry.unit, entry.reviewed_evidence,
        tuple(_evidence(f, c, filing_xbrl, i) for i, (_, f, c) in enumerate(eligible, 1)),
        DAndAScopeAudit(entry.reviewed_entry_json, artifacts.digests,
                       tuple(o for o, _, _ in eligible), tuple(support), tuple(audit)),
    )
    if isinstance(direct_result, NormalizedHistoricalValue):
        if Decimal(str(direct_result.value)) != entry.expected_value:
            return AmbiguousHistoricalMetric(
                FinancialMetric.D_AND_A, AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
                (direct_result.chosen_source, *direct_result.confirming_sources, *candidates),
            )
        return replace(direct_result, confirming_sources=(
            *direct_result.confirming_sources, *candidates), policy_provenance=provenance)
    if not isinstance(direct_result, MissingHistoricalMetric):
        raise DAndAScopePolicyError("Invalid D&A direct result")
    return NormalizedHistoricalValue(
        FinancialMetric.D_AND_A, entry.expected_value, "USD",
        HistoricalPeriod(entry.annual_start, entry.annual_end),
        candidates[0], candidates[1:], provenance,
    )


def validate_d_and_a_scope_provenance(provenance):
    """Reject incomplete, foreign or reordered audit payloads at output boundary."""
    audit = provenance.d_and_a_scope
    entry = next((e for e in D_AND_A_SCOPE_EQUIVALENCE_POLICY.entries
                  if e.accession_number == provenance.accession_number), None)
    if (entry is None or audit is None
            or provenance.policy_id != D_AND_A_SCOPE_POLICY_ID
            or provenance.policy_version != D_AND_A_SCOPE_POLICY_VERSION
            or provenance.economic_scope != entry.economic_scope
            or provenance.company_cik != entry.company_cik
            or provenance.report_date != entry.report_date
            or provenance.annual_start != entry.annual_start
            or provenance.annual_end != entry.annual_end
            or provenance.taxonomy != entry.taxonomy
            or provenance.concept != entry.concept or provenance.unit != entry.unit
            or provenance.reviewed_evidence != entry.reviewed_evidence
            or audit.reviewed_entry_json != entry.reviewed_entry_json
            or audit.verified_artifact_digests != entry.artifact_digests):
        raise DAndAScopePolicyError("Invalid D&A policy/audit provenance")
    ordinals = tuple(o.original_instance_ordinal for o in audit.occurrences)
    if (ordinals != tuple(sorted(set(ordinals)))
            or any(type(o) is not int or o < 0 for o in ordinals)):
        raise DAndAScopePolicyError("Invalid original D&A occurrence order")
    eligible = tuple(o for o in audit.occurrences if o.disposition == "ELIGIBLE")
    if (tuple(o.original_instance_ordinal for o in eligible)
            != audit.confirming_original_ordinals
            or len(eligible) != len(provenance.filing_xbrl_evidence)):
        raise DAndAScopePolicyError("Lost D&A confirming occurrence multiplicity")
    for o, e in zip(eligible, provenance.filing_xbrl_evidence):
        f, c = o.fact, o.context
        if (f.namespace != entry.namespace or f.concept != entry.concept
                or f.numeric_value != entry.expected_value or f.is_nil
                or f.dimensions or not _usd(f)
                or f.start != entry.annual_start or f.end != entry.annual_end
                or c.entity_identifier_scheme != "http://www.sec.gov/CIK"
                or not c.entity_identifier.isdigit()
                or int(c.entity_identifier) != entry.company_cik
                or f.raw_value != e.raw_value or f.decimals != e.decimals
                or f.context_id != e.context_id or f.unit_ref != e.unit_ref
                or f.source_url != e.source_url or f.accession_number != e.accession_number
                or e.observation_filed != entry.filed
                or e.primary_document != entry.primary_document):
            raise DAndAScopePolicyError("Inconsistent D&A occurrence provenance")
    for s in entry.support:
        matches = tuple(e for e in audit.supporting_facts
                        if e.namespace == s.namespace and e.concept == s.concept
                        and e.dimensions == s.dimensions)
        if not matches or any(e.value != s.expected_value or e.decimals != s.decimals
                              or e.is_nil or e.unit != "USD"
                              or e.start != entry.annual_start or e.end != entry.annual_end
                              or e.accession_number != entry.accession_number
                              for e in matches):
            raise DAndAScopePolicyError("Incomplete D&A separately typed asset support")
