"""One opt-in AAPL reported history; reuse immutable reported-input machinery.

No retrieval, comparative registration, analyst treatments or economic totals.
The MSFT registry, models, serialization and sidecars remain unchanged.
"""

import base64
from datetime import date
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zlib

from valuation_platform.analyst import cash_flow_inputs as cf
from valuation_platform.analyst.nwc import Period


_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_PATH = _ROOT / "docs/company-data-preparation/aapl-reported-cash-flow-bundle.json"
_REGISTRY_SHA256 = "d185b995c566d6bfb3b165627283b5ab52edc8ead1e62332d3d9458d0667b747"
_CONTRACT = "reviewed-aapl-reported-cash-flow-inputs"
_SCHEMA = "reported-cash-flow-input-bundle-v1"


def _registry():
    body = _REGISTRY_PATH.read_bytes()
    if hashlib.sha256(body).hexdigest() != _REGISTRY_SHA256:
        raise cf.CashFlowInputError("Immutable AAPL review changed; new review required")
    return json.loads(body)


def registered_bundle_ids() -> tuple[str, ...]:
    return tuple(b["bundle_id"] for b in _registry()["bundles"])


def _spec(bundle_id):
    doc = _registry()
    for spec in doc["bundles"]:
        if spec["bundle_id"] == bundle_id:
            return doc, spec
    raise cf.CashFlowInputError("Only reviewed AAPL FY2025 is registered")


def _build(doc, spec, receipts):
    p = spec["period"]
    period = Period(p["cik"], p["accession"], date.fromisoformat(p["annual_start"]),
                    date.fromisoformat(p["annual_end"]), spec["form"])
    source = cf._instance(receipts, period)
    inputs = []
    for value in spec["inputs"]:
        occurrences = cf._occurrences(*source, value["namespace"], value["input_id"], period, False)
        if (tuple(o.ordinal for o in occurrences) != tuple(value["ordinals"])
                or any(o.context_id != spec["annual_context_id"] or o.unit_id != "usd"
                       or o.decimals != value["decimals"] for o in occurrences)):
            raise cf.CashFlowInputError("Occurrences differ from exact AAPL review")
        inputs.append(cf.ReportedInput(value["input_id"], cf.InputKind(value["kind"]),
                                      Decimal(value["value_usd"]), value["display_multiplier"],
                                      value["location_and_scope"], occurrences))
    return cf.ReportedCashFlowBundle(
        spec["bundle_id"], doc["version"], period, doc["review_author"],
        date.fromisoformat(doc["reviewed_on"]), doc["evidence_reference"], receipts,
        tuple(inputs), tuple(cf.UnknownInput(**u) for u in spec["unknowns"]),
        tuple(spec["cfo_terms"]), tuple(spec["limitations"]))


def load_aapl_bundle(bundle_id: str) -> cf.ReportedCashFlowBundle:
    """Verify retained originals and frozen identity; never access the network."""
    try:
        doc, spec = _spec(bundle_id)
        for key in ("inventory", "artifact_manifest"):
            if hashlib.sha256((_ROOT / doc[key + "_path"]).read_bytes()).hexdigest() != doc[key + "_sha256"]:
                raise cf.CashFlowInputError("Retained evidence reference changed")
        rows = json.loads((_ROOT / doc["inventory_path"]).read_text())["rows"]
        row = next(r for r in rows if all(r[k] == v for k, v in spec["period"].items()))
        if (row["ticker"] != "AAPL" or {r["source_url"] for r in spec["artifacts"]} !=
                {row["primary_url"], row["instance_url"]}):
            raise cf.CashFlowInputError("Not the frozen selected AAPL filing")
        manifest = json.loads((_ROOT / doc["artifact_manifest_path"]).read_text())
        receipts = []
        for ref in spec["artifacts"]:
            entries = [a for a in manifest["artifacts"] if a["source_url"] == ref["source_url"]]
            if (len(entries) != 1 or any(entries[0][k] != v for k, v in ref.items())
                    or entries[0]["storage_encoding"] != "gzip_base64"):
                raise cf.CashFlowInputError("Original artifact metadata mismatch")
            body = gzip.decompress(base64.b64decode(entries[0]["response_body_gzip_base64"], validate=True))
            receipts.append(cf._receipt(ref, body))
        return _build(doc, spec, tuple(receipts))
    except (OSError, EOFError, zlib.error, StopIteration, KeyError, ValueError, TypeError, ET.ParseError) as exc:
        raise cf.CashFlowInputError("Cannot bind reviewed retained AAPL bundle") from exc


def serialize(bundle: cf.ReportedCashFlowBundle) -> str:
    """Separate AAPL contract; retain originals and every source representation."""
    if type(bundle) is not cf.ReportedCashFlowBundle:
        raise cf.CashFlowInputError("Reported input bundle required")
    doc, spec = _spec(bundle.bundle_id)
    if bundle != _build(doc, spec, bundle.artifacts):
        raise cf.CashFlowInputError("Only exact reviewed AAPL bundle may serialize")
    artifacts = []
    for receipt, ref in zip(bundle.artifacts, spec["artifacts"]):
        if receipt != cf._receipt(ref, receipt.artifact.body):
            raise cf.CashFlowInputError("Reviewed receipt metadata changed")
        artifacts.append({**ref, "storage_encoding": "gzip_base64",
                          "response_body_gzip_base64": base64.b64encode(
                              gzip.compress(receipt.artifact.body, mtime=0)).decode("ascii")})
    return json.dumps({"schema": _SCHEMA, "contract": _CONTRACT,
                       "registry_sha256": _REGISTRY_SHA256, "bundle": cf._view(bundle),
                       "artifacts": artifacts}, sort_keys=True, separators=(",", ":"))


def deserialize(payload: str) -> cf.ReportedCashFlowBundle:
    """Recheck pinned review, original receipts and reported CFO bridge only."""
    try:
        def unique(pairs):
            d = {}
            for k, v in pairs:
                if k in d:
                    raise cf.CashFlowInputError("Duplicate serialized key")
                d[k] = v
            return d

        data = json.loads(payload, object_pairs_hook=unique)
        if (set(data) != {"schema", "contract", "registry_sha256", "bundle", "artifacts"}
                or data["schema"] != _SCHEMA or data["contract"] != _CONTRACT
                or data["registry_sha256"] != _REGISTRY_SHA256):
            raise cf.CashFlowInputError("Unknown AAPL serialization contract")
        doc, spec = _spec(data["bundle"]["bundle_id"])
        if len(data["artifacts"]) != len(spec["artifacts"]):
            raise cf.CashFlowInputError("Both reviewed original artifacts required")
        receipts = []
        for value, ref in zip(data["artifacts"], spec["artifacts"]):
            if (set(value) != set(ref) | {"storage_encoding", "response_body_gzip_base64"}
                    or any(value[k] != v for k, v in ref.items())
                    or value["storage_encoding"] != "gzip_base64"):
                raise cf.CashFlowInputError("Exact reviewed receipt required")
            body = gzip.decompress(base64.b64decode(value["response_body_gzip_base64"], validate=True))
            receipts.append(cf._receipt(ref, body))
        result = _build(doc, spec, tuple(receipts))
        if json.dumps(data["bundle"], sort_keys=True) != json.dumps(cf._view(result), sort_keys=True):
            raise cf.CashFlowInputError("Serialized role/scope/unknown/evidence differs from review")
        return result
    except (OSError, EOFError, zlib.error, KeyError, ValueError, TypeError, ET.ParseError) as exc:
        raise cf.CashFlowInputError("Invalid AAPL reported input serialization") from exc
