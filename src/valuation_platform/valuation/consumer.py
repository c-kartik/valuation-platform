"""Read-only, exact retained revenue selections; no historical rebuild/approval.

Reuse the existing relevant-content/hash and manual-identity validators. Pin the
already accepted audit rather than call approval creation or activation scripts.
Only revenue is projected: historical proxies and optional context are not gates.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from valuation_platform.analyst.analyst_overrides import _json, relevant
from valuation_platform.analyst.historical_inputs import ManualIdentity
from valuation_platform.analyst.nwc import Period
from valuation_platform.analyst.prepared_assembly import canonical, digest
from .forecast import ForecastValidationError, RevenueAnchor


PACKAGE = "docs/company-data-preparation/meta-analyst-input-package.json"
DECISIONS = "docs/company-data-preparation/trillion-review-batch.json"
IDENTITY = {"cik": 1326801, "accession": "0001628280-26-003942",
            "annual_start": "2025-01-01", "annual_end": "2025-12-31", "form": "10-K"}
APPROVAL_SHA256 = "ac2514aa5c57e8959f38f90e9cd8687748b490a01d75647e172b2922fed54927"

# Fixed retained selections, not a ticker resolver or latest-filing policy.
ANCHORS = {
    "meta-fy2025": {"ticker": "META", "package": PACKAGE, "identity": IDENTITY},
    "googl-fy2025": {
        "ticker": "GOOGL", "issuer": "Alphabet (GOOG/GOOGL)",
        "package": "docs/company-data-preparation/googl-analyst-input-package.json",
        "identity": {"cik": 1652044, "accession": "0001652044-26-000018",
                     "annual_start": "2025-01-01", "annual_end": "2025-12-31", "form": "10-K"},
        "audit_sha256": "728eaf073b0ef2fb5234f835e018e2290f7c3eac652cc91cb05e14cdef41d847",
    },
    "aapl-fy2025": {
        "ticker": "AAPL", "issuer": "AAPL",
        "package": "docs/company-data-preparation/aapl-analyst-input-package.json",
        "identity": {"cik": 320193, "accession": "0000320193-25-000079",
                     "annual_start": "2024-09-29", "annual_end": "2025-09-27", "form": "10-K"},
        "audit_sha256": "f0a91b70b853ec380091a779b227d742c5d1d0aa0add21fdd09e91d39cf96f62",
    },
}


def prepare_meta_revenue_anchor(package: dict, decisions: list) -> RevenueAnchor:
    """Validate an existing accepted view, without activating or changing it.

    The one-audit pin is intentionally narrow: a later approval needs a scoped
    consumer update. These checks validate retained bindings, not fresh SEC XML
    or completeness of any other historical family or actual forecast inputs.
    """
    try:
        audit = package["history_approval"]
        if (audit["sha256"] != APPROVAL_SHA256 or audit["sha256"] !=
                digest({k: v for k, v in audit.items() if k != "sha256"})):
            raise ForecastValidationError("Stale or malformed META approval")
        ManualIdentity(audit["author"], audit["recorded_at_utc"], audit["rationale"])
        parent = {k: v for k, v in package.items()
                  if k not in ("history_approval", "current_history")}
        selected = [d for d in decisions if d["ticker"] == "META"]
        if (package["ticker"] != "META" or
                audit["source_revision"] != digest(relevant(parent)) or
                audit["review_revision"] != package["review_revision"] or
                audit["proposal_revision"] != digest(relevant(selected)) or
                selected != audit["decisions"]):
            raise ForecastValidationError("Stale META source/review/proposal revision")
        identities = [r["identity"] for r in package["periods"]]
        view = package["current_history"]
        if (identities != audit["identities"] or len(identities) != 5 or
                identities[4] != IDENTITY or
                [r["identity"] for r in view["periods"]] != identities or
                view["approval_sha256"] != audit["sha256"] or
                view["authoritative_current_view"] is not True):
            raise ForecastValidationError("META anchor identity/approval binding mismatch")
        if view["active_decisions"] != [
            {"accepted": True, "decision_id": d["decision_id"], "status": "ACTIVE"}
            for d in selected
        ]:
            raise ForecastValidationError("META effective decisions disagree with approval")

        source_row = package["periods"][4]
        fact = source_row["facts"]["revenue"]
        value = view["periods"][4]["inputs"]["revenue"]
        expected = {
            "value": fact["value"], "raw_value": fact["value"], "unit": fact["unit"],
            "precision": fact["precision"],
            "precision_variants": fact.get("precision_variants", [fact["precision"]]),
            "origin": "reported", "source_origin": "reported", "sign_multiplier": 1,
            "as_of": fact.get("as_of"), "source_reference": "/periods/4/facts/revenue",
            "scope": fact.get("scope", fact.get("location", "Exact named source observation")),
            "approval_reference": "/history_approval",
            "review": "ACCEPTED_FOR_STATED_HISTORICAL_SCOPE",
        }
        if value != expected or value["value"] is None:
            raise ForecastValidationError("Required accepted revenue unavailable or mismatched")
        period = Period(IDENTITY["cik"], IDENTITY["accession"],
                        date.fromisoformat(IDENTITY["annual_start"]),
                        date.fromisoformat(IDENTITY["annual_end"]), IDENTITY["form"])
        # Sources/fact retain original occurrences, inline display scale and precision.
        # No optional effective input is inspected, required or promoted to an operand.
        return RevenueAnchor(
            period=period, revenue=Decimal(value["value"]), raw_value=value["raw_value"],
            precision=value["precision"], source_reference=PACKAGE + "#/periods/4/facts/revenue",
            effective_reference=PACKAGE + "#/current_history/periods/4/inputs/revenue",
            approval_reference=PACKAGE + "#/history_approval",
            source_details_json=canonical({"fact": fact, "sources": source_row["sources"]}),
            approval_details_json=canonical({k: audit[k] for k in (
                "schema", "version", "sequence", "sha256", "source_commit",
                "source_revision", "review_revision", "proposal_revision", "author",
                "recorded_at_utc", "scope", "valuation_consumption_approved")}),
            unit=value["unit"], sign_multiplier=value["sign_multiplier"],
        )
    except ForecastValidationError:
        raise
    except (KeyError, IndexError, TypeError, ValueError, ArithmeticError) as exc:
        raise ForecastValidationError("Invalid or unavailable META anchor binding") from exc


def load_meta_revenue_anchor(repository_root: Path) -> RevenueAnchor:
    """Read the retained local package and decisions. No network or writes."""
    try:
        package = _json((repository_root / PACKAGE).read_text())
        decisions = _json((repository_root / DECISIONS).read_text())["decisions"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ForecastValidationError("Retained META package/decisions unavailable") from exc
    return prepare_meta_revenue_anchor(package, decisions)


def prepare_revenue_anchor(kind: str, package: dict) -> RevenueAnchor:
    """Read-only GOOGL/AAPL projection from their pinned sequence-2 histories.

    Reuse relevant-content hashes and identity validation, not preparation builds
    or approval activation. The prior scoped audit and the company-wide historical
    audit have distinct roles. Optional effective inputs are not consumed/gated.
    """
    if kind not in ("googl-fy2025", "aapl-fy2025"):
        raise ForecastValidationError("Use a supported GOOGL/AAPL retained anchor kind")
    spec = ANCHORS[kind]
    ticker = spec["ticker"]
    prefix = ticker.lower()
    review_key, audit_key, view_key = (prefix + suffix for suffix in (
        "_history_review", "_history_approval", "_current_history"))
    try:
        audit, review, view = (package[key] for key in (audit_key, review_key, view_key))
        if (package["issuer"] != spec["issuer"] or audit["sha256"] != spec["audit_sha256"] or
                audit["sha256"] != digest({k: v for k, v in audit.items() if k != "sha256"})):
            raise ForecastValidationError(f"Stale or malformed {ticker} approval")
        ManualIdentity(audit["author"], audit["recorded_at_utc"], audit["rationale"])
        parent = {k: v for k, v in package.items() if k not in (audit_key, view_key)}
        source = {k: v for k, v in parent.items() if k != review_key}
        if (audit["source_revision"] != digest(relevant(parent)) or
                review["source_revision"] != digest(relevant(source)) or
                audit["review_revision"] != review["review_revision"] or
                review["review_revision"] != digest(relevant({
                    "periods": review["periods"], "proposals": review["consolidated_proposals"],
                    "parent_revision": review["source_revision"]}))):
            raise ForecastValidationError(f"Stale {ticker} source/review/proposal revision")
        prior = package["accepted_view"]["approval_audit"]
        if (audit["previous"] != prior["sha256"] or
                prior["sha256"] != digest({k: v for k, v in prior.items() if k != "sha256"})):
            raise ForecastValidationError(f"Broken {ticker} prior approval chain")
        identities = [row["identity"] for row in review["periods"]]
        if (len(identities) != 5 or identities != audit["identities"] or
                identities[4] != spec["identity"] or
                [row["identity"] for row in view["periods"]] != identities or
                view["authoritative_current_view"] is not True or
                view["approval_sha256"] != audit["sha256"]):
            raise ForecastValidationError(f"{ticker} anchor identity/approval binding mismatch")
        row = review["periods"][4]
        fact = row["facts"]["revenue"]
        value = view["periods"][4]["inputs"]["revenue"]
        base = f"/{review_key}/periods/4"
        expected = dict(value=fact["value"], unit=fact["unit"], precision=fact["precision"],
                        origin="reported", raw_value=fact["value"], multiplier=1,
                        as_of=fact["as_of"], source_reference=base + "/facts/revenue")
        if value != expected or value["value"] is None:
            raise ForecastValidationError(f"Required accepted {ticker} revenue unavailable or mismatched")
        source_checks = [x for x in row["family_checklist"] if x["field"] == "revenue"]
        checks = [x for x in view["periods"][4]["checklist"] if x["field"] == "revenue"]
        if (len(source_checks) != 1 or source_checks[0]["pending_decisions"] or
                source_checks[0]["status"] not in ("SOURCE_SUPPORTED", "EXISTING_SCOPED_APPROVAL") or
                source_checks[0]["evidence_references"] != [base + "/facts/revenue"] or
                checks != [dict(source_checks[0], status="SATISFIED_WITHIN_SOURCE_OR_PRIOR_SCOPE",
                                approval_reference=source_checks[0]["existing_approval_reference"])]):
            raise ForecastValidationError(f"{ticker} effective revenue acceptance mismatch")
        identity = spec["identity"]
        return RevenueAnchor(
            Period(identity["cik"], identity["accession"], date.fromisoformat(identity["annual_start"]),
                   date.fromisoformat(identity["annual_end"]), identity["form"]),
            Decimal(value["value"]), value["raw_value"], value["precision"],
            spec["package"] + "#" + base + "/facts/revenue",
            spec["package"] + f"#/{view_key}/periods/4/inputs/revenue",
            spec["package"] + "#/" + audit_key,
            canonical({"fact": fact, "sources": row["sources"]}),
            canonical({"history_approval": audit, "prior_scoped_approval": prior,
                       "prior_approval_reference": "/accepted_view/approval_audit",
                       "revenue_acceptance": checks[0],
                       "limitation": "Historical perimeter only; no company forecast/bridge acceptance"}),
            unit=value["unit"], sign_multiplier=value["multiplier"],
        )
    except ForecastValidationError:
        raise
    except (KeyError, IndexError, TypeError, ValueError, ArithmeticError, StopIteration) as exc:
        raise ForecastValidationError(f"Invalid or unavailable {ticker} anchor binding") from exc


def load_revenue_anchor(kind: str, repository_root: Path) -> RevenueAnchor:
    """Explicit local dispatch; no network, history rebuild, activation or writes."""
    if kind == "meta-fy2025":
        return load_meta_revenue_anchor(repository_root)
    if kind not in ANCHORS:
        raise ForecastValidationError("Unsupported retained anchor kind")
    try:
        package = _json((repository_root / ANCHORS[kind]["package"]).read_text())
    except (OSError, ValueError) as exc:
        raise ForecastValidationError(f"Retained {kind} package unavailable") from exc
    return prepare_revenue_anchor(kind, package)
