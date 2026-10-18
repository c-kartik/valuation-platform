"""Validate an editable local case; --run calculates its declared EV/equity scope."""

import argparse
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from valuation_platform.valuation.case_inputs import CaseInputError, load_case, run_case


def render_summary(result):
    """Display existing components; only scale/percentage arithmetic belongs here."""
    doc = result["submitted_inputs"]
    b = result["stage_b"]
    a = b["stage_a"]
    anchor = a["anchor"]
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        def money(value):
            return f"{Decimal(value) / Decimal('1000000'):,.8f}"

        def percent(value):
            return f"{Decimal(value) * Decimal('100'):.2f}%"

        column_width = max(14, *(len(money(value)) for year in a["years"]
                               for key, value in year.items()
                               if key not in ("period_index", "fiscal_year_label")))

        def row(label, values):
            return f"{label:<35} | " + " | ".join(f"{v:>{column_width}}" for v in values)

        years = a["years"]
        headers = row("Period", [f"Year {y['period_index']}" for y in years])
        company = "META" if doc["anchor"]["kind"] == "meta-fy2025" else "Synthetic fixture"
        stage_c = result.get("stage_c")
        lines = [
            "ANALYST REVIEW — EQUITY / VALUE PER SHARE" if stage_c else "ANALYST REVIEW — ENTERPRISE VALUE ONLY",
            f"Case: {result['case_name']}",
            f"Analyst: {doc['analyst']['author']} | Entered: {doc['analyst']['timestamp_utc']}",
            f"Input basis: {result['input_basis']} (supplied declarations; not economic approval)",
            f"Company: {company} | CIK {anchor['cik']}",
            f"Historical anchor: {anchor['form']} {anchor['accession']} | {anchor['annual_start']} to {anchor['annual_end']}",
            f"Anchor revenue: {money(anchor['revenue'])} USD millions | Source precision: {anchor['precision']}",
            f"Anchor reference: {anchor['source_reference']}",
            f"Fiscal-end analytical date: {b['timing']['analytical_t0']}",
            "Periods: " + "; ".join(f"{y['period_index']}={y['fiscal_year_label']}" for y in years),
            "", "Five-year input assumptions (%)", headers,
        ]
        annual_labels = (
            ("Revenue growth", "revenue_growth"),
            ("Operating margin", "operating_margin"),
            ("Operating tax rate", "forecast_tax_rate"),
            ("D&A / revenue", "d_and_a_percent_revenue"),
            ("Investment / revenue", "capex_percent_revenue"),
            ("WC cash / full revenue", "change_in_operating_nwc_percent_revenue"),
        )
        for label, key in annual_labels:
            lines.append(row(label, [percent(y[key]) for y in doc["forecast_years"]]))
        lines += [
            "Margins include SBC, operating-lease service costs and aligned D&A expense.",
            "Investment = cash PP&E plus non-overlapping new finance-leased operating assets; excludes finance principal.",
            "Working-capital cash requirement uses full forecast revenue: positive uses cash; negative releases cash.",
            "", "Forecast cash flows (USD millions; discount factors are unitless)", headers,
        ]
        for label, key in (
            ("Revenue", "revenue"), ("EBIT", "ebit"), ("Operating tax", "tax"),
            ("NOPAT", "nopat"), ("D&A", "d_and_a"), ("Investment", "investment"),
            ("Working-capital cash requirement", "working_capital_cash_requirement"), ("FCFF", "fcff"),
        ):
            lines.append(row(label, [money(y[key]) for y in years]))
        lines.append(row("Discount factor (unitless)", [f"{Decimal(y['discount_factor']):.6f}" for y in b["years"]]))
        lines.append(row("Discounted FCFF", [money(y["pv_fcff"]) for y in b["years"]]))
        lines += [
            "Operating tax reduces EBIT to NOPAT; D&A is added back; investment and positive WC cash are subtracted once.",
            "", f"WACC: {percent(doc['wacc'])} | Terminal growth: {percent(doc['terminal_growth'])}",
            "Explicit terminal assumptions (%) — independent of Year 5:",
        ]
        for label, key in (
            ("Operating margin", "operating_margin"), ("Operating tax rate", "operating_tax_rate"),
            ("D&A / revenue", "d_and_a_percent_revenue"), ("Investment / revenue", "investment_percent_revenue"),
            ("WC cash / full revenue", "working_capital_cash_requirement_percent_revenue"),
        ):
            lines.append(f"  {label}: {percent(doc['terminal'][key])}")
        lines += [
            "", "Enterprise-value reconciliation (USD millions)",
            f"Terminal FCFF: {money(b['terminal']['fcff'])}",
            f"Terminal value at end of Year 5: {money(b['terminal_value'])}",
            f"Explicit-period PV: {money(b['pv_explicit_fcff'])}",
            f"+ Discounted terminal value: {money(b['pv_terminal_value'])}",
            f"= Enterprise value (EV): {money(b['enterprise_value'])}",
        ]
        ev = Decimal(b["enterprise_value"])
        if ev.is_zero():
            lines.append("Discounted terminal value / EV contribution: undefined (EV is zero).")
        else:
            ratio = Decimal(b["pv_terminal_value"]) / ev
            lines.append(f"Discounted terminal value / EV contribution: {percent(ratio)}")
            if ratio < 0 or ratio > 1:
                condition = "is negative" if ratio < 0 else "exceeds 100%"
                lines.append(f"Contribution {condition} before display rounding; offsetting explicit/terminal PVs are preserved, not clamped.")
            if ev < 0:
                lines.append("EV is negative; the contribution is an arithmetic ratio, not a positive value allocation.")
        lines += [
            "EV is enterprise value, not equity value or per-share value.",
            "Display only: USD millions rounded to 8 decimals, percentages to 2, factors to 6 (HALF_EVEN).",
            "Rounded components may not sum on display. JSON retains full precision/provenance; display digits do not improve source precision.",
        ]
        if stage_c:
            bridge = stage_c["inputs"]
            shares = bridge["shares"]
            lines += ["", "Equity bridge (USD millions; signed contributions)",
                      f"Enterprise value: {money(b['enterprise_value'])}"]
            for line in stage_c["contributions"]:
                item = line["component"]
                sign = "+" if Decimal(line["signed_contribution"]) >= 0 else ""
                lines.append(f"  {item['component_id']} [{item['role']}; {item['origin']}; {item['population_id']}]: "
                             f"{sign}{money(line['signed_contribution'])}")
                lines.append(f"    Rationale: {item['rationale']}")
            for label, key in (("Eligible-asset subtotal (+)", "eligible_assets"),
                               ("Financing subtotal (subtract)", "financing_claims"),
                               ("Other-claim subtotal (subtract)", "other_equity_claims"),
                               ("Equity value", "equity_value")):
                lines.append(f"{label}: {money(stage_c[key])}")
            lines += [f"Valuation shares (actual shares, scale 1): {Decimal(stage_c['valuation_shares']):,f}",
                      f"Share observation date: {shares['observation_date']}",
                      f"Valuation class: {bridge['valuation_class_id']} | Equivalence: {shares['equivalence_convention']}",
                      f"Award convention: {shares['award_policy']}",
                      f"Share rationale: {shares['rationale']}",
                      f"Value per share (USD/share): {Decimal(stage_c['value_per_share']):,.8f}",
                      "Per-share display rounded to 8 decimals (HALF_EVEN); negative equity/value per share retained.",
                      "Bridge observations / exclusions / omissions (not numeric operands):"]
            if not bridge["observations"]:
                lines.append("  None declared; coverage is a submitted review, not proof of completeness.")
            for note in bridge["observations"]:
                value = "unknown amount, not zero" if note['value'] is None else f"{note['value']} {note['unit']}"
                lines.append(f"  {note['observation_id']} [{note['disposition']}; {note['origin']}]: {value}; {note['rationale']}")
            lines.append("Coverage declarations (not authenticated approvals):")
            for item in bridge["coverage"]:
                lines.append(f"  {item['role']}: populations={item['population_ids']}; omissions={item['omission_references']}; "
                             f"rationale={item['review']['rationale']}")
        lines += [
            "", "Timing: " + b["timing"]["notice"],
            "Scope: " + doc["scope"],
            "Analyst rationale: " + doc["analyst"]["rationale"],
            "Limitations (supplied inputs are not authenticated or economically validated):",
            *["- " + limitation for limitation in result["limitations"]],
        ]
        return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path, help="JSON case file; rates are fractional Decimal strings")
    parser.add_argument("--run", action="store_true", help="Calculate the case's explicit EV or equity/per-share scope")
    parser.add_argument("--format", choices=("summary", "json"), default="json",
                        help="Run output format (default: json); validation remains calculation-free")
    parser.add_argument("--output", type=Path, help="Save the selected run format to a new file; never overwrite an existing file")
    args = parser.parse_args(argv)
    if args.output and not args.run:
        parser.error("--output requires --run; validation never calculates or writes results")
    try:
        case = load_case(args.case)
        if not args.run:
            print("VALID: input structure and declared conventions only; no calculation or approval.")
            return 0
        if args.output:
            destination = args.output.resolve()
            # Keep new result files out of repository source/historical paths too.
            if destination.is_relative_to(ROOT) and not destination.is_relative_to(ROOT / "output"):
                raise CaseInputError(["--output must be outside the repository or under output/; source/history paths are protected"])
            if destination.exists() or destination == args.case.resolve():
                raise CaseInputError(["--output must name a new file distinct from the input; existing files are never overwritten"])
        result = run_case(case, ROOT)
        payload = render_summary(result) if args.format == "summary" else json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            # Exclusive creation also prevents a race from overwriting a file.
            with args.output.open("x", encoding="utf-8") as out:
                out.write(payload)
        else:
            print(payload, end="")
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
