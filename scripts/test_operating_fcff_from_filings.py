"""Test an EBIT-based FCFF build for the existing three-company five-year window.

No network requests, estimate imports, approval mutations, or valuation/UI writes.
Reuses retained source verification and the accepted CFO display populations.
"""
import argparse
import csv
from decimal import Decimal
from fractions import Fraction
import hashlib
from io import StringIO
import json
from pathlib import Path

from calculate_historical_fcff_from_filings import RetainedFiling, KINDS
from prepare_trillion_review_batch import primary_fact
from valuation_platform.analyst import statement_delivery as statements
from valuation_platform.review.operating_fcff import METHOD, amount, calculate, serialized
from valuation_platform.valuation.consumer import ANCHORS, load_revenue_anchor

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = "docs/company-data-preparation/historical-fcff-operating-test.json"
CSV_PATH = "docs/company-data-preparation/historical-fcff-operating-test.csv"
REPORT_PATH = "docs/historical-fcff-operating-test.md"
PRIOR_PATH = "docs/company-data-preparation/historical-fcff-filing-calculations.json"
NAMED_TRADE_CONCEPTS = frozenset((
    "IncreaseDecreaseInAccountsReceivable", "IncreaseDecreaseInInventories",
    "IncreaseDecreaseInOtherReceivables", "IncreaseDecreaseInAccountsPayable",
    "IncreaseDecreaseInAccountsPayableTrade", "IncreaseDecreaseInOtherAccountsPayable",
    "IncreaseDecreaseInAccruedRevenueShare", "IncreaseDecreaseInContractWithCustomerLiability",
    "IncreaseDecreaseInDeferredRevenue"))


def table_point(filing, identity, location, concept, namespace, contexts):
    """Reuse the existing exact primary-cell verifier, including tagged zero.

    Rounded note values can share QName/context with statement values. The
    existing review's actual statement coordinates disambiguate them.
    """
    if not hasattr(filing, "statement_tables"):
        filing.statement_tables = statements.parse({"body": filing.primary.artifact.body}, improved=True)
    row = filing.statement_tables[location["table"]][location["row"]]
    candidates = []
    for column, cell in enumerate(row):
        if "column" in location and column != location["column"]:
            continue
        for item in cell["facts"]:
            prefix, local = item["attrs"]["name"].split(":")
            if (local != concept or filing.namespaces[prefix] != namespace
                    or item["attrs"]["contextref"] not in contexts):
                continue
            candidates.append(primary_fact({"filing": filing}, item, location["table"], location["row"], column, location["caption"]))
    if len(candidates) != 1:
        raise ValueError("Exactly one source-bound primary statement cell required")
    return dict(candidates[0], evidence_depth="exact_primary_inline_and_instance_verified",
                source_identity=filing.source_identity, target_annual_start=identity["annual_start"],
                target_annual_end=identity["annual_end"], sources=filing.references)


def point_from(filing, identity, source):
    if source.get("primary_table"):
        result = table_point(filing, identity, source["primary_table"], source["concept"], source["namespace"],
                             {o["context_id"] for o in source["occurrences"]})
        if {o["ordinal"] for o in result["occurrences"]} != {o["ordinal"] for o in source["occurrences"]}:
            raise ValueError("Caption-specific original source occurrence changed")
    else:
        result = filing.extract(source["concept"], identity, source["namespace"])
    if amount(result["value"]) != amount(source["value"]):
        raise ValueError("Retained selection/source amount mismatch")
    return result


def statement_terms(row, filing):
    """Recheck the full displayed CFO sum, using explicit source cash signs."""
    identity = row["identity"]
    reconciliation = row["cfo_reconciliation"]
    terms = []
    if "terms" in reconciliation:
        if reconciliation["supported"] is not True or reconciliation["residual_used"] is not False:
            raise ValueError("Supported no-residual CFO required")
        for index, term in enumerate(reconciliation["terms"]):
            source = row["facts"][term["fact"]]
            terms.append(dict(caption=term["fact"], source=point_from(filing, identity, source),
                              cash_contribution_usd=term["contribution_usd"], cash_sign=term["multiplier"],
                              selection_reference=f"cfo_reconciliation/terms/{index}"))
    else:
        check = row.get("independent_display_check")
        reference = "independent_display_check"
        if check is None:
            supported = [(i, p) for i, p in enumerate(reconciliation["populations"]) if p["status"] == "SUPPORTED"]
            if len(supported) != 1:
                raise ValueError("Unique supported displayed CFO population required")
            index, check = supported[0]
            reference = f"cfo_reconciliation/populations/{index}"
        if check["status"] != "SUPPORTED" or amount(check["difference"]) != 0:
            raise ValueError("Independent CFO display must reconcile exactly")
        for index, term in enumerate(check["rows"]):
            if "fact" in term:
                source = point_from(filing, identity, term["fact"])
            else:
                source = table_point(filing, identity, {"table": term["table"], "row": term["row"], "caption": term["caption"]},
                                     term["concept"], term["namespace"], {term["context_id"]})
            raw, signed = amount(source["value"]), amount(term["value"])
            sign = signed / raw if raw else Fraction(term.get("sign", 1))
            if sign not in (-1, 1) or (not raw and signed):
                raise ValueError("Explicit cash contribution must be signed source amount")
            terms.append(dict(caption=term["caption"], source=source,
                              cash_contribution_usd=term["value"], cash_sign=int(sign),
                              selection_reference=f"{reference}/rows/{index}"))
    if len({(t["source"]["concept"], tuple(tuple(d) for d in t["source"]["occurrences"][0]["dimensions"])) for t in terms}) != len(terms):
        raise ValueError("Duplicate CFO statement population")
    for term in terms:
        if term["cash_sign"] not in (-1, 1) or amount(term["cash_contribution_usd"]) != amount(term["source"]["value"]) * term["cash_sign"]:
            raise ValueError("CFO source/contribution/sign mismatch")
    cfo = filing.extract("NetCashProvidedByUsedInOperatingActivities", identity)
    if sum((amount(t["cash_contribution_usd"]) for t in terms), Fraction()) != amount(cfo["value"]):
        raise ValueError("Full CFO population fails source control; no balancing plug allowed")
    return terms, cfo


def classify(term):
    """Analyst test perimeter; mixed rows retain their actual broad captions."""
    concept, caption = term["source"]["concept"], term["caption"].lower()
    if concept.startswith("IncreaseDecrease"):
        if "IncomeTax" in concept:
            return "separate_income_tax_movement"
        return "named_trade_movement" if concept in NAMED_TRADE_CONCEPTS else "mixed_asset_liability_movement"
    if "Depreciation" in concept or concept == "AmortizationAndImpairmentOfIntangibleAssets":
        return "reported_da_or_combined_impairment"
    if "impairment charges for" in caption or "abandonment" in caption:
        return "separate_operating_noncash_charge"
    if concept == "NetIncomeLoss":
        return "net_income_control"
    return "other_reconciliation_adjustment_not_in_test"


def build(root=ROOT):
    manifests, companies = {}, []
    prior_payload = (root / PRIOR_PATH).read_bytes()
    prior = {c["ticker"]: c for c in json.loads(prior_payload)["companies"]}
    for kind in KINDS:
        load_revenue_anchor(kind, root)
        spec = ANCHORS[kind]
        ticker, prefix = spec["ticker"], spec["ticker"].lower()
        payload = (root / spec["package"]).read_bytes()
        package = json.loads(payload)
        rows = package["periods"] if prefix == "meta" else package[prefix + "_history_review"]["periods"]
        if [row["identity"]["annual_end"][:4] for row in rows] != [str(year) for year in range(2021, 2026)]:
            raise ValueError("This method test is scoped to five selected FY2021-FY2025 annuals")
        filings = [RetainedFiling(root, row, manifests) for row in rows]
        periods = []
        for index, (row, filing) in enumerate(zip(rows, filings, strict=True)):
            identity = row["identity"]
            terms, cfo = statement_terms(row, filing)
            for term in terms:
                term["role_in_test"] = classify(term)
            noncash = [t for t in terms if t["role_in_test"] in (
                "reported_da_or_combined_impairment", "separate_operating_noncash_charge")]
            movements = [t for t in terms if t["role_in_test"] in (
                "named_trade_movement", "mixed_asset_liability_movement")]
            narrow = [t for t in movements if t["role_in_test"] == "named_trade_movement"]
            inputs = {"ebit": point_from(filing, identity, row["facts"]["ebit"]),
                      "cfo_control": cfo, "cash_ppe": filing.extract("PaymentsToAcquirePropertyPlantAndEquipment", identity),
                      "tax_provision": filing.extract("IncomeTaxExpenseBenefit", identity),
                      "pretax_income": point_from(filing, identity, row["facts"]["pretax"])}
            def run(movement_population):
                return calculate(*(inputs[k]["value"] for k in ("ebit", "tax_provision", "pretax_income")),
                                 [t["cash_contribution_usd"] for t in noncash], inputs["cash_ppe"]["value"],
                                 [t["cash_contribution_usd"] for t in movement_population])
            result, alternative = run(movements), run(narrow)
            nopat = amount(inputs["ebit"]["value"]) * (1 - amount(inputs["tax_provision"]["value"]) / amount(inputs["pretax_income"]["value"]))
            other_adjustments = sum((amount(t["cash_contribution_usd"]) for t in terms
                                     if t["role_in_test"] not in ("net_income_control", "reported_da_or_combined_impairment",
                                         "separate_operating_noncash_charge", "named_trade_movement", "mixed_asset_liability_movement")), Fraction())
            # Exact bridge to reported CFO less cash PP&E. This is an identity,
            # not an allocation of mixed rows or proof of operating equivalence.
            tax = amount(inputs["tax_provision"]["value"]) / amount(inputs["pretax_income"]["value"])
            net_nonoperating_after_tax = (amount(inputs["pretax_income"]["value"]) - amount(inputs["ebit"]["value"])) * (1-tax)
            test_value = nopat + sum((amount(t["cash_contribution_usd"]) for t in noncash+movements),Fraction()) - amount(inputs["cash_ppe"]["value"])
            cash_fcf = amount(cfo["value"]) - amount(inputs["cash_ppe"]["value"])
            if test_value + net_nonoperating_after_tax + other_adjustments != cash_fcf:
                raise ValueError("EBIT-to-CFO bridge fails; no residual permitted")
            old = prior[ticker]["periods"][index]
            for key in ("cash_ppe", "tax_provision", "pretax_income"):
                if inputs[key]["value"] != old["inputs"][key]["value"]:
                    raise ValueError("Prior comparison period/source selection changed")
            if cfo["value"] != old["inputs"]["cfo"]["value"] or identity != old["identity"]:
                raise ValueError("Prior CFO/annual identity changed")
            interest = filing.total_interest(identity)
            if interest is None and prefix == "meta" and index < 2:
                interest = filings[2].total_interest(identity)
            comparison = None
            if interest is not None:
                prior_value = cash_fcf + amount(interest["value"]) * (1-tax)
                if serialized(prior_value)["exact_fraction_usd"] != old["fcff"]["exact_fraction_usd"]:
                    raise ValueError("Prior FCFF does not independently reproduce")
                comparison = {"prior_cfo_method": serialized(prior_value),
                              "operating_test_minus_cfo_method": serialized(test_value-prior_value),
                              "interest_source": interest}
            elif old["fcff"] is not None:
                raise ValueError("Prior interest gap changed")
            periods.append({"identity": identity, "fiscal_year_label": "FY"+identity["annual_end"][:4],
                "inputs": inputs, "statement_terms": terms, "operating_method_test": result,
                "named_trade_only_alternative": alternative,
                "mixed_movement_exposure": serialized(sum((amount(t["cash_contribution_usd"]) for t in movements if t not in narrow), Fraction())),
                "cfo_reconciliation": {"status": "EXACT_SOURCE_ROW_SUM", "difference_usd": "0", "term_count": len(terms)},
                "cash_fcf_bridge": {"net_nonoperating_after_reported_etr": serialized(net_nonoperating_after_tax),
                    "excluded_statement_adjustments_and_explicit_tax_movements": serialized(other_adjustments),
                    "cash_fcf": serialized(cash_fcf), "difference_usd": "0", "residual_used": False},
                "prior_method_comparison": comparison,
                "status": "CALCULATED_REVIEW_TEST_INPUT_ALIGNMENT_UNRESOLVED",
                "verified_operating_fcff": None,
                "limitations": [
                    "Reported consolidated ETR applied to EBIT is an allocation convention; tax charges are not normalized and provision is not cash operating tax.",
                    "Broad asset/liability cash-movement rows can contain tax, noncurrent or other mixed components. Excluding explicitly labelled income-tax rows does not prove the rest is tax-free operating WC.",
                    "Reported cash-flow D&A/combined impairment is a disclosed population, not a newly certified complete income-recognized D&A total. No finance ROU amortization is added a second time.",
                    "Cash PP&E is the named investment perimeter. No estimated finance additions, capital-creditor allocation, acquisition allocation or capitalized-interest adjustment is made.",
                    "SBC stays expensed in EBIT; its CFO add-back is excluded. No other mixed adjustment is declared zero or immaterial."]})
        companies.append({"ticker": ticker, "package": spec["package"], "package_sha256": hashlib.sha256(payload).hexdigest(), "periods": periods})
    return {"schema_version": "historical-operating-fcff-test-v1", "as_of": "2026-11-02", "methodology": METHOD,
        "scope": "GOOGL/AAPL/META FY2021-FY2025; five reported annuals, no FY2026 extrapolation",
        "purpose": "Test the standard EBIT-based approach, not approve historical chart or valuation inputs",
        "input_estimates_permitted": False, "tax_convention": "Reported income-tax provision / reported pretax income, applied to EBIT; no normalization or cash-tax equivalence claim",
        "movement_convention": "Signed disclosed statement changes in assets/liabilities, excluding explicitly identified income-tax rows. Mixed rows remain visibly mixed; no balance-sheet delta proxy.",
        "noncash_convention": "Reported D&A/combined impairment captions plus separately identified facilities/data-center noncash impairment/abandonment adjustments; no SBC add-back or second finance amortization add-back",
        "alternative_notice": "Named trade-only alternative measures sensitivity to including mixed rows. It is neither complete FCFF nor a confidence interval or bound on true cash flow.",
        "calculated_test_periods": sum(len(c["periods"]) for c in companies),
        "certified_operating_fcff_periods": sum(p["verified_operating_fcff"] is not None for c in companies for p in c["periods"]),
        "publishable": False,
        "prior_comparison_source": {"path": PRIOR_PATH, "sha256": hashlib.sha256(prior_payload).hexdigest()}, "companies": companies}


def csv_output(data):
    stream = StringIO(newline="")
    fields = ("ticker", "fiscal_year", "ebit_usd", "tax_provision_usd", "pretax_income_usd", "reported_etr", "nopat_usd",
              "selected_noncash_costs_usd", "cash_ppe_usd", "selected_movement_cash_contribution_usd", "operating_test_billions",
              "named_trade_only_alternative_billions", "mixed_movement_exposure_usd", "prior_cfo_method_billions", "difference_from_prior_billions", "status", "primary_filing")
    writer = csv.DictWriter(stream, fields, lineterminator="\n"); writer.writeheader()
    for c in data["companies"]:
        for p in c["periods"]:
            i, r, comp = p["inputs"], p["operating_method_test"], p["prior_method_comparison"]
            writer.writerow(dict(ticker=c["ticker"], fiscal_year=p["fiscal_year_label"], ebit_usd=i["ebit"]["value"], tax_provision_usd=i["tax_provision"]["value"],
                pretax_income_usd=i["pretax_income"]["value"], reported_etr=r["reported_etr"], nopat_usd=r["nopat"]["amount_usd"],
                selected_noncash_costs_usd=r["noncash_costs"]["amount_usd"], cash_ppe_usd=i["cash_ppe"]["value"],
                selected_movement_cash_contribution_usd=r["movement_cash_contribution"]["amount_usd"], operating_test_billions=r["result"]["display_billions"],
                named_trade_only_alternative_billions=p["named_trade_only_alternative"]["result"]["display_billions"], mixed_movement_exposure_usd=p["mixed_movement_exposure"]["amount_usd"],
                prior_cfo_method_billions=comp["prior_cfo_method"]["display_billions"] if comp else "",
                difference_from_prior_billions=comp["operating_test_minus_cfo_method"]["display_billions"] if comp else "", status=p["status"],
                primary_filing=next(s["url"] for s in i["ebit"]["sources"] if s["url"].endswith(".htm"))))
    return stream.getvalue()


def render(data):
    def million(value): return f"{Decimal(value)/1000000:,.3f}"
    lines = ["# Historical FCFF — operating-profit method test", "", "November 2, 2026. Alphabet, Apple and Meta, FY2021–FY2025.", "",
        "**All 15 operating-method arithmetic tests calculate without an interest estimate.**",
        "This resolves the interest-input dependency, including Apple FY2024/25.",
        "It does not yet establish 15 fully reconciled operating FCFF observations:",
        "mixed cash-movement rows, D&A scope and the investment perimeter still matter.",
        "The figures below are explicitly a method test; verified_operating_fcff remains null.", "",
        "## Tested definition", "",
        "`EBIT × (1 − reported tax provision / reported pretax income) + disclosed D&A/identified noncash operating charges − cash PP&E + selected signed cash movements`", "",
        "The standard EBIT/NOPAT approach is described by [CFA Institute](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation)",
        "and [Wall Street Prep](https://www.wallstreetprep.com/knowledge/unlevered-free-cash-flow/).",
        "Our statement-population choices below are explicit test conventions, not those sources' endorsement of these issuer inputs.", "",
        "- Every numerical operand is verified against retained SEC primary inline and extracted XBRL, including exact annual dates, dimensions, units and source hashes.",
        "- Use reported consolidated ETR, without clipping or normalizing. This is an allocation convention, not an observed unlevered cash-tax bill.",
        "- Keep SBC expensed in operating profit. Exclude the separate CFO SBC add-back.",
        "- Alphabet FY2021/22 includes both disclosed depreciation/impairment and intangible amortization/impairment captions. Later years use disclosed depreciation; missing intangible detail is not zero-filled.",
        "- Meta includes separately disclosed facilities and data-center noncash charges/reversals once, in addition to D&A. They are not renamed D&A. No second finance-lease amortization add-back.",
        "- Use the disclosed asset/liability cash movements, excluding explicitly named income-tax movements. Mixed Other and accrued rows remain mixed, not certified operating WC. Positive contribution adds cash; cash use is its negative.",
        "- Deduct cash PP&E only. No finance-lease mix estimates, debt-based interest estimates, book-delta substitution or residual balancing item.", "",
        "## Results — USD billions, method-test figures", "", "| Company | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |", "|---|---:|---:|---:|---:|---:|"]
    for c in data["companies"]:
        lines.append("| "+c["ticker"]+" | "+" | ".join(p["operating_method_test"]["result"]["display_billions"] for p in c["periods"])+" |")
    lines += ["", "These are reproducible filing-operand calculations under the stated perimeter, **not forecasts or fabricated missing amounts**.",
        "They are also **not yet certified cash FCFF**; a source-supported number does not validate the classification of a mixed source row.", "",
        "## Check against the previous CFO method", "", "| Company | FY | Operating test | Prior CFO method | Difference: operating − prior |", "|---|---|---:|---:|---:|"]
    for c in data["companies"]:
        for p in c["periods"]:
            r, comp = p["operating_method_test"]["result"]["display_billions"], p["prior_method_comparison"]
            lines.append(f"| {c['ticker']} | {p['fiscal_year_label']} | {r} | "+(f"{comp['prior_cfo_method']['display_billions']} | {comp['operating_test_minus_cfo_method']['display_billions']} |" if comp else "Unavailable: interest undisclosed | — |"))
    lines += ["", "The two methods do not currently have identical economic perimeters. Each of the 15 tests has an exact, zero-residual bridge:", "",
        "`operating test + (pretax income − EBIT) × (1 − ETR) + excluded CFO adjustments/explicit tax movements = reported CFO − cash PP&E`.", "",
        "Where disclosed, adding interest expense × (1 − ETR) to the right side independently reproduces all 13 prior results.",
        "The bridge explicitly includes excluded SBC, deferred taxes, securities gains/losses, Other and tax movements; it never assigns a residual to WC.",
        "This explains why switching formulas alone cannot establish equivalent FCFF.", "",
        "## Input-alignment test", "", "A second calculation includes only explicitly named trade cash movements, excluding mixed Other/accrued rows.",
        "The difference shows the size of the classification exposure; neither variant is a confidence interval or a bound on economic FCFF.", "",
        "| Company | FY | Broad disclosed-movement test | Named-trade-only test | Mixed movement contribution |", "|---|---|---:|---:|---:|"]
    for c in data["companies"]:
        for p in c["periods"]:
            lines.append(f"| {c['ticker']} | {p['fiscal_year_label']} | {p['operating_method_test']['result']['display_billions']} | {p['named_trade_only_alternative']['result']['display_billions']} | {p['mixed_movement_exposure']['display_billions']} |")
    lines += ["", "### Specific issues found", "",
        "- **Apple:** the EBIT route needs no missing interest input. But FY2024's reported tax provision includes the Ireland State Aid charge, and FY2025 cash taxes/Other movements include subsequent timing effects. The FY2025 10-K Note 7 describes a 10.2B net FY2024 charge and 15.8B payable via escrow. Neither ETR nor broad Other movements are silently normalized. The cash-flow D&A caption is disclosed; complete expense/inventory timing is not newly certified.",
        "- **Alphabet:** early noncash captions explicitly include impairment, while FY2023–25 separately display depreciation. Intangible/Other scope changes and operating/finance lease overlap remain limitations. Explicit cash income-tax movements are excluded; mixed accrual movements are not automatically tax-free.",
        "- **Meta:** facilities/data-center noncash charges are separate from D&A. FY2025's tax provision is materially affected by deferred tax/valuation-allowance items; applying reported ETR retains those effects, rather than treating this as normalized cash tax. Mixed liabilities and financed investment remain separate review needs.", "",
        "## Operand schedules — USD millions", "",
        "Positive movement contribution adds cash; a negative value represents a use of cash. Source rounding is retained; displayed calculated digits add no filing precision.", ""]
    for c in data["companies"]:
        lines += ["### "+c["ticker"], "", "| FY | EBIT | Tax provision | Pretax | Selected noncash costs | Cash PP&E | Movement contribution | Test result |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for p in c["periods"]:
            i, r = p["inputs"], p["operating_method_test"]
            values = [i[k]["value"] for k in ("ebit", "tax_provision", "pretax_income")]+[r["noncash_costs"]["amount_usd"], i["cash_ppe"]["value"], r["movement_cash_contribution"]["amount_usd"], r["result"]["amount_usd"]]
            lines.append("| "+p["fiscal_year_label"]+" | "+" | ".join(million(x) for x in values)+" |")
        lines += ["", "Primary SEC filings:", ""]
        for p in c["periods"]:
            url = next(s["url"] for s in p["inputs"]["ebit"]["sources"] if s["url"].endswith(".htm"))
            lines.append(f"- [{p['fiscal_year_label']} 10-K]({url}) — {p['identity']['annual_start']} to {p['identity']['annual_end']}.")
        lines.append("")
    lines += ["## Conclusion and reproduction", "",
        "The EBIT approach works as an arithmetic route for all 15 periods and removes the interest-disclosure dependency.",
        "The remaining task is a defined operating tax/D&A/movement/investment reconciliation, rather than inventing interest.",
        "Do not replace live historical FCFF, forecast calibration, EV or original approved history with these test figures.",
        "The existing forecast's financed-investment perimeter is not certified by this cash-PP&E-only test.", "",
        "- [Exact source operands, classified rows, fraction arithmetic and full bridges](company-data-preparation/historical-fcff-operating-test.json).",
        "- [Flat calculation/comparison CSV](company-data-preparation/historical-fcff-operating-test.csv).",
        "- Replay: `PYTHONPATH=src .venv/bin/python scripts/test_operating_fcff_from_filings.py --check`.",
        "- Original filing receipts, frozen normalization, analyst packages and approval payloads are preserved. The earlier CFO calculation remains a separate definition; withdrawn estimates remain withdrawn.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    data = build()
    for name, text in {JSON_PATH: json.dumps(data, sort_keys=True, indent=2)+"\n", CSV_PATH: csv_output(data), REPORT_PATH: render(data)}.items():
        path = ROOT/name
        if args.check:
            if path.read_bytes() != text.encode(): raise SystemExit("Operating test replay differs: "+name)
        else: path.write_bytes(text.encode())
    print(f"{data['calculated_test_periods']} operating-method calculations; no interest estimates; input alignment remains explicit")


if __name__ == "__main__": main()
