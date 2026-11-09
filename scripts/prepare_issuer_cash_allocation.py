"""Apple/Meta reporting-only cash allocation and issuer-specific PP&E.

No existing SEC/DCF pipeline or accepted quarterly package is changed. Retain
missing earliest-disclosure FY2021 sources explicitly; reproduce offline thereafter.
"""
import argparse
from datetime import date, datetime, timedelta, timezone
import gzip
import json
import os
from html.parser import HTMLParser
from pathlib import Path
from prepare_cash_allocation import Instance, FIELDS as ALPHABET_FIELDS, CASH, ROOT, sha, require

CIKS={'AAPL':320193,'META':1326801}
EXTRA={
 'marketableMaturities':('ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities',1),
 'commercialPaper':('ProceedsFromRepaymentsOfCommercialPaper',1),
 'financeLeasePayments':('FinanceLeasePrincipalPayments',-1),
 'bankOverdrafts':('ProceedsFromRepaymentsOfBankOverdrafts',1),
 'ppeSales':('ProceedsFromSaleOfPropertyPlantAndEquipment',1),
 'heldForSalePurchases':('meta:PaymentsForHeldForSaleAssets',-1),
 'ventureDistributions':(('meta:ProceedsFromOneTimeVentureDistribution','EquityMethodInvestmentDividendsOrDistributions'),1),
}
INVESTING=('ppe','marketablePurchases','marketableSales','marketableMaturities','otherPurchases','otherSales','acquisitions','otherInvesting','heldForSalePurchases','ventureDistributions','ppeSales')
FINANCING=('awards','buybacks','dividends','debtProceeds','debtRepayments','minority','commonIssued','preferredIssued','otherFinancing','commercialPaper','financeLeasePayments','bankOverdrafts')
REQUIRED={'cfo','ppe','marketablePurchases','marketableSales','otherInvesting','investing','awards','buybacks','financing','change'}
PPE_CATEGORIES={
 'AAPL':[('landBuildings','Land and buildings','us-gaap:LandAndBuildingMember'),('machinery','Machinery, equipment & internal-use software','aapl:MachineryEquipmentAndInternalUseSoftwareMember'),('leasehold','Leasehold improvements','us-gaap:LeaseholdImprovementsMember')],
 'META':[('land','Land','us-gaap:LandMember'),('servers','Servers and network assets','meta:ServersAndNetworkAssetsComponentsStoredBySuppliersMember'),('buildings','Buildings','us-gaap:BuildingMember'),('leasehold','Leasehold improvements','us-gaap:LeaseholdImprovementsMember'),('equipment','Equipment and other','meta:EquipmentAndOtherMember'),('financeLeases','Finance-lease right-of-use assets',None),('pending','Construction in progress','us-gaap:ConstructionInProgressMember')],
}


def mapping(ticker):
    result={**ALPHABET_FIELDS,**EXTRA}
    # Explicitly absent/unreported concepts use None, never a fabricated fact.
    for key in ['minority','commonIssued','preferredIssued','otherSales','commercialPaper','financeLeasePayments','heldForSalePurchases','ventureDistributions','bankOverdrafts','ppeSales']:
        result[key]=None
    result.update(awards=('PaymentsRelatedToTaxWithholdingForShareBasedCompensation',-1),
        acquisitions=('PaymentsToAcquireBusinessesNetOfCashAcquired',-1),
        debtProceeds=('ProceedsFromIssuanceOfLongTermDebt',1),debtRepayments=('RepaymentsOfLongTermDebt',-1),
        marketablePurchases=('PaymentsToAcquireAvailableForSaleSecuritiesDebt',-1),
        marketableSales=('ProceedsFromSaleOfAvailableForSaleSecuritiesDebt',1))
    if ticker=='AAPL':
        result['commercialPaper']=EXTRA['commercialPaper'];result['commonIssued']=('ProceedsFromIssuanceOfCommonStock',1)
        result['otherPurchases']=ALPHABET_FIELDS['otherPurchases'];result['otherSales']=ALPHABET_FIELDS['otherSales']
    else:
        result.update(marketablePurchases=(('PaymentsToAcquireMarketableSecurities','PaymentsToAcquireAvailableForSaleSecuritiesDebt'),-1),
            marketableSales=(('ProceedsFromSaleAndMaturityOfMarketableSecurities','ProceedsFromSaleAndMaturityOfAvailableForSaleSecurities','ProceedsFromSaleOfAvailableForSaleSecuritiesDebt'),1),
            otherPurchases=('meta:PaymentsForEquitySecuritiesWithoutReadilyDeterminableFairValue',-1),
            acquisitions=(('meta:PaymentsToAcquireBusinessesNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets','meta:PaymentsToAcquireBusinessesAndIntangibleAssets'),-1),
            ppeSales=EXTRA['ppeSales'],bankOverdrafts=EXTRA['bankOverdrafts'],financeLeasePayments=EXTRA['financeLeasePayments'],heldForSalePurchases=EXTRA['heldForSalePurchases'],ventureDistributions=EXTRA['ventureDistributions'])
    return result


def amount(row,key):
    return row['values'][key] if row['values'][key] is not None else 0


def reconcile(row):
    for group,subtotal in [(INVESTING,'investing'),(FINANCING,'financing')]:
        got=sum(amount(row,k) for k in group)
        require(got==row['values'][subtotal],f"{row['id']} {subtotal} components {got} != {row['values'][subtotal]}")
    require(sum(amount(row,k) for k in ['cfo','investing','financing','fx'])==row['values']['change'],'Cash movement mismatch')
    require(row['values']['opening']+row['values']['change']==row['values']['closing'],'Closing cash mismatch')


def combine(rows,coefficients,**metadata):
    values={};evidence={}
    for key in mapping('AAPL'):
        present=[(r['values'][key],c) for r,c in zip(rows,coefficients) if r['values'][key] is not None]
        values[key]=sum(v*c for v,c in present) if present else None
        evidence[key]={'method':metadata['method'],'terms':[{'coefficient':c,'period_id':r['id']} for r,c in zip(rows,coefficients)]}
    positive=all(c==1 for c in coefficients)
    values['opening']=rows[0]['values']['opening'] if positive else rows[1]['values']['closing']
    values['closing']=rows[-1]['values']['closing'] if positive else rows[0]['values']['closing']
    result={**metadata,'values':values,'evidence':evidence};reconcile(result);return result


class CashStatementTables(HTMLParser):
    """Identify the actual cash-flow table, excluding tagged note-only values."""
    def __init__(self):
        super().__init__();self.stack=[];self.candidates=[]
    def handle_starttag(self,tag,attrs):
        if tag=='table':self.stack.append(set())
        if tag=='ix:nonfraction':
            name=dict(attrs).get('name','')
            for table in self.stack:table.add(name)
    def handle_endtag(self,tag):
        if tag=='table' and self.stack:
            concepts=self.stack.pop()
            if all(any(c.endswith(':'+subtotal) for c in concepts) for subtotal in ['NetCashProvidedByUsedInOperatingActivities','NetCashProvidedByUsedInInvestingActivities','NetCashProvidedByUsedInFinancingActivities']):self.candidates.append(concepts)
    def selected(self):
        require(bool(self.candidates),'No identifiable consolidated cash-flow table')
        size=min(map(len,self.candidates));smallest=[c for c in self.candidates if len(c)==size]
        require(all(c==smallest[0] for c in smallest),'Ambiguous consolidated cash-flow tables')
        return smallest[0]


class Sources:
    def __init__(self,ticker,root,fetch_missing):
        self.ticker,self.root,self.fetch_missing=ticker,root,fetch_missing
        self.original=json.loads((root/f'data/reporting-audit/{ticker}-sources.json').read_text())['files']
        self.path=root/f'data/cash-allocation/{ticker}-sources.json'
        self.extension=json.loads(self.path.read_text()) if self.path.exists() else {'ticker':ticker,'files':{}}
        self.filings={};self.statements={}
        for url,entry in self.original.items():
            if 'submissions/' not in url:continue
            raw=self.read(url);payload=json.loads(raw);columns=payload.get('filings',{}).get('recent',payload)
            if 'accessionNumber' in columns:
                for i,acc in enumerate(columns['accessionNumber']):
                    self.filings[acc]={k:columns[k][i] for k in ['form','filingDate','reportDate','primaryDocument']}

    def read(self,url):
        original=url in self.original;entry=self.original.get(url) or self.extension['files'].get(url)
        directory=self.root/f"data/{'reporting-audit' if original else 'cash-allocation'}/sources/{self.ticker}"
        if entry:
            raw=gzip.decompress((directory/entry['file']).read_bytes());require(sha(raw)==entry['sha256'],'Retained source hash mismatch');return raw
        require(self.fetch_missing,'Missing retained source: '+url)
        require(bool(os.environ.get('SEC_USER_AGENT')),'Set identifying SEC_USER_AGENT')
        from valuation_platform.sec.client import SECClient
        print('Retaining '+self.ticker+' '+url,flush=True)
        raw=SECClient(os.environ['SEC_USER_AGENT'],timeout=45).get_bytes(url)
        directory.mkdir(parents=True,exist_ok=True);name=sha(url.encode())+'.gz'
        (directory/name).write_bytes(gzip.compress(raw,mtime=0));self.extension['files'][url]={'file':name,'sha256':sha(raw)}
        self.save()
        return raw

    def get_bytes(self,url):return self.read(url)
    def get_json(self,url):return json.loads(self.read(url))

    def instance(self,operand):
        acc=operand['accession'];entries={**self.original,**self.extension['files']}
        urls=[u for u in entries if '/'+acc.replace('-','')+'/' in u and u.endswith('.xml')]
        if not urls:
            require(self.fetch_missing,'Missing retained instance '+acc)
            from valuation_platform.sec.filing_xbrl import discover_extracted_xbrl
            from valuation_platform.sec.submissions import SECFiling
            from valuation_platform.sec.tickers import SECCompanyIdentity
            require(acc in self.filings,'Missing submission metadata '+acc);f=self.filings[acc]
            filing=SECFiling(acc,f['form'],date.fromisoformat(f['filingDate']),date.fromisoformat(f['reportDate']),f['primaryDocument'])
            company=SECCompanyIdentity(self.ticker,CIKS[self.ticker],f'{CIKS[self.ticker]:010d}',self.ticker,'SEC',datetime.now(timezone.utc))
            url=discover_extracted_xbrl(self,company,filing).source_url;raw=self.read(url)
        else:
            require(len(urls)==1,'Ambiguous retained instance');url=urls[0];raw=self.read(url)
        return Instance(raw,url,operand['filed'],CIKS[self.ticker])

    def statement(self,operand):
        acc=operand['accession']
        if acc not in self.statements:
            require(acc in self.filings,'Missing primary-document metadata')
            url=f"https://www.sec.gov/Archives/edgar/data/{CIKS[self.ticker]}/{acc.replace('-','')}/{self.filings[acc]['primaryDocument']}"
            raw=self.read(url);parser=CashStatementTables();parser.feed(raw.decode('utf-8'))
            self.statements[acc]={'source_url':url,'sha256':sha(raw),'concepts':sorted(parser.selected())}
        return self.statements[acc]

    def save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps(self.extension,indent=2,sort_keys=True)+'\n')


def prepare(ticker,root=ROOT,fetch_missing=False):
    require(ticker in CIKS,'Unsupported issuer')
    history_bytes=(root/f'frontend/public/research-data/{ticker}.json').read_bytes();history=json.loads(history_bytes)
    fact_bytes=(root/f'data/quarterly-reporting/sources/{ticker}.json.gz').read_bytes();facts=json.loads(gzip.decompress(fact_bytes))['facts']['us-gaap']
    sources=Sources(ticker,root,fetch_missing);instances={};reported={};fields=mapping(ticker)
    def cumulative(op):
        key=op['accession']+':'+op['start']+':'+op['end']
        if key not in reported:
            require(op['filed']<=history['as_of'],'Source after review cutoff')
            if op['accession'] not in instances:instances[op['accession']]=sources.instance(op)
            ins=instances[op['accession']];evidence={};excluded={}
            statement=sources.statement(op)
            for k,rule in fields.items():
                if rule:
                    candidates=(rule[0],) if isinstance(rule[0],str) else rule[0]
                    resolved=[]
                    for concept in candidates:
                        if concept.startswith('meta:'):
                            prefix='meta' if 'meta' in ins.ns else 'fb'
                            require(ins.ns.get(prefix,'').startswith('http://www.facebook.com/'),'Wrong Meta taxonomy namespace')
                            concept=prefix+':'+concept.split(':')[1]
                        resolved.append(concept)
                    displayed=[c for c in resolved if (c if ':' in c else 'us-gaap:'+c) in statement['concepts']]
                    rule=(tuple(displayed or resolved),rule[1])
                fact=ins.fact(rule[0],start=op['start'],end=op['end'],sign=rule[1],optional=k not in REQUIRED) if rule else None
                if fact:
                    tag=fact['concept'];prefix=next(prefix for prefix,uri in ins.ns.items() if tag.startswith('{'+uri+'}'))
                    if prefix+':'+tag.split('}')[-1] not in statement['concepts']:
                        require(k not in REQUIRED,'Required amount is absent from the actual cash-flow table')
                        excluded[k]={'fact':fact,'reason':'Tagged note-only amount; not a separate cash-flow statement component.'};fact=None
                evidence[k]=fact
            evidence['opening']=ins.fact(CASH,instant=str(date.fromisoformat(op['start'])-timedelta(days=1)))
            evidence['closing']=ins.fact(CASH,instant=op['end'])
            row={'id':key,'start':op['start'],'end':op['end'],'method':'reported','values':{k:e['value'] if e else None for k,e in evidence.items()},'evidence':evidence,'excluded_note_facts':excluded,'statement_source_url':statement['source_url']}
            require(row['values']['cfo']==op['value'],'CFO contradicts accepted cohort/Company Facts');reconcile(row);reported[key]=row
        return reported[key]
    annual_ops=sorted([a for a in history['validation']['annual_tie_outs'] if a['metric']=='cfo' and a['fiscal_year']>=2021],key=lambda a:a['fiscal_year'])
    require(annual_ops[0]['fiscal_year']==2021,'Missing full FY2021 annual cohort')
    annual=[{**cumulative(a['annual']),'id':f"FY{a['fiscal_year']}",'label':f"FY{a['fiscal_year']}",'operand_ids':[cumulative(a['annual'])['id']]} for a in annual_ops]
    quarters=[]
    for a in annual_ops:
        op=a['annual'];earliest={}
        for f in facts['NetCashProvidedByUsedInOperatingActivities']['units']['USD']:
            if f.get('start')==op['start'] and f['end']<op['end'] and f['form']=='10-Q' and f['filed']<=history['as_of']:
                if f['end'] not in earliest or (f['filed'],f['accn'])<(earliest[f['end']]['filed'],earliest[f['end']]['accn']):earliest[f['end']]=f
        require(len(earliest)==3,'Incomplete fiscal YTD history')
        previous=None
        for q,f in enumerate([earliest[e] for e in sorted(earliest)]+[None],1):
            o={'accession':f['accn'],'start':f['start'],'end':f['end'],'filed':f['filed'],'value':f['val']} if f else op
            current=cumulative(o);start=str(date.fromisoformat(previous['end'])+timedelta(days=1)) if previous else o['start'];id=f"FY{a['fiscal_year']}-Q{q}"
            require(69<=(date.fromisoformat(o['end'])-date.fromisoformat(start)).days<=109,'Wrong fiscal quarter duration')
            if previous:
                row=combine([current,previous],[1,-1],id=id,label=id.replace('-',' '),start=start,end=o['end'],method='annual less nine months' if q==4 else 'successive YTD differences',operand_ids=[current['id'],previous['id']])
            else:row={**current,'id':id,'label':id.replace('-',' '),'operand_ids':[current['id']]}
            quarters.append(row);previous=current
    # Current incomplete fiscal year follows the accepted existing reporting series.
    for h in history['rows']:
        if any(r['id']==h['id'] for r in quarters):continue
        ops=[cumulative(o) for o in h['evidence']['cfo']['operands']]
        row=combine(ops,[1,-1],id=h['id'],label=h['id'].replace('-',' '),start=h['start'],end=h['end'],method=h['evidence']['cfo']['method'],operand_ids=[o['id'] for o in ops]) if len(ops)==2 else {**ops[0],'id':h['id'],'label':h['id'].replace('-',' '),'operand_ids':[ops[0]['id']]}
        quarters.append(row)
    for i,q in enumerate(quarters):
        if i:require(str(date.fromisoformat(quarters[i-1]['end'])+timedelta(days=1))==q['start'],'Nonconsecutive quarters')
    for h in history['rows']:
        r=next(q for q in quarters if q['id']==h['id']);require(r['start']==h['start'] and r['end']==h['end'] and r['values']['cfo']==h['values']['cfo'] and -r['values']['ppe']==h['values']['cash_capex'],'Quarter contradicts existing reporting')
        require(r['operand_ids']==[o['accession']+':'+o['start']+':'+o['end'] for o in h['evidence']['cfo']['operands']],'Wrong accepted quarterly accession')
    for a in annual:
        qs=[q for q in quarters if q['id'].startswith(a['id']+'-')];require(len(qs)==4,'Incomplete annual cohort')
        for k in fields:require(sum(amount(q,k) for q in qs)==amount(a,k),'Annual component tie failed '+k)
    ttm=[combine(quarters[i-3:i+1],[1]*4,id=quarters[i]['id'],label='TTM · '+quarters[i]['label'],start=quarters[i-3]['start'],end=quarters[i]['end'],method='sum of four standalone quarters',operand_ids=[q['id'] for q in quarters[i-3:i+1]]) for i in range(3,len(quarters))]
    latest=annual_ops[-1];ins=instances[latest['annual']['accession']];ppe=[]
    for a in annual_ops[-2:]:
        instant=a['annual']['end'];ev={}
        for k,label,member in PPE_CATEGORIES[ticker]:
            concept='FinanceLeaseRightOfUseAssetBeforeAccumulatedAmortization' if member is None else 'PropertyPlantAndEquipmentGross'
            ev[k]=ins.fact(concept,instant=instant,dimensions=[('us-gaap:PropertyPlantAndEquipmentByTypeAxis',member)] if member else [])
        if ticker=='AAPL':gross='PropertyPlantAndEquipmentGross';dep='AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment';net='PropertyPlantAndEquipmentNet'
        else:
            gross='PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetBeforeAccumulatedDepreciationAndAmortization';dep='PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAccumulatedDepreciationAndAmortization';net='PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization'
        for k,c in [('gross',gross),('depreciation',dep),('net',net)]:ev[k]=ins.fact(c,instant=instant)
        values={k:f['value'] for k,f in ev.items()};require(sum(values[k] for k,_,_ in PPE_CATEGORIES[ticker])==values['gross'],'PP&E categories do not reconcile');require(values['gross']-values['depreciation']==values['net'],'Net PP&E does not reconcile')
        ppe.append({'year':str(a['fiscal_year']),'date':instant,'values':values,'evidence':ev,'servers_network_share_approx':None,'composition_basis':'Reported gross asset categories from the latest annual PP&E note; not a cash-capex split.'})
    if fetch_missing:sources.save()
    require(sources.path.exists(),'Missing retained source manifest')
    return {'schema_version':1,'policy':ticker.lower()+'-cash-allocation-v1','ticker':ticker,'as_of':history['as_of'],'currency':'USD',
        'extension_manifest_sha256':sha(sources.path.read_bytes()),'company_facts_sha256':sha(fact_bytes),'history_snapshot_sha256':sha(history_bytes),'history_source_snapshot_sha256':history['source_snapshot_sha256'],
        'basis':'Original first-disclosure fiscal cohorts; Q2/Q3 are YTD differences and Q4 is annual less nine months. TTM sums four standalone quarters.',
        'annual':annual,'quarterly':quarters,'ttm':ttm,'reported_periods':reported,'ppe':ppe,
        'ppe_categories':[{'id':k,'label':label} for k,label,_ in PPE_CATEGORIES[ticker]],
        'statement_evidence':sources.statements,
        'sources':{a:{'source_url':i.url,'filed':i.filed,'sha256':i.hash} for a,i in sorted(instances.items())},
        'validation':{'annual_periods':len(annual),'quarterly_periods':len(quarters),'ttm_periods':len(ttm),'reported_periods':len(reported),'filings':len(instances),'ppe_balances':len(ppe),'annual_component_ties':len(annual)*len(fields)},
        'limitations':['PP&E is a year-end balance view, not cash-capex attribution. No Alphabet-specific infrastructure share is assumed.',
            'Absent captions remain null. Component sums must reconcile without residual plugs.',
            'Finance-lease principal is a financing cash flow, separate from cash PP&E purchases.',
            'Existing Python/DCF inputs, financial methods and model dates remain unchanged.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--ticker',choices=CIKS,required=True);parser.add_argument('--fetch-missing',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    package=prepare(args.ticker,fetch_missing=args.fetch_missing);content=json.dumps(package,indent=2,sort_keys=True)+'\n';target=ROOT/f'frontend/public/cash-allocation/{args.ticker}.json'
    if args.check:require(target.read_text()==content,'Package does not reproduce')
    else:target.write_text(content)
    print(json.dumps(package['validation']))

if __name__=='__main__':main()
