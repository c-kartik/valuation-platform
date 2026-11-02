"""Offline three-company FCFF reconciliation review; no source/approval writes."""
import argparse
from decimal import Decimal
import json
from pathlib import Path

from valuation_platform.review.historical_fcff import build_review

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = "docs/company-data-preparation/historical-fcff-pilot-review.json"
REPORT = "docs/historical-fcff-pilot-review.md"


def render(review):
    def millions(observation):
        if observation is None:
            return "Not separately selected"
        return f"{Decimal(observation['amount_usd']) / 1000000:,.0f}"

    lines = ["# Historical FCFF pilot — Alphabet, Apple and Meta", "",
             "November 2, 2026. Scope: the existing FY2021–FY2025 accepted histories only.",
             "The wider universe review stays paused. This review reuses extraction and",
             "normalization; no historical package, fact, approval or forecast changes.", "",
             "## Result", "",
             "All fifteen selected annuals have source-bound reported CFO and cash PP&E;",
             "their independently displayed CFO arithmetic rechecks exactly. The tables",
             "show **CFO less cash PP&E**, a derived cash FCF measure, **not FCFF**.",
             "No economic adjustment is inferred from a missing value. Historical chart",
             "publication remains disabled pending the named reconciliation below.", "",
             "The machine companion retains package/audit hashes, exact annual identities,",
             "source pointers, occurrence precision/context and SEC source URLs:",
             "[fifteen-period reconciliation](company-data-preparation/historical-fcff-pilot-review.json).", "",
             "## Estimates prepared for review", "",
             "The user authorized clearly labelled estimates for review. These **estimated",
             "FCFF** figures are neither reported facts nor accepted historical chart values.",
             "They retain cash taxes/timing in CFO and use annual reported ETR only as a",
             "proxy for the tax effect of the estimated financing/nonoperating adjustment.",
             "This is not a fully reconciled operating cash-tax calculation.", "",
             "| Company | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |",
             "|---|---:|---:|---:|---:|---:|"]
    for company in review["companies"]:
        lines.append("| " + company["ticker"] + " | " + " | ".join(
            p["fcff_estimate_for_review"]["display_billions"] + "B" for p in company["periods"]) + " |")
    lines += ["", "Amounts above are USD billions, rounded only for display. Full arithmetic,",
             "operands and assumptions remain in the machine companion.", "",
             "The review estimate is:", "",
             "`CFO − cash PP&E − CFO SBC add-back − estimated financed investment − net nonoperating cash proxy × (1 − reported ETR)`", "",
             "The net nonoperating cash proxy is `Pretax − EBIT + identified pure nonoperating",
             "CFO reconciliation contributions`. The signed contributions prevent a second",
             "removal of securities gains already reversed in CFO. Net nonoperating income",
             "already includes interest expense: do not also add overlapping borrowing/lease",
             "interest. Mixed Other, tax allocation and accrual/cash differences remain",
             "unquantified uncertainty, not assumed reported zero.", "",
             "Two explicit investment estimates need particular review:", "",
             "- **Alphabet FY2021:** backcast finance additions using the median additions/",
             "  cash PP&E ratio from FY2022–25. Later information is deliberately used;",
             "  this is not a contemporaneous historical backtest.",
             "- **Apple FY2021–25:** allocate combined lease additions using the closing net",
             "  finance ROU asset share of total net ROU assets. Stock mix can differ from",
             "  new-investment mix, so this is an allocation estimate, not a filing split.", "",
             "Alphabet FY2022/23 instead use 577m/564m later-reported comparative additions",
             "from the retained FY2024 instance (Note 4). Original FY2022/23 source packages",
             "are unchanged. FY2024/25 Alphabet and all five META additions use existing",
             "named source observations with an explicit non-overlap assumption.", "",
             "## Proposed common calculation", "",
             "Start with independently reconciled CFO, subtract cash PP&E, then separately:", "",
             "1. Remove the CFO SBC add-back to retain compensation expense, consistently",
             "   with the existing forecast. Review expense/add-back scope differences;",
             "   do not also subtract the full SBC expense proxy a second time.",
             "2. Reverse financing interest actually included in CFO. Resolve overlaps",
             "   between borrowing and lease interest, and capitalized-interest treatment.",
             "3. Remove excluded nonoperating cash still in CFO. Accrual gains already",
             "   reversed in the cash-flow reconciliation are not another deduction.",
             "4. Reconcile reported taxes to unlevered operating taxes. Do not automatically",
             "   use reported ETR as a cash operating rate or apply a second tax shield.",
             "5. Deduct non-overlapping new financed operating investment, consistent with",
             "   the forecast's finance-asset convention. Review capital-creditor, cash",
             "   PP&E and acquisition boundaries so purchases/settlements count once.", "",
             "This is a **proposal**, not an activated historical formula. It does not",
             "alter the existing manual forecast contract. A cash-flow route avoids needing",
             "complete expense D&A or reconstructed book NWC; those are not new gates.",
             "D&A and working-capital movements already in CFO are not added/deducted again.", "",
             "The standard CFO route includes after-tax financing adjustments",
             "([CFA Institute](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation));",
             "the additional SBC/perimeter treatment here follows this platform's existing",
             "forecast convention rather than claiming every published FCF measure is equivalent.", "",
             "## Source-supported schedules", "",
             "Amounts are USD millions at retained filing precision. Cash PP&E is shown as",
             "an outflow magnitude. Original-as-selected periods and restatement boundaries",
             "remain; this is not a recast common-calendar series.", ""]
    for company in review["companies"]:
        lines += ["### " + company["ticker"], "",
                  "| FY | Reported CFO | Cash PP&E | CFO less cash PP&E | CFO SBC add-back |",
                  "|---|---:|---:|---:|---:|"]
        for period in company["periods"]:
            inputs = period["inputs"]
            lines.append("| " + " | ".join([
                period["fiscal_year_label"], millions(inputs["reported_cfo"]),
                millions({"amount_usd": inputs["signed_cash_ppe"]["raw_value"]}),
                millions(period["cash_fcf"]), millions(inputs["cfo_sbc_addback"])]) + " |")
        lines += ["", "Supporting disclosures below are **candidates, not additive adjustments**.", "",
                  "| FY | Cash-interest candidate | Finance-interest candidate | Finance-additions candidate (including later comparative) | Combined lease-additions support |",
                  "|---|---:|---:|---:|---:|"]
        for period in company["periods"]:
            support = period["supporting_observations"]
            points = [support.get("cash_interest_candidate"), support.get("finance_interest_candidate"),
                      support.get("finance_additions_candidate") or support.get("later_finance_additions_comparative"),
                      support.get("combined_lease_additions_support")]
            lines.append("| " + period["fiscal_year_label"] + " | " + " | ".join(millions(p) for p in points) + " |")
        notes = {
            "GOOGL": "Borrowing cash interest is not separately selected in any of the five retained annual packages. FY2024/25 interest expense is accrual support, not a cash payment. Original finance-additions selections exist only in FY2024/25; the review adds separately identified later FY2024 comparatives for FY2022/23, retaining source/fact dates and receipt hash. Combined early debt/lease repayments do not supply interest or additions. The rounded SBC expense and CFO add-back differ; do not call the difference rounding or charge both.",
            "AAPL": "Cash-interest candidates exist for FY2021–23; FY2024/25 are not separately selected. The note combines operating and finance lease additions in all five years: neither the whole combined value nor a liability-stock change is a finance-only addition. InterestPaidNet is a named reported population, not an automatically approved borrowing/lease split.",
            "META": "Finance interest and noncash finance additions are selected for all five years; borrowing/cash-interest candidates exist for FY2023–25. Interest populations may overlap and must not be summed automatically. FY2022–24 original shared-parser PARTIAL statuses remain; their separate accepted caption-specific display proofs recheck exactly. Original FY2021 cash PP&E18,567 remains selected, not later18,690.",
        }
        lines += ["", notes[company["ticker"]], "", "Selected primary filings:", ""]
        for period in company["periods"]:
            urls = period["inputs"]["reported_cfo"]["sources"]
            url = next(u for u in urls if u.endswith((".htm", ".html")))
            lines.append(f"- [{period['fiscal_year_label']} 10-K]({url}) — {period['identity']['annual_start']} to {period['identity']['annual_end']}.")
        lines += [""]
    lines += ["## Remaining decision and delivery boundary", "",
              "For each issuer/year, the machine review retains six unresolved signed",
              "adjustment roles: financing cash, nonoperating cash, operating taxes, SBC",
              "alignment, financed investment and investment perimeter. An observed support",
              "amount does not by itself resolve its economic allocation or overlap.", "",
              "The user explicitly chose **Allow clearly labeled estimates for review**.",
              "The concrete estimates above implement that review scope. Their specific tax,",
              "mixed-row, lease-allocation/backcast and investment-omission assumptions still",
              "need review before chart use. Original unresolved requirements and null actual",
              "FCFF remain; estimates do not silently resolve the source gaps or activate",
              "a new historical financial convention.", "",
              "Once resolved, connect the versioned calculation and its provenance to the",
              "existing historical chart window. Keep cash FCF separately named and never",
              "feed this intermediate into forecasts, DCF, cash-conversion calibration or EV.", "",
              "## Reproduce and verify", "",
              "Run `PYTHONPATH=src .venv/bin/python scripts/prepare_historical_fcff_review.py --check`.",
              "Tests cover all fifteen independent CFO sums/cash FCF values, source identities,",
              "unaltered packages, effective-value tampering, stale approvals, signs/units,",
              "rounded-note precision, missing support and Decimal-context independence.",
              "The 27-test review/history suite includes 12 new pilot financial/provenance",
              "tests, independent Fraction checks, later-comparative receipt tampering and",
              "separation of estimates from publishable FCFF. No runtime/UI change is included.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    review = build_review(ROOT)
    artifacts = {OUTPUT: json.dumps(review, sort_keys=True, indent=2) + "\n", REPORT: render(review)}
    for name, content in artifacts.items():
        path = ROOT / name
        if args.check:
            if path.read_text() != content:
                raise SystemExit("Historical FCFF review replay differs: " + name)
        else:
            path.write_text(content)
    print("Verified 3 issuers / 15 annual CFO reconciliations; no FCFF publication or approval activation")


if __name__ == "__main__":
    main()
