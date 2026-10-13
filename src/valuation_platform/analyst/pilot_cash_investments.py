"""Four retained year-end component inventories, never a liquid-assets total.

Original receipts and bundles are reused; no generic policy or schema changes.
Combined/strategic/restricted populations remain distinct and cannot be summed.
"""

from dataclasses import dataclass, replace
from decimal import Decimal
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path

from . import historical_inputs as h
from .cash_flow_inputs import Occurrence, InputKind, ReportedInput
from . import retained_components as retained
from ..sec.filing_xbrl import FilingXBRLDataError
from ..normalization.balance_sheet import CASH_AND_CASH_EQUIVALENTS_POLICY, SHORT_TERM_INVESTMENTS_POLICY

EVIDENCE_PATH = Path(__file__).resolve().parents[3] / "docs/pilot-cash-investment-evidence.json"
EVIDENCE_SHA256 = "b9c1da7534ed8fb02530d6d2b8f8bbce22cbc0bede6079ca1b34b3fce3b7996d"


class _Tags(HTMLParser):
    """Nested inline facts share displayed text; retain each original identity."""
    def __init__(self):
        super().__init__(); self.tags = {}; self.stack = []; self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "ix:nonfraction":
            self.stack.append([dict(attrs), ""])

    def handle_data(self, data):
        self.parts.append(data)
        for active in self.stack:
            active[1] += data

    def handle_endtag(self, tag):
        if tag == "ix:nonfraction" and self.stack:
            active = self.stack.pop()
            identity = active[0].get("id")
            if identity in self.tags:
                raise h.InputError("Duplicate inline occurrence ID")
            self.tags[identity] = active


@dataclass(frozen=True)
class Component:
    spec: dict
    candidates: tuple[ReportedInput, ...]
    selected: int | None
    reason: str | None


def review_for(source):
    body = EVIDENCE_PATH.read_bytes()
    if hashlib.sha256(body).hexdigest() != EVIDENCE_SHA256:
        raise h.InputError("Cash/investment reviewed evidence changed")
    review = next((r for r in json.loads(body)["periods"] if r["bundle_id"] == source.bundle_id), None)
    if review is None:
        raise h.InputError("Only four reviewed period registrations")
    return review


def inspect(source, review=None):
    review = review_for(source) if review is None else review
    period = source.period
    identity = dict(cik=period.cik, accession=period.accession, annual_start=str(period.annual_start),
                    annual_end=str(period.annual_end), form=period.form)
    if review["bundle_id"] != source.bundle_id or review["period"] != identity:
        raise h.InputError("Exact accession and authoritative annual identity required")
    instance = next(r for r in source.artifacts if r.artifact.url.endswith("_htm.xml"))
    primary = next(r for r in source.artifacts if r.artifact.url.endswith(".htm"))
    if (review["instance_sha256"] != instance.artifact.sha256 or review["primary_sha256"] != primary.artifact.sha256
            or review["instance_url"] != instance.artifact.url or review["primary_url"] != primary.artifact.url
            or review["digest_type"] != "sha256_sec_response_body_bytes"):
        raise h.InputError("Exact original-body receipt binding required")
    try:
        evidence = retained.prepare(period, source.artifacts, (
            retained.ArtifactBinding(review["instance_url"], review["instance_sha256"], "instance"),
            retained.ArtifactBinding(review["primary_url"], review["primary_sha256"], "support")))
    except FilingXBRLDataError as exc:
        raise h.InputError("Invalid instant context/unit/nil/numeric evidence") from exc
    namespaces = evidence.namespaces
    primary_tags = _Tags(); primary_tags.feed(primary.artifact.body.decode("utf-8"))
    text = " ".join(" ".join(primary_tags.parts).split())
    if any(note["text"] not in text for note in review["scope_notes"]):
        raise h.InputError("Reviewed scope note excerpt not retained")
    results = []
    for spec in review["components"]:
        if spec["namespace"] != namespaces.get(spec["taxonomy"]):
            raise h.InputError("Exact namespace/taxonomy binding required")
        policy = {"cash_equivalents": CASH_AND_CASH_EQUIVALENTS_POLICY,
                  "current_investments": SHORT_TERM_INVESTMENTS_POLICY}.get(spec["component_id"])
        if policy is not None and not any(c.concept.taxonomy == spec["taxonomy"] and c.concept.name == spec["concept"]
                and (c.applicable_ciks is None or period.cik in c.applicable_ciks) for c in policy.candidates):
            raise h.InputError("Existing approved direct cash/current investment semantics required")
        inspected = retained.inspect(evidence, retained.SelectionSpec(spec["component_id"],
            (retained.Selector(spec["namespace"], spec["concept"], ()),), "instant", "USD",
            spec["role"], spec["scope"], tuple(u["reason"] for u in review["unknowns"])))
        candidates = tuple(ReportedInput(spec["concept"], InputKind.BOOK_BALANCE, c.value, 1,
            spec["scope"], tuple(Occurrence(**o.__dict__) for o in c.occurrences)) for c in inspected.candidates)
        for statement in spec["statements"]:
            if statement["id"] not in primary_tags.tags:
                raise h.InputError("Exact reviewed statement/note tag missing")
            attrs, raw = primary_tags.tags[statement["id"]]
            if any(attrs.get(k) != v for k, v in statement["attributes"].items()) or raw.strip() != statement["displayed_value"]:
                raise h.InputError("Reviewed statement precision/scale/context/representation changed")
            # Independent display check, not a scope-equivalence or rounding rule.
            point = Decimal(raw.strip().replace(",", "") + "e" + attrs["scale"])
            if attrs.get("sign") == "-": point = point.copy_negate()
            if candidates and not any(i.value_usd == point and any(o.context_id == attrs["contextref"]
                    and o.unit_id == attrs["unitref"] and o.decimals == attrs["decimals"] for o in i.occurrences)
                    for i in candidates):
                # Differing eligible candidates are retained as unresolved below;
                # statement mismatch cannot select another concept or date.
                if len({i.value_usd for i in candidates}) == 1:
                    candidates_match = False
                    break
        else:
            candidates_match = True
        if spec["gated"]:
            reason = "Issuer-extension combined caption remains support-only, separately gated; no primitive or scope-equivalence acceptance."
        elif not candidates:
            reason = "No eligible nondimensional exact year-end USD observation for this reviewed component."
        elif len({i.value_usd for i in candidates}) != 1:
            reason = "Differing eligible representations/values remain unresolved; precision alone cannot establish exact equality."
        elif not candidates_match:
            reason = "Eligible observation does not independently match reviewed statement/note representation."
        else:
            reason = None
        results.append(Component(spec, candidates, 0 if reason is None else None, reason))
    return review, tuple(results)


def mapping_entry(source, inspection=None):
    review, components = inspect(source) if inspection is None else inspection
    bindings = []
    for component in components:
        bindings.append(dict(input_id=component.spec["component_id"], origin="reported", role=component.spec["role"],
            population=component.spec["component_id"], unit="USD", scale=1, sign=1,
            precision=component.candidates[0].occurrences[0].decimals if component.selected is not None else "unknown",
            retained_cash=dict(evidence_sha256=EVIDENCE_SHA256, spec=component.spec,
                selected=component.selected, null_reason=component.reason,
                candidates=[dict(value_usd=str(i.value_usd), occurrences=[o.__dict__ | dict(start=None, end=str(o.end), dimensions=list(o.dimensions)) for o in i.occurrences]) for i in component.candidates])))
    return dict(status="mapped", origin="reported", quality="limited", review="reviewed", scope="restricted",
        completeness="partial", aggregation="none", bindings=bindings, null_reason=None,
        unresolved_requirements=[u["component_id"] + ": " + u["reason"] for u in review["unknowns"]])


def values(row, source, entry):
    review, components = inspect(source)
    if entry != mapping_entry(source, (review, components)):
        raise h.InputError("Exact component candidates/scope/overlap mapping required")
    instance = next(r for r in source.artifacts if r.artifact.url.endswith("_htm.xml"))
    primary = next(r for r in source.artifacts if r.artifact.url.endswith(".htm"))
    results = []
    for component in components:
        spec = component.spec; observations = []
        locator = json.dumps(dict(evidence_path="docs/pilot-cash-investment-evidence.json", evidence_sha256=EVIDENCE_SHA256,
            reviewed_period=review["period"], component=spec, scope_notes=review["scope_notes"],
            mapping_sha256=row.get("mapping_sha256"), digest_type=review["digest_type"]), sort_keys=True)
        for item in component.candidates:
            refs = tuple(h.SourceReference(f"{source.bundle_id}:{spec['component_id']}:ordinal-{o.ordinal}", source.period,
                instance, json.dumps(dict(locator=json.loads(locator), unit_id=o.unit_id, nil=o.nil), sort_keys=True),
                o.namespace, o.concept, o.context_id, o.ordinal, None, o.end, "USD", o.raw_value, o.decimals, o.dimensions)
                for o in item.occurrences)
            # A note reference is not an invented extracted-instance occurrence.
            refs += (h.SourceReference(f"{source.bundle_id}:{spec['component_id']}:primary:{item.occurrences[0].ordinal}",
                source.period, primary, locator, "", "", "", None, None, source.period.annual_end,
                "USD", str(item.value_usd), item.occurrences[0].decimals, ()),)
            observations.append(h.InputValue(f"cash_investment:{spec['component_id']}:ordinal-{item.occurrences[0].ordinal}",
                h.Field.CASH_INVESTMENTS, source.period, source.period.annual_end, item.value_usd, "USD", 1, 1,
                item.occurrences[0].decimals, spec["role"], h.Origin.REPORTED, h.Quality.LIMITED, spec["scope"],
                h.Scope(spec["scope_status"]), h.Completeness.PARTIAL, h.Review.REVIEWED, refs, None, None, (),
                "Exact retained reported component observation; not excess/unrestricted cash or an approved aggregate.",
                ("mapping_status:mapped", "reported_input_kind:book_balance", "no_aggregation_or_valuation_authorization",
                 "possible_overlap:" + ",".join(spec["overlap_with"]), "support_only" if spec["gated"] else "reported_component_only"),
                tuple(entry["unresolved_requirements"]), None, (spec["component_id"],)))
        if component.selected is not None:
            results.append(replace(observations[component.selected], alternatives=tuple(v for i, v in enumerate(observations) if i != component.selected)))
        else:
            results.append(_null(source, spec["component_id"], component.reason, tuple(observations),
                h.Quality.CONFLICTING if len({i.value_usd for i in component.candidates}) > 1 else h.Quality.LIMITED))
    results.extend(_null(source, u["component_id"], u["reason"]) for u in review["unknowns"])
    return tuple(results)


def _null(source, identity, reason, alternatives=(), quality=h.Quality.UNASSESSED):
    return h.InputValue(f"cash_investment:{identity}:unresolved", h.Field.CASH_INVESTMENTS, source.period,
        source.period.annual_end, None, "USD", 1, 1, "unknown", "unavailable_cash_investment_requirement",
        h.Origin.UNAVAILABLE, quality, reason, h.Scope.UNKNOWN, h.Completeness.UNKNOWN, h.Review.REVIEWED,
        (), None, None, alternatives, "No value selected or inferred; retained related observations are not a complete aggregate.",
        ("required_value_unresolved", "no_aggregation_or_valuation_authorization", "null_sign_scale_precision_are_not_observations"),
        (reason,), reason, ())
