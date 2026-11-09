"""Offline Alphabet cash allocation/PPE consumer; never writes existing pipelines.

Reads the accepted quarterly cohort and hash-verified retained filing instances.
Writes only the new cash-allocation package and its evidence receipt.
"""
import argparse
from datetime import date, timedelta
from decimal import Decimal
import gzip
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
POLICY = 'alphabet-cash-allocation-v2'
X = '{http://www.xbrl.org/2003/instance}'
D = '{http://xbrl.org/2006/xbrldi}'
# sign converts XBRL payment-positive amounts to signed cash flows.
FIELDS = {
    'cfo': ('NetCashProvidedByUsedInOperatingActivities', 1),
    'ppe': ('PaymentsToAcquirePropertyPlantAndEquipment', -1),
    'marketablePurchases': ('PaymentsToAcquireMarketableSecurities', -1),
    'marketableSales': ('ProceedsFromSaleAndMaturityOfMarketableSecurities', 1),
    'otherPurchases': ('PaymentsToAcquireOtherInvestments', -1),
    'otherSales': ('ProceedsFromSaleAndMaturityOfOtherInvestments', 1),
    'acquisitions': ('goog:AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets', -1),
    'otherInvesting': ('PaymentsForProceedsFromOtherInvestingActivities', -1),
    'investing': ('NetCashProvidedByUsedInInvestingActivities', 1),
    'awards': ('goog:NetProceedsPaymentsRelatedToStockBasedAwardActivities', -1),
    'buybacks': ('PaymentsForRepurchaseOfCommonStock', -1),
    'dividends': (('PaymentsOfDividends', 'PaymentsOfOrdinaryDividends'), -1),
    'debtProceeds': ('ProceedsFromDebtNetOfIssuanceCosts', 1),
    'debtRepayments': ('RepaymentsOfDebtAndCapitalLeaseObligations', -1),
    'minority': ('ProceedsFromMinorityShareholders', 1),
    'commonIssued': ('ProceedsFromIssuanceOfCommonStock', 1),
    'preferredIssued': ('ProceedsFromIssuanceOfConvertiblePreferredStock', 1),
    'otherFinancing': ('ProceedsFromPaymentsForOtherFinancingActivities', 1),
    'financing': ('NetCashProvidedByUsedInFinancingActivities', 1),
    'fx': ('EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents', 1),
    'change': ('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect', 1),
}
OPTIONAL = {'dividends', 'minority', 'commonIssued', 'preferredIssued', 'otherFinancing'}
INVESTING = ('ppe', 'marketablePurchases', 'marketableSales', 'otherPurchases', 'otherSales', 'acquisitions', 'otherInvesting')
FINANCING = ('awards', 'buybacks', 'dividends', 'debtProceeds', 'debtRepayments', 'minority', 'commonIssued', 'preferredIssued', 'otherFinancing')
CASH = 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents'
PPE_GROSS = 'PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetBeforeAccumulatedDepreciationAndAmortization'
PPE_NET = 'PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization'
PPE_DEP = 'PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAccumulatedDepreciationAndAmortization'
PPE_AXIS = 'us-gaap:PropertyPlantAndEquipmentByTypeAxis'
PPE_MEMBERS = {'technical': 'goog:TechnicalInfrastructureMember', 'office': 'goog:OfficeSpaceMember',
    'other': 'goog:CorporateAndOtherAssetsMember', 'service': 'goog:DepreciablePropertyPlantAndEquipmentMember',
    'pending': 'us-gaap:AssetUnderConstructionMember'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Instance:
    def __init__(self, data, url, filed, entity=1652044):
        require(b'<!DOCTYPE' not in data.upper() and b'<!ENTITY' not in data.upper(), 'Unsafe XML')
        self.ns = dict(item for _, item in ET.iterparse(io.BytesIO(data), events=['start-ns']))
        self.root = ET.fromstring(data)
        self.contexts = {c.attrib['id']: c for c in self.root.findall(X+'context')}
        self.units = {u.attrib['id']: u for u in self.root.findall(X+'unit')}
        self.url, self.filed, self.hash, self.entity = url, filed, sha(data), entity

    def qname(self, value):
        prefix, local = value.split(':') if ':' in value else ('us-gaap', value)
        return '{'+self.ns[prefix]+'}'+local

    def fact(self, concepts, start=None, end=None, instant=None, dimensions=(), optional=False, sign=1):
        concepts = (concepts,) if isinstance(concepts, str) else concepts
        allowed = {self.qname(c) for c in concepts}
        dims = sorted((self.qname(a), self.qname(m)) for a, m in dimensions)
        hits = []
        for f in self.root:
            if f.tag not in allowed:
                continue
            c = self.contexts.get(f.attrib.get('contextRef'))
            if c is None or c.find('.//'+D+'typedMember') is not None:
                continue
            entity = c.findtext(X+'entity/'+X+'identifier')
            require(entity and int(entity) == self.entity, 'Wrong filing entity')
            got_dims = sorted((self.qname(v.attrib['dimension']), self.qname(v.text)) for v in c.findall('.//'+D+'explicitMember'))
            if got_dims != dims:
                continue
            if instant:
                matches = c.findtext(X+'period/'+X+'instant') == instant
            else:
                matches = c.findtext(X+'period/'+X+'startDate') == start and c.findtext(X+'period/'+X+'endDate') == end
            if not matches:
                continue
            require(f.attrib.get('{http://www.w3.org/2001/XMLSchema-instance}nil') not in ('true','1'), 'Nil required fact')
            unit = self.units.get(f.attrib.get('unitRef'))
            measure = unit.findtext(X+'measure') if unit is not None and len(unit) == 1 else None
            require(measure is not None, 'Missing simple unit')
            is_ratio = any(c.endswith('Percentage') for c in concepts)
            require(self.qname(measure) == ('{http://www.xbrl.org/2003/instance}pure' if is_ratio else '{http://www.xbrl.org/2003/iso4217}USD'), 'Wrong fact unit')
            raw = Decimal(f.text)
            require(raw.is_finite() and (is_ratio or raw == raw.to_integral_value()), 'Noninteger or nonfinite USD')
            hits.append((f, raw))
        if not hits:
            require(optional, 'Missing filing fact: '+str(concepts)+' '+str((start,end,instant)))
            return None
        require(len({v for _,v in hits}) == 1, 'Conflicting filing facts: '+str(concepts))
        raw = hits[0][1]
        return {'value': float(raw) if is_ratio else int(raw)*sign, 'reported_value': float(raw) if is_ratio else int(raw),
            'sign': sign, 'concept': hits[0][0].tag, 'context_ids': sorted({f.attrib['contextRef'] for f,_ in hits}),
            'dimensions': [list(v) for v in dims], 'start': start, 'end': end, 'instant': instant,
            'filed': self.filed, 'source_url': self.url, 'source_sha256': self.hash}


def amount(row, key):
    # An absent caption remains null in the package/evidence. It contributes no
    # component to a reconciled statement, rather than becoming a reported zero.
    return row['values'][key] if row['values'][key] is not None else 0


def reconcile(row):
    v = row['values']
    require(sum(amount(row,k) for k in INVESTING) == v['investing'], 'Investing components do not reconcile')
    require(sum(amount(row,k) for k in FINANCING) == v['financing'], 'Financing components do not reconcile')
    require(v['cfo']+v['investing']+v['financing']+v['fx'] == v['change'], 'Cash movement does not reconcile')
    require(v['opening']+v['change'] == v['closing'], 'Closing cash does not reconcile')


def combine(rows, coefficients, **metadata):
    values, evidence = {}, {}
    for k in FIELDS:
        present = [(r['values'][k], c) for r,c in zip(rows,coefficients) if r['values'][k] is not None]
        values[k] = sum(v*c for v,c in present) if present else None
        evidence[k] = {'method': metadata['method'], 'terms': [
            {'coefficient': c, 'period_id': r['id']} for r,c in zip(rows,coefficients)]}
    values['opening'] = rows[0]['values']['opening'] if all(c==1 for c in coefficients) else rows[1]['values']['closing']
    values['closing'] = rows[-1]['values']['closing'] if all(c==1 for c in coefficients) else rows[0]['values']['closing']
    result = {**metadata, 'values': values, 'evidence': evidence}
    reconcile(result)
    return result


def retain_extension_sources(root=ROOT):
    """Explicitly retain two earliest-disclosure 2021 quarters in a new store."""
    import os
    from valuation_platform.sec.client import SECClient
    from valuation_platform.sec.filing_xbrl import discover_extracted_xbrl
    from valuation_platform.sec.submissions import SECFiling
    from valuation_platform.sec.tickers import SECCompanyIdentity
    from datetime import datetime, timezone
    require(bool(os.environ.get('SEC_USER_AGENT')), 'Set an identifying SEC_USER_AGENT')
    original=json.loads((root/'data/reporting-audit/GOOGL-sources.json').read_text())['files']
    directory=root/'data/cash-allocation/sources/GOOGL';directory.mkdir(parents=True,exist_ok=True)
    target=root/'data/cash-allocation/GOOGL-sources.json'
    manifest=json.loads(target.read_text()) if target.exists() else {'ticker':'GOOGL','files':{}}
    client=SECClient(os.environ['SEC_USER_AGENT'],timeout=45)
    class Retainer:
        def get_bytes(self,url):
            name=sha(url.encode())+'.gz';entry=manifest['files'].get(url);path=directory/name
            if entry:
                raw=gzip.decompress(path.read_bytes());require(sha(raw)==entry['sha256'],'Extension source hash mismatch');return raw
            raw=client.get_bytes(url);path.write_bytes(gzip.compress(raw,mtime=0));manifest['files'][url]={'file':name,'sha256':sha(raw)};return raw
        def get_json(self,url):
            return json.loads(self.get_bytes(url))
    filings={}
    for url,entry in original.items():
        if 'submissions/' not in url:continue
        raw=gzip.decompress((root/'data/reporting-audit/sources/GOOGL'/entry['file']).read_bytes());require(sha(raw)==entry['sha256'],'Submission hash mismatch')
        payload=json.loads(raw);columns=payload.get('filings',{}).get('recent',payload)
        if 'accessionNumber' in columns:
            for i,acc in enumerate(columns['accessionNumber']):
                if acc in ['0001652044-21-000020','0001652044-21-000047']:
                    filings[acc]=SECFiling(acc,columns['form'][i],date.fromisoformat(columns['filingDate'][i]),date.fromisoformat(columns['reportDate'][i]),columns['primaryDocument'][i])
    company=SECCompanyIdentity('GOOGL',1652044,'0001652044','Alphabet','SEC',datetime.now(timezone.utc));retainer=Retainer()
    for acc in ['0001652044-21-000020','0001652044-21-000047']:
        require(acc in filings,'Missing retained submission metadata')
        artifact=discover_extracted_xbrl(retainer,company,filings[acc]);retainer.get_bytes(artifact.source_url)
    target.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')


def prepare(root=ROOT):
    history_bytes = (root/'frontend/public/research-data/GOOGL.json').read_bytes()
    history = json.loads(history_bytes)
    manifest = json.loads((root/'data/reporting-audit/GOOGL-sources.json').read_text())['files']
    extra_bytes=(root/'data/cash-allocation/GOOGL-sources.json').read_bytes()
    extra_manifest=json.loads(extra_bytes)['files']
    require(not set(extra_manifest).intersection(manifest), 'Extension must not replace original sources')
    manifest={**manifest,**extra_manifest}
    instances, periods = {}, {}
    def instance(o):
        accession = o['accession']
        if accession not in instances:
            urls = [u for u in manifest if '/'+accession.replace('-','')+'/' in u and u.endswith('.xml')]
            require(len(urls)==1, 'Ambiguous retained filing')
            u = urls[0]
            source_dir='data/cash-allocation/sources/GOOGL' if u in extra_manifest else 'data/reporting-audit/sources/GOOGL'
            raw = gzip.decompress((root/source_dir/manifest[u]['file']).read_bytes())
            require(sha(raw)==manifest[u]['sha256'], 'Retained source hash mismatch')
            require(o['filed']<=history['as_of'], 'Source after review cutoff')
            instances[accession] = Instance(raw, u, o['filed'])
        return instances[accession]
    def cumulative(o):
        key = o['accession']+':'+o['start']+':'+o['end']
        if key not in periods:
            ins = instance(o)
            evidence = {k: ins.fact(c, start=o['start'], end=o['end'], optional=k in OPTIONAL, sign=sign)
                for k,(c,sign) in FIELDS.items()}
            opening = str(date.fromisoformat(o['start'])-timedelta(days=1))
            evidence['opening'] = ins.fact(CASH, instant=opening)
            evidence['closing'] = ins.fact(CASH, instant=o['end'])
            row = {'id':key, 'start':o['start'], 'end':o['end'], 'method':'reported',
                'values':{k:e['value'] if e else None for k,e in evidence.items()}, 'evidence':evidence}
            require(row['values']['cfo']==o['value'], 'CFO contradicts accepted reporting cohort')
            reconcile(row)
            periods[key] = row
        return periods[key]
    annual = []
    annual_ops = sorted([a for a in history['validation']['annual_tie_outs'] if a['metric']=='cfo'], key=lambda a:a['fiscal_year'])[-5:]
    require(len(annual_ops)==5, 'Need five accepted annual periods')
    for a in annual_ops:
        r = cumulative(a['annual'])
        annual.append({**r,'id':'FY'+str(a['fiscal_year']),'operand_ids':[r['id']], 'label':'FY'+str(a['fiscal_year'])})
    # Extend only this cash-allocation consumer. The original 20-quarter history
    # and all its selected accessions/values remain unchanged.
    facts_bytes=(root/'data/quarterly-reporting/sources/GOOGL.json.gz').read_bytes()
    facts=json.loads(gzip.decompress(facts_bytes))['facts']['us-gaap']
    initial_year=annual_ops[0]['fiscal_year']
    require(initial_year==2021,'Review the initial-year extension before changing coverage')
    early=[]
    for quarter,end in [(1,'2021-03-31'),(2,'2021-06-30'),(3,'2021-09-30')]:
        def earliest(concept):
            eligible=[f for f in facts[concept]['units']['USD'] if f.get('start')=='2021-01-01' and f['end']==end and f['filed']<=history['as_of'] and f['form']=='10-Q']
            require(bool(eligible),'Missing early-quarter Company Facts anchor')
            f=min(eligible,key=lambda r:(r['filed'],r['accn']))
            return {'accession':f['accn'],'start':f['start'],'end':f['end'],'filed':f['filed'],'value':f['val']}
        op=earliest('NetCashProvidedByUsedInOperatingActivities');capex=earliest('PaymentsToAcquirePropertyPlantAndEquipment')
        require(capex['accession']==op['accession'],'Early-quarter capex/CFO filing disagreement')
        current=cumulative(op)
        require(-current['values']['ppe']==capex['value'],'Cash capex contradicts earliest Company Facts')
        previous=early[-1]['evidence']['cfo']['operands'][0] if early else None
        early.append({'id':f'FY2021-Q{quarter}','start':f'2021-{(quarter-1)*3+1:02d}-01','end':end,
            'values':{'cfo':op['value']-(previous['value'] if previous else 0),
                'cash_capex':capex['value']-(early[-1]['capex_ytd'] if early else 0)},
            'capex_ytd':capex['value'],'evidence':{'cfo':{'operands':[op]+([previous] if previous else []),
                'method':'reported' if quarter==1 else 'successive YTD differences'}}})
    quarters = []
    for q in early+history['rows']:
        operands = [cumulative(o) for o in q['evidence']['cfo']['operands']]
        if len(operands)==1:
            row = {**operands[0],'id':q['id'],'label':q['id'].replace('-',' '),'operand_ids':[operands[0]['id']]}
        else:
            row = combine(operands,[1,-1],id=q['id'],label=q['id'].replace('-',' '),start=q['start'],end=q['end'],
                method=q['evidence']['cfo']['method'],operand_ids=[r['id'] for r in operands])
        require(row['values']['cfo']==q['values']['cfo'] and -row['values']['ppe']==q['values']['cash_capex'], 'Quarter contradicts existing reporting')
        require(not quarters or str(date.fromisoformat(quarters[-1]['end'])+timedelta(days=1))==row['start'],'Nonconsecutive cash quarters')
        quarters.append(row)
    for year_row in annual:
        selected=[q for q in quarters if q['id'].split('-')[0]==year_row['id']]
        require(len(selected)==4,'Incomplete annual cash-allocation cohort')
        for k in FIELDS:
            require(sum(amount(q,k) for q in selected)==amount(year_row,k),'Annual quarter tie failed: '+year_row['id']+' '+k)
    ttm = [combine(quarters[i-3:i+1],[1]*4,id=quarters[i]['id'],label='TTM · '+quarters[i]['label'],
        start=quarters[i-3]['start'],end=quarters[i]['end'],method='sum of four standalone quarters',
        operand_ids=[q['id'] for q in quarters[i-3:i+1]]) for i in range(3,len(quarters))]
    # Independent annual balance selection: latest annual filing's two comparatives.
    latest = annual_ops[-1]['annual']; ins=instance(latest);ppe=[]
    for year in [annual_ops[-1]['fiscal_year']-1,annual_ops[-1]['fiscal_year']]:
        instant=str(year)+'-12-31'
        facts={k:ins.fact(PPE_GROSS,instant=instant,dimensions=[(PPE_AXIS,member)]) for k,member in PPE_MEMBERS.items()}
        facts['depreciation']=ins.fact(PPE_DEP,instant=instant)
        facts['net']=ins.fact(PPE_NET,instant=instant)
        # The approximate 60% disclosure is explicitly reviewed in the 2025 note.
        require(latest['end']=='2025-12-31', 'Review the infrastructure composition note before updating this policy')
        vals={k:f['value'] for k,f in facts.items()}
        require(vals['technical']+vals['office']+vals['other']==vals['service'], 'PP&E categories do not reconcile')
        require(vals['service']+vals['pending']-vals['depreciation']==vals['net'], 'Net PP&E does not reconcile')
        ppe.append({'year':str(year),'date':instant,'values':vals,'evidence':facts,'servers_network_share_approx':0.60,
            'composition_basis':'Approximate share of technical infrastructure, disclosed for both dates in the 2025 PP&E note; not a cash-capex split.'})
    sources = {a:{'source_url':ins.url,'filed':ins.filed,'sha256':ins.hash} for a,ins in sorted(instances.items())}
    return {'schema_version':1,'policy':POLICY,'ticker':'GOOGL','as_of':history['as_of'],'currency':'USD',
        'extension_manifest_sha256':sha(extra_bytes),'company_facts_sha256':sha(facts_bytes),'history_snapshot_sha256':sha(history_bytes),'history_source_snapshot_sha256':history['source_snapshot_sha256'],
        'basis':'Accepted first-disclosure annual/YTD cohort; standalone quarters by subtraction; TTM sums four complete quarters.',
        'annual':annual,'quarterly':quarters,'ttm':ttm,'reported_periods':periods,'ppe':ppe,'sources':sources,
        'validation':{'annual_periods':len(annual),'quarterly_periods':len(quarters),'ttm_periods':len(ttm),
            'reported_periods':len(periods),'filings':len(sources),'ppe_balances':len(ppe)},
        'limitations':['Alphabet only; other issuers require separately reviewed mappings.',
            'Absent financing captions remain null, not reported zeros. Component completeness is gated by exact subtotal reconciliation.',
            'Cash balances include the cash-flow statement restricted-cash scope; they are not excess-cash estimates.',
            'Net pooled funding does not attribute a particular use to a particular source. FX is outside the allocation pool.',
            'PP&E dates are independent year-end balances, not quarterly/TTM spending categories. No cash capex breakdown is inferred.',
            'Existing DCF inputs, model dates and financial definitions are unchanged.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch-missing',action='store_true',help='Retain the specifically approved 2021 source filings')
    parser.add_argument('--check',action='store_true',help='Reproduce in memory and compare with committed package')
    args=parser.parse_args()
    if args.fetch_missing:retain_extension_sources()
    package=prepare(); output=ROOT/'frontend/public/cash-allocation/GOOGL.json'
    content=json.dumps(package,indent=2,sort_keys=True)+'\n'
    if args.check:
        require(output.read_text()==content,'Cash-allocation package is not reproducible')
    else:
        output.parent.mkdir(parents=True,exist_ok=True);output.write_text(content)
    print(json.dumps(package['validation']))

if __name__=='__main__':
    main()
