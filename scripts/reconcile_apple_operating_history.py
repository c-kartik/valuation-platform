"""Replay exact bridges from original source-row workpapers to adopted Apple FCFF."""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
from valuation_platform.review.apple_operating_history import read_overlay
from valuation_platform.review.operating_fcff import serialized
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/company-resolutions/AAPL/operating-fcff-2026-11-04/legacy-comparison.json'

def build():
    adopted=read_overlay(ROOT)
    original=json.loads((ROOT/'docs/company-resolutions/AAPL/results.json').read_text())
    result=[]
    for p,old in zip(adopted['periods'],original['periods'],strict=True):
        assert p['identity']==old['identity']
        inp=p['inputs'];v={k:F(x) for k,x in inp.items()}
        candidate=old['operating_fcff_candidate']
        terms=candidate['statement_terms']
        by_concept={r['caption']:F(r['cash_contribution_usd']) for r in terms}
        cfo=F(candidate['inputs']['cfo_control']['value'])
        assert sum(by_concept.values(),F())==cfo
        assert by_concept['DepreciationDepletionAndAmortization']==v['da']
        other=sum((F(r['cash_contribution_usd']) for r in terms if r['caption'] not in {'NetIncomeLoss','DepreciationDepletionAndAmortization','ShareBasedCompensation'}),F())
        tax=1-v['tax_provision']/v['pretax_income']
        bridge={'remove_allocated_after_tax_net_nonoperating':-(v['pretax_income']-v['ebit'])*tax,
                'retain_sbc_as_expense':-by_concept['ShareBasedCompensation'],
                'remove_all_other_reported_cfo_adjustments':-other,
                'apply_defined_current_nwc_investment':-(v['closing_nwc']-v['opening_nwc'])}
        new=F(int(p['fcff']['exact_fraction_usd']['numerator']),int(p['fcff']['exact_fraction_usd']['denominator']))
        cash_fcf=cfo-v['cash_ppe']
        difference=new-cash_fcf-sum(bridge.values(),F())
        assert difference==0
        result.append({'fiscal_year':p['fiscal_year'],'new_standardized_fcff':p['fcff'],
            'old_cash_fcf':serialized(cash_fcf),'legacy_cfo_fcff_usd':old['platform_before']['fcff_usd'],
            'new_minus_cash_fcf':serialized(new-cash_fcf),'bridge_terms':{k:serialized(x) for k,x in bridge.items()},
            'bridge_difference_usd':str(difference),'balancing_plug_used':False,'other_cfo_terms_are_not_claimed_pure_wc':True})
    return {'formula':'new FCFF - cash FCF = - after-tax net nonoperating - SBC - other CFO adjustments - defined current NWC increase','periods':result}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');a=parser.parse_args()
    body=json.dumps(build(),indent=2)+'\n'
    if a.check:
        assert json.loads(OUT.read_text())==json.loads(body), 'Bridge replay differs'
    else:OUT.write_text(body)
    print('PASS: five exact reported-cash/standardized-FCFF bridges; no balancing plug.')
