"""Source-bound FY2025 cash/debt/claims/share preparation; no equity adoption.

Run from the repository root with PYTHONPATH=src .venv/bin/python <this file>
--check. Class dimensions and cover dates are never collapsed into a denominator.
"""
import argparse
from collections import defaultdict
from decimal import Decimal, Context, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'scripts'))
from calculate_historical_fcff_from_filings import RetainedFiling
from prepare_msft_analyst_package import inline_amount
from valuation_platform.preload.extract import inline_document
from valuation_platform.valuation.consumer import ANCHORS

FOLDER=Path(__file__).resolve().parent
XI='{http://www.xbrl.org/2003/instance}'
DI='{http://xbrl.org/2006/xbrldi}'
CATEGORIES={
 'cash_investment_support':{
  'CashAndCashEquivalentsAtCarryingValue','MarketableSecuritiesCurrent','MarketableSecuritiesNoncurrent',
  'ShortTermInvestments','OtherLongTermInvestments','LongTermInvestments','NonmarketableEquitySecuritiesCarryingValue',
  'EquityMethodInvestmentsAndOther','EquityMethodInvestments','RestrictedCashAndCashEquivalentsAtCarryingValue',
  'RestrictedCashAndCashEquivalentsNoncurrent','CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents',
  'CashCashEquivalentsAndMarketableSecurities','CashCashEquivalentsAndShortTermInvestments'},
 'debt_lease_support':{
  'CommercialPaper','LongTermDebtCurrent','LongTermDebtNoncurrent','ShortTermBorrowings','ShortTermDebtCurrent',
  'LongTermDebtFairValue','DebtInstrumentCarryingAmount','FinanceLeaseLiability','FinanceLeaseLiabilityCurrent',
  'FinanceLeaseLiabilityNoncurrent','OperatingLeaseLiability','OperatingLeaseLiabilityCurrent','OperatingLeaseLiabilityNoncurrent'},
 'claims_support':{
  'NoncontrollingInterestInVariableInterestEntity','RedeemableNoncontrollingInterestInVariableInterestEntity',
  'MinorityInterest','RedeemableNoncontrollingInterestEquityCarryingAmount','NoncontrollingInterestInConsolidatedEntity',
  'ConvertiblePreferredStockNonredeemableOrRedeemableIssuerOptionValue','PreferredStockValue','PreferredStockSharesOutstanding',
  'PreferredStockRedemptionValue','PreferredStockLiquidationPreferenceValue','DefinedBenefitPlanFundedStatusOfPlan',
  'DefinedBenefitPlanAmountsRecognizedInBalanceSheetLiability','DefinedBenefitPlanAmountsRecognizedInBalanceSheetLiabilityNoncurrent',
  'UnrecognizedTaxBenefits','UnrecognizedTaxBenefitsIncomeTaxPenaltiesAndInterestAccrued',
  'AccruedLitigationSettlementAmount','LegalRelatedAccruedLiabilitiesCurrent','LegalRelatedAccruedLiabilitiesNoncurrent'},
 'dated_share_support':{'CommonStockSharesOutstanding','EntityCommonStockSharesOutstanding','CommonStockSharesIssued'},
 'existing_awards_support':{
  'ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber',
  'ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsOutstandingNumber',
  'ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedWeightedAverageGrantDateFairValue',
  'EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognized'}
}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def qname(namespaces,lexical):
    prefix,local=lexical.split(':',1) if ':' in lexical else ('',lexical)
    if prefix not in namespaces:raise ValueError('Unknown source QName prefix')
    return namespaces[prefix]+'#'+local


def context(c,namespaces):
    identifiers=c.findall('.//'+XI+'identifier');p=c.find(XI+'period')
    if len(identifiers)!=1 or identifiers[0].get('scheme')!='http://www.sec.gov/CIK' or p is None:
        raise ValueError('Exact SEC entity/period required')
    if list(c.iter(DI+'typedMember')):raise ValueError('Typed dimensions require explicit review')
    dims=sorted((qname(namespaces,e.get('dimension')),qname(namespaces,e.text)) for e in c.iter(DI+'explicitMember'))
    return {'cik':int(identifiers[0].text),'start':p.findtext(XI+'startDate'),
        'end':p.findtext(XI+'instant') or p.findtext(XI+'endDate'),
        'dimensions':[{'axis':a,'member':m} for a,m in dims]}


def unit(u,namespaces):
    if u is None:raise ValueError('Explicit source unit required')
    measures=u.findall(XI+'measure')
    if len(measures)==1 and len(u)==1:
        expanded=qname(namespaces,measures[0].text)
        if expanded=='http://www.xbrl.org/2003/iso4217#USD':return 'USD'
        if expanded=='http://www.xbrl.org/2003/instance#shares':return 'shares'
    divide=u.find(XI+'divide')
    if divide is not None:
        top=divide.findall(XI+'unitNumerator/'+XI+'measure');bottom=divide.findall(XI+'unitDenominator/'+XI+'measure')
        if len(top)==len(bottom)==1 and qname(namespaces,top[0].text)=='http://www.xbrl.org/2003/iso4217#USD' and qname(namespaces,bottom[0].text)=='http://www.xbrl.org/2003/instance#shares':return 'USD_per_share'
    raise ValueError('Unsupported selected source unit')


def numeric(attrs,text):
    fmt=attrs.get('format','').split(':')[-1]
    if fmt in ('fixed-zero','zerodash'):
        if text.strip().lower() not in ('—','–','-','0','no','none'):
            raise ValueError('Fixed zero lacks explicit zero display: '+repr(text))
        return Decimal(0)
    return inline_amount(attrs,text)


def verified_points(filing,as_of):
    primary,ns,contexts,units=inline_document(filing.primary.artifact.body)
    tags={c:category for category,concepts in CATEGORIES.items() for c in concepts}
    nodes={e.get('id'):e for e in primary.iter() if e.get('id')}
    out=[]
    for ordinal,node in enumerate(filing.root):
        local=node.tag.split('}')[-1]
        if local not in tags or not node.get('unitRef'):continue
        c=filing.contexts.get(node.get('contextRef'))
        if c is None:raise ValueError('Instance source context missing')
        scope=context(c,filing.namespaces)
        if scope['cik']!=filing.period.cik or scope['start'] is not None:continue
        if scope['end']!=as_of and local!='EntityCommonStockSharesOutstanding':continue
        # Cover-date counts are retained separately, never selected for the
        # fiscal-end population. Older balance comparatives are not selected.
        expected_unit=unit(filing.units.get(node.get('unitRef')),filing.namespaces)
        xml_id=node.get('id');inline=nodes.get(xml_id)
        if inline is None or not inline.tag.endswith('}nonFraction'):
            raise ValueError('Selected instance observation has no exact primary ID')
        primary_scope=context(contexts[inline.get('contextRef')],ns)
        if primary_scope!=scope or unit(units.get(inline.get('unitRef')),ns)!=expected_unit:
            raise ValueError('Primary/instance source date, class, entity or unit mismatch')
        if qname(ns,inline.get('name'))!=node.tag[1:].split('}')[0]+'#'+local:
            raise ValueError('Primary/instance QName differs')
        attrs={k.lower():v for k,v in inline.attrib.items()};text=''.join(inline.itertext()).strip()
        with localcontext(Context(prec=80)):
            value=Decimal(node.text)
            if not value.is_finite() or numeric(attrs,text)!=value:
                raise ValueError('Primary/instance numerical representation differs')
        if inline.get('decimals')!=node.get('decimals'):raise ValueError('Source precision differs')
        out.append({'category':tags[local],'concept':local,'namespace':node.tag[1:].split('}')[0],
            'value':format(value,'f'),'unit':expected_unit,'precision':node.get('decimals'),
            'scope':scope,'source_identity':filing.source_identity,'sources':filing.references,
            'instance_ordinal':ordinal,'instance_context_id':node.get('contextRef'),
            'primary_locator':'inline#'+xml_id,'primary_display':text,'primary_scale':inline.get('scale','0'),
            'primary_format':inline.get('format'),'primary_sign':inline.get('sign'),
            'used_as_valuation_operand':False})
    return out


def unique(points,concept,*,dimensions=(),unit_name='USD',as_of=None):
    candidates=[p for p in points if p['concept']==concept and p['unit']==unit_name and
        tuple((d['axis'],d['member']) for d in p['scope']['dimensions'])==tuple(dimensions)
        and (as_of is None or p['scope']['end']==as_of)]
    values={Fraction(p['value']) for p in candidates}
    if not values:return {'value':None,'status':'NOT_SEPARATELY_DISCLOSED_IN_SELECTED_SOURCE','observations':[]}
    if len(values)>1:return {'value':None,'status':'COMPETING_SOURCE_POPULATIONS','observations':candidates}
    return {'value':candidates[0]['value'],'unit':unit_name,'status':'REPORTED_SUPPORT_NOT_SELECTED_OPERAND','observations':candidates}


def class_controls(points,as_of,ticker):
    share_points=[p for p in points if p['concept']=='CommonStockSharesOutstanding' and p['scope']['end']==as_of]
    classes={}
    for p in share_points:
        ds=p['scope']['dimensions']
        if len(ds)==1 and ds[0]['axis'].endswith('#StatementClassOfStockAxis'):
            member=ds[0]['member'];label='Class '+('C' if member.endswith('#CapitalClassCMember') else member.split('#')[-1].replace('CommonClass','').replace('Member',''))
            if label in classes and Fraction(classes[label]['value'])!=Fraction(p['value']):raise ValueError('Competing same-class count')
            classes[label]=p
    if ticker=='META':
        totals=[p for p in share_points if len(p['scope']['dimensions'])==1 and p['scope']['dimensions'][0]['member'].endswith('#CommonStockMember')]
    else:totals=[p for p in share_points if not p['scope']['dimensions']]
    if not totals or len({Fraction(p['value']) for p in totals})!=1:raise ValueError('Exact reported total share support required')
    total=totals[0]
    check=None
    if classes:
        difference=sum(Fraction(p['value']) for p in classes.values())-Fraction(total['value'])
        if difference:raise ValueError('Class count does not reconcile to reported total')
        check={'difference_shares':'0','economic_equivalence_inferred':False,'source_total':total,'class_sources':classes}
    return {'year_end_reported_total':total,'class_sources':classes,'class_sum_control':check,
        'cover_date_counts':[p for p in points if p['concept']=='EntityCommonStockSharesOutstanding'],
        'weighted_average_eps_shares_selected':False,'approved_valuation_denominator':None,
        'class_equivalence':'NOT_ADOPTED','award_adjusted_denominator':None}


def excerpts(filing):
    patterns={'class_rights':r'certificate of incorporation authorizes|Class A and Class B common stock|Class A common stock is entitled|rights of the holders|rights.*identical',
        'award_service_cost':r'unrecognized.*compensation (?:cost|expense)|unrecognized share-based compensation',
        'cash_restrictions':r'restricted cash|restricted from general use|operating cash',
        'nci_scope':r'noncontrolling interest|wholly owned subsidiaries',
        'debt_fair_value':r'fair value of (?:the Company.s|our) (?:Notes|long-term debt|senior)' }
    result={}
    for key,pattern in patterns.items():
        matches=list(re.finditer(pattern,filing.text,re.I))
        result[key]={'match_count':len(matches),'excerpts':[{'offset':m.start(),'text':filing.text[max(0,m.start()-100):m.end()+700]} for m in matches[:8]]}
    return {'sources':filing.references,'matches':result,'interpretation':'Source statements retained for rights/eligibility/claims review, not an adopted equivalence or fair-value conclusion.'}


def google_cover_prose(filing):
    """Exact reviewed cover prose where no numeric instance fact was found."""
    pattern=(r'As of January 28, 2026\s*, there wer\s*e\s+([\d,]+) million shares of Alphabet.s Class A stock outstanding,\s+'
        r'([\d,]+) million shares of Alphabet.s Class B stock outstanding, and\s+'
        r'([\d,]+) million shares of the Alphabet.s Class C stock outstanding\.')
    matches=list(re.finditer(pattern,filing.text))
    if len(matches)!=1:raise ValueError('Reviewed Alphabet cover-share prose changed')
    m=matches[0]
    return {'date':'2026-01-28','origin':'REPORTED_PRIMARY_PROSE_NO_NUMERIC_INSTANCE_BINDING',
        'counts_shares':{'Class '+label:str(int(value.replace(',',''))*1000000) for label,value in zip('ABC',m.groups(),strict=True)},
        'precision':'-6','offset':m.start(),'excerpt':m.group(0),'sources':filing.references,
        'used_as_anchor_denominator':False,'economic_equivalence_inferred':False}


def build(root=ROOT):
    companies=[];inputs={}
    for ticker in ('AAPL','META','GOOGL'):
        kind=ticker.lower()+'-fy2025';path=Path(ANCHORS[kind]['package']);inputs[str(path)]=sha(root/path)
        package=json.loads((root/path).read_text());prefix=ticker.lower()
        rows=package['periods'] if ticker=='META' else package[prefix+'_history_review']['periods']
        row=rows[-1]
        if row['identity']['annual_end'][:4]!='2025':raise ValueError('Approved FY2025 anchor only')
        filing=RetainedFiling(root,row,{});as_of=row['identity']['annual_end'];points=verified_points(filing,as_of)
        facts={concept:unique(points,concept,as_of=as_of) for category in ('cash_investment_support','debt_lease_support','claims_support') for concept in CATEGORIES[category]}
        cash_components=['CashAndCashEquivalentsAtCarryingValue','MarketableSecuritiesCurrent']
        if ticker=='AAPL':cash_components.append('MarketableSecuritiesNoncurrent')
        if any(facts[c]['value'] is None for c in cash_components):raise ValueError('Required gross reported cash support missing')
        cash_subtotal=sum(Fraction(facts[c]['value']) for c in cash_components)
        debts=['LongTermDebtNoncurrent']
        if ticker in ('AAPL','GOOGL'):debts.insert(0,'LongTermDebtCurrent')
        if ticker=='AAPL':debts.insert(0,'CommercialPaper')
        if any(facts[c]['value'] is None for c in debts):raise ValueError('Required named debt support missing')
        debt_subtotal=sum(Fraction(facts[c]['value']) for c in debts)
        controls=class_controls(points,as_of,ticker)
        controls['cover_primary_prose_support']=google_cover_prose(filing) if ticker=='GOOGL' else None
        companies.append({'ticker':ticker,'anchor':kind,'as_of':as_of,'source_identity':row['identity'],
            'status':'OPEN_SOURCE_PREPARED_NOT_PER_SHARE_READY','source_points':points,'nondimensional_support':facts,
            'reported_cash_and_marketable_subtotal':{'value_usd':str(cash_subtotal),'components':cash_components,
                'classification':'DERIVED_REPORTED_SUBTOTAL_NOT_ELIGIBLE_CASH','operating_reserve_deducted':False,'approved_eligible_amount_usd':None},
            'named_debt_carrying_subtotal':{'value_usd':str(debt_subtotal),'components':debts,
                'classification':'DERIVED_NAMED_DEBT_CARRYING_SUBTOTAL_NOT_COMPLETE_FINANCING_CLAIM','finance_lease_added':False,
                'face_principal_or_fair_value_added':False,'approved_financing_claim_usd':None},
            'shares':controls,'awards':[p for p in points if p['category']=='existing_awards_support'],
            'claims':[p for p in points if p['category']=='claims_support'],
            'review_excerpts':excerpts(filing),
            'approved_bridge':{'eligible_assets_usd':None,'financing_claims_usd':None,'other_equity_claims_usd':None,
                'nci_fair_value_usd':None,'existing_award_value_usd':None,'valuation_share_count':None,
                'common_equity_value_usd':None,'fair_value_per_share_usd':None},
            'remaining_reviews':['Define operating cash reserve and eligible/nonoperating investment coverage; review overlap with consolidated valuation',
                'Review debt fair-value/carrying selection, financing costs and lease perimeter once; book subtotals are not market-value totals',
                'Review other claims coverage, litigation/tax/pension obligations and contingent or subsidiary capital where applicable',
                'Review dated shares and class rights; no common-unit equivalence adopted for META/GOOGL',
                'Value pre-anchor award rights separately from future service cost; no automatic RSU addition or second SBC charge']+
                (['Alphabet NCI book observations do not supply NCI fair value or annual parent-common cash attribution'] if ticker=='GOOGL' else []),
            'no_missing_claims_assumed_zero':True,'no_automatic_publication':True})
    return {'schema_version':'pilot-share-bridge-source-preparation-v1','review_date':'2026-11-03',
        'status':'OPEN','scope':'AAPL/META/GOOGL existing FY2025 valuation-anchor support; dates/rights/claims preserved',
        'inputs_sha256':inputs,'companies':companies,
        'validation':{'verified_companies':3,'exact_class_sum_controls':2,'per_share_ready_companies':0},
        'consumer_contract':'Source support only. Require reviewed coverage, economic classification, class/award and valuation-date decisions before making BridgeComponent/ValuationShares operands. Never coerce null to zero or sum overlapping observations.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true');args=parser.parse_args()
    data=build();payload=json.dumps(data,indent=2,sort_keys=True)+'\n';path=FOLDER/'source-schedules.json'
    if args.write:path.write_text(payload)
    elif path.read_text()!=payload:raise SystemExit('Share-bridge source preparation differs; review before writing')
    print(json.dumps(data['validation'],sort_keys=True))


if __name__=='__main__':main()
