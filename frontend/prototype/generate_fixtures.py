"""Offline synthetic illustrations. Never imported or run by the web prototype.

Run from repository root with PYTHONPATH=src .venv/bin/python
frontend/prototype/generate_fixtures.py. Existing A/B/C and reverse engines own
all financial calculations. Monetary amounts AND shares are uniformly scaled
10,000,000x from the engine's revenue-100 fixture (USD100 -> USD1bn).
"""
from copy import deepcopy
from decimal import Decimal, localcontext
import json
from pathlib import Path
from valuation_platform.valuation.case_inputs import read_case, run_case
from valuation_platform.valuation.reverse_inputs import read_reverse, run_reverse

ROOT = Path(__file__).resolve().parents[2]
ANNUAL = ['revenue_growth','operating_margin','forecast_tax_rate','d_and_a_percent_revenue','capex_percent_revenue','change_in_operating_nwc_percent_revenue']
TERMINAL = ['operating_margin','operating_tax_rate','d_and_a_percent_revenue','investment_percent_revenue','working_capital_cash_requirement_percent_revenue']
PROFILES = {
 'steady': ([10,24,25,5,10,1], [25,25,5,8,'0.5'],10,3),
 'lower': ([6,20,25,5,11,1], [22,25,5,'8.5','0.5'],11,'2.5'),
 'higher': ([14,27,25,5,11,1], [28,25,5,9,'0.5'],9,'3.5'),
 'heavy': ([10,15,25,5,35,2], [30,25,5,8,'0.5'],10,3),
}
def fraction(v): return format(Decimal(str(v))/100,'f')
def inputs(values,term,w,g):
 return {'annual':[{k:str(v) for k,v in zip(['growth','margin','tax','da','investment','wc'],values)} for _ in range(5)],'terminal':dict(zip(['margin','tax','da','investment','wc'],map(str,term))),'wacc':str(w),'g':str(g)}
def case(profile,w,g):
 values,term,_,_=PROFILES[profile]
 c=json.loads((ROOT/'examples/valuation/synthetic-equity.json').read_text())
 c['case_name']='Northstar Instruments — fictional prototype illustration'
 for i,y in enumerate(c['forecast_years']):
  y.update(dict(zip(ANNUAL,map(fraction,values))));y['fiscal_year_label']=f'FY{2026+i}'
 c.update(wacc=fraction(w),terminal_growth=fraction(g),terminal=dict(zip(TERMINAL,map(fraction,term))))
 for component in c['bridge']['components']:
  component['amount']={'asset-a':'13','asset-b':'2','financing':'20','claim':'2.5'}[component['component_id']]
 c['bridge']['shares']['shares']='10'
 return c

def pack(result):
 b=result['stage_b'];c=result['stage_c']
 def millions(v):return format(Decimal(v)*10,'f')
 return {'years':[{k:millions(y[k]) for k in ['revenue','ebit','tax','nopat','d_and_a','investment','working_capital_cash_requirement','fcff']} | {'pv_fcff':millions(b['years'][i]['pv_fcff']),'discount_factor':b['years'][i]['discount_factor']} for i,y in enumerate(b['stage_a']['years'])],
 'ev':millions(b['enterprise_value']),'explicitPV':millions(b['pv_explicit_fcff']),'terminalPV':millions(b['pv_terminal_value']),'terminalValue':millions(b['terminal_value']),'terminalFCFF':millions(b['terminal']['fcff']),
 'equity':millions(c['equity_value']),'perShare':c['value_per_share'],'terminalContribution':format(Decimal(b['pv_terminal_value'])/Decimal(b['enterprise_value'])*100,'f')}

def generate():
 out={'basis':'EXCLUSIVELY_SYNTHETIC_OFFLINE_ENGINE_FIXTURES','money_unit':'USD millions','share_unit':'millions of shares','anchor_revenue':'1000','scaling':'All engine USD and actual shares uniformly multiplied by 10000000; displayed money/shares divided by 1000000; USD/share unchanged.','profiles':{},'variants':[],'reverse':[]}
 for name,(v,t,w,g) in PROFILES.items():
  out['profiles'][name]=inputs(v,t,w,g)
  pairs={(str(a),str(b)) for a in [9,10,11] for b in ['2.5',3,'3.5']}|{('3','2'),('4','2'),('4','3')}
  for wv,gv in sorted(pairs):
   doc=case(name,wv,gv);result=run_case(read_case(json.dumps(doc)),ROOT)
   out['variants'].append({'profile':name,'inputs':inputs(v,t,wv,gv),'result':pack(result)})
  for metric,target in [('VALUE_PER_SHARE','25'),('VALUE_PER_SHARE','1000'),('ENTERPRISE_VALUE','250')]:
   lower,upper=('-1','1') if name=='heavy' else ('-0.10','0.30')
   request={'schema_version':'analyst-reverse-dcf-request-v1','reverse_dcf_name':'Fictional prototype record','source':{'kind':'single_case','case':case(name,w,g),'analytical_date':'2025-12-31','information_cutoff':'2026-01-29'},'target':{'metric':metric,'amount':target,'unit':'USD/share' if metric=='VALUE_PER_SHARE' else 'USD','date':'2025-12-31'},'growth_bounds':{'lower':lower,'upper':upper}}
   result=run_reverse(read_reverse(json.dumps(request)),ROOT)
   solution=result['solution']
   out['reverse'].append({'profile':name,'inputs':inputs(v,t,w,g),'metric':'price' if metric=='VALUE_PER_SHARE' else 'ev','target':target if metric=='VALUE_PER_SHARE' else '2500','lower':str(Decimal(lower)*100),'upper':str(Decimal(upper)*100),'status':result['status'],'reason':result['reason'],'growth':format(Decimal(solution['constant_annual_growth'])*100,'f') if solution else None,'result':pack(solution['forward_result']) if solution else None})
 return out
if __name__=='__main__':
 with localcontext() as ctx:
  ctx.prec=50
  data=generate();(ROOT/'frontend/src/prototype/fixtures.json').write_text(json.dumps(data,indent=2)+'\n')
 print('Synthetic only:',len(data['variants']),'forward illustrations;',[(x['profile'],x['metric'],x['target'],x['status']) for x in data['reverse']])
