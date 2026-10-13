"""Structural retained-evidence inspection, with no financial acceptance.

Callers supply exact identities and selectors plus their own role/scope and
unresolved requirements. Matching is not proof of economic equivalence, coverage
or non-overlap. This module knows no issuer, metric policy, registry or adapter.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import hashlib
import json
import re
from types import MappingProxyType
from typing import Mapping

from . import historical_inputs as h
from .cash_flow_inputs import Receipt, _instance
from ..sec import filing_xbrl as x


@dataclass(frozen=True)
class ArtifactBinding:
    url: str
    sha256: str
    role: str  # instance or support; exact expected body, not a new receipt
    digest_type: str = 'sha256_sec_response_body_bytes'

    def __post_init__(self):
        if (not isinstance(self.url, str) or not self.url.strip() or not re.fullmatch(r'[0-9a-f]{64}', self.sha256)
                or self.role not in ('instance', 'support') or self.digest_type != 'sha256_sec_response_body_bytes'):
            raise h.InputError('Explicit original-body artifact binding required')


@dataclass(frozen=True)
class Selector:
    namespace: str
    concept: str
    dimensions: tuple[str, ...]  # () explicitly selects nondimensional facts

    def __post_init__(self):
        h._text(self.namespace); h._text(self.concept); h._strings(self.dimensions)


@dataclass(frozen=True)
class SelectionSpec:
    field_id: str
    selectors: tuple[Selector, ...]
    period_kind: str  # annual duration or fiscal-year-end instant
    unit: str
    role: str
    scope: str
    unresolved_requirements: tuple[str, ...]

    def __post_init__(self):
        for value in (self.field_id, self.role, self.scope): h._text(value)
        if (type(self.selectors) is not tuple or not self.selectors or any(type(s) is not Selector for s in self.selectors)
                or len(set(self.selectors)) != len(self.selectors) or self.period_kind not in ('annual', 'instant') or self.unit != 'USD'):
            raise h.InputError('Explicit unique monetary selectors and annual/instant mode required')
        h._strings(self.unresolved_requirements)


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
    normalized_unit: str = 'USD'
    dimensions: tuple[str, ...] = ()
    nil: bool = False


@dataclass(frozen=True)
class Candidate:
    namespace: str
    concept: str
    value: Decimal  # raw source USD, scale 1; no output sign/economic conversion
    precision: str
    occurrences: tuple[Occurrence, ...]
    evidence_references: tuple[h.SourceReference, ...]


@dataclass(frozen=True)
class Evidence:
    period: h.Period
    receipts: tuple[Receipt, ...]
    instance: Receipt | None
    namespaces: Mapping[str, str]
    contexts: Mapping[str, x.FilingXBRLContext]
    facts: tuple[tuple[x.FilingXBRLFact, int], ...]
    unresolved_requirements: tuple[str, ...]


@dataclass(frozen=True)
class Inspection:
    specification: 'SelectionSpec | InstantObservationSpec'
    candidates: tuple[Candidate, ...]
    evidence_receipts: tuple[Receipt, ...]
    competing_values: tuple[Decimal, ...]  # unequal observed values, not a financial decision
    unresolved_requirements: tuple[str, ...]


@dataclass(frozen=True)
class InstantObservationSpec:
    """Explicit observed instant and unit, without year-end/class equivalence."""
    field_id: str
    selectors: tuple[Selector, ...]
    as_of: date
    unit: str
    role: str
    scope: str
    unresolved_requirements: tuple[str, ...]

    def __post_init__(self):
        for v in (self.field_id,self.role,self.scope): h._text(v)
        if (type(self.as_of) is not date or self.unit not in ('USD','shares') or
                type(self.selectors) is not tuple or not self.selectors or
                any(type(s) is not Selector for s in self.selectors) or len(set(self.selectors))!=len(self.selectors)):
            raise h.InputError('Explicit observation date/unit and unique selectors required')
        h._strings(self.unresolved_requirements)


def dimensions(context):
    """Expanded dimension/member identity; never interpreted as economic scope."""
    return tuple(f'{{{d.dimension.namespace}}}{d.dimension.local_name}=' +
        (f'{{{d.explicit_member.namespace}}}{d.explicit_member.local_name}' if d.explicit_member else d.typed_member_xml)
        for d in context.dimensions)


def prepare(period, receipts, bindings):
    """Bind original receipts and replay existing DEI/context/unit/fact parsers.

Missing required bodies are explicit requirements, not reconstructed receipts.
Conflicting identities or corrupt structural evidence fail. No network or store.
"""
    if (type(period) is not h.Period or type(receipts) is not tuple or any(type(r) is not Receipt for r in receipts)
            or type(bindings) is not tuple or not bindings or any(type(b) is not ArtifactBinding for b in bindings)
            or len({b.url for b in bindings}) != len(bindings) or sum(b.role == 'instance' for b in bindings) != 1):
        raise h.InputError('Exact period, receipts and one instance binding required')
    if len({r.artifact.url for r in receipts}) != len(receipts):
        raise h.InputError('Duplicate retained artifact URL')
    for r in receipts:
        if (r.artifact.accession != period.accession or hashlib.sha256(r.artifact.body).hexdigest() != r.artifact.sha256
                or r.byte_length != len(r.artifact.body)):
            raise h.InputError('Retained source identity/body/receipt length mismatch')
    bound = []; missing = []; instance = None
    for b in bindings:
        r = next((r for r in receipts if r.artifact.url == b.url), None)
        if r is None:
            missing.append('Missing retained ' + b.role + ' body: ' + b.url); continue
        if r.artifact.sha256 != b.sha256:
            raise h.InputError('Expected original-body digest differs from retained receipt')
        bound.append(r)
        if b.role == 'instance': instance = r
    ns = {}; contexts = {}; facts = ()
    if instance is not None:
        root, _, _, ns = _instance((instance,), period)
        contexts = {c.context_id: c for c in x._parse_contexts(root, ns)}
        units = {u.unit_id: u for u in x._parse_units(root, ns)}
        parsed = x._parse_facts(root, contexts, units, period.accession, instance.artifact.url)
        facts = tuple(zip(parsed, (i for i,e in enumerate(root) if e.get('contextRef') is not None)))
    return Evidence(period, tuple(bound), instance, MappingProxyType(ns), MappingProxyType(contexts), facts, tuple(missing))


def inspect(evidence, specification):
    """Group only exact supplied signatures; return observations, never selection.

Context/unit IDs may differ when all specified semantic fields match. Original
precision/representations remain separate candidates, regardless of equality.
No concept-name classifications, zero inference, completeness or sum permission.
"""
    if type(evidence) is not Evidence or type(specification) is not SelectionSpec:
        raise h.InputError('Prepared retained evidence and explicit selection specification required')
    start=evidence.period.annual_start if specification.period_kind=='annual' else None
    return _inspect_at(evidence,specification,start,evidence.period.annual_end)


def inspect_instant(evidence,specification):
    """Observe the supplied actual date/class; never choose a cover date or sum."""
    if type(evidence) is not Evidence or type(specification) is not InstantObservationSpec:
        raise h.InputError('Prepared evidence and explicit instant observation specification required')
    return _inspect_at(evidence,specification,None,specification.as_of)


def _inspect_at(evidence,specification,start,end):
    p = evidence.period; groups = {}
    selectors = {(s.namespace, s.concept, frozenset(s.dimensions)) for s in specification.selectors}
    measure=(x.FilingXBRLQName('http://www.xbrl.org/2003/instance','shares') if specification.unit=='shares' else
             x.FilingXBRLQName('http://www.xbrl.org/2003/iso4217','USD'))
    for fact, ordinal in evidence.facts:
        c = evidence.contexts[fact.context_id]
        ds = dimensions(c)
        if ((fact.namespace, fact.concept, frozenset(ds)) not in selectors or c.start != start or c.end != end
                or c.entity_identifier_scheme != 'http://www.sec.gov/CIK' or int(c.entity_identifier) != p.cik): continue
        if (fact.is_nil or fact.numeric_value is None or fact.unit is None or fact.unit.denominator_measures
                or fact.unit.numerator_measures != (measure,)
                or not re.fullmatch(r'INF|-?\d+', fact.decimals or '')):
            raise h.InputError('Eligible fact requires non-nil exact '+specification.unit+' numeric/precision evidence')
        o = Occurrence(fact.namespace, fact.concept, c.context_id, p.cik, c.start, c.end, fact.unit_ref,
            fact.raw_value, fact.decimals, ordinal, normalized_unit=specification.unit, dimensions=ds)
        key = (fact.namespace, fact.concept, fact.numeric_value, fact.decimals, tuple(sorted(ds)))
        groups.setdefault(key, []).append(o)
    candidates = []
    for (namespace, concept, value, precision, _), occurrences in groups.items():
        refs = tuple(h.SourceReference(f'{p.accession}:{specification.field_id}:ordinal-{o.ordinal}', p,
            evidence.instance, json.dumps(dict(field_id=specification.field_id, supplied_role=specification.role,
                supplied_scope=specification.scope, unit_id=o.unit_id, nil=o.nil,
                inspection_only=True, scale=1, sign=1), sort_keys=True), namespace, concept, o.context_id,
            o.ordinal, o.start, o.end, specification.unit, o.raw_value, o.decimals, o.dimensions) for o in occurrences)
        candidates.append(Candidate(namespace, concept, value, precision, tuple(occurrences), refs))
    values = tuple(dict.fromkeys(c.value for c in candidates))
    requirements = evidence.unresolved_requirements + specification.unresolved_requirements
    if not candidates: requirements += ('No eligible exact-period observation for ' + specification.field_id + '; absence is not zero.',)
    if len(values) > 1: requirements += ('Competing unequal observed values for ' + specification.field_id + '; selection remains outside inspection.',)
    return Inspection(specification, tuple(candidates), evidence.receipts, values if len(values) > 1 else (), requirements)
