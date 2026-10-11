"""One opt-in Alphabet reported history; reuse immutable reported-input machinery.

No retrieval, comparative registration, analyst treatments or economic totals.
An explicit refreshed receipt never overwrites the original metadata gap.
The MSFT registry, models, serialization and sidecars remain unchanged.
"""

import base64
import gzip
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zlib

from valuation_platform.analyst import cash_flow_inputs as cf
from valuation_platform.analyst import aapl_cash_flow_inputs as _base


_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_PATH = _ROOT / "docs/company-data-preparation/googl-reported-cash-flow-bundle.json"
_REGISTRY_SHA256 = "97ca73213b6bb46dfdaec67f930d3abd0cfbd6d1a17e50047998c0b2764f509f"
_CONTRACT = "reviewed-googl-reported-cash-flow-inputs"
_SCHEMA = "reported-cash-flow-input-bundle-v1"


def _registry():
    body = _REGISTRY_PATH.read_bytes()
    if hashlib.sha256(body).hexdigest() != _REGISTRY_SHA256:
        raise cf.CashFlowInputError("Immutable Alphabet review changed; new review required")
    return json.loads(body)


def registered_bundle_ids() -> tuple[str, ...]:
    return tuple(b["bundle_id"] for b in _registry()["bundles"])


def _spec(bundle_id):
    doc = _registry()
    for spec in doc["bundles"]:
        if spec["bundle_id"] == bundle_id:
            return doc, spec
    raise cf.CashFlowInputError("Only reviewed Alphabet FY2024 is registered")


def _build(doc, spec, receipts):
    # Reuse the exact USD annual builder; its models/validators are unchanged.
    return _base._build(doc, spec, receipts)


def _documents(doc):
    result = {}
    for key in ("inventory", "artifact_manifest", "refresh_manifest"):
        body = (_ROOT / doc[key + "_path"]).read_bytes()
        if hashlib.sha256(body).hexdigest() != doc[key + "_sha256"]:
            raise cf.CashFlowInputError("Pinned original/refresh evidence changed")
        result[key] = json.loads(body)
    return result


def _history(doc, receipts):
    documents = _documents(doc)
    history = doc["evidence_history"]
    original = history["original_instance"]
    old = [a for a in documents["artifact_manifest"]["artifacts"]
           if a["source_url"] == original["source_url"]]
    fresh = documents["refresh_manifest"]["artifacts"]
    if (len(old) != 1 or len(fresh) != 1
            or any(old[0][k] != v for k, v in original.items())
            or original["retrieved_at_utc"] is not None or original["http_status"] is not None
            or documents["refresh_manifest"]["original_artifact_reference"]["sha256"] != original["sha256"]):
        raise cf.CashFlowInputError("Original metadata gap/history must remain explicit")
    old_body = gzip.decompress(base64.b64decode(old[0]["response_body_gzip_base64"], validate=True))
    fresh_body = gzip.decompress(base64.b64decode(fresh[0]["response_body_gzip_base64"], validate=True))
    if (hashlib.sha256(old_body).hexdigest() != original["sha256"]
            or len(old_body) != original["byte_length"] or old_body != fresh_body
            or len(receipts) != 2 or receipts[1] != cf._receipt(fresh[0], fresh_body)):
        raise cf.CashFlowInputError("Explicit refreshed receipt and original body binding required")
    return history


def load_googl_bundle(bundle_id: str) -> cf.ReportedCashFlowBundle:
    """Verify retained originals and frozen identity; never access the network."""
    try:
        doc, spec = _spec(bundle_id)
        documents = _documents(doc)
        rows = documents["inventory"]["rows"]
        row = next(r for r in rows if all(r[k] == v for k, v in spec["period"].items()))
        if (row["ticker"] != "GOOGL" or {r["source_url"] for r in spec["artifacts"]} !=
                {row["primary_url"], row["instance_url"]}):
            raise cf.CashFlowInputError("Not the frozen selected Alphabet filing")
        manifest = documents["artifact_manifest"]
        receipts = []
        for ref in spec["artifacts"]:
            source = documents["refresh_manifest"] if ref["source_url"].endswith("_htm.xml") else manifest
            entries = [a for a in source["artifacts"] if a["source_url"] == ref["source_url"]]
            if (len(entries) != 1 or any(entries[0][k] != v for k, v in ref.items())
                    or entries[0]["storage_encoding"] != "gzip_base64"):
                raise cf.CashFlowInputError("Original artifact metadata mismatch")
            body = gzip.decompress(base64.b64decode(entries[0]["response_body_gzip_base64"], validate=True))
            receipts.append(cf._receipt(ref, body))
        _history(doc, tuple(receipts))
        return _build(doc, spec, tuple(receipts))
    except (OSError, EOFError, zlib.error, StopIteration, KeyError, ValueError, TypeError, ET.ParseError) as exc:
        raise cf.CashFlowInputError("Cannot bind reviewed retained Alphabet bundle") from exc


def serialize(bundle: cf.ReportedCashFlowBundle) -> str:
    """Separate Alphabet contract; retain originals and every source representation."""
    if type(bundle) is not cf.ReportedCashFlowBundle:
        raise cf.CashFlowInputError("Reported input bundle required")
    doc, spec = _spec(bundle.bundle_id)
    if bundle != _build(doc, spec, bundle.artifacts):
        raise cf.CashFlowInputError("Only exact reviewed Alphabet bundle may serialize")
    history = _history(doc, bundle.artifacts)
    artifacts = []
    for receipt, ref in zip(bundle.artifacts, spec["artifacts"]):
        if receipt != cf._receipt(ref, receipt.artifact.body):
            raise cf.CashFlowInputError("Reviewed receipt metadata changed")
        artifacts.append({**ref, "storage_encoding": "gzip_base64",
                          "response_body_gzip_base64": base64.b64encode(
                              gzip.compress(receipt.artifact.body, mtime=0)).decode("ascii")})
    return json.dumps({"schema": _SCHEMA, "contract": _CONTRACT,
                       "registry_sha256": _REGISTRY_SHA256, "bundle": cf._view(bundle),
                       "artifacts": artifacts, "evidence_history": history}, sort_keys=True, separators=(",", ":"))


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
        if (set(data) != {"schema", "contract", "registry_sha256", "bundle", "artifacts", "evidence_history"}
                or data["schema"] != _SCHEMA or data["contract"] != _CONTRACT
                or data["registry_sha256"] != _REGISTRY_SHA256):
            raise cf.CashFlowInputError("Unknown Alphabet serialization contract")
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
        history = _history(doc, tuple(receipts))
        if json.dumps(data["evidence_history"], sort_keys=True) != json.dumps(history, sort_keys=True):
            raise cf.CashFlowInputError("Serialized original receipt gap/history differs from review")
        result = _build(doc, spec, tuple(receipts))
        if json.dumps(data["bundle"], sort_keys=True) != json.dumps(cf._view(result), sort_keys=True):
            raise cf.CashFlowInputError("Serialized role/scope/unknown/evidence differs from review")
        return result
    except (OSError, EOFError, zlib.error, KeyError, ValueError, TypeError, ET.ParseError) as exc:
        raise cf.CashFlowInputError("Invalid Alphabet reported input serialization") from exc
