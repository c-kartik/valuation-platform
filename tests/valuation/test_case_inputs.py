"""Only synthetic numerical cases execute; META template stays unset."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal as D, Inexact, ROUND_DOWN, Rounded, localcontext
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from valuation_platform.valuation import case_inputs as c

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples/valuation"
SCRIPT = ROOT / "scripts/run_analyst_case.py"
spec = importlib.util.spec_from_file_location("run_analyst_case", SCRIPT)
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


def document():
    return json.loads((EXAMPLES / "synthetic-base.json").read_text())


def parse(doc):
    return c.read_case(json.dumps(doc))


class CaseInputTests(unittest.TestCase):
    def test_example_matches_independent_a_b_hand_calculations(self):
        result = c.run_case(c.load_case(EXAMPLES / "synthetic-base.json"), ROOT)
        a = result["stage_b"]["stage_a"]
        self.assertEqual(a["years"][0]["revenue"], "110.00")
        self.assertEqual(D(a["years"][0]["fcff"]), D("8.8"))
        self.assertEqual(D(a["years"][4]["fcff"]), D("12.88408"))
        b = result["stage_b"]
        # Independent A/B fixture retained in the consumer contract.
        self.assertEqual(D(b["pv_explicit_fcff"]), D("27.7063942144"))
        self.assertEqual(D(b["terminal"]["fcff"]), D("30.438639"))
        self.assertEqual(D(b["enterprise_value"]), D("77.5770603520"))
        self.assertTrue(a["anchor"]["source_reference"].startswith("synthetic:"))
        self.assertEqual(result["input_basis"], "SYNTHETIC_FIXTURE")

    def test_growth_and_margin_are_editable_without_engine_changes(self):
        doc = document()
        base = c.run_case(parse(doc), ROOT)
        for field, value in (("revenue_growth", "0.00"), ("operating_margin", "0.30")):
            changed = deepcopy(doc)
            changed["forecast_years"][0][field] = value
            result = c.run_case(parse(changed), ROOT)
            first = result["stage_b"]["stage_a"]["years"][0]
            self.assertEqual(D(first["fcff"]), D("8") if field == "revenue_growth" else D("17.05"))
            self.assertNotEqual(result["stage_b"]["enterprise_value"], base["stage_b"]["enterprise_value"])

    def test_each_year_and_all_rates_remain_independent(self):
        doc = document()
        for i, year in enumerate(doc["forecast_years"]):
            for key in c.ANNUAL_RATES:
                year[key] = str(D(year[key]) + D(i) / D(100))
        case = parse(doc)
        for i, year in enumerate(case.assumptions.forecast_years):
            for key in c.ANNUAL_RATES:
                self.assertEqual(getattr(year, key), D(doc["forecast_years"][i][key]))
        changed = document()
        changed["forecast_years"][2]["operating_margin"] = "0.30"
        result = c.run_case(parse(changed), ROOT)["stage_b"]["stage_a"]["years"]
        self.assertEqual(D(result[1]["fcff"]), D("9.68"))
        self.assertEqual(D(result[2]["fcff"]), D("20.6305"))
        self.assertEqual(D(result[3]["fcff"]), D("11.7128"))

    def test_terminal_explicit_and_not_copied_from_year_five(self):
        doc = document()
        base = c.run_case(parse(doc), ROOT)["stage_b"]
        doc["forecast_years"][4]["operating_margin"] = "0.40"
        edited = c.run_case(parse(doc), ROOT)["stage_b"]
        self.assertEqual(edited["terminal_assumptions"], base["terminal_assumptions"])
        self.assertEqual(D(edited["terminal"]["fcff"]), D("30.438639"))
        doc["terminal"]["operating_margin"] = "0.40"
        separate = c.run_case(parse(doc), ROOT)["stage_b"]
        self.assertEqual(separate["stage_a"], edited["stage_a"])
        self.assertNotEqual(separate["terminal_value"], edited["terminal_value"])
        for key in c.TERMINAL_RATES:
            incomplete = document()
            del incomplete["terminal"][key]
            with self.assertRaisesRegex(c.CaseInputError, "terminal." + key):
                parse(incomplete)

    def test_unset_meta_lists_every_missing_rate_and_analyst_field(self):
        raw = (EXAMPLES / "meta-fy2025-unset.json").read_text()
        doc = json.loads(raw)
        with patch.object(c, "forecast_five_years") as a, patch.object(c, "discount_to_enterprise_value") as b:
            with self.assertRaises(c.CaseInputError) as failure:
                c.read_case(raw)
            self.assertEqual(sum("UNSET;" in e for e in failure.exception.errors), 37)
            for i in range(5):
                for field in c.ANNUAL_RATES:
                    self.assertIn(f"forecast_years[{i}].{field}: UNSET", str(failure.exception))
            for field in c.TERMINAL_RATES:
                self.assertIn("terminal." + field + ": UNSET", str(failure.exception))
            self.assertIn("analyst.author", str(failure.exception))
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                self.assertEqual(cli.main([str(EXAMPLES / "meta-fy2025-unset.json")]), 2)
            self.assertEqual(stderr.getvalue().count(": UNSET;"), 37)
            a.assert_not_called(); b.assert_not_called()
        self.assertEqual({k:v for k,v in doc["anchor"].items() if k != "kind"}, c.IDENTITY)
        self.assertNotIn("0.1467", raw); self.assertNotIn("0.3655", raw)

    def test_rates_reject_ambiguous_nonfinite_and_numeric_representations(self):
        for value in (0.12, 1, True, "12%", "12 percent", ".12", " 0.12", "1,2", "NaN", "sNaN", "Infinity", "-Infinity", "1e999999999999999999999999"):
            doc = document(); doc["forecast_years"][0]["revenue_growth"] = value
            with self.subTest(value=value), self.assertRaises(c.CaseInputError):
                parse(doc)
        for token in ("0.12", "1e-2", "NaN", "Infinity", "-Infinity"):
            raw = json.dumps(document()).replace('"0.10"', token, 1)
            with self.subTest(token=token), self.assertRaisesRegex(c.CaseInputError, "JSON number"):
                c.read_case(raw)

    def test_duplicate_keys_unknown_fields_and_versions(self):
        raw = json.dumps(document())
        for repeated in ('"case_name": "duplicate",', '"nested": {"a":1,"a":2},'):
            with self.assertRaisesRegex(c.CaseInputError, "Duplicate JSON key"):
                c.read_case("{" + repeated + raw[1:])
        for change in ({"schema_version": "2"}, {"shares": "100"}, {"bridge": {}}):
            doc = document(); doc.update(change)
            with self.assertRaises(c.CaseInputError):parse(doc)
        doc = document(); doc["conventions"]["forecast"] = "old"
        with self.assertRaisesRegex(c.CaseInputError, "conventions.forecast"):parse(doc)
        doc = document(); doc["conventions"]["discounting"] = "mid-year"
        with self.assertRaisesRegex(c.CaseInputError, "conventions.discounting"):parse(doc)

    def test_supported_anchors_require_exact_company_dates_and_basis(self):
        for change in ({"kind":"other"}, {"cik":1326801}, {"cik":True}, {"annual_end":"2024-12-31"},
                       {"annual_start":"2025-02-01"}, {"accession":"new"}, {"form":"10-Q"}, {"kind":[]}):
            doc = document(); doc["anchor"].update(change)
            with self.subTest(change=change), self.assertRaisesRegex(c.CaseInputError, "anchor."):parse(doc)
        doc = document(); doc["input_basis"] = "MANUAL_INPUT"
        with self.assertRaisesRegex(c.CaseInputError, "input_basis"):parse(doc)
        # Validation of a deliberately synthetic-rate document with a META identity
        # never resolves or executes that anchor; no actual case is run in tests.
        doc = document(); doc["anchor"] = dict(kind="meta-fy2025", **c.IDENTITY)
        doc["input_basis"] = "MANUAL_INPUT"
        with patch.object(c, "load_meta_revenue_anchor") as loader:
            self.assertEqual(parse(doc).anchor_kind, "meta-fy2025")
            loader.assert_not_called()

    def test_missing_and_invalid_models_use_existing_validation(self):
        for raw in ("[]", "null", "{", "{}"):
            with self.assertRaises(c.CaseInputError):c.read_case(raw)
        for field,value in (("wacc","0"),("terminal_growth","0.25")):
            doc = document();doc[field] = value
            with self.assertRaises(c.CaseInputError):parse(doc)
        for field,value in (("revenue_growth","-1.1"),("forecast_tax_rate","1.1"),("capex_percent_revenue","-0.1")):
            doc = document();doc["forecast_years"][1][field] = value
            with self.assertRaisesRegex(c.CaseInputError, r"forecast_years\[1\]"):parse(doc)
        for change in ([], document()["forecast_years"][:-1], list(reversed(document()["forecast_years"]))):
            doc = document();doc["forecast_years"] = change
            with self.assertRaises(c.CaseInputError):parse(doc)
        doc = document();doc["terminal"]["investment_percent_revenue"] = "-0.1"
        with self.assertRaisesRegex(c.CaseInputError, "terminal"):parse(doc)

    def test_metadata_and_exact_submitted_decimal_strings_survive(self):
        doc = document();doc["case_name"] = "Edited analyst case"
        doc["forecast_years"][0]["revenue_growth"] = "0.1000"
        doc["analyst"]["rationale"] = "My synthetic rationale, including cost consistency."
        raw = json.dumps(doc, indent=4)
        case = c.read_case(raw)
        result = c.run_case(case, ROOT)
        self.assertEqual(case.submitted_json, raw)
        self.assertEqual(result["submitted_inputs"], doc)
        self.assertEqual(result["submitted_inputs"]["forecast_years"][0]["revenue_growth"], "0.1000")
        self.assertEqual(result["semantic_input_review"], "NOT_ASSESSED_BY_CALCULATOR")
        self.assertEqual(c.run_case(case, ROOT), result)
        with self.assertRaises(FrozenInstanceError):case.anchor_kind = "meta-fy2025"
        with self.assertRaises(c.CaseInputError):c.run_case(replace(case, anchor_kind="meta-fy2025"), ROOT)

    def test_metadata_scope_and_utc_date_required(self):
        for change in ({"author":""},{"timestamp_utc":"2026-01-01"},{"timestamp_utc":"2026-01-01T00:00:00+04:00"},{"rationale":None}):
            doc = document();doc["analyst"].update(change)
            with self.assertRaisesRegex(c.CaseInputError,"analyst"):parse(doc)
        for key,value in (("scope",None),("limitations",[]),("limitations",[None])):
            doc = document();doc[key]=value
            with self.assertRaises(c.CaseInputError):parse(doc)

    def test_validation_calls_no_engine_or_anchor_and_cli_writes_nothing(self):
        with patch.object(c,"forecast_five_years") as a, patch.object(c,"discount_to_enterprise_value") as b, patch.object(c,"load_meta_revenue_anchor") as loader:
            parse(document())
            out=io.StringIO()
            with redirect_stdout(out):self.assertEqual(cli.main([str(EXAMPLES/"synthetic-base.json")]),0)
            self.assertIn("no calculation",out.getvalue())
            a.assert_not_called();b.assert_not_called();loader.assert_not_called()

    def test_normal_run_stdout_only_and_explicit_output_is_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);casefile=folder/"case.json"
            casefile.write_text(json.dumps(document()));before=casefile.read_bytes()
            run=subprocess.run([sys.executable,str(SCRIPT),str(casefile),"--run"],capture_output=True,text=True,cwd=tmp)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(D(json.loads(run.stdout)["stage_b"]["enterprise_value"]),D("77.5770603520"))
            self.assertEqual(list(folder.iterdir()),[casefile]);self.assertEqual(casefile.read_bytes(),before)
            output=folder/"result.json"
            for destination in (casefile,):
                with redirect_stderr(io.StringIO()):self.assertEqual(cli.main([str(casefile),"--run","--output",str(destination)]),2)
            with redirect_stdout(io.StringIO()):self.assertEqual(cli.main([str(casefile),"--run","--output",str(output)]),0)
            saved=output.read_bytes()
            with redirect_stderr(io.StringIO()):self.assertEqual(cli.main([str(casefile),"--run","--output",str(output)]),2)
            self.assertEqual(output.read_bytes(),saved);self.assertEqual(casefile.read_bytes(),before)

    def test_output_cannot_enter_source_history_paths_and_requires_run(self):
        source=EXAMPLES/"synthetic-base.json"
        dest=ROOT/"docs/evidence/forbidden-case-output.json"
        with patch.object(cli,"run_case") as execute,redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main([str(source),"--run","--output",str(dest)]),2)
            execute.assert_not_called()
            with self.assertRaises(SystemExit):cli.main([str(source),"--output",str(dest)])
        self.assertFalse(dest.exists())

    def test_input_examples_engine_and_historical_artifacts_preserved(self):
        paths=[*EXAMPLES.glob("*.json"),* (ROOT/"src/valuation_platform/valuation").glob("*.py"),
               ROOT/"docs/company-data-preparation/meta-analyst-input-package.json",
               ROOT/"docs/company-data-preparation/trillion-review-batch.json"]
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        with patch.object(c,"load_meta_revenue_anchor",side_effect=AssertionError("synthetic path cannot read META")):
            c.run_case(c.load_case(EXAMPLES/"synthetic-base.json"),ROOT)
        self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})

    def test_decimal_caller_context_isolation(self):
        raw=json.dumps(document())
        case=c.read_case(raw)
        with localcontext() as ctx:
            ctx.prec=3;ctx.rounding=ROUND_DOWN;ctx.traps[Inexact]=True;ctx.clear_flags();ctx.flags[Rounded]=True
            before=ctx.copy()
            self.assertEqual(c.read_case(raw),case)
            result=c.run_case(case,ROOT)
            self.assertEqual(D(result["stage_b"]["enterprise_value"]),D("77.5770603520"))
            self.assertEqual((ctx.prec,ctx.rounding,ctx.flags,ctx.traps),(before.prec,before.rounding,before.flags,before.traps))


class InvestorCaseTests(unittest.TestCase):
    def investor(self, kind=None):
        d = document()
        d.pop('analyst'); d.pop('scope')
        d['schema_version'] = c.INVESTOR_CASE_SCHEMA
        d['preparation'] = {'provenance': 'ANONYMOUS_INVESTOR',
                            'timestamp_utc': '2026-10-21T10:00:00Z', 'notes': None}
        if kind:
            d['anchor'] = dict(kind=kind, **c.ANCHORS[kind]['identity'])
            d['input_basis'] = 'MANUAL_INPUT'
            d['conventions']['forecast'] = 'manual-fcff-v1'
        return d

    def test_no_paperwork_same_financial_components_all_anchors(self):
        for kind in (None, *c.ANCHORS):
            d = self.investor(kind); before = deepcopy(d)
            investor = c.run_case(parse(d), ROOT)
            legacy = deepcopy(d); legacy.pop('preparation')
            legacy.update(schema_version=c.CASE_SCHEMA, analyst=document()['analyst'], scope=document()['scope'])
            expected = c.run_case(parse(legacy), ROOT)
            self.assertEqual(investor['stage_b'], expected['stage_b'])
            self.assertEqual(investor['schema_version'], c.INVESTOR_RESULT_SCHEMA)
            self.assertIsNone(parse(d).analyst)
            self.assertEqual(investor['submitted_inputs'], d)
            self.assertNotIn('analyst', investor['submitted_inputs'])
            self.assertNotIn('scope', investor['submitted_inputs'])
            self.assertEqual(d, before)
            summary = cli.render_summary(investor)
            self.assertIn('Investment rationale: absent', summary)
            self.assertIn('Optional personal notes: absent', summary)

    def test_notes_and_metadata_strictness_without_legacy_relaxation(self):
        d = self.investor()
        for notes in (None, '  My words\nonly  ', 'Edited', 'x' * 2048):
            d['preparation']['notes'] = notes
            self.assertEqual(c.run_case(parse(d), ROOT)['submitted_inputs']['preparation']['notes'], notes)
        for field, value in [('notes', ''), ('notes', ' '), ('notes', 5), ('notes', 'x'*2049),
                             ('provenance', 'VERIFIED_ANALYST'), ('timestamp_utc', None),
                             ('timestamp_utc', '2026-10-21'), ('timestamp_utc', '2026-10-21T10:00:00+04:00')]:
            bad = self.investor(); bad['preparation'][field] = value
            with self.assertRaisesRegex(c.CaseInputError, 'preparation.' + field): parse(bad)
        for field, value in [('analyst', document()['analyst']), ('scope', 'Invented scope'),
                             ('information_cutoff', '2026-10-21'), ('bridge', {})]:
            bad = self.investor(); bad[field] = value
            with self.assertRaisesRegex(c.CaseInputError, 'unknown field'): parse(bad)
        legacy = document(); legacy['analyst']['rationale'] = None
        with self.assertRaisesRegex(c.CaseInputError, 'analyst.rationale'): parse(legacy)

    def test_same_bindings_and_numerical_validation(self):
        for field, value in [('cik', 999), ('annual_end', '2026-12-31'), ('accession', 'wrong')]:
            d = self.investor('meta-fy2025'); d['anchor'][field] = value
            with self.assertRaisesRegex(c.CaseInputError, 'anchor.' + field): parse(d)
        for field, value in [('wacc', None), ('wacc', '0'), ('terminal_growth', '0.25'), ('wacc', 0.25)]:
            d = self.investor(); d[field] = value
            with self.assertRaises(c.CaseInputError): parse(d)
        d = self.investor(); d['forecast_years'][0]['forecast_tax_rate'] = '1.01'
        with self.assertRaisesRegex(c.CaseInputError, 'forecast_tax_rate'): parse(d)
        text = json.dumps(self.investor()).replace('"wacc": "0.25"', '"wacc":"0.25","wacc":"0.3"')
        with self.assertRaisesRegex(c.CaseInputError, 'Duplicate JSON key'): c.read_case(text)


if __name__ == "__main__":
    unittest.main()
