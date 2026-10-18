"""Validate an editable local case; --run explicitly requests A/B calculation."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from valuation_platform.valuation.case_inputs import CaseInputError, load_case, run_case


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path, help="JSON case file; rates are fractional Decimal strings")
    parser.add_argument("--run", action="store_true", help="Explicitly calculate forecast and enterprise value")
    parser.add_argument("--output", type=Path, help="Save run JSON to a new file; never overwrite an existing file")
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
        payload = json.dumps(run_case(case, ROOT), sort_keys=True, indent=2) + "\n"
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
