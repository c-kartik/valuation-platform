"""Bounded retained-instance review for four pilot Revenue/EBIT mappings.

No retrieval, new concept semantics, derivation or change to frozen resolvers.
Structural parsing and annual-DEI checks reuse existing SEC/bundle code. The
reviewed face-statement locator is not a license to discard a conflicting fact.
"""

from dataclasses import dataclass
from decimal import Decimal
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path

from . import historical_inputs as h
from .cash_flow_inputs import _instance, Occurrence, ReportedInput, InputKind
from ..sec import filing_xbrl as x
from ..normalization.concepts import REVENUE_POLICY, OPERATING_INCOME_POLICY

EVIDENCE_PATH = Path(__file__).resolve().parents[3] / "docs/pilot-direct-income-evidence.json"
EVIDENCE_SHA256 = "efd4618955e56e17bd3a9b0b44374b501236151adcdefc04a4e661834844b274"
POLICIES = {h.Field.REVENUE: REVENUE_POLICY, h.Field.EBIT: OPERATING_INCOME_POLICY}


class _Inline(HTMLParser):
    """Read the one reviewed inline tag, not a label-based financial search."""
    def __init__(self, identity):
        super().__init__()
        self.identity, self.matches, self.active = identity, [], None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "ix:nonfraction" and attrs.get("id") == self.identity:
            self.active = [attrs, ""]

    def handle_data(self, data):
        if self.active is not None:
            self.active[1] += data

    def handle_endtag(self, tag):
        if tag == "ix:nonfraction" and self.active is not None:
            self.matches.append(self.active)
            self.active = None


@dataclass(frozen=True)
class Inspection:
    candidates: tuple[ReportedInput, ...]
    statement: dict
    selected: int | None
    reason: str | None


def entries():
    body = EVIDENCE_PATH.read_bytes()
    if hashlib.sha256(body).hexdigest() != EVIDENCE_SHA256:
        raise h.InputError("Reviewed direct-income evidence bytes changed")
    return json.loads(body)["entries"]


def inspect(source, field, review):
    """Retain every eligible signature; a conflict never becomes precedence.

The parser's structural helpers are used without constructing synthetic filing
dates or retrieval metadata. Ordinals remain original root-child positions,
matching existing reported bundles (not filtered-parser fact indexes).
"""
    if field not in POLICIES or source.period.form != "10-K":
        raise h.InputError("Only approved direct annual Revenue/OperatingIncomeLoss semantics")
    period = source.period
    identity = {"cik": period.cik, "accession": period.accession,
                "annual_start": str(period.annual_start), "annual_end": str(period.annual_end), "form": period.form}
    if review["bundle_id"] != source.bundle_id or review["period"] != identity or review["field"] != field.value:
        raise h.InputError("Exact reviewed source/period/field required")
    instance = next(r for r in source.artifacts if r.artifact.url.endswith("_htm.xml"))
    primary = next(r for r in source.artifacts if r.artifact.url.endswith(".htm"))
    if (instance.artifact.sha256 != review["instance_sha256"] or
            primary.artifact.sha256 != review["primary_sha256"] or
            instance.artifact.url != review["instance_url"] or primary.artifact.url != review["primary_url"] or
            review["digest_type"] != "sha256_sec_response_body_bytes"):
        raise h.InputError("Exact original response-body digests required")
    root, _, _, namespaces = _instance(source.artifacts, period)
    parsed_contexts = x._parse_contexts(root, namespaces)
    contexts = {c.context_id: c for c in parsed_contexts}
    units = {u.unit_id: u for u in x._parse_units(root, namespaces)}
    facts = x._parse_facts(root, contexts, units, period.accession, instance.artifact.url)
    elements = tuple(e for e in root if e.get("contextRef") is not None)
    ordinals = {id(e): i for i, e in enumerate(root)}
    groups = {}
    for fact, element in zip(facts, elements):
        if not any(key.taxonomy == "us-gaap" and key.name == fact.concept for key in POLICIES[field].candidates):
            continue
        if fact.namespace != namespaces.get("us-gaap") or not fact.namespace.startswith("http://fasb.org/us-gaap/"):
            continue
        c = contexts[fact.context_id]
        if (c.entity_identifier_scheme != "http://www.sec.gov/CIK" or
                int(c.entity_identifier) != period.cik or c.start != period.annual_start or
                c.end != period.annual_end or c.dimensions):
            continue
        if (fact.is_nil or fact.numeric_value is None or fact.unit is None or
                fact.unit.denominator_measures or fact.unit.numerator_measures !=
                (x.FilingXBRLQName("http://www.xbrl.org/2003/iso4217", "USD"),)):
            raise h.InputError("Eligible direct fact must be non-nil exact USD numeric evidence")
        o = Occurrence(fact.namespace, fact.concept, c.context_id, period.cik, c.start, c.end,
                       fact.unit_ref, fact.raw_value, fact.decimals, ordinals[id(element)])
        # Different precision/concept representations remain separate candidates,
        # each preserving its originals; only exact numeric agreement can confirm.
        key = (fact.namespace, fact.concept, fact.numeric_value, fact.decimals)
        groups.setdefault(key, []).append(o)
    candidates = tuple(ReportedInput(key[1], InputKind.ACCRUED_INCOME, key[2], 1,
        review["statement_scope"], tuple(occurrences)) for key, occurrences in groups.items())
    parser = _Inline(review["statement_id"])
    parser.feed(primary.artifact.body.decode("utf-8"))
    if len(parser.matches) != 1:
        raise h.InputError("One exact reviewed face-statement tag required")
    attrs, raw = parser.matches[0]
    expected = review["statement_attributes"]
    if any(attrs.get(k) != v for k, v in expected.items()) or raw.strip() != review["displayed_value"]:
        raise h.InputError("Reviewed statement representation changed")
    statement_value = Decimal(raw.strip().replace(",", "") + "e" + attrs["scale"])
    if attrs.get("sign") == "-":
        statement_value = statement_value.copy_negate()
    statement = dict(review, statement_value_usd=str(statement_value))
    matching = [i for i, item in enumerate(candidates) if item.value_usd == statement_value
                and item.input_id == attrs["name"].split(":")[1]
                and any(o.context_id == attrs["contextref"] and o.unit_id == attrs["unitref"]
                        and o.decimals == attrs["decimals"] for o in item.occurrences)]
    if not candidates:
        return Inspection((), statement, None, "No eligible exact annual direct fact")
    if len({item.value_usd for item in candidates}) != 1:
        return Inspection(candidates, statement, None, "Conflicting eligible direct values; no precedence or statement override")
    if len(matching) != 1:
        return Inspection(candidates, statement, None, "Eligible facts do not independently match reviewed face-statement representation")
    return Inspection(candidates, statement, matching[0], None)


def reviewed(source, field):
    review = next((e for e in entries() if e["bundle_id"] == source.bundle_id and e["field"] == field.value), None)
    if review is None:
        raise h.InputError("No new issuer or period approval")
    return inspect(source, field, review)


def binding(source, field, inspection=None):
    """Machine mapping of all eligible candidates, not counts-only provenance."""
    result = reviewed(source, field) if inspection is None else inspection
    if result.selected is None:
        raise h.InputError(result.reason)
    selected = result.candidates[result.selected]
    return {"input_id": selected.input_id, "origin": "reported", "role": "reported_revenue" if field is h.Field.REVENUE else "reported_operating_income",
            "population": field.value, "unit": "USD", "scale": 1, "sign": 1,
            "precision": selected.occurrences[0].decimals, "context_id": selected.occurrences[0].context_id,
            "occurrence_ordinals": [o.ordinal for o in selected.occurrences],
            "retained_direct": {"evidence_path": "docs/pilot-direct-income-evidence.json", "evidence_sha256": EVIDENCE_SHA256,
                "statement": result.statement, "selected": result.selected,
                "candidates": [{"namespace": i.occurrences[0].namespace, "concept": i.input_id,
                    "value_usd": str(i.value_usd), "occurrences": [o.__dict__ | {"start": str(o.start), "end": str(o.end), "dimensions": list(o.dimensions)} for o in i.occurrences]}
                    for i in result.candidates]}}
