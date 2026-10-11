"""Exact reviewed gross cash PP&E acceptance; never a generic fallback."""
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
    FilingXBRLQName, SECFilingXBRL, parse_filing_xbrl_instance,
)
from .concepts import FinancialMetric
from .models import (
    AmbiguityReason, AmbiguousHistoricalMetric, CapexOccurrenceAudit, CapexScopeAudit,
    EvidenceSourceKind, FactEvidence, FilingXBRLEvidence, HistoricalPeriod,
    HistoricalPolicyProvenance, MissingHistoricalMetric, MissingReason,
    NormalizedHistoricalValue, ReviewedPolicyEvidence,
)

CAPEX_SCOPE_POLICY_ID = "capex_scope_equivalence"
CAPEX_SCOPE_POLICY_VERSION = "1"
CAPEX_SCOPE_CLASSIFICATION = "GROSS_CASH_PPE_EQUIVALENT"
_ISO = "http://www.xbrl.org/2003/iso4217"
_RESEARCH = "docs/capex-scope-evidence-design.md"


class CapexScopePolicyError(ValueError):
    """Invalid curated entry or structurally inconsistent source evidence."""


@dataclass(frozen=True)
class CapexScopePolicyEntry:
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
    artifact_digests: tuple[tuple[str, str], ...]
    reviewed_entry_json: str
    metric: FinancialMetric = FinancialMetric.CAPEX
    support: tuple = ()

    @property
    def key(self):
        return (self.metric, self.company_cik, self.accession_number, self.form,
                self.filed, self.primary_document, self.report_date,
                self.annual_start, self.annual_end, self.namespace, self.taxonomy,
                self.concept, (), self.unit, self.economic_scope)

    def __post_init__(self):
        try:
            r = json.loads(self.reviewed_entry_json)
            f = r['filing']
            o = r['operand_occurrences'][0]
            _validate_representation_records(r)
            prefix = ('https://www.sec.gov/Archives/edgar/data/'
                      f"{self.company_cik}/{self.accession_number.replace('-', '')}/")
            valid = (
                self.metric is FinancialMetric.CAPEX
                and type(self.company_cik) is int and self.company_cik == r['cik']
                and self.company_cik in (1018724, 59478)
                and re.fullmatch(r'[0-9]{10}-[0-9]{2}-[0-9]{6}', self.accession_number)
                and self.accession_number == f['accession_number']
                and self.form == f['form'] == '10-K'
                and self.filed.isoformat() == f['filing_date']
                and self.primary_document == f['primary_document']
                and self.report_date.isoformat() == f['report_date']
                and self.annual_start.isoformat() == r['annual_start']
                and self.annual_end.isoformat() == r['annual_end']
                and self.annual_start < self.annual_end == self.report_date
                and self.namespace + '#' + self.concept == o['concept_key']
                and self.taxonomy == 'us-gaap' and self.unit == 'USD'
                and self.concept == ('PaymentsToAcquireProductiveAssets'
                    if self.company_cik == 1018724 else 'PaymentsToAcquireOtherPropertyPlantAndEquipment')
                and self.economic_scope == r['scope_classification'] == CAPEX_SCOPE_CLASSIFICATION
                and isinstance(self.expected_value, Decimal) and self.expected_value.is_finite()
                and self.expected_value > 0
                and self.expected_value == Decimal(r['expected_value_usd']) == Decimal(o['numeric_value'])
                and self.instance_url == r['source_url'] and self.instance_digest == r['instance_sha256']
                and not self.support and not r['contexts'][o['context_id']]['dimensions']
                and o['normalized_unit'] == 'USD' and not o['is_nil']
                and type(self.reviewed_evidence) is tuple and len(self.reviewed_evidence) == 3
                and len({e.evidence_id for e in self.reviewed_evidence}) == 3
                and tuple((e.source_url, e.content_digest) for e in self.reviewed_evidence)
                    == tuple((a['source_url'], a['sha256']) for a in r['reviewed_evidence'])
                and all(e.review_status == 'approved' and e.research_artifact == _RESEARCH
                    and e.rationale == r['scope_rationale'] + ' ' + r['incentive_treatment']
                    and e.filing_location == a['report']['LongName'] + ' — ' + a['report']['HtmlFileName']
                    for e, a in zip(self.reviewed_evidence, r['reviewed_evidence']))
                and type(self.artifact_digests) is tuple
                and self.artifact_digests == _digests(r)
                and all(u.startswith(prefix) and re.fullmatch(r'[0-9a-f]{64}', h)
                        for u, h in self.artifact_digests)
                and (self.instance_url, self.instance_digest) in self.artifact_digests
                and r['operand_concept_metadata'][o['concept_key']]['presentation_roles']
                and any('Purchases of property and equipment' in s for s in r['cashflow_captions'])
            )
        except (KeyError, TypeError, ValueError, IndexError):
            valid = False
        if not valid:
            raise CapexScopePolicyError('Incomplete or inconsistent Capex reviewed entry')


def _digests(r):
    return tuple(dict.fromkeys((a['source_url'], a['sha256'])
        for a in (*r['mandatory_artifacts'], *r['reviewed_evidence'])))


def _validate_representation_records(record, artifacts=None):
    """Raw response and retained JSON hashes are independent byte attestations."""
    raw_kind = 'sha256_sec_response_body_bytes'
    for a in (*record['mandatory_artifacts'], *record['reviewed_evidence']):
        if a.get('digest_type') != raw_kind:
            raise CapexScopePolicyError('Unsupported Capex artifact digest representation')
    if record['cik'] == 1018724:
        refreshed = record.get('evidence_refresh', ())
        if len(refreshed) != 3 or len({a['source_url'] for a in refreshed}) != 3:
            raise CapexScopePolicyError('Missing AMZN explicitly reviewed refresh')
        for a, review in zip(record['reviewed_evidence'], refreshed):
            if (a['source_url'] != review['source_url'] or a['sha256'] != review['sha256']
                    or review['accession_number'] != record['filing']['accession_number']
                    or review['digest_type'] != raw_kind
                    or review['representation'] != 'sec_response_body_bytes'
                    or review['old_digest_type'] != 'claimed_sha256_sec_response_body_bytes'
                    or review['old_status'] != 'unverifiable_original_body_unavailable'
                    or not re.fullmatch(r'[0-9a-f]{64}', review['old_sha256'])
                    or review['review_status'] != 'approved' or not review['scope_assertions']
                    or not review['cited_passage'] or not review['substantive_review']
                    or review['http_status'] != 200 or not review['retrieved_at']):
                raise CapexScopePolicyError('Incomplete AMZN explicit refresh provenance')
            if artifacts is not None:
                body = artifacts[a['source_url']]
                if (hashlib.sha256(body).hexdigest() != review['sha256']
                        or len(body) != review['byte_count']):
                    raise CapexScopePolicyError('Changed AMZN refreshed response bytes')
    correction = record.get('representation_correction')
    if correction is None:
        if record['cik'] == 59478:
            raise CapexScopePolicyError('Missing LLY representation correction audit')
        return
    text = correction['retained_utf8_text'].encode('utf-8')
    source = correction['source_url']
    if (record['cik'] != 59478
            or correction['accession_number'] != record['filing']['accession_number']
            or correction['retained_digest_type'] != 'sha256_retained_reserialized_json_utf8_bytes'
            or correction['response_digest_type'] != raw_kind
            or hashlib.sha256(text).hexdigest() != correction['retained_digest']
            or len(text) != correction['retained_byte_count']
            or not source.endswith('/index.json')
            or (source, correction['response_digest']) not in _digests(record)):
        raise CapexScopePolicyError('Invalid Capex representation correction audit')
    # Parse only after verifying the retained bytes; parsed equality never
    # replaces the independent SEC response-body hash check.
    retained = json.loads(text)
    if artifacts is not None:
        raw = artifacts[source]
        if (hashlib.sha256(raw).hexdigest() != correction['response_digest']
                or len(raw) != correction['response_byte_count']
                or json.loads(raw) != retained):
            raise CapexScopePolicyError('Changed raw/retained Capex index representation')


def _entry(r):
    f = r['filing']; o = r['operand_occurrences'][0]
    namespace, concept = o['concept_key'].split('#')
    return CapexScopePolicyEntry(
        r['cik'], f['accession_number'], f['form'], date.fromisoformat(f['filing_date']),
        f['primary_document'], date.fromisoformat(f['report_date']),
        date.fromisoformat(r['annual_start']), date.fromisoformat(r['annual_end']),
        namespace, 'us-gaap', concept, 'USD', CAPEX_SCOPE_CLASSIFICATION,
        Decimal(r['expected_value_usd']), r['source_url'], r['instance_sha256'],
        tuple(ReviewedPolicyEvidence(
            f"capex-{r['cik']}-{r['annual_end']}-{i}", a['source_url'],
            a['report']['LongName'] + ' — ' + a['report']['HtmlFileName'], _RESEARCH,
            date.fromisoformat(r['review_date']), 'approved',
            r['scope_rationale'] + ' ' + r['incentive_treatment'], a['sha256'],
        ) for i, a in enumerate(r['reviewed_evidence'], 1)),
        _digests(r), json.dumps(r, sort_keys=True, separators=(',', ':')),
    )


@dataclass(frozen=True)
class CapexScopePolicy:
    policy_id: str
    version: str
    entries: tuple[CapexScopePolicyEntry, ...]

    def __post_init__(self):
        if (self.policy_id != CAPEX_SCOPE_POLICY_ID or self.version != CAPEX_SCOPE_POLICY_VERSION
                or type(self.entries) is not tuple or len(self.entries) != 10
                or any(not isinstance(e, CapexScopePolicyEntry) for e in self.entries)
                or len({e.key for e in self.entries}) != 10):
            raise CapexScopePolicyError('Invalid immutable Capex policy/version/entry set')


@dataclass(frozen=True)
class VerifiedCapexArtifacts:
    accession_number: str
    digests: tuple[tuple[str, str], ...]

    def __post_init__(self):
        if (type(self.digests) is not tuple or not self.digests
                or len({u for u, _ in self.digests}) != len(self.digests)
                or any(not re.fullmatch(r'[0-9a-f]{64}', h) for _, h in self.digests)):
            raise CapexScopePolicyError('Invalid reviewed artifact attestation')


CAPEX_SCOPE_EQUIVALENCE_POLICY = CapexScopePolicy(
    CAPEX_SCOPE_POLICY_ID, CAPEX_SCOPE_POLICY_VERSION,
    tuple(_entry(r) for r in json.loads(Path(__file__).with_name('capex_scope_registry.json').read_text())),
)
_V2_RECORDS = json.loads(Path(__file__).with_name('capex_scope_v2_registry.json').read_text())


def _v2_fields(r):
    f = r['filing']
    return dict(company_cik=r['cik'], accession_number=f['accession_number'],
        form=f['form'], filed=date.fromisoformat(f['filing_date']),
        primary_document=f['primary_document'], report_date=date.fromisoformat(f['report_date']),
        annual_start=date.fromisoformat(r['annual_start']), annual_end=date.fromisoformat(r['annual_end']),
        namespace=r['namespace'], taxonomy=r['taxonomy'], concept=r['concept'], unit=r['normalized_unit'],
        economic_scope=r['scope_classification'], expected_value=Decimal(r['expected_value_usd']),
        instance_url=r['source_url'], instance_digest=r['instance_sha256'],
        reviewed_evidence=tuple(ReviewedPolicyEvidence(a['evidence_id'], a['source_url'],
            a['location'], a['research_artifact'], date.fromisoformat(a['review_date']),
            a['review_status'], a['rationale'], a['sha256']) for a in r['reviewed_evidence']),
        artifact_digests=_digests(r), reviewed_entry_json=json.dumps(r, sort_keys=True, separators=(',', ':')),
        metric=FinancialMetric.CAPEX, support=())


@dataclass(frozen=True)
class CVXCapexScopePolicyEntry(CapexScopePolicyEntry):
    """Only the five independently reviewed v2 records, never research flags."""
    def __post_init__(self):
        canonical = next((r for r in _V2_RECORDS
                          if r['filing']['accession_number'] == self.accession_number), None)
        if canonical is None or any(getattr(self, k) != v for k, v in _v2_fields(canonical).items()):
            raise CapexScopePolicyError('Incomplete or unpublished CVX v2 entry')
        if type(self.company_cik) is not int or not isinstance(self.expected_value, Decimal):
            raise CapexScopePolicyError('Invalid CVX entry types')
        prefix = ('https://www.sec.gov/Archives/edgar/data/93410/'
                  + self.accession_number.replace('-', '') + '/')
        if (self.company_cik != 93410 or self.form != '10-K'
                or not self.annual_start < self.annual_end == self.report_date
                or not self.expected_value.is_finite() or self.expected_value <= 0
                or canonical['policy_version'] != '2' or not canonical['production_policy_approval']
                or len(self.reviewed_evidence) != (8 if self.annual_end.year == 2023 else 7)
                or len({e.evidence_id for e in self.reviewed_evidence}) != len(self.reviewed_evidence)
                or any(e.review_status != 'approved' or not e.rationale for e in self.reviewed_evidence)
                or any(not u.startswith(prefix) or not re.fullmatch(r'[0-9a-f]{64}', h)
                       for u, h in self.artifact_digests)
                or (self.instance_url, self.instance_digest) not in self.artifact_digests
                or any(a['representation'] != 'sec_response_body_bytes'
                       or type(a['byte_length']) is not int or a['byte_length'] <= 0
                       for a in canonical['mandatory_artifacts'])):
            raise CapexScopePolicyError('Incomplete CVX raw evidence or scope review')
        _validate_representation_records(canonical)


@dataclass(frozen=True)
class CVXCapexScopePolicy(CapexScopePolicy):
    def __post_init__(self):
        if (self.policy_id != CAPEX_SCOPE_POLICY_ID or self.version != '2'
                or type(self.entries) is not tuple
                or self.entries != tuple(CVXCapexScopePolicyEntry(**_v2_fields(r)) for r in _V2_RECORDS)
                or len(self.entries) != 5):
            raise CapexScopePolicyError('Invalid immutable CVX v2 policy')


CAPEX_SCOPE_V2_POLICY = CVXCapexScopePolicy(CAPEX_SCOPE_POLICY_ID, '2',
    tuple(CVXCapexScopePolicyEntry(**_v2_fields(r)) for r in _V2_RECORDS))


@dataclass(frozen=True)
class CapexScopePolicyCatalog:
    policies: tuple[CapexScopePolicy, ...]

    def __post_init__(self):
        if self.policies != (CAPEX_SCOPE_EQUIVALENCE_POLICY, CAPEX_SCOPE_V2_POLICY):
            raise CapexScopePolicyError('Unpublished Capex catalog')
        keys = [(e.company_cik, e.accession_number, e.annual_start, e.annual_end)
                for p in self.policies for e in p.entries]
        if len(keys) != len(set(keys)):
            raise CapexScopePolicyError('Overlapping active Capex entries')


CAPEX_SCOPE_POLICY_CATALOG = CapexScopePolicyCatalog((CAPEX_SCOPE_EQUIVALENCE_POLICY, CAPEX_SCOPE_V2_POLICY))


def published_capex_scope_policy_for(company_cik, filing, annual_period):
    matches = tuple(p for p in CAPEX_SCOPE_POLICY_CATALOG.policies
                    if capex_scope_entry_for(company_cik, filing, annual_period, p) is not None)
    if len(matches) > 1:
        raise CapexScopePolicyError('Overlapping published Capex entries')
    return matches[0] if matches else CAPEX_SCOPE_EQUIVALENCE_POLICY


def published_capex_scope_entry_for(company_cik, filing, annual_period):
    return capex_scope_entry_for(company_cik, filing, annual_period,
        published_capex_scope_policy_for(company_cik, filing, annual_period))


def capex_scope_entry_for(company_cik, filing, annual_period,
                          policy=CAPEX_SCOPE_EQUIVALENCE_POLICY):
    if policy not in CAPEX_SCOPE_POLICY_CATALOG.policies:
        raise CapexScopePolicyError("Unpublished Capex version or reviewed evidence")
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
            raise CapexScopePolicyError("Inconsistent authoritative Capex annual evidence")
    return entry


def verify_capex_artifacts(entry, artifacts: Mapping[str, bytes],
                            filing_xbrl: SECFilingXBRL):
    """Check retrieved bytes, including binding the parsed instance to those bytes."""
    digests = tuple((u, hashlib.sha256(artifacts[u]).hexdigest())
                    for u, _ in entry.artifact_digests if u in artifacts)
    if digests != entry.artifact_digests:
        raise CapexScopePolicyError("Missing or changed selected Capex reviewed artifact")
    _validate_representation_records(json.loads(entry.reviewed_entry_json), artifacts)
    if isinstance(entry, CVXCapexScopePolicyEntry):
        for a in json.loads(entry.reviewed_entry_json)['mandatory_artifacts']:
            if len(artifacts[a['source_url']]) != a['byte_length']:
                raise CapexScopePolicyError('Changed CVX raw artifact byte length')
    parsed = parse_filing_xbrl_instance(
        artifacts[entry.instance_url], company=filing_xbrl.company,
        filing=filing_xbrl.filing, source_url=entry.instance_url,
        retrieved_at=filing_xbrl.retrieved_at,
    )
    if (parsed.facts != filing_xbrl.facts or parsed.contexts != filing_xbrl.contexts
            or parsed.units != filing_xbrl.units):
        raise CapexScopePolicyError("Parsed Capex instance is not the verified source")
    return VerifiedCapexArtifacts(entry.accession_number, digests)


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


def apply_curated_capex_scope_policy(
    bucket, direct_result, company_cik, annual_period, filing_xbrl,
    artifacts=None, policy=CAPEX_SCOPE_EQUIVALENCE_POLICY,
):
    """Accept one exact semantic signature, keeping all original occurrences."""
    if direct_result.metric is not FinancialMetric.CAPEX:
        raise CapexScopePolicyError("Capex policy received another metric")
    if isinstance(direct_result, AmbiguousHistoricalMetric):
        return direct_result
    entry = capex_scope_entry_for(company_cik, bucket.filing, annual_period, policy)
    if entry is None or filing_xbrl is None or artifacts is None:
        return direct_result
    if (artifacts.accession_number != entry.accession_number
            or artifacts.digests != entry.artifact_digests):
        raise CapexScopePolicyError("Incomplete or mismatched Capex reviewed evidence")
    if (filing_xbrl.company.cik != company_cik or filing_xbrl.filing != bucket.filing
            or filing_xbrl.source_url != entry.instance_url):
        raise CapexScopePolicyError("Inconsistent Capex instance source/accession metadata")
    contexts = {c.context_id: c for c in filing_xbrl.contexts}
    units = {u.unit_id: u for u in filing_xbrl.units}
    if len(contexts) != len(filing_xbrl.contexts) or len(units) != len(filing_xbrl.units):
        raise CapexScopePolicyError("Duplicate Capex context or unit definition")
    eligible, audit, support = [], [], []
    nil_statuses = {}
    support_matches = {s: [] for s in entry.support}
    v2_support_keys = {(s['namespace'], s['concept']) for s in
        json.loads(entry.reviewed_entry_json)['support_occurrences']} if isinstance(entry, CVXCapexScopePolicyEntry) else set()
    for ordinal, f in enumerate(filing_xbrl.facts):
        if ((f.namespace, f.concept) not in v2_support_keys
                and not re.search(r"purchases|payments|capital|property|equipment|lease|acquis|proceeds|incentive", f.concept, re.I)):
            continue
        c = contexts.get(f.context_id)
        if c is None:
            raise CapexScopePolicyError("Missing Capex fact context")
        if (f.start != c.start or f.end != c.end or f.dimensions != c.dimensions
                or f.source_url != filing_xbrl.source_url
                or f.accession_number != entry.accession_number):
            raise CapexScopePolicyError("Broken Capex context/source/accession linkage")
        if ((f.unit_ref is not None and (f.unit != units.get(f.unit_ref) or f.unit is None))
                or (f.unit_ref is None and f.unit is not None)):
            raise CapexScopePolicyError("Broken Capex unit linkage")
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
        if (entity and period and (concept or relevant_support)
                and (not isinstance(entry, CVXCapexScopePolicyEntry)
                     or (not f.dimensions and (_usd(f) or f.unit is None)))):
            if isinstance(entry, CVXCapexScopePolicyEntry) and concept and not f.dimensions:
                if f.is_nil and (f.numeric_value is not None or f.raw_value not in (None, '')):
                    raise CapexScopePolicyError('Contradictory CVX nil representation')
                if not f.is_nil:
                    try:
                        if Decimal(f.raw_value) != f.numeric_value:
                            raise CapexScopePolicyError('Inconsistent CVX raw numeric representation')
                    except (TypeError, ArithmeticError, ValueError) as exc:
                        raise CapexScopePolicyError('Malformed CVX raw numeric representation') from exc
            if not f.is_nil and (f.unit_ref is None or f.unit is None):
                raise CapexScopePolicyError("Missing Capex numeric unit linkage")
            signature = (f.namespace, f.concept, f.start, f.end, f.dimensions,
                         f.unit.numerator_measures if f.unit else None,
                         f.unit.denominator_measures if f.unit else None)
            nil_statuses.setdefault(signature, set()).add(f.is_nil)
            if not f.is_nil and (not isinstance(f.numeric_value, Decimal)
                               or not f.numeric_value.is_finite()):
                raise CapexScopePolicyError("Malformed Capex numeric evidence")
        for s in entry.support:
            if (entity and period and f.namespace == s.namespace and f.concept == s.concept
                    and f.dimensions == s.dimensions and _usd(f) and not f.is_nil):
                support_matches[s].append((ordinal, f, c))
                reason = "REVIEWED_SCOPE_SUPPORT"
        if reason == "ELIGIBLE":
            eligible.append((ordinal, f, c))
        audit.append(CapexOccurrenceAudit(ordinal, f, c, reason))
    if any(len(statuses) > 1 for statuses in nil_statuses.values()):
        raise CapexScopePolicyError("Capex nil/numeric collision")
    candidates = tuple(_compact(_evidence(f, c, filing_xbrl, i))
                       for i, (_, f, c) in enumerate(eligible, 1))
    values = {f.numeric_value for _, f, _ in eligible}
    if len(values) > 1:
        return AmbiguousHistoricalMetric(FinancialMetric.CAPEX,
                                        AmbiguityReason.CONFLICTING_CONCEPT_VALUES, candidates)
    if not values:
        return direct_result
    if (isinstance(direct_result, NormalizedHistoricalValue)
            and values != {Decimal(str(direct_result.value))}):
        return AmbiguousHistoricalMetric(
            FinancialMetric.CAPEX, AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
            (direct_result.chosen_source, *direct_result.confirming_sources, *candidates),
        )
    if values != {entry.expected_value}:
        return (replace(direct_result, reason=MissingReason.CURATED_CAPEX_EVIDENCE_MISMATCH)
                if isinstance(direct_result, MissingHistoricalMetric) else direct_result)
    for s, matches in support_matches.items():
        if not matches:
            return direct_result
        if any(f.numeric_value != s.expected_value or f.decimals != s.decimals
               for _, f, _ in matches):
            return (replace(direct_result, reason=MissingReason.CURATED_CAPEX_EVIDENCE_MISMATCH)
                    if isinstance(direct_result, MissingHistoricalMetric) else direct_result)
        support.extend(_evidence(f, c, filing_xbrl, i)
                       for i, (_, f, c) in enumerate(matches, 1))
    provenance = HistoricalPolicyProvenance(
        policy.policy_id, policy.version, entry.economic_scope, company_cik,
        entry.accession_number, entry.report_date, entry.annual_start, entry.annual_end,
        entry.taxonomy, entry.concept, entry.unit, entry.reviewed_evidence,
        tuple(_evidence(f, c, filing_xbrl, i) for i, (_, f, c) in enumerate(eligible, 1)),
        None,
        CapexScopeAudit(entry.reviewed_entry_json, artifacts.digests,
                       tuple(o for o, _, _ in eligible), tuple(support), tuple(audit)),
    )
    if isinstance(direct_result, NormalizedHistoricalValue):
        if Decimal(str(direct_result.value)) != entry.expected_value:
            return AmbiguousHistoricalMetric(
                FinancialMetric.CAPEX, AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
                (direct_result.chosen_source, *direct_result.confirming_sources, *candidates),
            )
        return replace(direct_result, confirming_sources=(
            *direct_result.confirming_sources, *candidates), policy_provenance=provenance)
    if not isinstance(direct_result, MissingHistoricalMetric):
        raise CapexScopePolicyError("Invalid Capex direct result")
    return NormalizedHistoricalValue(
        FinancialMetric.CAPEX, entry.expected_value, "USD",
        HistoricalPeriod(entry.annual_start, entry.annual_end),
        candidates[0], candidates[1:], provenance,
    )


def validate_capex_scope_provenance(provenance):
    """Reject incomplete, foreign or reordered audit payloads at output boundary."""
    audit = provenance.capex_scope
    policy = next((p for p in CAPEX_SCOPE_POLICY_CATALOG.policies
                   if p.version == provenance.policy_version), None)
    entry = next((e for e in policy.entries
                  if e.accession_number == provenance.accession_number), None) if policy else None
    if (entry is None or audit is None
            or provenance.policy_id != CAPEX_SCOPE_POLICY_ID
            or policy is None
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
        raise CapexScopePolicyError("Invalid Capex policy/audit provenance")
    ordinals = tuple(o.original_instance_ordinal for o in audit.occurrences)
    if (ordinals != tuple(sorted(set(ordinals)))
            or any(type(o) is not int or o < 0 for o in ordinals)):
        raise CapexScopePolicyError("Invalid original Capex occurrence order")
    eligible = tuple(o for o in audit.occurrences if o.disposition == "ELIGIBLE")
    if (tuple(o.original_instance_ordinal for o in eligible)
            != audit.confirming_original_ordinals
            or not eligible or audit.supporting_facts
            or len(eligible) != len(provenance.filing_xbrl_evidence)):
        raise CapexScopePolicyError("Lost Capex confirming occurrence multiplicity")
    for index, (o, e) in enumerate(zip(eligible, provenance.filing_xbrl_evidence), 1):
        f, c = o.fact, o.context
        if policy.version == '2' and (e.occurrence_ordinal != index or e.is_nil != f.is_nil
                or e.entity_identifier != c.entity_identifier
                or e.entity_identifier_scheme != c.entity_identifier_scheme):
            raise CapexScopePolicyError('Changed CVX confirming occurrence provenance')
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
                or f.source_url != entry.instance_url or f.accession_number != entry.accession_number
                or c.context_id != f.context_id or c.start != f.start or c.end != f.end
                or c.dimensions != f.dimensions or e.value != entry.expected_value
                or e.namespace != entry.namespace or e.concept != entry.concept
                or e.unit != 'USD' or e.dimensions or e.is_nil
                or e.start != entry.annual_start or e.end != entry.annual_end
                or e.observation_filed != entry.filed
                or e.primary_document != entry.primary_document):
            raise CapexScopePolicyError("Inconsistent Capex occurrence provenance")
    for s in entry.support:
        matches = tuple(e for e in audit.supporting_facts
                        if e.namespace == s.namespace and e.concept == s.concept
                        and e.dimensions == s.dimensions)
        if not matches or any(e.value != s.expected_value or e.decimals != s.decimals
                              or e.is_nil or e.unit != "USD"
                              or e.start != entry.annual_start or e.end != entry.annual_end
                              or e.accession_number != entry.accession_number
                              for e in matches):
            raise CapexScopePolicyError("Incomplete Capex separately typed asset support")
