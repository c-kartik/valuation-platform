"""Replay filing evidence and report the adopted three-company historical basis."""
import argparse
import csv
from decimal import Context, Decimal, localcontext
from io import StringIO
import json
from pathlib import Path

import calculate_historical_fcff_from_filings as source
from valuation_platform.review.cfo_history import LEDGER, adopted_window, policy

ROOT = Path(__file__).resolve().parents[1]
REPORT = "docs/historical-cfo-fcff-adoption.md"
CSV = "docs/company-data-preparation/historical-cfo-fcff-adoption.csv"


def build(root=ROOT):
    # Not just a copy of prior numbers: replay all primary/instance operands,
    # retained response receipts and accepted-source bindings before adoption.
    evidence = source.build(root)
    if evidence != json.loads((root / LEDGER).read_text()):
        raise ValueError("Source evidence no longer replays")
    companies = [{"kind": kind, "periods": adopted_window(root, kind)} for kind in source.KINDS]
    return {"policy": policy(), "companies": companies,
            "calculated": sum(p["fcff"] is not None for c in companies for p in c["periods"]),
            "missing": sum(p["fcff"] is None for c in companies for p in c["periods"])}


def outputs(data):
    lines = ["# Adopted historical CFO-based FCFF — three-company pilot", "",
        "November 2, 2026. User-approved scope: Alphabet, Apple and Meta, FY2021–FY2025.",
        "The default catalog/chart history now uses the reviewed CFO-based calculation.",
        "The existing EBIT-based forecast, submitted assumptions and enterprise values are unchanged.", "",
        "## Selected method", "",
        "**FCFF = reported CFO + reported interest expense × (1 − reported tax provision / pretax income) − cash PP&E.**", "",
        "The [CFA Institute curriculum](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation)",
        "teaches both CFO and EBIT starting points. It does not designate this particular",
        "reported-ETR, cash-PP&E implementation as uniquely preferred or certified.",
        "These are derived values from filing-supported inputs under a disclosed definition,",
        "not separately reported FCFF facts or exact observed unlevered cash-tax amounts.", "",
        "## Results — USD billions", "",
        "| Company | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |",
        "|---|---:|---:|---:|---:|---:|"]
    stream = StringIO(newline="")
    fields = ["kind", "fiscal_year", "period_start", "period_end", "fcff_usd", "basis", "status", "cfo", "cash_ppe", "interest_expense", "tax_provision", "pretax_income", "sources"]
    writer = csv.DictWriter(stream, fields, lineterminator="\n"); writer.writeheader()
    with localcontext(Context(prec=60)):
        for company in data["companies"]:
            values = [f'{Decimal(p["fcff"])/Decimal(1000000000):.2f}' if p["fcff"] is not None else "Unavailable" for p in company["periods"]]
            lines.append("| " + company["kind"].split("-")[0].upper() + " | " + " | ".join(values) + " |")
            for p in company["periods"]:
                calculation = p["fcff_calculation"]
                writer.writerow({"kind": company["kind"], "fiscal_year": p["fiscal_year_label"],
                    "period_start": p["revenue"]["period_start"], "period_end": p["revenue"]["period_end"],
                    "fcff_usd": p["fcff"], "basis": p["fcff_basis"], "status": calculation["status"],
                    **calculation["inputs"], "sources": " | ".join(calculation["sources"])})
    lines += ["", f'**{data["calculated"]}/15 calculated; {data["missing"]}/15 remain unavailable.**',
        "These are the same 13 reproducible CFO calculations already obtained during review;",
        "the change is their adoption for historical display, not a claim of new disclosures.", "",
        "## Blockers removed as prerequisites for this definition", "",
        "| Previous requirement | Treatment under the adopted historical method |",
        "|---|---|",
        "| Rebuild D&A and other noncash adjustments | Already inside reported CFO; no second add-back |",
        "| Allocate every mixed working-capital cash row | Already inside reported CFO; no second WC deduction |",
        "| Reconstruct operating-only historical cash taxes | Use reported CFO and the explicit reported-ETR interest adjustment; no claim of exact operating cash taxes |",
        "| Split all finance-asset additions | Historical investment is cash PP&E; unknown financed investment is outside this stated measure, not treated as zero |", "",
        "The previously unresolved accounting allocations remain unresolved. They no longer",
        "block this narrower historical calculation; they may still matter for economic",
        "comparability, forecasting and a different investment definition.", "",
        "## Remaining blockers and differences", "",
        "- **Apple FY2024–25:** required total interest expense is not separately disclosed",
        "  in the reviewed annual filings/XBRL. No zero, net Other income, coupon estimate",
        "  or EBIT-method fallback is substituted. CFO less cash PP&E of 108.807B/98.767B",
        "  is available separately but is not labelled FCFF.",
        "- **Tax-rate convention:** reported provision/pretax is reproducible but can reflect",
        "  unusual charges. It is neither a disclosed actual interest tax shield nor an",
        "  automatically approved forecast rate. Nonpositive pretax requires separate review.",
        "- **SBC:** the selected historical CFO keeps the reported SBC add-back. The current",
        "  forecast retains SBC as an operating expense. There is no automatic conversion.",
        "- **Investment:** history subtracts cash PP&E; the existing forecast can include",
        "  new finance-leased operating assets. Principal is not deducted again from history.",
        "- **Non-operating cash/taxes:** amounts inside reported CFO remain there unless",
        "  a future separately approved adjustment establishes another basis.", "",
        "## Consumer behavior", "",
        "Both DCF and scenario charts display available historical FCFF bars and exact",
        "year readouts. Historical FCFF is explicitly labelled as derived from reported",
        "inputs in the basis notice and source details. All five operands and official",
        "source links are exposed in the expandable chart observations. Missing Apple",
        "years remain absent bars with an explicit missing-interest reason.", "",
        "Historical-to-historical FCFF endpoint guides are allowed for compatible positive",
        "endpoints. FCFF CAGR does not connect CFO-based history to the EBIT-based forecast.",
        "Revenue comparisons continue across the anchor. Historical results do not fill",
        "forward assumptions or affect EV. Source precision limits calculated digits.", "",
        "## Verification and scope", "",
        "- Offline evidence replay checks source receipt URL/hash/length, primary-inline",
        "  and extracted-instance amounts, target periods and accepted package bindings.",
        "- Startup checks the pinned ledger, original package digest, period identity and",
        "  all 13 calculated results before generating the bounded catalog.",
        "- [Full source evidence and exact arithmetic](company-data-preparation/historical-fcff-filing-calculations.json).",
        "- [Selected results and operands CSV](company-data-preparation/historical-cfo-fcff-adoption.csv).",
        "- Replay: `PYTHONPATH=src .venv/bin/python scripts/adopt_historical_cfo_fcff.py --check`.",
        "- Frozen normalization, original approvals and all earlier numerical audit artifacts",
        "  are preserved. The estimated pilot stays withdrawn. Expansion beyond these",
        "  three companies remains paused; 13/15 is not a 500-company coverage claim.", "",
        "## Validation", "",
        "60 financial review/history tests, 206 valuation tests and 66 API tests pass,",
        "including targeted reruns after finalizing the bundle. All 272 frontend tests",
        "pass across the full run and targeted reruns; integration tests that exceeded",
        "the default five-second limit were rerun with one worker and a 15-second limit.",
        "The production frontend build passes. No timeout setting in source was changed.", "",
        "The local API returns 5/5/3 available years for GOOGL/META/AAPL. Browser inspection",
        "confirms Alphabet's historical bars and FY2025 readout of 73.88B, while its",
        "existing enterprise value remains 1.42tn. Apple/Meta still require their existing",
        "forward inputs before the workspace can display a forecast chart.", "",
        "![Alphabet historical FCFF preview](assets/historical-cfo-fcff-pilot.jpg)", ""]
    return {REPORT: "\n".join(lines), CSV: stream.getvalue()}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build()
    for name, text in outputs(data).items():
        path = ROOT / name
        if args.check:
            if path.read_bytes() != text.encode():
                raise SystemExit("Adoption output differs: " + name)
        else:
            path.write_text(text)
    print(f'Historical CFO basis: {data["calculated"]}/15 calculated, {data["missing"]}/15 missing; source replay passed')


if __name__ == "__main__":
    main()
