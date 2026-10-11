"""Isolated reported input packaging; only statement reconciliation arithmetic.

No retrieval, adjusted cash-flow subtotal, historical policy or valuation consumer.
The two reviewed registrations are explicit opt-in, never a ticker fallback.
"""

from __future__ import annotations

import base64
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal, localcontext
from enum import Enum
import gzip
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zlib

from valuation_platform.analyst.nwc import Artifact, Period


class CashFlowInputError(ValueError):
    """Incomplete, unreviewed, structurally invalid or inconsistent packaging."""


class InputKind(str, Enum):
    CASH_SUBTOTAL = "cash_subtotal"
    CASH_PAYMENT = "cash_payment"
    ACCRUED_EXPENSE = "accrued_expense"
    ACCRUED_INCOME = "accrued_income"
    ACCRUED_TAX_BENEFIT = "accrued_tax_benefit"
    NONCASH_EXPENSE = "noncash_expense"
    NONCASH_ADDITION = "noncash_addition"
    BOOK_BALANCE = "book_balance"
    RECONCILIATION = "reported_reconciliation_item"
    CASH_FX = "cash_reconciliation_effect"


def _text(value: object) -> None:
    if type(value) is not str or not value.strip():
        raise CashFlowInputError("Explicit nonempty identity/scope required")


def _tuple(value: object, cls: type, *, required: bool = True) -> None:
    if type(value) is not tuple or (required and not value) or any(type(v) is not cls for v in value):
        raise CashFlowInputError("Immutable typed entries required")


@dataclass(frozen=True)
class Receipt:
    artifact: Artifact
    byte_length: int
    retrieved_at_utc: str
    http_status: int
    retrieval_mode: str

    def __post_init__(self) -> None:
        if (type(self.artifact) is not Artifact or type(self.byte_length) is not int
                or self.byte_length != len(self.artifact.body)
                or type(self.http_status) is not int or self.http_status != 200):
            raise CashFlowInputError("Verified original response and retrieval metadata required")
        _text(self.retrieved_at_utc)
        _text(self.retrieval_mode)
        try:
            stamp = datetime.fromisoformat(self.retrieved_at_utc)
            if stamp.utcoffset() is None or stamp.utcoffset().total_seconds() != 0:
                raise ValueError("UTC required")
        except ValueError as exc:
            raise CashFlowInputError("Explicit UTC retrieval time required") from exc


@dataclass(frozen=True)
class Occurrence:
    namespace: str
    concept: str
    context_id: str
    entity_cik: int
    start: date | None
    end: date
    unit_id: str
    raw_value: str
    decimals: str
    ordinal: int
    normalized_unit: str = "USD"
    dimensions: tuple[str, ...] = ()
    nil: bool = False

    def __post_init__(self) -> None:
        for v in (self.namespace, self.concept, self.context_id, self.unit_id,
                  self.raw_value, self.decimals):
            _text(v)
        if (type(self.entity_cik) is not int or self.entity_cik <= 0
                or type(self.end) is not date or self.start is not None and type(self.start) is not date
                or self.start is not None and self.start > self.end
                or type(self.ordinal) is not int or self.ordinal < 0
                or self.normalized_unit != "USD" or self.dimensions != ()
                or type(self.dimensions) is not tuple or self.nil is not False
                or not re.fullmatch(r"INF|-?\d+", self.decimals)):
            raise CashFlowInputError("Invalid non-nil nondimensional exact-USD occurrence")
        try:
            if not Decimal(self.raw_value).is_finite():
                raise ValueError("Nonfinite")
        except Exception as exc:
            raise CashFlowInputError("Finite raw numeric representation required") from exc


@dataclass(frozen=True)
class ReportedInput:
    input_id: str
    kind: InputKind
    value_usd: Decimal
    display_multiplier: int
    location_and_scope: str
    occurrences: tuple[Occurrence, ...]
    source_kind: str = "sec_reported"

    def __post_init__(self) -> None:
        _text(self.input_id)
        _text(self.location_and_scope)
        _tuple(self.occurrences, Occurrence)
        if (type(self.kind) is not InputKind or type(self.value_usd) is not Decimal
                or not self.value_usd.is_finite() or type(self.display_multiplier) is not int
                or self.display_multiplier not in (-1, 1) or self.source_kind != "sec_reported"):
            raise CashFlowInputError("Reported point, role and explicit sign required")
        first = self.occurrences[0]
        if self.input_id != first.concept or any((o.namespace, o.concept, o.entity_cik, o.start, o.end) !=
               (first.namespace, first.concept, first.entity_cik, first.start, first.end)
               or Decimal(o.raw_value) != self.value_usd for o in self.occurrences):
            raise CashFlowInputError("Conflicting or different-scope occurrences cannot confirm")
        ordinals = tuple(o.ordinal for o in self.occurrences)
        if ordinals != tuple(sorted(set(ordinals))):
            raise CashFlowInputError("Retain unique deterministic occurrence order")

    @property
    def displayed_value_usd(self) -> Decimal:
        # copy_negate is exact even under an unusually small ambient context.
        return self.value_usd if self.display_multiplier == 1 else self.value_usd.copy_negate()


@dataclass(frozen=True)
class UnknownInput:
    input_id: str
    status: str
    reason: str
    value_usd: None = None

    def __post_init__(self) -> None:
        _text(self.input_id)
        _text(self.reason)
        if self.status not in ("unavailable", "unresolved_scope") or self.value_usd is not None:
            raise CashFlowInputError("Unknown inputs are not estimates or zeros")


_XI = "{http://www.xbrl.org/2003/instance}"
_CFO = "NetCashProvidedByUsedInOperatingActivities"
_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_PATH = _ROOT / "docs/company-data-preparation/msft-reported-cash-flow-bundles.json"
_REGISTRY_SHA256 = "c3c35e020066f0887d9d8fe493f975afe9e6f0ea4b1785d2f341691ebb49d993"
_CONTRACT = "reviewed-msft-reported-cash-flow-inputs"
_SCHEMA = "reported-cash-flow-input-bundle-v1"


def _instance(receipts: tuple[Receipt, ...], period: Period):
    sources = [r.artifact for r in receipts if r.artifact.url.endswith("_htm.xml")]
    if len(sources) != 1:
        raise CashFlowInputError("One exact extracted instance required")
    a = sources[0]
    if b"<!DOCTYPE" in a.body.upper() or b"<!ENTITY" in a.body.upper():
        raise CashFlowInputError("Unsafe instance")
    root = ET.fromstring(a.body)
    if root.tag != _XI + "xbrl":
        raise CashFlowInputError("Extracted instance required")
    namespaces = dict(item for _, item in ET.iterparse(BytesIO(a.body), events=["start-ns"]))
    contexts = {c.attrib["id"]: c for c in root.findall(_XI + "context")}
    units = {u.attrib["id"]: u for u in root.findall(_XI + "unit")}
    if (len(contexts) != len(root.findall(_XI + "context"))
            or len(units) != len(root.findall(_XI + "unit"))):
        raise CashFlowInputError("Duplicate context/unit IDs")
    forms = {f.text for f in root if f.tag.startswith("{http://xbrl.sec.gov/dei/")
             and f.tag.endswith("}DocumentType")}
    annuals = set()
    for f in root:
        if (f.tag.startswith("{http://xbrl.sec.gov/dei/")
                and f.tag.endswith("}DocumentFiscalPeriodFocus") and f.text == "FY"):
            c = contexts[f.attrib["contextRef"]]
            if (_context(c) == (period.cik, period.annual_start, period.annual_end)):
                annuals.add(period.annual_start)
    if forms != {"10-K"} or annuals != {period.annual_start}:
        raise CashFlowInputError("Source must establish exact non-amended FY context")
    return root, contexts, units, namespaces


def _context(c):
    if c.find(".//" + _XI + "segment") is not None or c.find(".//" + _XI + "scenario") is not None:
        return None  # Dimensioned source facts remain in the body, not eligible.
    identifiers = c.findall(".//" + _XI + "identifier")
    p = c.find(_XI + "period")
    if len(identifiers) != 1 or identifiers[0].get("scheme") != "http://www.sec.gov/CIK":
        raise CashFlowInputError("Invalid entity identity")
    start = p.findtext(_XI + "startDate")
    end = p.findtext(_XI + "endDate")
    instant = p.findtext(_XI + "instant")
    if (instant is not None and (start is not None or end is not None)
            or instant is None and (start is None or end is None)):
        raise CashFlowInputError("Invalid period structure")
    return (int(identifiers[0].text), date.fromisoformat(start) if start else None,
            date.fromisoformat(instant or end))


def _occurrences(root, contexts, units, namespaces, namespace, concept, period, instant):
    expected = (period.cik, None if instant else period.annual_start, period.annual_end)
    result = []
    for ordinal, f in enumerate(root):
        if f.tag != "{" + namespace + "}" + concept:
            continue
        c = contexts[f.attrib["contextRef"]]  # Broken links are errors, not omission.
        if _context(c) != expected:
            continue
        measures = list(units[f.attrib["unitRef"]])
        if len(measures) != 1 or measures[0].tag != _XI + "measure":
            raise CashFlowInputError("Exact USD measure required")
        prefix, name = measures[0].text.split(":")
        if namespaces[prefix] != "http://www.xbrl.org/2003/iso4217" or name != "USD":
            raise CashFlowInputError("Eligible source is not exact USD")
        if f.get("{http://www.w3.org/2001/XMLSchema-instance}nil", "false") not in ("false", "0"):
            raise CashFlowInputError("Nil/numeric source collision")
        result.append(Occurrence(namespace, concept, f.attrib["contextRef"], expected[0],
                                 expected[1], expected[2], f.attrib["unitRef"], f.text,
                                 f.attrib["decimals"], ordinal))
    return tuple(result)


@dataclass(frozen=True)
class ReportedCashFlowBundle:
    bundle_id: str
    version: str
    period: Period
    review_author: str
    reviewed_on: date
    evidence_reference: str
    artifacts: tuple[Receipt, ...]
    inputs: tuple[ReportedInput, ...]
    unknowns: tuple[UnknownInput, ...]
    cfo_terms: tuple[str, ...]
    limitations: tuple[str, ...]
    is_complete_operating_nwc: bool = False
    valuation_consumption_approved: bool = False

    def __post_init__(self) -> None:
        for s in (self.bundle_id, self.version, self.review_author, self.evidence_reference):
            _text(s)
        for seq, cls in ((self.artifacts, Receipt), (self.inputs, ReportedInput),
                         (self.unknowns, UnknownInput), (self.cfo_terms, str), (self.limitations, str)):
            _tuple(seq, cls)
        for s in self.cfo_terms + self.limitations:
            _text(s)
        if (type(self.period) is not Period or type(self.reviewed_on) is not date
                or self.is_complete_operating_nwc is not False
                or self.valuation_consumption_approved is not False):
            raise CashFlowInputError("Historical preparation only; no certification")
        identities = [v.input_id for v in self.inputs + self.unknowns]
        if len(identities) != len(set(identities)) or len(set(self.cfo_terms)) != len(self.cfo_terms):
            raise CashFlowInputError("Duplicate input/unknown/reconciliation identity")
        if (len(self.artifacts) != 2 or len({r.artifact.url for r in self.artifacts}) != 2
                or any(r.artifact.accession != self.period.accession or
                       int(r.artifact.url.split('/data/')[1].split('/')[0]) != self.period.cik
                       for r in self.artifacts)
                or sum(r.artifact.url.endswith('.htm') for r in self.artifacts) != 1):
            raise CashFlowInputError("Exact selected primary and instance required")
        try:
            source = _instance(self.artifacts, self.period)
            for value in self.inputs:
                first = value.occurrences[0]
                if _occurrences(*source, first.namespace, first.concept, self.period,
                                first.start is None) != value.occurrences:
                    raise CashFlowInputError("Retain every exact eligible source occurrence")
            terms = tuple(self.input(k) for k in self.cfo_terms)
            if any(t.kind not in (InputKind.ACCRUED_INCOME, InputKind.RECONCILIATION) for t in terms):
                raise CashFlowInputError("Only reported CFO reconciliation operands allowed")
            if self.input(_CFO).kind is not InputKind.CASH_SUBTOTAL:
                raise CashFlowInputError("Reported CFO subtotal required")
            if not self.cfo_reconciles:
                raise CashFlowInputError("Reported CFO bridge does not reconcile")
        except (ET.ParseError, KeyError, IndexError, ValueError, TypeError, AttributeError) as exc:
            raise CashFlowInputError("Invalid source/input/statement binding") from exc

    def input(self, input_id: str) -> ReportedInput:
        for value in self.inputs:
            if value.input_id == input_id:
                return value
        raise CashFlowInputError("Input unavailable; never inferred zero")

    @property
    def cfo_reconciles(self) -> bool:
        values = tuple(self.input(k).displayed_value_usd for k in self.cfo_terms)
        with localcontext() as ctx:
            ctx.prec = max(28, sum(len(v.as_tuple().digits) + abs(v.as_tuple().exponent)
                                   for v in values) + 10)
            return sum(values, Decimal(0)) == self.input(_CFO).value_usd


def _registry():
    body = _REGISTRY_PATH.read_bytes()
    if hashlib.sha256(body).hexdigest() != _REGISTRY_SHA256:
        raise CashFlowInputError("Immutable reviewed registry changed; new version/review required")
    return json.loads(body)


def registered_bundle_ids() -> tuple[str, ...]:
    return tuple(b['bundle_id'] for b in _registry()['bundles'])


def _spec(bundle_id: str):
    doc = _registry()
    for spec in doc['bundles']:
        if spec['bundle_id'] == bundle_id:
            return doc, spec
    raise CashFlowInputError("Only two reviewed exact-period bundles registered")


def _build(doc, spec, receipts):
    p = spec['period']
    period = Period(p['cik'], p['accession'], date.fromisoformat(p['annual_start']),
                    date.fromisoformat(p['annual_end']), spec['form'])
    source = _instance(receipts, period)
    inputs = []
    for value in spec['inputs']:
        instant = value['kind'] == InputKind.BOOK_BALANCE.value
        occurrences = _occurrences(*source, value['namespace'], value['input_id'], period, instant)
        expected_context = spec['instant_context_id'] if instant else spec['annual_context_id']
        if (tuple(o.ordinal for o in occurrences) != tuple(value['ordinals'])
                or any(o.context_id != expected_context or o.unit_id != 'U_USD'
                       or o.decimals != value['decimals'] for o in occurrences)):
            raise CashFlowInputError("Occurrences differ from exact reviewed registry")
        inputs.append(ReportedInput(value['input_id'], InputKind(value['kind']),
                                    Decimal(value['value_usd']), value['display_multiplier'],
                                    value['location_and_scope'], occurrences))
    return ReportedCashFlowBundle(spec['bundle_id'], doc['version'], period,
                                  doc['review_author'], date.fromisoformat(doc['reviewed_on']),
                                  doc['evidence_reference'], receipts, tuple(inputs),
                                  tuple(UnknownInput(**u) for u in spec['unknowns']),
                                  tuple(spec['cfo_terms']), tuple(spec['limitations']))


def load_msft_bundle(bundle_id: str) -> ReportedCashFlowBundle:
    """Explicit opt-in to a reviewed retained bundle; performs no network access."""
    try:
        doc, spec = _spec(bundle_id)
        for key in ('inventory', 'artifact_manifest'):
            if hashlib.sha256((_ROOT / doc[key + '_path']).read_bytes()).hexdigest() != doc[key + '_sha256']:
                raise CashFlowInputError("Retained evidence reference changed")
        rows = json.loads((_ROOT / doc['inventory_path']).read_text())['rows']
        row = next(r for r in rows if all(r[k] == v for k, v in spec['period'].items()))
        if (row['ticker'] != 'MSFT' or {r['source_url'] for r in spec['artifacts']} !=
                {row['primary_url'], row['instance_url']}):
            raise CashFlowInputError("Not the frozen selected filing")
        manifest = json.loads((_ROOT / doc['artifact_manifest_path']).read_text())
        receipts = []
        for ref in spec['artifacts']:
            entries = [a for a in manifest['artifacts'] if a['source_url'] == ref['source_url']]
            if len(entries) != 1 or any(entries[0][k] != v for k, v in ref.items()):
                raise CashFlowInputError("Original artifact metadata mismatch")
            if entries[0]['storage_encoding'] != 'gzip_base64':
                raise CashFlowInputError("Unsupported retained body encoding")
            body = gzip.decompress(base64.b64decode(entries[0]['response_body_gzip_base64'], validate=True))
            receipts.append(_receipt(ref, body))
        return _build(doc, spec, tuple(receipts))
    except (OSError, EOFError, zlib.error, StopIteration, KeyError, ValueError, TypeError, ET.ParseError) as exc:
        raise CashFlowInputError("Cannot bind reviewed retained bundle") from exc


def _receipt(ref, body):
    return Receipt(Artifact(ref['source_url'], ref['accession'], ref['representation'],
                            ref['digest_type'], ref['sha256'], body), ref['byte_length'],
                   ref['retrieved_at_utc'], ref['http_status'], ref['retrieval_mode'])


def _occurrence_dict(o):
    return {**asdict(o), 'start': o.start.isoformat() if o.start else None,
            'end': o.end.isoformat(), 'dimensions': list(o.dimensions)}


def _view(bundle):
    return {'bundle_id': bundle.bundle_id, 'version': bundle.version,
            'period': {'cik': bundle.period.cik, 'accession': bundle.period.accession,
                       'annual_start': bundle.period.annual_start.isoformat(),
                       'annual_end': bundle.period.annual_end.isoformat(), 'form': bundle.period.form},
            'review_author': bundle.review_author, 'reviewed_on': bundle.reviewed_on.isoformat(),
            'evidence_reference': bundle.evidence_reference,
            'inputs': [{'input_id': i.input_id, 'kind': i.kind.value, 'source_kind': i.source_kind,
                        'value_usd': str(i.value_usd), 'display_multiplier': i.display_multiplier,
                        'displayed_value_usd': str(i.displayed_value_usd),
                        'location_and_scope': i.location_and_scope,
                        'occurrences': [_occurrence_dict(o) for o in i.occurrences]} for i in bundle.inputs],
            'unknowns': [asdict(u) for u in bundle.unknowns], 'cfo_terms': list(bundle.cfo_terms),
            'limitations': list(bundle.limitations), 'cfo_reconciles': bundle.cfo_reconciles,
            'is_complete_operating_nwc': bundle.is_complete_operating_nwc,
            'valuation_consumption_approved': bundle.valuation_consumption_approved}


def serialize(bundle: ReportedCashFlowBundle) -> str:
    """Separate schema; original bodies included once each, not per occurrence."""
    if type(bundle) is not ReportedCashFlowBundle:
        raise CashFlowInputError("Reported input bundle required")
    doc, spec = _spec(bundle.bundle_id)
    expected = _build(doc, spec, bundle.artifacts)
    if bundle != expected:
        raise CashFlowInputError("Only exact reviewed bundles may be serialized by this contract")
    artifacts = []
    for receipt, ref in zip(bundle.artifacts, spec['artifacts']):
        if receipt != _receipt(ref, receipt.artifact.body):
            raise CashFlowInputError("Reviewed receipt metadata changed")
        artifacts.append({**ref, 'storage_encoding': 'gzip_base64',
                          'response_body_gzip_base64': base64.b64encode(
                              gzip.compress(receipt.artifact.body, mtime=0)).decode('ascii')})
    return json.dumps({'schema': _SCHEMA, 'contract': _CONTRACT,
                       'registry_sha256': _REGISTRY_SHA256, 'bundle': _view(bundle),
                       'artifacts': artifacts}, sort_keys=True, separators=(',', ':'))


def deserialize(payload: str) -> ReportedCashFlowBundle:
    """Verify raw bodies and exact review, then recompute the reported bridge."""
    try:
        def unique(pairs):
            d = {}
            for k, v in pairs:
                if k in d:
                    raise CashFlowInputError("Duplicate serialized key")
                d[k] = v
            return d
        data = json.loads(payload, object_pairs_hook=unique)
        if (set(data) != {'schema', 'contract', 'registry_sha256', 'bundle', 'artifacts'}
                or data['schema'] != _SCHEMA or data['contract'] != _CONTRACT
                or data['registry_sha256'] != _REGISTRY_SHA256):
            raise CashFlowInputError("Unknown separate serialization contract")
        doc, spec = _spec(data['bundle']['bundle_id'])
        if len(data['artifacts']) != len(spec['artifacts']):
            raise CashFlowInputError("Both reviewed original artifacts required")
        receipts = []
        for value, ref in zip(data['artifacts'], spec['artifacts']):
            if (set(value) != set(ref) | {'storage_encoding', 'response_body_gzip_base64'}
                    or any(value[k] != v for k, v in ref.items()) or value['storage_encoding'] != 'gzip_base64'):
                raise CashFlowInputError("Exact reviewed receipt required")
            body = gzip.decompress(base64.b64decode(value['response_body_gzip_base64'], validate=True))
            receipts.append(_receipt(ref, body))
        result = _build(doc, spec, tuple(receipts))
        # Canonical JSON comparison also rejects bool/int confusion and extra fields.
        if json.dumps(data['bundle'], sort_keys=True) != json.dumps(_view(result), sort_keys=True):
            raise CashFlowInputError("Serialized input/scope/unknown/summary differs from review")
        return result
    except (OSError, EOFError, zlib.error, KeyError, ValueError, TypeError, ET.ParseError) as exc:
        raise CashFlowInputError("Invalid reported input serialization") from exc
