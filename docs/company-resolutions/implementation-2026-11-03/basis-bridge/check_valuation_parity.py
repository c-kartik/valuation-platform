"""Execute fresh committed-policy/current-policy preload EV parity, read-only.
Both sides use the current engine and identical retained sources; only the
policy file origin is varied. Does not backtest an earlier engine or certify
issuer assumptions, FCFE financing, equity discounting or share values.
"""
from pathlib import Path
import sys,json,hashlib,subprocess,tempfile
from decimal import Decimal
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from valuation_platform.preload.generate import generate,engine_request
from valuation_platform.valuation.case_inputs import read_case,run_case

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def sha(b):return hashlib.sha256(b).hexdigest()
def check(write=True):
 baseline=json.loads((HERE/'baseline-tax-policy.json').read_text());output=[]
 timestamp='2026-11-03T00:00:00+00:00'
 for p in baseline['policies']:
  ticker=p['ticker'];policy_path=ROOT/p['path'];current=policy_path.read_bytes()
  old=subprocess.check_output(['git','show',p['source_git_commit']+':'+p['path']],cwd=ROOT)
  if sha(old)!=p['source_git_blob_sha256']:raise ValueError('Committed policy SHA differs from reviewed baseline')
  if sha(old)!=sha(current):raise ValueError('Policy changed; this zero-change test requires an explicitly unchanged reviewed policy')
  with tempfile.TemporaryDirectory(prefix='policy-parity-',dir=HERE) as tmp:
   oldfile=Path(tmp)/'committed-policy.json';oldfile.write_bytes(old)
   before=generate(ROOT,ticker=ticker,policy_path=oldfile,generated_at=timestamp)
   after=generate(ROOT,ticker=ticker,generated_at=timestamp)
  if before!=after:raise ValueError('Freshly generated profiles differ')
  records=[]
  for label in ('Base','Bear','Bull'):
   bd=engine_request(before,label,'perpetual_growth');ad=engine_request(after,label,'perpetual_growth')
   if bd!=ad:raise ValueError('Scenario documents differ')
   if len(bd['forecast_years'])!=5:raise ValueError('Expected five-year forecast')
   bv=run_case(read_case(json.dumps(bd)),ROOT);av=run_case(read_case(json.dumps(ad)),ROOT)
   if bv!=av:raise ValueError('Independently executed valuation responses differ')
   b=Decimal(bv['stage_b']['enterprise_value']);a=Decimal(av['stage_b']['enterprise_value'])
   if a-b!=0:raise ValueError('Nonzero EV difference')
   records.append({'scenario':label,'forecast_periods':5,'method':'FCFF_PERPETUAL_GROWTH_WACC','before_request_sha256':digest(bd),'after_request_sha256':digest(ad),'before_request':bd,'after_request':ad,'before_enterprise_value_usd':str(b),'after_enterprise_value_usd':str(a),'enterprise_value_difference_usd':str(a-b),'before_result':bv,'after_result':av,'entire_request_equal':True,'entire_result_equal':True,'annual_tax_before':[y['forecast_tax_rate'] for y in bd['forecast_years']],'annual_tax_after':[y['forecast_tax_rate'] for y in ad['forecast_years']],'terminal_tax_before':bd['terminal_valuation']['terminal']['operating_tax_rate'],'terminal_tax_after':ad['terminal_valuation']['terminal']['operating_tax_rate']})
  output.append({'ticker':ticker,'baseline_git_commit':p['source_git_commit'],'policy_path':p['path'],'baseline_policy_sha256':sha(old),'current_policy_sha256':sha(current),'policy_bytes_identical':True,'before_generated_profile_sha256':digest(before),'after_generated_profile_sha256':digest(after),'before_economic_hash':before['economic_hash'],'after_economic_hash':after['economic_hash'],'generated_profiles_equal':True,'scenarios':records})
 result={'schema_version':'reviewed-tax-policy-executed-valuation-parity-v1','review_date':'2026-11-03','fixed_generated_at':timestamp,'scope':'Fresh AAPL/META committed-policy versus current-policy FCFF five-year Base/Bear/Bull estimates','test_design':'Before policy is read from the pinned committed baseline; current policy is read from current file. Both sides independently generate preloads and run the current run_case engine with the same retained source bank. Policies are byte-identical. This isolates the approved no-numeric-change policy review, not a changed historical input or engine version.','issuer_count':2,'scenario_pairs':6,'independent_engine_executions':12,'all_input_documents_equal':True,'all_result_documents_equal':True,'all_enterprise_value_differences_zero':True,'accepted_inputs_or_runtime_modified':False,'companies':output,'limitations':['These are conditional FCFF operating-enterprise values under the existing analytical fiscal-end origin and later-filed data, not current-date fair values or approved investment recommendations.','Zero parity verifies that this policy review changes no numerical input/output; it does not certify the assumptions, equity bridge, FCFE model, cost of equity or outstanding awards.','S1 remains a partial basis bridge. Historical and forecast bases are not fully reconciled.','S2 FCFE financing, tax, terminal and discounting economics remain OPEN. Manual cost of equity is a user assumption, not issuer certification.']}
 if write:(HERE/'valuation-parity.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 return result
if __name__=='__main__':
 r=check();print(json.dumps({'pairs':r['scenario_pairs'],'executions':r['independent_engine_executions'],'all_ev_differences_zero':True,'enterprise_values':{c['ticker']:{s['scenario']:s['after_enterprise_value_usd'] for s in c['scenarios']} for c in r['companies']}},indent=2))
