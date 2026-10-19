"""Validate three complete Bear/Base/Bull cases; calculate only with --run."""

import argparse
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from valuation_platform.valuation.consumer import ANCHORS
from valuation_platform.valuation.scenario_inputs import (
    ScenarioInputError, load_scenario_set, run_scenario_set, serialize_scenarios,
)


def render_summary(result):
    """Compare existing components; isolated Decimal arithmetic is display only."""
    entries = result["scenarios"]
    first = entries[0]["result"]
    doc = first["submitted_inputs"]
    anchor = first["stage_b"]["stage_a"]["anchor"]
    company = ANCHORS.get(doc["anchor"]["kind"], {}).get("ticker", "Synthetic fixture")
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        def money(value):
            return f"{Decimal(value) / Decimal('1000000'):,.8f}"

        def percent(value):
            return f"{Decimal(value) * Decimal(100):.2f}%"

        def row(label, values):
            return f"{label} | " + " | ".join(values)

        lines = ["ANALYST SCENARIO COMPARISON — Bear / Base / Bull",
                 f"Set: {result['scenario_set_name']}", f"Company: {company} | CIK {anchor['cik']}",
                 f"Anchor: {anchor['form']} {anchor['accession']} | {anchor['annual_start']} to {anchor['annual_end']}",
                 f"Anchor revenue: {money(anchor['revenue'])} USD millions | Source: {anchor['source_reference']}",
                 f"Analytical date: {entries[0]['analytical_date']} | Declared information cutoff: {entries[0]['information_cutoff']}",
                 f"Input basis: {first['input_basis']} | Scope: {'EQUITY_PER_SHARE' if 'stage_c' in first else 'ENTERPRISE_VALUE'}",
                 "Timing: " + first["stage_b"]["timing"]["notice"],
                 "Cutoff is a shared submitted declaration; source availability is not authenticated.",
                 "Amounts: USD millions; share counts: actual shares; per-share values: USD/share.",
                 "", row("Metric", [x["label"] for x in entries])]
        for i in range(5):
            label = doc["forecast_years"][i]["fiscal_year_label"]
            for title, key in (("Revenue", "revenue"), ("FCFF", "fcff")):
                lines.append(row(f"{label} {title}", [money(x["result"]["stage_b"]["stage_a"]["years"][i][key]) for x in entries]))
        for title, key in (("WACC", "wacc"), ("Terminal growth", "terminal_growth")):
            lines.append(row(title, [percent(x["result"]["submitted_inputs"][key]) for x in entries]))
        for title, key in (("Operating margin", "operating_margin"), ("Operating tax", "operating_tax_rate"),
                           ("D&A/revenue", "d_and_a_percent_revenue"), ("Investment/revenue", "investment_percent_revenue"),
                           ("WC cash/full revenue", "working_capital_cash_requirement_percent_revenue")):
            lines.append(row("Terminal " + title, [percent(x["result"]["submitted_inputs"]["terminal"][key]) for x in entries]))
        lines.append(row("Terminal FCFF", [money(x["result"]["stage_b"]["terminal"]["fcff"]) for x in entries]))
        for title, key in (("Explicit-period PV", "pv_explicit_fcff"), ("Terminal value at Year 5", "terminal_value"),
                           ("Discounted terminal value", "pv_terminal_value"), ("Enterprise value (EV)", "enterprise_value")):
            lines.append(row(title, [money(x["result"]["stage_b"][key]) for x in entries]))
        contributions = []
        for entry in entries:
            b = entry["result"]["stage_b"]
            ev = Decimal(b["enterprise_value"])
            if ev.is_zero():
                contributions.append("undefined (EV is zero)")
                continue
            ratio = Decimal(b["pv_terminal_value"]) / ev
            text = percent(ratio)
            if ratio < 0 or ratio > 1:
                text += " (signed/over 100%; offsetting PVs, not clamped)"
            if ev < 0:
                text += " (negative EV; arithmetic ratio)"
            contributions.append(text)
        lines += [row("Terminal contribution / EV", contributions),
                  "EV = explicit-period PV + discounted terminal value; EV is not equity or value/share."]
        if "stage_c" in first:
            c = first["stage_c"]
            shares = c["inputs"]["shares"]
            lines += ["", "Fixed bridge across scenarios (USD millions; same declared inputs):"]
            for item in c["contributions"]:
                lines.append(f"  {item['component']['component_id']} [{item['component']['role']}]: {money(item['signed_contribution'])}")
            lines += [f"Eligible-asset subtotal (+): {money(c['eligible_assets'])}",
                      f"Financing subtotal (subtract): {money(c['financing_claims'])}",
                      f"Other-claim subtotal (subtract): {money(c['other_equity_claims'])}",
                      row("Equity value", [money(x["result"]["stage_c"]["equity_value"]) for x in entries]),
                      f"Fixed valuation shares: {Decimal(c['valuation_shares']):,f} actual shares | Date: {shares['observation_date']}",
                      f"Class: {shares['class_id']} | Equivalence: {shares['equivalence_convention']}",
                      f"Award convention: {shares['award_policy']} | Share rationale: {shares['rationale']}",
                      row("Scope-qualified value/share (USD/share)", [f"{Decimal(x['result']['stage_c']['value_per_share']):,.8f}" for x in entries]),
                      "Shared bridge observations / exclusions / omissions (not additional operands):"]
            for note in c["inputs"]["observations"]:
                value = "unknown amount, not zero" if note["value"] is None else f"{note['value']} {note['unit']}"
                lines.append(f"  {note['observation_id']} [{note['disposition']}]: {value}; {note['rationale']}")
            for coverage in c["inputs"]["coverage"]:
                lines.append(f"  Coverage {coverage['role']}: {coverage['review']['rationale']}; omissions={coverage['omission_references']}")
        lines += ["", "Investment = cash PP&E plus non-overlapping new finance-leased operating assets; principal excluded.",
                  "WC cash requirement uses full revenue: positive uses cash, negative releases cash. SBC/service leases stay in margins.",
                  "Display only: money in USD millions and USD/share rounded to 8 decimals; percentages to 2 (HALF_EVEN).",
                  "Rounded components may not sum. JSON retains full precision, submitted assumptions and provenance."]
        for entry in entries:
            r = entry["result"]
            d = r["submitted_inputs"]
            lines += ["", f"{entry['label']}: {r['case_name']}",
                      f"Analyst: {d['analyst']['author']} | Entered: {d['analyst']['timestamp_utc']}",
                      "Rationale: " + d["analyst"]["rationale"], "Scope: " + d["scope"],
                      *["- " + value for value in r["limitations"]]]
        lines += ["", *result["limitations"], "No valuation ordering, expected value or economic approval is implied."]
        return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario_set", type=Path)
    parser.add_argument("--run", action="store_true", help="Explicitly calculate all three validated cases")
    parser.add_argument("--format", choices=("json", "summary"), default="json")
    parser.add_argument("--output", type=Path, help="Save to a new file outside source/history paths; never overwrite")
    args = parser.parse_args(argv)
    if args.output and not args.run:
        parser.error("--output requires --run; validation never calculates or writes results")
    try:
        scenarios = load_scenario_set(args.scenario_set)
        if not args.run:
            print("VALID: three complete comparable cases; no calculation or economic approval.")
            return 0
        if args.output:
            destination = args.output.resolve()
            if destination.is_relative_to(ROOT) and not destination.is_relative_to(ROOT / "output"):
                raise ScenarioInputError(["--output must be outside the repository or under output/; source/history paths are protected"])
            if destination.exists() or destination == args.scenario_set.resolve():
                raise ScenarioInputError(["--output must name a new file distinct from the input; existing files are never overwritten"])
        result = run_scenario_set(scenarios, ROOT)
        payload = render_summary(result) if args.format == "summary" else serialize_scenarios(result)
        if args.output:
            with args.output.open("x", encoding="utf-8") as output:
                output.write(payload)
        else:
            print(payload, end="")
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
