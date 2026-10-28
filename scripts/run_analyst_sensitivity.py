"""Validate an explicit WACC × terminal-growth request; calculate only with --run."""

import argparse
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from valuation_platform.valuation.consumer import ANCHORS
from valuation_platform.valuation.sensitivity_inputs import (
    SensitivityInputError, load_sensitivity, run_sensitivity, serialize_sensitivity,
)


def render_summary(result):
    """Display supplied results only, with isolated Decimal unit conversion/rounding."""
    ref = result["reference_result"]
    doc = result["selected_case"]
    selection = result["selection"]
    anchor = ref["stage_b"]["stage_a"]["anchor"]
    company = ANCHORS.get(doc["anchor"]["kind"], {}).get("ticker", "Synthetic fixture")
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        def money(value):
            return f"{Decimal(value) / Decimal('1000000'):,.8f}"

        def percent(value):
            return f"{Decimal(value) * Decimal(100):.2f}%"

        identity = (f"Anonymous investor | Prepared: {doc['preparation']['timestamp_utc']}" if "preparation" in doc
                    else f"Analyst: {doc['analyst']['author']}")
        lines = ["WACC × TERMINAL-GROWTH SENSITIVITY", f"Request: {result['sensitivity_name']}",
                 f"Company: {company} | Case: {doc['case_name']} | Scenario: {selection['scenario_label'] or 'single case (explicit)'}",
                 f"Input basis: {doc['input_basis']} | {identity}",
                 f"Anchor: {anchor['annual_start']} to {anchor['annual_end']} | CIK {anchor['cik']} | {anchor['accession']}",
                 f"Analytical date: {selection['analytical_date']} | Declared information cutoff: {selection['information_cutoff']}",
                 "Timing: " + ref["stage_b"]["timing"]["notice"],
                 f"Reference WACC: {percent(doc['wacc'])} | Terminal growth: {percent(doc['terminal_growth'])}",
                 f"Reference enterprise value: {money(ref['stage_b']['enterprise_value'])} USD millions",
                 "EV is enterprise value, not equity or value/share."]
        if "stage_c" in ref:
            c = ref["stage_c"]
            shares = c["inputs"]["shares"]
            lines += [f"Reference equity: {money(c['equity_value'])} USD millions",
                      f"Reference scope-qualified value/share: {Decimal(c['value_per_share']):,.8f} USD/share",
                      f"Fixed shares: {c['valuation_shares']} actual shares | {shares['observation_date']} | {shares['class_id']}",
                      f"Class equivalence: {shares['equivalence_convention']} | Awards: {shares['award_policy']}"]
        matrices = [("Enterprise value matrix — USD millions", "enterprise_value", money)]
        if "stage_c" in ref:
            matrices.append(("Scope-qualified value/share matrix — USD/share", "value_per_share", lambda x: f"{Decimal(x):,.8f}"))
        for title, key, display in matrices:
            lines += ["", title, "WACC rows / g columns | " + " | ".join(percent(g) for g in result["terminal_growth_values"])]
            # Exact strings accompany percentage labels: very close axes may round alike.
            lines.append("Exact g fractions | " + " | ".join(result["terminal_growth_values"]))
            for wacc, row in zip(result["wacc_values"], result["cells"]):
                lines.append(percent(wacc) + f" [{wacc}] | " + " | ".join("INVALID*" if cell["status"] == "INVALID" else display(cell["metrics"][key]) for cell in row))
        lines += ["", "* INVALID: terminal growth >= WACC; no result, repair or interpolation.",
                  "Held fixed: " + result["held_fixed"], *result["limitations"],
                  "Display only: USD millions / USD per share to 8 decimals, percentages to 2, HALF_EVEN. Rounded cells may appear equal.",
                  "JSON retains exact submitted rate strings, full reference/provenance, cell PV reconciliation, terminal contributions and signed-reference changes.",
                  *(["Optional notes (not evidence/approval): " + (doc["preparation"]["notes"] or "not supplied")] if "preparation" in doc
                    else ["Rationale: " + doc["analyst"]["rationale"], "Scope: " + doc["scope"]]), *ref["limitations"]]
        if "stage_c" in ref:
            lines.append("Fixed bridge exclusions/omissions (not extra operands):")
            for note in ref["stage_c"]["inputs"]["observations"]:
                lines.append(f"{note['observation_id']} [{note['disposition']}]: {note['rationale']}")
            for coverage in ref["stage_c"]["inputs"]["coverage"]:
                lines.append(f"{coverage['role']}: {coverage['review']['rationale']}; omissions={coverage['omission_references']}")
        return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--run", action="store_true", help="Explicitly calculate reference and valid cells")
    parser.add_argument("--format", choices=("json", "summary"), default="json")
    parser.add_argument("--output", type=Path, help="Save a new file outside source/history paths; never overwrite")
    args = parser.parse_args(argv)
    if args.output and not args.run:
        parser.error("--output requires --run; validation never calculates or writes results")
    try:
        request = load_sensitivity(args.request)
        if not args.run:
            print("VALID: explicit selected case and grid; no calculation or economic approval.")
            return 0
        if args.output:
            destination = args.output.resolve()
            if destination.is_relative_to(ROOT) and not destination.is_relative_to(ROOT / "output"):
                raise SensitivityInputError(["--output must be outside the repository or under output/; source/history paths are protected"])
            if destination.exists() or destination == args.request.resolve():
                raise SensitivityInputError(["--output must name a new file distinct from the input; existing files are never overwritten"])
        result = run_sensitivity(request, ROOT)
        payload = render_summary(result) if args.format == "summary" else serialize_sensitivity(result)
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
