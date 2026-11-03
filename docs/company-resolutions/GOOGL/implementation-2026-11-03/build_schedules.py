"""Reproduce approved Alphabet G1-G3 schedules without changing immutable facts.
Run from any directory: python docs/company-resolutions/GOOGL/implementation-2026-11-03/build_schedules.py
"""
from __future__ import annotations
import base64, gzip, hashlib, json, re
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LEDGER = ROOT / 'docs/evidence/analyst-operating-nwc-response-bodies.json'
PREVIOUS = ROOT / 'docs/company-resolutions/GOOGL/results.json'

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def norm(text): return ' '.join(text.split())

class Filing(HTMLParser):
    def __init__(self):
        super().__init__(); self.text=[]; self.hidden=0; self.active=[]; self.facts={}
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag in ('script','style','ix:hidden'): self.hidden+=1
        if tag=='ix:nonfraction': self.active.append({'attrs':attrs,'text':[],'visible':not self.hidden})
    def handle_endtag(self, tag):
        if tag=='ix:nonfraction' and self.active:
            f=self.active.pop()
            if f['visible']: self.facts[f['attrs'].get('id')]=f
        if tag in ('script','style','ix:hidden'): self.hidden-=1
    def handle_data(self, value):
        if not self.hidden: self.text.append(value)
        for fact in self.active: fact['text'].append(value)

def build():
    ledger=json.loads(LEDGER.read_text()); prior=json.loads(PREVIOUS.read_text())
    sources={}; parsed={}
    for year, artifact in zip(range(2021,2026),[24,26,28,30,32]):
        a=ledger['artifacts'][artifact]; raw=gzip.decompress(base64.b64decode(a['response_body_gzip_base64']))
        assert hashlib.sha256(raw).hexdigest()==a['sha256']
        p=Filing(); p.feed(raw.decode()); parsed[year]=(p,raw.decode())
        sources[year]={'url':a['source_url'],'sha256':a['sha256'],'retained_reference':f'docs/evidence/analyst-operating-nwc-response-bodies.json#/artifacts/{artifact}'}
    def point(source_year, xml_id, target_year, expected, caption):
        p,body=parsed[source_year]; fact=p.facts[xml_id]; a=fact['attrs']; display=norm(''.join(fact['text']))
        value=Fraction(display.replace(',','').replace('(','-').replace(')',''))*10**int(a.get('scale',0))
        if a.get('sign')=='-': value=-value
        assert value==int(expected),(xml_id,value,expected)
        assert a['unitref']=='usd', 'Unexpected unit'
        assert re.search(r'<(?:[\w-]+:)?unit\b[^>]*id=[\"\']usd[\"\'][^>]*>[\s\S]*?<[^>]*measure[^>]*>[^<]*:USD<',body,re.I), 'USD unit metadata missing'
        context_id=a['contextref']; match=re.search(r'<(?:[\w-]+:)?context\b[^>]*\bid=[\"\']'+re.escape(context_id)+r'[\"\'][^>]*>([\s\S]*?)</(?:[\w-]+:)?context>',body,re.I)
        assert match and str(target_year)+'-01-01' in match[1] and str(target_year)+'-12-31' in match[1]
        assert not re.search(r'<(?:[\w-]+:)?(?:explicitMember|typedMember)',match[1],re.I)
        return {'amount_usd':str(int(value)),'caption':caption,'source':sources[source_year],'inline_id':xml_id,'context_id':context_id,'concept':a['name'],'precision':a.get('decimals'),'target_fiscal_year':target_year,'classification':'SEC_REPORTED_FACT'}
    lease={2021:None,2022:point(2024,'f-977',2022,586000000,'Financing cash flows used for finance leases'),2023:point(2024,'f-978',2023,705000000,'Financing cash flows used for finance leases'),2024:point(2024,'f-979',2024,405000000,'Financing cash flows used for finance leases'),2025:point(2025,'f-1000',2025,1988000000,'Financing cash flows used for finance leases')}
    assets={2021:None,2022:point(2024,'f-983',2022,577000000,'Assets obtained in exchange for finance lease liabilities'),2023:point(2024,'f-984',2023,564000000,'Assets obtained in exchange for finance lease liabilities'),2024:point(2024,'f-985',2024,313000000,'Assets obtained in exchange for finance lease liabilities'),2025:point(2025,'f-1006',2025,1606000000,'Assets obtained in exchange for finance lease liabilities')}
    nci_book=[4300000000,3800000000,3400000000,4200000000,3400000000]
    rnci_book=[1100000000]*4+[841000000]
    rows=[]
    for old,nci,rnci in zip(prior['periods'],nci_book,rnci_book):
        year=old['fiscal_year']; p,_=parsed[year]; text=norm(' '.join(p.text))
        m=re.search(r'(?:Total noncontrolling interests.*?See Note 7|As of December 31, 2023 and 2024, total noncontrolling interests.*?See Note 7)',text,re.I)
        assert m and 'not material' in m[0]
        assert str(year) in m[0] and re.search(r'\$\s*'+re.escape(str(nci/1e9))+r'\s*billion',m[0]), 'Book NCI display not bound'
        rnci_text=norm(' '.join(parsed[2022][0].text)) if year==2021 else m[0]
        assert (re.search(r'\$\s*1\.1\s*billion',rnci_text) if year<2025 else re.search(r'\$\s*841\s*million',rnci_text)), 'RNCI display not bound'
        funding=sum(int(r['signed_cash_usd']) for r in old['financing']['source_rows'] if r['included_in_net_borrowing'])
        cash=int(old['inputs']['cfo'])-int(old['net_cash_investment']['amount_usd'])
        assert cash+funding==int(old['fcfe']['amount_usd'])
        outside=[r for r in old['financing']['source_rows'] if r['classification']=='NONCONTROLLING_CAPITAL_NOT_DEBT']
        assert all(not r['included_in_net_borrowing'] for r in outside)
        fcff=Fraction(int(old['fcff']['exact_fraction_usd']['numerator']),int(old['fcff']['exact_fraction_usd']['denominator']))
        expected=Fraction(cash)+Fraction(int(old['inputs']['interest_expense']))*(1-Fraction(int(old['inputs']['tax_provision']),int(old['inputs']['pretax_income'])))
        assert fcff==expected
        rows.append({'ticker':'GOOGL','fiscal_year':year,'annual_end':old['identity']['annual_end'],'cash_inputs_usd':old['inputs'],'net_cash_investment_usd':old['net_cash_investment']['amount_usd'],'identified_net_borrowing_usd':str(funding),'fcff':{**old['fcff'],'ownership_scope':'CONSOLIDATED','availability':'AVAILABLE_UNDER_STATED_CASH_CONVENTION','source_reference':f'docs/company-resolutions/GOOGL/results.json#/periods/{year-2021}/fcff'},'consolidated_fcfe_before_nci_allocation':{**old['fcfe'],'availability':'AVAILABLE_CONSOLIDATED_ONLY','ownership_scope':'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION'},'parent_common_fcfe':{'amount_usd':None,'availability':'UNAVAILABLE_ATTRIBUTION_NOT_DISCLOSED','blocker':'G1','reason':'Consolidated statements and reviewed official subsidiary announcements do not provide complete annual cash-flow and ownership populations attributable to parent common shareholders.'},'ownership_schedule':{'outside_capital_cash_usd':str(sum(int(r['signed_cash_usd']) for r in outside)),'outside_capital_included_in_borrowing':False,'nci_cash_allocation_usd':None,'book_nci_usd_rounded':str(nci),'book_rnci_usd_rounded_included_in_nci':str(rnci),'rnci_source':sources[2022] if year==2021 else sources[year],'book_nci_used_as_fair_value':False,'nci_fair_value_usd':None,'nci_fair_value_status':'UNRESOLVED_VALUATION_INPUT_G2','source':sources[year],'note':'Note 5, Variable Interest Entities','source_excerpt':m[0],'precision_notice':'Book NCI displayed in billions, not an exact fair value; RNCI is included, not additive.'},'lease_schedule':{'financing_cash':lease[year],'financing_cash_contained_in_debt_repayments':True,'additional_cash_deduction_usd':'0','noncash_assets_obtained':assets[year],'noncash_assets_added_to_cash_capex_usd':'0','prepayments':{'amount_usd_rounded':'1100000000' if year==2025 else None,'source_precision':'$1.1 billion' if year==2025 else None,'status':'ROUNDED_DISCLOSED_AMOUNT' if year==2025 else 'NOT_SEPARATELY_BOUND_NOT_ZERO','included_in_financing_cash':True if year==2025 else None,'source':sources[2025] if year==2025 else None},'commenced_lease_principal_usd':None,'cash_noncash_timing_alignment_status':'OPEN_G3','reason':'No complete exact prepayment/addition/commencement/FX/modification/principal roll-forward has been established; no residual inferred from rounded footnote.'},'numerical_change_from_prior_consolidated_result_usd':'0','source':sources[year]})
    assert 'includes $ 1.1 billion of prepayments for finance leases not yet commenced' in norm(' '.join(parsed[2025][0].text))
    assert len(rows)==5
    research=json.loads((HERE/'research/manifest.json').read_text())
    for item in research:
        assert digest(ROOT/item['file'])==item['sha256'], 'Retained official research body changed'
    result={'schema_version':'googl-approved-ownership-lease-schedules-v1','review_date':'2026-11-03','company_status':'OPEN','authorization':'User approved preferred treatments in OPEN-ROADBLOCKS.md; implementation does not supply missing issuer disclosures or approve an invented ownership estimate.','inputs':{'previous_results':{'path':str(PREVIOUS.relative_to(ROOT)),'sha256':digest(PREVIOUS)},'read_only_evidence_ledger':{'path':str(LEDGER.relative_to(ROOT)),'sha256':digest(LEDGER)}},'periods':rows,'research_attempts':research,'open_roadblocks':{'G1':'No exact full parent-common annual cash attribution.','G2':'No supported complete dated NCI fair-value/ownership bridge.','G3':'Cash containment proven; full economic-investment timing bridge not complete.'},'validation':{'source_body_hash_checks':5,'official_research_body_hash_checks':3,'lease_or_asset_inline_point_checks':8,'exact_consolidated_fcfe_checks':5,'exact_consolidated_fcff_checks':5,'parent_common_fcfe_values_invented':0,'fair_values_invented':0,'additional_lease_deductions':0}}
    return result

def main():
    result=build(); (HERE/'schedules.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result['validation'],sort_keys=True))
if __name__=='__main__': main()
