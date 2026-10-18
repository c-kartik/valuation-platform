"""Read-only, exact META FY2025 revenue boundary; no historical rebuild/approval.

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
