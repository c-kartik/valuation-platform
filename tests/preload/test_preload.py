"""Reproduction, source selection, financial preparation and unchanged-engine agreement."""
from copy import deepcopy
from decimal import Decimal, localcontext, getcontext
from fractions import Fraction as F
import json
from pathlib import Path
import shutil,socket,subprocess,tempfile,unittest
from unittest.mock import patch
from valuation_platform.preload.rules import growth,cagr,fade,wacc,incremental_cash_ratio,diagnostic_axes,number
from valuation_platform.preload.profile import validate_profile,refresh_diff,select_observation,read_json,digest,exclusive_json
from valuation_platform.preload.generate import generate,engine_request,resolve_listing
from valuation_platform.valuation.case_inputs import read_case,run_case
ROOT=Path(__file__).resolve().parents[2]

class RulesTests(unittest.TestCase):
 def test_synthetic_growth_cagr_and_fade(self):
  self.assertEqual(Decimal(growth('150','100')),Decimal('.5'))
  self.assertEqual(Decimal(cagr('100','121',2)),Decimal('.1'))
  self.assertEqual([Decimal(v) for v in fade('.2','.04')],list(map(Decimal,['.2','.16','.12','.08','.04'])))
  self.assertNotEqual(Decimal(cagr('100','150',2)),Decimal('.5'))
 def test_wc_signed_full_revenue_and_zero(self):
  self.assertEqual(Decimal(incremental_cash_ratio('.25','.2')),Decimal('.04'))
  self.assertEqual(Decimal(incremental_cash_ratio('-.2','.2')),Decimal('-.05'))
  self.assertEqual(Decimal(incremental_cash_ratio('0','.2')),0)
  with self.assertRaises(ValueError):incremental_cash_ratio('-1','.2')
 def test_wacc_independent_weights_one_shield_and_context(self):
  expected=(F('0.05')+F('1.2')*F('.04'))*F('.9')+(F('.05')+F('.01'))*(1-F('.25'))*F('.1')
  with localcontext() as ctx:
   ctx.prec=5;ctx.rounding='ROUND_UP';before=ctx.copy()
   actual=wacc('.05','.04','1.2','.01','.9','.1','.25')
   self.assertEqual(ctx.prec,before.prec);self.assertEqual(ctx.rounding,before.rounding)
  self.assertEqual(F(actual),expected)
  with self.assertRaises(ValueError):wacc('.05','.04','1','.01','.9','.2','.2')
 def test_no_clamp_and_decimal_strings(self):
  axes=diagnostic_axes('.01','.03','.02','.005')
  self.assertEqual(Decimal(axes['wacc_values'][0]),Decimal('-.01'))
  for v in [1,1.1,'NaN','1e-3',None]:
   with self.assertRaises(ValueError):number(v)
 def test_selection_duplicate_incompatible_and_explicit_restatement(self):
  row={'id':'old','key':'revenue','value':'100','unit':'USD','definition':'revenue','start':'2025-01-01','end':'2025-12-31','published_at':'2026-02-01'}
  kwargs=dict(definition='revenue',unit='USD',cutoff='2026-10-30')
  self.assertEqual(select_observation([row],'revenue',**kwargs),row)
  with self.assertRaises(LookupError):select_observation([],'revenue',**kwargs)
  with self.assertRaises(ValueError):select_observation([row,row],'revenue',**kwargs)
  with self.assertRaises(TypeError):select_observation([row],'revenue',**{**kwargs,'definition':'expense-da'})
  new={**row,'id':'restated','value':'110','supersedes':'old','published_at':'2026-09-01'}
  self.assertEqual(select_observation([row,new],'revenue',**kwargs)['value'],'110')
  self.assertEqual(select_observation([row,new],'revenue',**{**kwargs,'cutoff':'2026-03-01'})['value'],'100')

class ProfileTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.profile=generate(ROOT);cls.doc=engine_request(cls.profile);cls.result=run_case(read_case(json.dumps(cls.doc)),ROOT)
 def configured(self,**changes):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);path=Path(temp.name)/'policy.json';policy=read_json(ROOT/'data/preload/googl-v1/policy.json');policy['configuration'].update(changes);policy['configuration_provenance']['exit']='Explicit synthetic verification multiple; not company evidence';path.write_text(json.dumps(policy));return generate(ROOT,policy_path=path)
 def test_offline_determinism_generation_time_not_economic_hash(self):
  with patch.object(socket,'socket',side_effect=AssertionError('network')):
   a=generate(ROOT,generated_at='2026-10-30T00:00:00Z');b=generate(ROOT,generated_at='2026-10-30T01:00:00Z')
  self.assertEqual(a['economic_hash'],b['economic_hash']);self.assertEqual(a['economic'],b['economic']);self.assertNotEqual(a['generated_at'],b['generated_at'])
 def test_every_field_exact_provenance_and_unavailable_exit(self):
  p=self.profile;e=p['economic'];self.assertEqual(len(e['fields']),38)
  for path,f in e['fields'].items():
   self.assertTrue(f['rule']);self.assertTrue(f['classification']);self.assertTrue(f['limitation']);self.assertTrue(f['operands'])
   if f['value'] is not None:self.assertIsInstance(f['value'],str)
  self.assertIsNone(e['fields']['exit_ev_ebit_multiple']['value'])
  self.assertEqual(e['optional_bridge']['status'],'UNSUPPORTED_PREPARATION')
  self.assertEqual(resolve_listing('GOOG')['cik'],resolve_listing('GOOGL')['cik']);self.assertNotEqual(resolve_listing('GOOG')['listing_class'],resolve_listing('GOOGL')['listing_class'])
  with self.assertRaises(ValueError):resolve_listing('META')
 def test_scope_and_configured_inputs_not_historical_complete(self):
  f=self.profile['economic']['fields'];i=f['forecast_years[0].capex_percent_revenue']['operands']
  self.assertEqual(i['cash_ppe_usd'],'200000000000');self.assertEqual(Decimal(i['new_financed_assets_usd']),Decimal('5000000000'))
  self.assertIn('EXCLUDED',i['principal']);self.assertIn('no complete',f['forecast_years[0].d_and_a_percent_revenue']['limitation'])
  self.assertEqual(f['forecast_years[0].d_and_a_percent_revenue']['status'],'CONFIGURED_CONVENTION')
  self.assertEqual(f['terminal.d_and_a_percent_revenue']['value'],'0.16')
  self.assertNotEqual(f['forecast_years[4].d_and_a_percent_revenue']['value'],'0.16')
 def test_missing_not_zero_and_partial_profile_survives(self):
  missing=self.configured(expense_da_start_usd=None)
  self.assertIsNone(missing['economic']['fields']['forecast_years[0].d_and_a_percent_revenue']['value'])
  self.assertIsNotNone(missing['economic']['fields']['forecast_years[0].revenue_growth']['value'])
  with self.assertRaisesRegex(ValueError,'d_and_a_percent_revenue'):engine_request(missing)
  zero=self.configured(expense_da_start_usd='0')
  self.assertEqual(Decimal(zero['economic']['fields']['forecast_years[0].d_and_a_percent_revenue']['value']),0)
 def test_refresh_configuration_forecasts_gaps_and_valuation_explicit(self):
  b=self.configured(growth_endpoint='0.06',exit_ev_ebit_multiple='15')
  diff=refresh_diff(self.profile,b)
  self.assertTrue(diff['configuration_changes']);self.assertTrue(diff['forecast_changes']);self.assertTrue(diff['gap_changes']);self.assertIsNone(diff['valuation_changes']);self.assertNotEqual(self.profile['economic_hash'],b['economic_hash'])
  self.assertEqual(diff['source_changes'],{});validate_profile(self.profile)
 def test_strict_profile_hash_tamper_and_duplicate_json(self):
  p=deepcopy(self.profile);p['economic']['fields']['wacc']['value']='0.1'
  with self.assertRaisesRegex(ValueError,'hash'):validate_profile(p)
  with tempfile.TemporaryDirectory() as t:
   f=Path(t)/'bad.json';f.write_text('{"value":"1","value":"2"}')
   with self.assertRaisesRegex(ValueError,'Duplicate'):read_json(f)
   out=Path(t)/'new.json';exclusive_json(out,{'test':'1'})
   with self.assertRaises(FileExistsError):exclusive_json(out,{'test':'2'})
 def test_scenarios_named_diagnostics_and_independent_terminal(self):
  e=self.profile['economic'];base=e['scenarios']['Base'];bear=e['scenarios']['Bear']
  self.assertEqual(Decimal(bear['wacc'])-Decimal(base['wacc']),Decimal('.01'))
  self.assertEqual(bear['terminal.operating_margin'],base['terminal.operating_margin'])
  self.assertEqual(bear['forecast_years[0].capex_percent_revenue'],base['forecast_years[0].capex_percent_revenue'])
 def test_exit_missing_fails_but_supported_explicit_multiple_adapts(self):
  with self.assertRaisesRegex(ValueError,'exit_ev_ebit_multiple'):engine_request(self.profile,method='exit_multiple')
  profile=self.configured(exit_ev_ebit_multiple='15');doc=engine_request(profile,method='exit_multiple');r=run_case(read_case(json.dumps(doc)),ROOT)
  self.assertEqual(r['stage_b']['terminal_method'],'exit_multiple');self.assertEqual(r['stage_b']['stage_a']['years'],self.result['stage_b']['stage_a']['years'])
 def test_invalid_spread_is_not_capped(self):
  p=self.configured(terminal_growth='0.10')
  self.assertEqual(p['economic']['fields']['terminal_growth']['value'],'0.10')
  with self.assertRaises(ValueError):engine_request(p)
 def test_independent_fraction_engine_reconciliation(self):
  doc=self.doc;r=self.result;b=r['stage_b'];previous=F('402836000000');discount=1+F(doc['wacc']);pv=F(0)
  def near(raw,expected):self.assertLess(abs(F(str(raw))-expected),F('0.000000000000000000000000000001'))
  for i,row in enumerate(doc['forecast_years']):
   revenue=previous*(1+F(row['revenue_growth']));ebit=revenue*F(row['operating_margin']);tax=max(ebit,0)*F(row['forecast_tax_rate']);da=revenue*F(row['d_and_a_percent_revenue']);investment=revenue*F(row['capex_percent_revenue']);wc=revenue*F(row['change_in_operating_nwc_percent_revenue']);fcff=ebit-tax+da-investment-wc
   for key,value in {'revenue':revenue,'ebit':ebit,'tax':tax,'nopat':ebit-tax,'d_and_a':da,'investment':investment,'working_capital_cash_requirement':wc,'fcff':fcff}.items():near(b['stage_a']['years'][i][key],value)
   discounted=fcff/discount**(i+1);near(b['years'][i]['pv_fcff'],discounted);pv+=discounted;previous=revenue
  t=doc['terminal_valuation'];tr=previous*(1+F(t['terminal_growth']));ratios=t['terminal'];ebit=tr*F(ratios['operating_margin']);fcff=ebit-max(ebit,0)*F(ratios['operating_tax_rate'])+tr*(F(ratios['d_and_a_percent_revenue'])-F(ratios['investment_percent_revenue'])-F(ratios['working_capital_cash_requirement_percent_revenue']));tv=fcff/(F(doc['wacc'])-F(t['terminal_growth']));tpv=tv/discount**5
  near(b['terminal']['fcff'],fcff);near(b['terminal_value'],tv);near(b['pv_explicit_fcff'],pv);near(b['pv_terminal_value'],tpv);near(b['enterprise_value'],pv+tpv)
 def test_source_integrity_and_incompatible_definition(self):
  with tempfile.TemporaryDirectory() as t:
   dataset=Path(t)/'data';shutil.copytree(ROOT/'data/preload/googl-v1',dataset)
   o=read_json(dataset/'observations.json');o[0]['definition']='incompatible';(dataset/'observations.json').write_text(json.dumps(o))
   p=generate(ROOT,dataset=dataset);self.assertEqual(p['economic']['fields']['forecast_years[0].revenue_growth']['status'],'INCOMPATIBLE_DEFINITION')
   (dataset/'sources/q3-2026-release.html').write_text('changed')
   with self.assertRaisesRegex(ValueError,'immutable'):generate(ROOT,dataset=dataset)
 def test_wrong_period_scope_and_stale_sources_are_not_executable(self):
  with tempfile.TemporaryDirectory() as t:
   data=Path(t)/'data';shutil.copytree(ROOT/'data/preload/googl-v1',data)
   obs=read_json(data/'observations.json');next(o for o in obs if o['key']=='q32026_revenue')['start']='2020-01-01';(data/'observations.json').write_text(json.dumps(obs))
   p=generate(ROOT,dataset=data);self.assertEqual(p['economic']['fields']['forecast_years[0].revenue_growth']['status'],'INCOMPATIBLE_DEFINITION')
   with self.assertRaisesRegex(ValueError,'revenue_growth'):engine_request(p)
   policy=read_json(data/'policy.json');policy['review_date']='2027-01-30';(data/'policy.json').write_text(json.dumps(policy))
   p=generate(ROOT,dataset=data);self.assertEqual(p['economic']['fields']['wacc']['status'],'STALE')
 def test_unavailable_status_nonnull_value_and_scenario_mismatch_reject(self):
  p=deepcopy(self.profile);p['economic']['fields']['wacc']['status']='MISSING_EVIDENCE';p['economic_hash']=digest(p['economic'])
  with self.assertRaisesRegex(ValueError,'Unavailable'):engine_request(p)
  p=deepcopy(self.profile);p['economic']['scenarios']['Base']['wacc']='0.1';p['economic_hash']=digest(p['economic'])
  with self.assertRaisesRegex(ValueError,'Base scenario'):validate_profile(p)
 def test_refresh_exposes_rationale_only_rule_and_policy_changes(self):
  p=deepcopy(self.profile);p['economic']['configuration_provenance']['wacc']='Changed documented rationale';p['economic']['fields']['wacc']['limitation']='Changed limitation';p['economic']['policy']['version']='test-v2';p['economic_hash']=digest(p['economic'])
  d=refresh_diff(self.profile,p);self.assertTrue(d['configuration_rationale_changes']);self.assertTrue(d['field_preparation_changes']);self.assertTrue(d['policy_changes']);self.assertEqual(d['forecast_changes'],{})
 def test_missing_cash_growth_is_partial_and_zero_commissioning_is_allowed(self):
  p=self.configured(cash_ppe_growth=None)
  self.assertEqual(p['economic']['fields']['forecast_years[0].capex_percent_revenue']['status'],'MISSING_EVIDENCE')
  self.assertIsNotNone(p['economic']['fields']['wacc']['value'])
  p=self.configured(commissioning_allowance='0');self.assertEqual(Decimal(p['economic']['fields']['forecast_years[4].d_and_a_percent_revenue']['operands']['expense_da_usd']),Decimal('33000000000'))
 def test_engine_templates_and_original_runtime_pins_are_byte_preserved(self):
  baseline='cb67dd8a7ad97e68bb05798e64be260f0bbb4bf8'
  # The approved ten-year extension changed valuation code after the original
  # preload milestone. Keep original template/resource pins; preserve engine
  # bytes against that explicit reviewed extension, not the five-year engine.
  engine_baseline='634d98b11a63735f942a0f52e9eb4c138451462f'
  paths=subprocess.check_output(['git','ls-tree','-r','--name-only',baseline,'src/valuation_platform/valuation','examples/valuation'],cwd=ROOT).decode().splitlines()
  templates=[p for p in paths if p.endswith('-unset.json')];self.assertEqual(len(templates),9)
  for path in paths:
   reference=engine_baseline if path.startswith('src/valuation_platform/valuation/') else baseline
   self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',reference+':'+path],cwd=ROOT),path)
  original=json.loads(subprocess.check_output(['git','show',baseline+':src/valuation_platform/api/bundle-files.json'],cwd=ROOT))
  current=read_json(ROOT/'src/valuation_platform/api/bundle-files.json')
  for key,value in original['resources'].items():self.assertEqual(current['resources'][key],value)
 def test_explicit_acquisition_new_outside_snapshot_only(self):
  from valuation_platform.preload.acquire import acquire
  class Response:
   is_redirect=False
   def raise_for_status(self):pass
   def iter_content(self,size):return iter([b'<html>synthetic primary-source acquisition test</html>'])
  with tempfile.TemporaryDirectory() as t,patch.dict('os.environ',{'SEC_USER_AGENT':'Software test contact@example.com'}),patch('requests.get',return_value=Response()) as get:
   destination=Path(t)/'source'
   receipt=acquire('https://www.sec.gov/example',destination,published_at='2026-10-30')
   self.assertEqual(receipt['extraction_version'],'UNREVIEWED');self.assertTrue((destination/'source.html').exists());self.assertEqual(get.call_count,1)
   with self.assertRaises(ValueError):acquire('https://www.sec.gov/example',destination)
   with self.assertRaises(ValueError):acquire('https://unapproved.example.com/data',Path(t)/'other')
   self.assertEqual(get.call_count,1)
 def test_dated_profile_wacc_independently_matches_declared_build(self):
  actual=F(self.profile['economic']['fields']['wacc']['value'])
  expected=(F('0.0505')+F('1.10')*F('0.037'))*F('0.96')+(F('0.0505')+F('0.0075'))*(1-F('0.20'))*F('0.04')
  self.assertEqual(actual,expected)
 def test_cli_reproduction_and_export_exact_engine_result(self):
  with tempfile.TemporaryDirectory() as t:
   out=Path(t);from scripts.prepare_preload import main
   main(['generate',str(out/'profile.json')]);main(['export',str(out/'profile.json'),str(out/'export'),'--run'])
   doc=read_json(out/'export/request.json');actual=read_json(out/'export/result.json');expected=run_case(read_case(json.dumps(doc)),ROOT)
   self.assertEqual(actual,expected)
   candidate=self.configured(growth_endpoint='0.06');(out/'candidate.json').write_text(json.dumps(candidate));main(['export',str(out/'candidate.json'),str(out/'candidate-run'),'--run']);main(['diff',str(out/'profile.json'),str(out/'candidate.json'),str(out/'diff.json'),'--previous-result',str(out/'export/result.json'),'--candidate-result',str(out/'candidate-run/result.json')]);diff=read_json(out/'diff.json');self.assertTrue(diff['forecast_changes']);self.assertNotEqual(diff['valuation_changes']['previous_ev'],diff['valuation_changes']['candidate_ev'])

if __name__=='__main__':unittest.main()
