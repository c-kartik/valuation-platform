"""Validate bounded reverse DCF; --run certifies uniqueness and solves growth."""

import argparse
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from valuation_platform.valuation.consumer import ANCHORS
from valuation_platform.valuation.reverse_inputs import ReverseInputError, load_reverse, run_reverse, serialize_reverse


def render_summary(result):
    """Display forward components and solver diagnostics; no valuation formulas."""
    doc, reference = result["selected_case"], result["reference_result"]
    selection = result["selection"]
    target = result["submitted_inputs"]["target"]
    bounds = result["submitted_inputs"]["growth_bounds"]
    company = ANCHORS.get(doc["anchor"]["kind"], {}).get("ticker", "Synthetic fixture")
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        def pct(value): return f"{Decimal(value)*100:.8f}%"
        def money(value): return f"{Decimal(value)/Decimal('1000000'):,.8f}"
        lines = ["BOUNDED REVERSE DCF — CONSTANT ANNUAL REVENUE GROWTH",
                 f"Case: {doc['case_name']} | Company: {company} | Scenario: {selection['scenario_label'] or 'explicit single case'}",
                 (f"Analyst: {doc['analyst']['author']} | Basis: {doc['input_basis']}" if "analyst" in doc else f"Anonymous investor | Basis: {doc['input_basis']} | Prepared: {doc['preparation']['timestamp_utc']}"),
                 f"Fiscal period: {doc['anchor']['annual_start']} to {doc['anchor']['annual_end']}",
                 f"Analytical date: {selection['analytical_date']} | Declared cutoff: {selection['information_cutoff']}",
                 "Timing: " + reference["stage_b"]["timing"]["notice"],
                 "Original annual growth path: " + " / ".join(pct(x) for x in result["original_growth_path"]),
                 f"Target: {target['metric']} = {target['amount']} {target['unit']} | Date: {target['date']}",
                 f"Bounds: {pct(bounds['lower'])} to {pct(bounds['upper'])}; replace all five growth rates, no shift; terminal g fixed at {pct(doc['terminal_growth'])}.",
                 "Held fixed: " + result["held_fixed"],
                 f"Status: {result['status']} | {result['reason']}",
                 "Certificate: " + result["monotonicity"]["direction"] + " | " + result["monotonicity"]["reason"],
                 f"Iterations: {result['iterations']} | Forward evaluations (including original/fresh verification): {result['evaluations']}",
                 "Technical policy: " + str(result["numerical_policy"])]
        if result["final_bracket"]:
            bracket = result["final_bracket"]
            lines.append(f"Final growth bracket: [{bracket['lower_growth']}, {bracket['upper_growth']}] fractions | width {bracket['width']}")
        solution = result["solution"]
        if solution:
            forward = solution["forward_result"]
            b = forward["stage_b"]
            lines += [f"Solved constant annual growth: {pct(solution['constant_annual_growth'])} ({solution['constant_annual_growth']} fraction)",
                      f"Achieved: {solution['achieved_metric']} {target['unit']}",
                      f"Signed residual: {solution['signed_residual']} | Absolute: {solution['absolute_residual']} | Tolerance: {solution['residual_tolerance']}",
                      "Forward amounts: USD millions (display only)", "Year | Revenue | FCFF"]
            lines += [f"{y['fiscal_year_label']} | {money(y['revenue'])} | {money(y['fcff'])}" for y in b["stage_a"]["years"]]
            lines += [f"Explicit-period PV: {money(b['pv_explicit_fcff'])}", f"Terminal PV: {money(b['pv_terminal_value'])}",
                      f"Enterprise value: {money(b['enterprise_value'])} USD millions; EV is not equity or value/share."]
            if "stage_c" in forward:
                c = forward["stage_c"]
                lines += [f"Equity value: {money(c['equity_value'])} USD millions", f"Scope-qualified value/share: {Decimal(c['value_per_share']):,.8f} USD/share"]
        else:
            lines.append("No solved growth or solution forward valuation is returned. Bracket values, if any, are diagnostics only.")
        if "stage_c" in reference:
            c = reference["stage_c"]; shares = c["inputs"]["shares"]
            lines += [f"Fixed shares: {c['valuation_shares']} actual shares | {shares['observation_date']} | Class: {shares['class_id']}",
                      f"Equivalence: {shares['equivalence_convention']} | Awards: {shares['award_policy']}"]
            for observation in c["inputs"]["observations"]:
                lines.append(f"{observation['observation_id']} [{observation['disposition']}]: {observation['rationale']}")
            for coverage in c["inputs"]["coverage"]:
                lines.append(f"Coverage {coverage['role']}: {coverage['review']['rationale']}; omissions={coverage['omission_references']}")
        lines += (["Rationale: " + doc["analyst"]["rationale"], "Scope: " + doc["scope"]] if "analyst" in doc else ["Optional notes (not evidence/approval): " + (doc["preparation"]["notes"] or "None supplied")])
        lines += [
                  *reference["limitations"], *result["limitations"],
                  "Display only: money/share rounded HALF_EVEN to 8 decimals; JSON retains full precision, exact certificate, submitted inputs and provenance."]
        return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--format", choices=("json", "summary"), default="json")
    parser.add_argument("--output", type=Path, help="New file only; failed solve diagnostics also save with exit code 3")
    args = parser.parse_args(argv)
    if args.output and not args.run:
        parser.error("--output requires --run; validation never calculates or writes results")
    try:
        request = load_reverse(args.request)
        if not args.run:
            print("VALID: request structure only; uniqueness/reachability not assessed; no calculation or economic approval.")
            return 0
        if args.output:
            destination = args.output.resolve()
            if destination.is_relative_to(ROOT) and not destination.is_relative_to(ROOT / "output"):
                raise ReverseInputError(["--output must be outside the repository or under output/; source/history paths are protected"])
            if destination.exists() or destination == args.request.resolve():
                raise ReverseInputError(["--output must name a new file distinct from the input; existing files are never overwritten"])
        result = run_reverse(request, ROOT)
        payload = render_summary(result) if args.format == "summary" else serialize_reverse(result)
        if args.output:
            with args.output.open("x", encoding="utf-8") as output:
                output.write(payload)
        else:
            print(payload, end="")
        return 0 if result["status"] == "SUCCESS" else 3
    except (OSError, ValueError, UnicodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
