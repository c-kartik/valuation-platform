"""Explicit four-period adapter; no resolver, aggregation or readiness decision.

D&A has an unresolved required slot. Its alternatives are labeled non-substitutable
support observations, not candidate complete primitives. Original proofs are
serialized once using their existing closed bundle serializers.
"""

from dataclasses import fields, is_dataclass, replace
from datetime import date
from decimal import Decimal
from enum import Enum
import hashlib
import json
from pathlib import Path

from valuation_platform.analyst import historical_inputs as h
from valuation_platform.analyst import cash_flow_inputs as msft
from valuation_platform.analyst import aapl_cash_flow_inputs as aapl
from valuation_platform.analyst import googl_cash_flow_inputs as googl
from valuation_platform.analyst.nwc import Artifact
from valuation_platform.analyst import pilot_direct_income as direct
from valuation_platform.analyst import pilot_cash_investments as cash


ROOT = Path(__file__).resolve().parents[3]
MAPPING_PATH = ROOT / "docs/pilot-historical-input-mappings.json"
MAPPING_SHA256 = "9ec38a0e22a235cc82aa76d1eaca8d64f328247881b46a09a650a73bd4a3d9ff"
SCHEMA = "pilot-historical-input-adapter-v1"
_SOURCES = {
    "msft-reported-cash-flow-fy2025": ("MSFT", msft, msft.load_msft_bundle),
    "msft-reported-cash-flow-fy2026": ("MSFT", msft, msft.load_msft_bundle),
    "aapl-reported-cash-flow-fy2025": ("AAPL", aapl, aapl.load_aapl_bundle),
    "googl-reported-cash-flow-fy2024": ("GOOGL", googl, googl.load_googl_bundle),
}


def _mapping():
    body = MAPPING_PATH.read_bytes()
    if hashlib.sha256(body).hexdigest() != MAPPING_SHA256:
        raise h.InputError("Committed mapping changed; no implicit treatment extension")
    return json.loads(body)


def _rows(issuer):
    if issuer not in ("MSFT", "AAPL", "GOOGL"):
        raise h.InputError("Only the three explicit pilot preparation histories are available")
    return tuple(r for r in _mapping()["periods"] if r["issuer"] == issuer)


def _reference(row, item, receipt, occurrence=None, direct_review=None):
    locator = {
        "registry": row["registry_path"], "registry_sha256": row["registry_sha256"],
        "mapping_sha256": MAPPING_SHA256, "source_input_id": item.input_id,
        "source_kind": item.kind.value, "location_and_scope": item.location_and_scope,
        "unit_id": None if occurrence is None else occurrence.unit_id,
        "nil": None if occurrence is None else occurrence.nil,
        "source_reference_kind": "primary_statement" if occurrence is None else "extracted_instance_occurrence",
    }
    if direct_review is not None:
        locator["retained_direct_evidence"] = direct_review.statement
        locator["direct_evidence_sha256"] = direct.EVIDENCE_SHA256
        locator["source_reference_kind"] = ("reviewed_inline_face_statement" if occurrence is None
                                            else "retained_direct_instance_occurrence")
    first = item.occurrences[0] if occurrence is None else occurrence
    identity = "primary-statement" if occurrence is None else f"ordinal-{occurrence.ordinal}"
    return h.SourceReference(
        source_id=f"{row['bundle_id']}:{item.input_id}:{identity}", period=first_period(row), receipt=receipt,
        locator=json.dumps(locator, sort_keys=True, separators=(",", ":")),
        namespace="" if occurrence is None else occurrence.namespace,
        concept="" if occurrence is None else occurrence.concept,
        context_id="" if occurrence is None else occurrence.context_id,
        occurrence_ordinal=None if occurrence is None else occurrence.ordinal,
        start=first.start, end=first.end, unit=first.normalized_unit,
        raw_value=str(item.value_usd) if occurrence is None else occurrence.raw_value,
        decimals=first.decimals, dimensions=first.dimensions)


def first_period(row):
    p = row["period"]
    return h.Period(p["cik"], p["accession"], date.fromisoformat(p["annual_start"]),
                    date.fromisoformat(p["annual_end"]), p["form"])


def _observation(row, field, entry, binding, source):
    item = source.input(binding["input_id"])
    instance = next(r for r in source.artifacts if r.artifact.url.endswith("_htm.xml"))
    if (source.period != first_period(row) or binding["scale"] != 1 or
            binding["sign"] != item.display_multiplier or binding["unit"] != "USD" or
            binding["occurrence_ordinals"] != [o.ordinal for o in item.occurrences] or
            any(o.context_id != binding["context_id"] or o.decimals != binding["precision"]
                for o in item.occurrences)):
        raise h.InputError("Exact source/mapping binding mismatch")
    refs = tuple(_reference(row, item, instance, o) for o in item.occurrences)
    if field is h.Field.CFO:
        primary = next(r for r in source.artifacts if r.artifact.url.endswith(".htm"))
        refs += (_reference(row, item, primary),)
    flags = (f"mapping_status:{entry['status']}", f"reported_input_kind:{item.kind.value}",
             f"population:{binding['population']}", "no_aggregation_or_valuation_authorization")
    if entry["status"] == "limited_support":
        flags += ("support_only", "non_substitutable_for_required_da_primitive")
    return h.InputValue(
        input_id=f"{field.value}:{item.input_id}", field=field, period=source.period, as_of=None,
        value=item.displayed_value_usd, unit=binding["unit"], scale=binding["scale"], sign=binding["sign"],
        precision=binding["precision"], role=binding["role"], origin=h.Origin(binding["origin"]),
        quality=h.Quality(entry["quality"]), scope=item.location_and_scope,
        scope_status=h.Scope(entry["scope"]), completeness=h.Completeness(entry["completeness"]),
        review=h.Review(entry["review"]), sources=refs, manual=None, formula=None, alternatives=(),
        selection_rationale=f"Exact committed {row['registry_path']}#{binding['registry_pointer']}; "
                            f"registry SHA-256 {row['registry_sha256']}; source observation only, not economic equivalence.",
        flags=flags, unresolved_requirements=tuple(entry["unresolved_requirements"]), null_reason=None,
        coverage_keys=(binding["population"],))


def _direct_value(row, field, entry, source, inspection):
    """Retain competing/equivalent candidates, never compute or discard conflict."""
    instance = next(r for r in source.artifacts if r.artifact.url.endswith("_htm.xml"))
    primary = next(r for r in source.artifacts if r.artifact.url.endswith(".htm"))
    observations = []
    for i, item in enumerate(inspection.candidates):
        refs = tuple(_reference(row, item, instance, o, inspection) for o in item.occurrences)
        if i == inspection.selected:
            refs += (_reference(row, item, primary, direct_review=inspection),)
        observations.append(h.InputValue(
            input_id=f"{field.value}:{item.input_id}:ordinal-{item.occurrences[0].ordinal}",
            field=field, period=source.period, as_of=None, value=item.value_usd, unit="USD", scale=1, sign=1,
            precision=item.occurrences[0].decimals, role="reported_revenue" if field is h.Field.REVENUE else "reported_operating_income",
            origin=h.Origin.REPORTED, quality=h.Quality.SUPPORTED, scope=item.location_and_scope,
            scope_status=h.Scope.CONSOLIDATED_REPORTED, completeness=h.Completeness.COMPLETE,
            review=h.Review.REVIEWED, sources=refs, manual=None, formula=None, alternatives=(),
            selection_rationale="Approved direct concept; every exact annual eligible occurrence retained; "
                "independent reviewed inline face-statement representation required; no precedence override.",
            flags=("mapping_status:mapped", "reported_input_kind:accrued_income", f"population:{field.value}",
                   "direct_reported_statement_total_only", "no_aggregation_or_valuation_authorization"),
            unresolved_requirements=tuple(entry["unresolved_requirements"]), null_reason=None,
            coverage_keys=(field.value,)))
    if inspection.selected is None:
        unresolved = dict(entry, quality="conflicting" if inspection.candidates else "unassessed",
                          completeness="unknown", scope="unknown", status="unavailable",
                          null_reason=inspection.reason,
                          unresolved_requirements=[inspection.reason, *entry["unresolved_requirements"]])
        result = _unavailable(row, field, unresolved, tuple(observations))
        return replace(result, selection_rationale="No direct value selected; every eligible competing candidate retained.")
    chosen = observations[inspection.selected]
    return replace(chosen, alternatives=tuple(v for i, v in enumerate(observations) if i != inspection.selected))


def _unavailable(row, field, entry, support=()):
    bridge = field in (h.Field.CASH_INVESTMENTS, h.Field.DEBT_LEASES, h.Field.OTHER_BRIDGE)
    reason = entry["null_reason"] or entry["unresolved_requirements"][0]
    return h.InputValue(
        input_id=f"{field.value}:required_unresolved", field=field, period=first_period(row),
        as_of=first_period(row).annual_end if bridge else None, value=None,
        unit="shares" if field is h.Field.SHARES else "USD", scale=1, sign=1, precision="unknown",
        role="required_primitive_unresolved" if support else "unavailable_required_field",
        origin=h.Origin.UNAVAILABLE, quality=h.Quality(entry["quality"]), scope=reason,
        scope_status=h.Scope(entry["scope"]), completeness=h.Completeness(entry["completeness"]),
        review=h.Review(entry["review"]), sources=(), manual=None, formula=None, alternatives=support,
        selection_rationale="No value selected. Related D&A observations, if present, are evidence-only "
                            "alternatives, not equivalent substitute primitives.",
        flags=(f"mapping_status:{entry['status']}", "required_value_unresolved",
               "null_sign_scale_precision_are_not_observations", "no_aggregation_or_valuation_authorization"),
        unresolved_requirements=tuple(entry["unresolved_requirements"]), null_reason=reason, coverage_keys=())


def _annual(row, source):
    if source.bundle_id != row["bundle_id"] or source.period != first_period(row):
        raise h.InputError("Source identity mismatch")
    inputs = []
    for field in h.Field:
        entry = row["fields"][field.value]
        if field is h.Field.CASH_INVESTMENTS:
            inputs.extend(cash.values(dict(row, mapping_sha256=MAPPING_SHA256), source, entry))
            continue
        if field in direct.POLICIES:
            inspection = direct.reviewed(source, field)
            if inspection.selected is not None and entry["bindings"] != [direct.binding(source, field, inspection)]:
                raise h.InputError("Exact direct-income candidate/statement mapping required")
            inputs.append(_direct_value(row, field, entry, source, inspection))
            continue
        observations = tuple(_observation(row, field, entry, binding, source) for binding in entry["bindings"])
        if entry["status"] == "mapped":
            inputs.extend(observations)
        else:
            inputs.append(_unavailable(row, field, entry, observations))
    # Preserve whole reported package limitations and exact unresolved input metadata.
    unknowns = tuple("reported_input_unknown:" + json.dumps({"input_id": u.input_id,
        "status": u.status, "reason": u.reason, "value_usd": None}, sort_keys=True) for u in source.unknowns)
    provenance = (
        f"source_bundle:{source.bundle_id}; mapping_sha256:{MAPPING_SHA256}; registry_sha256:{row['registry_sha256']}",
        f"evidence_review:{row['evidence_review']}; source_unknowns:{row['registry_path']}#{row['source_unknowns_pointer']}",
        "supplementary_input_ids:" + json.dumps(row["supplementary_input_ids"], separators=(",", ":")),
        "Support alternatives retain source observations only; required D&A remains null. No completeness or readiness approval.")
    return h.AnnualBundle(f"pilot-preparation:{source.bundle_id}", 3, source.period,
                          tuple(inputs), source.limitations + unknowns + provenance)


def load_annual(bundle_id):
    if type(bundle_id) is not str or bundle_id not in _SOURCES:
        raise h.InputError("Only four original mapped pilot periods are permitted")
    issuer, _, loader = _SOURCES[bundle_id]
    row = next(r for r in _rows(issuer) if r["bundle_id"] == bundle_id)
    return _annual(row, loader(bundle_id))


def _history(issuer, sources):
    rows = _rows(issuer)
    if set(sources) != {r["bundle_id"] for r in rows}:
        raise h.InputError("Exact pilot history scope required; no comparative or extra periods")
    annuals = tuple(_annual(row, sources[row["bundle_id"]]) for row in rows)
    return h.HistoryBundle(f"pilot-preparation:{issuer}", 3, annuals[0].period.cik, annuals,
        (f"Restricted independently reviewed package scope: {len(annuals)} of five target annual periods. "
         "This is not a claim of short issuer history or approval of other selected periods.",))


def load_history(issuer):
    return _history(issuer, {r["bundle_id"]: _SOURCES[r["bundle_id"]][2](r["bundle_id"]) for r in _rows(issuer)})


def _metadata(value):
    """Typed model snapshot; original bytes live once in native source proofs."""
    if type(value) is Artifact:
        return {"type": "Artifact", "fields": {f.name: _metadata(getattr(value, f.name)) for f in fields(value)
                if f.name != "body"}, "original_body_reference": {"url": value.url, "sha256": value.sha256}}
    if is_dataclass(value):
        return {"type": type(value).__name__, "fields": {f.name: _metadata(getattr(value, f.name)) for f in fields(value)}}
    if isinstance(value, Enum):
        return {"enum": type(value).__name__, "value": value.value}
    if type(value) is Decimal:
        return {"decimal": str(value)}
    if type(value) is date:
        return {"date": value.isoformat()}
    if type(value) is tuple:
        return [_metadata(v) for v in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise h.InputError("Unsupported adapter metadata")


def serialize(history):
    if type(history) is not h.HistoryBundle:
        raise h.InputError("HistoryBundle required")
    issuer = next((key for key in ("MSFT", "AAPL", "GOOGL") if history.history_id == f"pilot-preparation:{key}"), None)
    rows = _rows(issuer)
    sources = {r["bundle_id"]: _SOURCES[r["bundle_id"]][2](r["bundle_id"]) for r in rows}
    if (history != _history(issuer, sources) or json.dumps(_metadata(history), sort_keys=True) !=
            json.dumps(_metadata(_history(issuer, sources)), sort_keys=True)):
        raise h.InputError("Only exact mapped adapter models may serialize")
    return json.dumps({"schema": SCHEMA, "model_schema": h.SCHEMA, "mapping_sha256": MAPPING_SHA256,
        "issuer": issuer, "history": _metadata(history), "source_proofs": [
            {"bundle_id": r["bundle_id"], "payload": _SOURCES[r["bundle_id"]][1].serialize(sources[r["bundle_id"]])}
            for r in rows]}, sort_keys=True, separators=(",", ":"))


def deserialize(payload):
    try:
        def unique(pairs):
            out = {}
            for key, value in pairs:
                if key in out:
                    raise h.InputError("Duplicate adapter key")
                out[key] = value
            return out
        data = json.loads(payload, object_pairs_hook=unique)
        if (set(data) != {"schema", "model_schema", "mapping_sha256", "issuer", "history", "source_proofs"}
                or data["schema"] != SCHEMA or data["model_schema"] != h.SCHEMA
                or data["mapping_sha256"] != MAPPING_SHA256):
            raise h.InputError("Separate exact adapter schema/mapping required")
        rows = _rows(data["issuer"])
        if (type(data["source_proofs"]) is not list or
                [p["bundle_id"] for p in data["source_proofs"]] != [r["bundle_id"] for r in rows]):
            raise h.InputError("Exact ordered source proofs required")
        sources = {}
        for proof in data["source_proofs"]:
            if set(proof) != {"bundle_id", "payload"}:
                raise h.InputError("Closed source proof shape required")
            bundle = _SOURCES[proof["bundle_id"]][1].deserialize(proof["payload"])
            if bundle.bundle_id != proof["bundle_id"]:
                raise h.InputError("Source proof identity mismatch")
            sources[bundle.bundle_id] = bundle
        result = _history(data["issuer"], sources)
        if json.dumps(_metadata(result), sort_keys=True) != json.dumps(data["history"], sort_keys=True):
            raise h.InputError("Adapter evidence, values, roles or requirements changed")
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise h.InputError("Invalid exact pilot adapter serialization") from exc
