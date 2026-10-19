"""Scenario orchestration and CLI; all forward assumptions are synthetic."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal as D, Inexact, ROUND_DOWN, Rounded, localcontext
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from valuation_platform.valuation import case_inputs as c, scenario_inputs as s
from tests.valuation.test_case_inputs import ROOT, EXAMPLES, cli as single_cli
from tests.valuation.test_case_summary import values

SCRIPT = ROOT / "scripts/run_analyst_scenarios.py"
spec = importlib.util.spec_from_file_location("run_analyst_scenarios", SCRIPT)
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


def document(equity=False):
    name = "synthetic-scenarios-equity.json" if equity else "synthetic-scenarios-ev.json"
    return json.loads((EXAMPLES / name).read_text())


def parse(doc):
    return s.read_scenario_set(json.dumps(doc))


def execute(doc=None):
    return s.run_scenario_set(parse(document() if doc is None else doc), ROOT)


class ScenarioTests(unittest.TestCase):
    def test_full_results_equal_independent_single_runs_in_fixed_order(self):
        for equity in (False, True):
            doc = document(equity)
            doc["scenarios"].reverse()
            result = execute(doc)
            self.assertEqual([x["label"] for x in result["scenarios"]], list(s.LABELS))
            self.assertEqual(result["submitted_inputs"], doc)
            for entry in result["scenarios"]:
                raw = next(x["case"] for x in doc["scenarios"] if x["label"] == entry["label"])
                self.assertEqual(entry["result"], c.run_case(c.read_case(json.dumps(raw)), ROOT))
            self.assertEqual(s.serialize_scenarios(result), s.serialize_scenarios(execute(doc)))
            base = result["scenarios"][1]["result"]
            self.assertEqual(D(base["stage_b"]["enterprise_value"]), D("77.577060352"))
            if equity:
                self.assertEqual(D(base["stage_c"]["value_per_share"]), D("16.644265088"))

    def test_annual_edits_propagate_only_in_edited_scenario(self):
        for field in ("revenue_growth", "operating_margin"):
            doc = document(); before = execute(doc)
            doc["scenarios"][1]["case"]["forecast_years"][2][field] = "0.30"
            after = execute(doc)
            for i in (0, 2):
                self.assertEqual(before["scenarios"][i], after["scenarios"][i])
            old, new = (x["scenarios"][1]["result"]["stage_b"] for x in (before, after))
            self.assertEqual(old["stage_a"]["years"][:2], new["stage_a"]["years"][:2])
            self.assertNotEqual(old["stage_a"]["years"][2]["fcff"], new["stage_a"]["years"][2]["fcff"])
            self.assertEqual(old["terminal_assumptions"], new["terminal_assumptions"])
            if field == "revenue_growth":
                self.assertNotEqual(old["stage_a"]["years"][4]["revenue"], new["stage_a"]["years"][4]["revenue"])
            else:
                self.assertEqual(old["stage_a"]["years"][3:], new["stage_a"]["years"][3:])

    def test_terminal_inputs_are_independent_and_no_year_five_copy(self):
        original = document(); before = execute(original)
        for field in c.TERMINAL_RATES:
            doc = deepcopy(original)
            doc["scenarios"][1]["case"]["terminal"][field] = "0.15"
            after = execute(doc)
            self.assertEqual(before["scenarios"][1]["result"]["stage_b"]["stage_a"],
                             after["scenarios"][1]["result"]["stage_b"]["stage_a"])
            self.assertNotEqual(before["scenarios"][1]["result"]["stage_b"]["terminal"],
                                after["scenarios"][1]["result"]["stage_b"]["terminal"])
            self.assertEqual(before["scenarios"][0], after["scenarios"][0])

    def test_missing_duplicate_labels_unknown_fields_and_incomplete_cases(self):
        edits = [
            (lambda d: d["scenarios"].pop(), "missing label Bull"),
            (lambda d: d["scenarios"][1].update(label="Bear"), r"scenarios\[1\].label: duplicate"),
            (lambda d: d["scenarios"][1].update(label="Upside"), r"scenarios\[1\].label"),
            (lambda d: d.update(probabilities={}), "scenario_set.probabilities"),
            (lambda d: d["scenarios"][1].update(case_file="base.json"), r"scenarios\[1\].case_file"),
            (lambda d: d["scenarios"][1]["case"].update(extra=True), r"scenarios\[1\].case.*extra"),
            (lambda d: d["scenarios"][1]["case"]["forecast_years"][2].update(revenue_growth=None), r"scenarios\[1\].case.forecast_years\[2\].revenue_growth"),
            (lambda d: d["scenarios"][1]["case"].pop("terminal"), r"scenarios\[1\].case.*terminal"),
        ]
        for edit, message in edits:
            doc = document(); edit(doc)
            with self.subTest(message=message), self.assertRaisesRegex(s.ScenarioInputError, message):
                parse(doc)
        for raw in ("null", "[]", "{", "{}"):
            with self.assertRaises(s.ScenarioInputError):s.read_scenario_set(raw)

    def test_duplicate_keys_and_number_errors_keep_nested_paths(self):
        raw = json.dumps(document())
        for changed, path in (
            (raw.replace('"revenue_growth": "0.10"', '"revenue_growth": "0.10", "revenue_growth": "0.20"', 1), r"scenarios\[1\].case.forecast_years\[0\].revenue_growth"),
            (raw.replace('"wacc": "0.25"', '"wacc": NaN', 1), r"scenarios\[0\].case.wacc"),
            (raw.replace('"revenue_growth": "0.10"', '"revenue_growth": 0.10', 1), r"scenarios\[1\].case.forecast_years\[0\].revenue_growth"),
        ):
            with self.assertRaisesRegex(s.ScenarioInputError, path):s.read_scenario_set(changed)

    def test_anchor_timing_basis_convention_period_and_scope_mismatches(self):
        edits = [
            (lambda e: e.update(analytical_date="2025-12-30"), "analytical_date"),
            (lambda e: e.update(information_cutoff="2026-02-01"), "information_cutoff"),
            (lambda e: e.update(information_cutoff="2025-12-30"), "information_cutoff"),
            (lambda e: e.update(information_cutoff=None), "information_cutoff"),
            (lambda e: e["case"]["anchor"].update(cik=1), "anchor.cik"),
            (lambda e: e["case"]["conventions"].update(forecast="manual-fcff-v1"), "conventions"),
            (lambda e: e["case"].update(input_basis="MANUAL_INPUT"), "input_basis"),
            (lambda e: e["case"]["forecast_years"][0].update(fiscal_year_label="Changed period"), "forecast_years"),
        ]
        for edit, field in edits:
            doc = document(); edit(doc["scenarios"][1])
            with self.subTest(field=field), self.assertRaisesRegex(s.ScenarioInputError, r"scenarios\[1\].*" + field):parse(doc)
        # Two individually valid company declarations still cannot be compared.
        doc = document()
        e = doc["scenarios"][1]
        e["case"]["anchor"] = {"kind": "meta-fy2025", **c.IDENTITY}
        e["case"]["input_basis"] = "MANUAL_INPUT"
        with self.assertRaisesRegex(s.ScenarioInputError, r"scenarios\[1\].case.anchor"):parse(doc)
        doc = document(True);doc["scenarios"][1]["case"] = document()["scenarios"][1]["case"]
        with self.assertRaisesRegex(s.ScenarioInputError, "cannot mix"):parse(doc)

    def test_all_bridge_share_metadata_must_match_without_overriding(self):
        edits = [lambda b:b["components"][0].update(amount="11"),
                 lambda b:b["shares"].update(shares="5"),
                 lambda b:b["shares"].update(rationale="Different award judgment"),
                 lambda b:b["coverage"][0]["review"].update(rationale="Different coverage"),
                 lambda b:b["observations"][0].update(rationale="Different exclusion")]
        for edit in edits:
            doc = document(True);edit(doc["scenarios"][1]["case"]["bridge"])
            with self.assertRaisesRegex(s.ScenarioInputError, r"scenarios\[1\].case.bridge.*identical"):parse(doc)
        doc = document(True);doc["scenarios"][1]["case"]["bridge"]["unresolved_requirements"] = ["Unresolved shares"]
        with self.assertRaisesRegex(s.ScenarioInputError, r"scenarios\[1\].case.bridge.unresolved_requirements"):parse(doc)

    def test_complete_validation_before_any_execution_and_failed_run_has_no_output(self):
        doc = document();doc["scenarios"][2]["case"]["terminal_growth"] = "0.25"
        with patch.object(s, "run_case") as engine, patch.object(c, "load_revenue_anchor") as loader:
            with self.assertRaisesRegex(s.ScenarioInputError, r"scenarios\[2\].case.terminal_growth"):
                parse(doc)
            engine.assert_not_called();loader.assert_not_called()
        parsed = parse(document())
        changed = replace(parsed, scenarios=parsed.scenarios[:-1])
        with patch.object(s, "run_case") as engine:
            with self.assertRaises(s.ScenarioInputError):s.run_scenario_set(changed, ROOT)
            engine.assert_not_called()
        # Execution failure cannot create an apparent partial-success result file.
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"case.json";path.write_text(json.dumps(document()));out=Path(tmp)/"result.json"
            with patch.object(s,"run_case",side_effect=[{}, ValueError("stale anchor")]), redirect_stderr(io.StringIO()):
                self.assertEqual(cli.main([str(path),"--run","--output",str(out)]),2)
            self.assertFalse(out.exists())

    def test_negative_flows_equity_and_nonordered_labels_are_preserved(self):
        doc = document(True)
        # Names imply no ordering: Bear has the highest value, Base is negative.
        doc["scenarios"][0]["case"]["terminal"]["operating_margin"] = "0.90"
        for y in doc["scenarios"][1]["case"]["forecast_years"]:y["operating_margin"] = "-0.10"
        doc["scenarios"][1]["case"]["terminal"]["operating_margin"] = "-0.10"
        result = execute(doc)
        ev = [D(x["result"]["stage_b"]["enterprise_value"]) for x in result["scenarios"]]
        self.assertGreater(ev[0], ev[2]);self.assertLess(ev[1],0)
        self.assertLess(D(result["scenarios"][1]["result"]["stage_c"]["equity_value"]),0)
        self.assertLess(D(result["scenarios"][1]["result"]["stage_b"]["stage_a"]["years"][0]["fcff"]),0)
        self.assertIn("negative EV; arithmetic ratio",cli.render_summary(result))

    def test_validation_no_calculations_retrieval_writes_or_context_changes(self):
        raw=json.dumps(document(True))
        with patch.object(s,"run_case") as run, patch.object(c,"forecast_five_years") as a, \
             patch.object(c,"discount_to_enterprise_value") as b, patch.object(c,"bridge_to_per_share") as bridge, \
             patch.object(c,"load_revenue_anchor") as load, patch.object(c,"load_meta_revenue_anchor") as meta:
            with patch.object(Path,"write_text",side_effect=AssertionError("no writes")), redirect_stdout(io.StringIO()):
                parse(document(True))
                self.assertEqual(cli.main([str(EXAMPLES/"synthetic-scenarios-equity.json")]),0)
            for mock in (run,a,b,bridge,load,meta):mock.assert_not_called()
        parsed=s.read_scenario_set(raw);result=s.run_scenario_set(parsed,ROOT);before=deepcopy(result)
        with self.assertRaises(FrozenInstanceError):parsed.scenario_set_name="mutated"
        with localcontext() as ctx:
            ctx.prec=3;ctx.rounding=ROUND_DOWN;ctx.traps[Inexact]=True;ctx.clear_flags();ctx.flags[Rounded]=True
            snapshot=ctx.copy()
            self.assertEqual(s.read_scenario_set(raw),parsed)
            self.assertEqual(s.run_scenario_set(parsed,ROOT),result)
            cli.render_summary(result);s.serialize_scenarios(result)
            self.assertEqual((ctx.prec,ctx.rounding,ctx.flags,ctx.traps),(snapshot.prec,snapshot.rounding,snapshot.flags,snapshot.traps))
        self.assertEqual(result,before);self.assertEqual(parsed.submitted_json,raw)

    def test_summary_components_units_rationale_and_fixed_bridge(self):
        result=execute(document(True));report=cli.render_summary(result)
        self.assertIn("USD millions",report);self.assertIn("USD/share",report)
        self.assertEqual(values(report,"WACC"),["25.00%"]*3)
        self.assertEqual(values(report,"Terminal growth"),["5.00%"]*3)
        self.assertEqual(values(report,"Synthetic period 1 Revenue"),["0.00010000","0.00011000","0.00012000"])
        self.assertEqual(values(report,"Synthetic period 1 FCFF"),["0.00000800","0.00000880","0.00000960"])
        for label,value in (("Explicit-period PV","0.00002771"),("Discounted terminal value","0.00004987"),
                            ("Enterprise value (EV)","0.00007758"),("Equity value","0.00006658"),
                            ("Terminal contribution / EV","64.29%"),("Scope-qualified value/share (USD/share)","16.64426509")):
            self.assertEqual(values(report,label)[1],value)
        self.assertIn("Eligible-asset subtotal (+): 0.00001200",report)
        self.assertIn("Financing subtotal (subtract): 0.00002000",report)
        self.assertIn("Other-claim subtotal (subtract): 0.00000300",report)
        self.assertIn("Fixed valuation shares: 4 actual shares | Date: 2025-12-31",report)
        self.assertIn("Declared information cutoff: 2026-01-31",report)
        for entry in result["scenarios"]:
            self.assertIn(entry["result"]["submitted_inputs"]["analyst"]["rationale"],report)
            for text in entry["result"]["limitations"]:self.assertIn(text,report)
        for note in result["scenarios"][0]["result"]["stage_c"]["inputs"]["observations"]:
            self.assertIn(note["rationale"],report)
        self.assertNotIn("Scope-qualified value/share",cli.render_summary(execute()))

    def test_summary_zero_signed_over_100_percent_and_display_rounding(self):
        # Renderer consumes supplied components; it never repairs/recalculates EV.
        result=execute()
        for entry,ev,pvt in zip(result["scenarios"],("0","-40","10"),("10","20","20")):
            entry["result"]["stage_b"].update(enterprise_value=ev,pv_terminal_value=pvt)
        report=cli.render_summary(result)
        contributions=values(report,"Terminal contribution / EV")
        self.assertIn("undefined (EV is zero)",contributions[0])
        self.assertIn("-50.00%",contributions[1]);self.assertIn("200.00%",contributions[2])
        self.assertIn("not clamped",contributions[1]);self.assertIn("not clamped",contributions[2])
        result=execute(document(True));base=result["scenarios"][1]["result"]
        base["stage_c"]["value_per_share"]="1.123456785"
        self.assertEqual(values(cli.render_summary(result),"Scope-qualified value/share (USD/share)")[1],"1.12345678")
        self.assertEqual(base["stage_c"]["value_per_share"],"1.123456785")

    def test_cli_default_json_explicit_output_and_protections(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);path=folder/"cases.json";path.write_text(json.dumps(document()));before=path.read_bytes()
            command=[sys.executable,str(SCRIPT),str(path)]
            valid=subprocess.run(command,capture_output=True,text=True,cwd=tmp)
            self.assertEqual(valid.returncode,0,valid.stderr);self.assertEqual(list(folder.iterdir()),[path])
            run=subprocess.run(command+["--run"],capture_output=True,text=True,cwd=tmp)
            self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(run.stdout,s.serialize_scenarios(execute()))
            for fmt in ("json","summary"):
                out=folder/("result."+fmt)
                with redirect_stdout(io.StringIO()):self.assertEqual(cli.main([str(path),"--run","--format",fmt,"--output",str(out)]),0)
                saved=out.read_bytes()
                with patch.object(cli,"run_scenario_set") as engine,redirect_stderr(io.StringIO()):
                    self.assertEqual(cli.main([str(path),"--run","--output",str(out)]),2);engine.assert_not_called()
                self.assertEqual(saved,out.read_bytes())
            for out in (path, ROOT/"docs/forbidden-scenario-output.json"):
                with patch.object(cli,"run_scenario_set") as engine,redirect_stderr(io.StringIO()):
                    self.assertEqual(cli.main([str(path),"--run","--output",str(out)]),2);engine.assert_not_called()
            with redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):cli.main([str(path),"--output",str(folder/"invalid")])
            self.assertEqual(path.read_bytes(),before)

    def test_company_templates_111_unset_and_existing_six_preserved(self):
        for issuer in ("meta","googl","aapl"):
            doc=json.loads((EXAMPLES/f"{issuer}-fy2025-scenarios-unset.json").read_text())
            for entry in doc["scenarios"]:
                case=entry["case"]
                rates=[y[k] for y in case["forecast_years"] for k in c.ANNUAL_RATES]+[case["wacc"],case["terminal_growth"],*case["terminal"].values()]
                self.assertEqual(rates,[None]*37);self.assertIsNone(case["analyst"]["rationale"])
            with self.assertRaises(s.ScenarioInputError) as error:parse(doc)
            self.assertEqual(str(error.exception).count("UNSET; supply a fractional"),111)
            for suffix in ("unset","equity-unset"):
                name=f"examples/valuation/{issuer}-fy2025-{suffix}.json"
                self.assertEqual((ROOT/name).read_bytes(),subprocess.check_output(["git","show","9da4a348858fb6e5ec1cc72e1c04746afc4b92ec:"+name],cwd=ROOT))

    def test_legacy_single_case_cli_json_bytes_unchanged(self):
        # Load the starting-HEAD CLI and compare actual legacy output bytes.
        source=subprocess.check_output(["git","show","9da4a348858fb6e5ec1cc72e1c04746afc4b92ec:scripts/run_analyst_case.py"],cwd=ROOT)
        old={"__file__":str(ROOT/"scripts/run_analyst_case.py"),"__name__":"legacy_cli"}
        exec(compile(source,"legacy_cli","exec"),old)
        for name in ("synthetic-base.json","synthetic-equity.json"):
            before=io.StringIO();after=io.StringIO()
            with redirect_stdout(before):self.assertEqual(old["main"]([str(EXAMPLES/name),"--run"]),0)
            with redirect_stdout(after):self.assertEqual(single_cli.main([str(EXAMPLES/name),"--run"]),0)
            self.assertEqual(before.getvalue(),after.getvalue())

    def test_original_engine_and_single_case_sources_unchanged(self):
        for name in ("assumptions.py", "case_inputs.py", "consumer.py", "forecast.py", "discounting.py", "bridge.py"):
            path="src/valuation_platform/valuation/"+name
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(
                ["git","show","9da4a348858fb6e5ec1cc72e1c04746afc4b92ec:"+path],cwd=ROOT))
        path="scripts/run_analyst_case.py"
        self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(
            ["git","show","9da4a348858fb6e5ec1cc72e1c04746afc4b92ec:"+path],cwd=ROOT))

    def test_three_retained_adapters_temporary_synthetic_integration_only(self):
        # Real retained revenue, deliberately synthetic forward assumptions/bridge.
        # No researched company forecasts, financial selections or saved defaults.
        packages=[ROOT/c.ANCHORS[k]["package"] for k in c.ANCHORS]
        hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in packages}
        with tempfile.TemporaryDirectory() as tmp,patch.object(socket,"socket",side_effect=AssertionError("network forbidden")):
            for kind,revenue in (("meta-fy2025","200966000000"),("googl-fy2025","402836000000"),("aapl-fy2025","416161000000")):
                for equity in (False,True):
                    doc=document(equity);identity=c.ANCHORS[kind]["identity"]
                    for entry in doc["scenarios"]:
                        entry["analytical_date"]=identity["annual_end"];entry["information_cutoff"]="2026-02-05"
                        case=entry["case"];case["anchor"]={"kind":kind,**identity};case["input_basis"]="MANUAL_INPUT"
                        case["case_name"]="SYNTHETIC FORECAST integration only on "+kind
                        case["analyst"]["rationale"]="SYNTHETIC ASSUMPTIONS on retained revenue only; not researched company scenarios."
                        case["conventions"]["forecast"]="manual-fcff-v1"
                        if equity:
                            bridge=case["bridge"];bridge["input_basis"]="MANUAL_INPUT";bridge["convention_version"]="manual-equity-bridge-v1"
                            for item in bridge["components"]:item.update(company_cik=identity["cik"],as_of=identity["annual_end"])
                            for item in bridge["observations"]:item.update(company_cik=identity["cik"])
                            bridge["shares"].update(company_cik=identity["cik"],observation_date=identity["annual_end"])
                    path=Path(tmp)/(kind+str(equity)+".json");path.write_text(json.dumps(doc));before=path.read_bytes()
                    out=Path(tmp)/(kind+str(equity)+"-output.json")
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(cli.main([str(path)]),0)
                        self.assertEqual(cli.main([str(path),"--run","--output",str(out)]),0)
                    result=json.loads(out.read_text())
                    for entry in result["scenarios"]:
                        a=entry["result"]["stage_b"]["stage_a"]["anchor"]
                        self.assertEqual(a["revenue"],revenue);self.assertEqual(a["annual_end"],identity["annual_end"])
                    self.assertEqual(path.read_bytes(),before)
            temporary=Path(tmp)
        self.assertFalse(temporary.exists())
        self.assertEqual(hashes,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in packages})


if __name__ == "__main__":
    unittest.main()
