"""Adopt the reviewed CFO-based historical series for the three-company pilot.

Display only: no historical value becomes a forecast operand or changes EV.
The immutable evidence ledger is replayed offline; startup checks its pin,
accepted-package identity and all arithmetic before projecting public values.
"""
import hashlib
import json
from urllib.parse import urlsplit

from valuation_platform.valuation.consumer import ANCHORS
from .filing_fcff import METHOD, calculate
from .history import historical_window

LEDGER = "docs/company-data-preparation/historical-fcff-filing-calculations.json"
LEDGER_SHA256 = "d157e0bd6a0ab9461b399855e39ec89dc5b4afc4436893227fe0497772a82e3e"
OPERANDS = ("cfo", "cash_ppe", "interest_expense", "tax_provision", "pretax_income")
BASIS = "REPORTED_CFO_CASH_PPE"
NOTICE = (
    "Historical FCFF is derived from reported CFO plus after-tax interest less cash PP&E; "
    "the tax rate is reported tax provision / pretax income. CFO retains its noncash "
    "adjustments, including stock compensation. Forecast FCFF uses operating income "
    "and submitted assumptions; stock compensation stays expensed and investment can "
    "include finance-asset additions. The bases differ; no FCFF CAGR joins history to forecast."
)


def adopted_window(root, kind):
    """Return accepted revenue with calculated historical FCFF and audit metadata.

    Missing disclosure stays null. No EBIT-method substitution for missing CFO
    inputs, no separate D&A/WC adjustment, no estimate, tax-event normalization,
    lease split, SBC reversal or capital-creditor plug is added to this series.
    """
    spec = ANCHORS[kind]
    payload = (root / LEDGER).read_bytes()
    if hashlib.sha256(payload).hexdigest() != LEDGER_SHA256:
        raise ValueError("Historical CFO evidence ledger differs from reviewed pin")
    ledger = json.loads(payload)
    if ledger["methodology"] != METHOD or ledger["input_estimates_permitted"]:
        raise ValueError("Unapproved historical CFO method")
    companies = [c for c in ledger["companies"] if c["ticker"] == spec["ticker"]]
    if len(companies) != 1:
        raise ValueError("Unique reviewed company required")
    company = companies[0]
    if (company["package"] != spec["package"] or
            company["package_sha256"] != hashlib.sha256((root / spec["package"]).read_bytes()).hexdigest()):
        raise ValueError("Historical CFO accepted package changed")
    periods = {}
    for period in company["periods"]:
        identity = period["identity"]
        key = (identity["annual_start"], identity["annual_end"], identity["accession"])
        if key in periods or identity["cik"] != spec["identity"]["cik"] or identity["form"] != "10-K":
            raise ValueError("Incompatible historical CFO identity")
        inputs = period["inputs"]
        sources = []
        for point in inputs.values():
            if point is None:
                continue
            if (point["evidence_depth"] != "exact_primary_inline_and_instance_verified" or
                    point["unit"] != "USD" or point["target_annual_start"] != key[0] or
                    point["target_annual_end"] != key[1]):
                raise ValueError("Historical CFO operand lacks exact target binding")
            for source in point["sources"]:
                url = source["url"]
                if urlsplit(url).scheme != "https" or urlsplit(url).hostname != "www.sec.gov":
                    raise ValueError("Official filing source required")
                if url.endswith(".htm") and url not in sources:
                    sources.append(url)
        interest = inputs["interest_expense"]
        calculated = calculate(*(inputs[k]["value"] for k in OPERANDS)) if interest is not None else None
        if calculated != period["fcff"]:
            raise ValueError("Historical CFO arithmetic mismatch")
        status = "CALCULATED" if calculated else "MISSING_INTEREST_DISCLOSURE"
        periods[key] = {
            "fcff": calculated["amount_usd"] if calculated else None,
            "fcff_basis": BASIS,
            "fcff_calculation": {
                "status": status,
                "inputs": {k: inputs[k]["value"] if inputs[k] else None for k in OPERANDS},
                "sources": sources,
                "reported_etr": calculated["reported_etr"] if calculated else None,
            },
        }
    window = historical_window(root, kind)
    for year in window:
        revenue = year["revenue"]
        key = (revenue["period_start"], revenue["period_end"], revenue["accession"])
        if key not in periods:
            raise ValueError("Historical CFO period not in accepted revenue window")
        year.update(periods[key])
    return window


def policy():
    return {"methodology": METHOD, "basis": BASIS, "classification": "DERIVED_FROM_REPORTED_INPUTS",
            "notice": NOTICE, "forecast_calibration": False, "cross_basis_cagr": False,
            "missing_input_policy": "Unavailable; never zero-filled, estimated or replaced by a different FCFF method."}
