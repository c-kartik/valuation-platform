"""Apple/Meta available-data packages in the existing detachable feature.

All SEC financials are consumed read-only. Apple product quarters reuse the
approved revenue-mix package, including its derived-quarter policy. Hardware
peers retain their own fiscal periods; no artificial calendar alignment.
"""
import copy
import hashlib
import json
from datetime import date
from prepare import BASE, ROOT, write, load, pick, FLOW
from review_businesses import MAPPINGS
from export_browser import build as alphabet_package, quarter_instance, segment_growth

AS_OF = '2026-11-11'
ORDERS = {'AAPL':['AAPL','DELL','HPQ','MSFT','GOOGL','AMZN','NFLX'],
          'META':['META','GOOGL','SNAP','PINS','RDDT','TTD','AMZN']}
NAMES = {'AAPL':'Apple','DELL':'Dell Technologies','HPQ':'HP','NFLX':'Netflix','SNAP':'Snap'}
NOTES = {
    'AAPL':'September fiscal year end. Product revenue is disclosed, but Mac/iPhone/Services operating profit is not. Quarterly product observations reuse the existing derived-quarter reporting package.',
    'DELL':'Client Solutions is a computer-hardware reference for Mac, not iPhone. Infrastructure/AI servers materially affect the consolidated company. Segment profit is a management measure, not consolidated GAAP EBIT.',
    'HPQ':'Personal Systems is the computer-hardware reference; the consolidated company also includes Printing. Fiscal reporting dates differ from Apple. Segment profit excludes corporate/reconciling items.',
    'NFLX':'Consumer-subscription context only: consolidated revenue includes advertising. Content investment is economically important and is not captured by cash PP&E capex alone.',
    'SNAP':'Direct social-advertising reference, with different scale and profitability. Advertising revenue excludes other revenue. Negative TTM EBIT is preserved; EV/EBIT would be not meaningful when EBIT is nonpositive.',
}

def quarter_pair(d):
    quarters=[r for r in d['quarters'] if 'metrics' in r]
    current=quarters[-1]
    prior=[r for r in quarters if r['quarter']==current['quarter'] and
           350 <= (date.fromisoformat(current['end'])-date.fromisoformat(r['end'])).days <= 378]
    if len(prior)!=1: raise ValueError('Ambiguous comparative fiscal quarter')
    return current,prior[0]

def peer(ticker, common):
    d=json.loads((BASE/'prepared'/f'{ticker}.json').read_text())
    if d['validation']['errors'] or d['validation']['mismatches']: raise ValueError(ticker+': failed validation')
    current,prior=quarter_pair(d)
    if ticker in common:
        result=copy.deepcopy(common[ticker])
    else:
        result={'name':NAMES[ticker], 'role':'Contextual peer', 'note':NOTES[ticker],
            'ttm':{k:d['ttm'][k]['value'] for k in ['revenue','ebit','cfo','cash_capex','sbc']},
            'revenue_operands':d['ttm']['revenue']['operands'],
            'balances':{k:d['balance_sheet_candidates'][k]['value'] for k in ['cash','short_term_investments','long_term_debt_current','long_term_debt_noncurrent','convertible_debt_noncurrent']},
            'financials_url':d['ttm']['revenue']['operands'][-1]['source_url']}
    result.update({'ttm_end':d['latest_period_end'],'quarter_start':current['start'],'quarter_end':current['end'],
        'quarter_growth':current['metrics']['revenue']['value']/prior['metrics']['revenue']['value']-1,
        'quarter_revenue':current['metrics']['revenue']['value'],
        'quarter_growth_basis':'Prepared fiscal quarter versus prior-year fiscal quarter; revision vintages can differ.'})
    return result

def comparative(instance, mapping, current_start, current_end, prior_start, prior_end):
    concept,dimensions=mapping
    operands=[]
    for start,end in [(prior_start,prior_end),(current_start,current_end)]:
        found=[f for f in instance.facts if f.concept==concept and '/us-gaap/' in f.namespace and not f.is_nil
            and f.numeric_value is not None and str(f.start)==start and str(f.end)==end
            and f.unit and not f.unit.is_divided and [m.local_name for m in f.unit.numerator_measures]==['USD']
            and {d.dimension.local_name:d.explicit_member.local_name if d.explicit_member else d.typed_member_xml for d in f.dimensions}==dimensions]
        values={int(f.numeric_value) for f in found}
        if len(values)!=1: raise ValueError(f'Missing/conflicting comparative {mapping} {start}/{end}')
        operands.append({'value':values.pop(),'start':start,'end':end,'concept':concept,'dimensions':dimensions,
                         'contexts':sorted({f.context_id for f in found}),'source_url':instance.source_url})
    prior,current=operands
    return {'prior':prior['value'],'current':current['value'],'growth':current['value']/prior['value']-1 if prior['value'] else None,
        'operands':operands,'current_start':current_start,'current_end':current_end,'prior_end':prior_end,
        'basis':'Same-filing comparative fiscal quarters; nominal USD'}

def card(name,scope,key,income=None,target=False):
    return {'name':name,'scope':scope,'growth_key':key,'income':income,'target':target}

def table(title,columns,rows,note=''):
    return {'title':title,'columns':[{'label':label,'format':fmt} for label,fmt in columns], 'rows':rows,'note':note}

def build(target):
    original=alphabet_package()
    peers={t:peer(t,original['peers']) for t in ORDERS[target]}
    peers[target]['role']='Target company'
    if target=='META':
        roles={'GOOGL':'Primary advertising reference','SNAP':'Social advertising peer','PINS':'Secondary advertising peer',
               'RDDT':'Secondary advertising peer','TTD':'Advertising technology reference','AMZN':'Commerce advertising benchmark'}
    else:
        roles={'DELL':'Computer hardware reference','HPQ':'Computer hardware reference','MSFT':'Enterprise ecosystem benchmark',
               'GOOGL':'Platform ecosystem benchmark','AMZN':'Subscription ecosystem benchmark','NFLX':'Consumer subscription reference'}
    for t,role in roles.items(): peers[t]['role']=role
    growth=copy.deepcopy(original['growth'])
    for key,g in growth.items():
        g.update({'current_start':'2026-07-01','current_end':'2026-09-30','prior_end':'2025-09-30',
                  'basis':'Same-filing comparative quarters; nominal USD'})
    provenance={}
    g=original['businesses']['GOOGL'];m=original['businesses']['META']
    if target=='META':
        snap=quarter_instance('SNAP','2026-09-30')
        growth['SNAP_advertising']=segment_growth(snap,MAPPINGS['SNAP']['advertising'])
        growth['SNAP_advertising'].update({'current_start':'2026-07-01','current_end':'2026-09-30','prior_end':'2025-09-30','basis':'Same-filing comparative quarter; nominal USD'})
        for ticker,field in [('META','family_of_apps'),('GOOGL','services')]:
            growth[f'{ticker}_{field}']=segment_growth(quarter_instance(ticker,'2026-09-30'),MAPPINGS[ticker][field])
            growth[f'{ticker}_{field}'].update({'current_start':'2026-07-01','current_end':'2026-09-30','prior_end':'2025-09-30','basis':'Same-filing comparative quarter; nominal USD'})
        groups=[{'title':'Meta Ads vs Google, Snap, Reddit & Pinterest','eyebrow':'Digital advertising','note':'Advertising revenue is compared directly where disclosed. Pinterest remains a total-company proxy. No advertising-only EBIT is inferred.',
            'cards':[card('Meta Ads','Family of Apps advertising','META_advertising',target=True),card('Google Ads','Search + YouTube ads + Network','GOOGL_advertising'),
                     card('Snap Ads','Advertising revenue; excludes other revenue','SNAP_advertising'),card('Reddit Ads','Advertising revenue; excludes other revenue','RDDT_advertising'),card('Pinterest','Total-company revenue proxy','PINS_total')]},
            {'title':'Family of Apps vs Google Services','eyebrow':'Reported platform profitability','note':'Management reporting units include more than advertising. Google Services includes subscriptions/devices. Cost allocations differ; these are not standalone market valuations.',
             'cards':[card('Meta Family of Apps','Reported management segment','META_family_of_apps',m['family_of_apps_ebit'],True),card('Google Services','Ads + subscriptions + platforms + devices','GOOGL_services',g['services_ebit'])]}]
        tables=[table('Meta operating segments',[('Reported unit','text'),('Revenue, $B','bn'),('Operating income, $B','bn')],
                      [['Family of Apps',m['family_of_apps'],m['family_of_apps_ebit']],['Reality Labs',m['reality_labs'],m['reality_labs_ebit']],['Consolidated Meta',m['family_of_apps']+m['reality_labs'],m['family_of_apps_ebit']+m['reality_labs_ebit']]],
                      'Family of Apps + Reality Labs reconcile exactly to consolidated revenue and operating income. Reality Labs losses remain in consolidated EBIT; no hardware/metaverse peer multiple is invented.')]
        growth_rows=[('Meta advertising','META_advertising'),('Meta Family of Apps','META_family_of_apps'),('Google advertising','GOOGL_advertising'),('Snap advertising','SNAP_advertising'),('Reddit advertising','RDDT_advertising'),('Pinterest company proxy','PINS_total')]
        limitations=['Meta consolidated EBIT retains Reality Labs losses; Family of Apps is not advertising-only profit.',
            'Pinterest uses a labelled total-company revenue proxy. Trade Desk net revenue differs from advertiser spend.',
            'Negative peer EBIT is preserved; it cannot support a meaningful EV/EBIT denominator.',
            'Nominal USD growth uses same-filing comparable periods for business cards.',
            'Market inputs, EV/share classification, comparable EBITDA and exit defaults remain unselected.']
    else:
        mix_path=ROOT/'frontend/public/revenue-mix-expanded/AAPL.json'
        mix=json.loads(mix_path.read_text());current=mix['rows'][-1]
        prior=next(r for r in mix['rows'] if r['fiscal_year']==current['fiscal_year']-1 and r['quarter']==current['quarter'])
        if sum(current['values'].values()) != current['total'] or sum(prior['values'].values()) != prior['total']:
            raise ValueError('Apple product totals do not reconcile')
        for name in ['iphone','mac','ipad','wearables','services']:
            value,previous=current['values'][name],prior['values'][name]
            growth['AAPL_'+name]={'current':value,'prior':previous,'growth':value/previous-1,
                'current_start':current['start'],'current_end':current['end'],'prior_end':prior['end'],
                'basis':'Existing approved revenue-mix fiscal-quarter derivation; annual less nine months for Q4; revision vintages can differ.',
                'operands':current['evidence'][name]['operands']+prior['evidence'][name]['operands']}
        provenance['shared_apple_revenue_mix_sha256']=hashlib.sha256(mix_path.read_bytes()).hexdigest()
        incomes={}
        for ticker,field,profit_field in [('DELL','client_solutions','client_solutions_ebit'),('HPQ','personal_systems','personal_systems_ebit')]:
            d=json.loads((BASE/'prepared'/f'{ticker}.json').read_text());cur,prev=quarter_pair(d)
            instance=quarter_instance(ticker,cur['end'])
            growth[ticker+'_'+field]=comparative(instance,MAPPINGS[ticker][field],cur['start'],cur['end'],prev['start'],prev['end'])
            review=json.loads((BASE/'business-review'/f'{ticker}.json').read_text())
            period=next(r for r in review['periods'] if r['start']==cur['start'] and r['end']==cur['end'])
            incomes[ticker]=period['fields'][profit_field]['value']
        growth['GOOGL_subscriptions_platforms_devices']=segment_growth(quarter_instance('GOOGL','2026-09-30'),MAPPINGS['GOOGL']['subscriptions_platforms_devices'])
        for ticker,field in [('MSFT','m365'),('AMZN','subscriptions')]:
            growth[ticker+'_'+field]=segment_growth(quarter_instance(ticker,'2026-09-30'),MAPPINGS[ticker][field])
        for key in ['GOOGL_subscriptions_platforms_devices','MSFT_m365','AMZN_subscriptions']:
            growth[key].update({'current_start':'2026-07-01','current_end':'2026-09-30','prior_end':'2025-09-30','basis':'Same-filing product/category comparative; nominal USD'})
        nflx=json.loads((BASE/'prepared/NFLX.json').read_text());cur,prev=quarter_pair(nflx)
        facts=load(BASE/'sources/NFLX-companyfacts.json.gz');acc=nflx['ttm']['revenue']['operands'][1]['accession']
        ops=[pick(facts,FLOW['revenue'],AS_OF,r['start'],r['end'],acc) for r in [prev,cur]]
        if any(o['value'] is None for o in ops):raise ValueError('Missing Netflix comparative')
        growth['NFLX_total']={'current':ops[1]['value'],'prior':ops[0]['value'],'growth':ops[1]['value']/ops[0]['value']-1,
            'current_start':cur['start'],'current_end':cur['end'],'prior_end':prev['end'],'basis':'Same-filing consolidated comparative; subscription + advertising proxy','operands':ops}
        groups=[{'title':'Mac vs Dell Client Solutions & HP Personal Systems','eyebrow':'Computer hardware','note':'Different fiscal quarters: Apple ends in September; Dell/HP latest available quarters end in July. Compare each issuer’s own YoY growth; these are not the same calendar quarter. Dell/HP segments include broader hardware/services than Mac; their management segment profit excludes separate corporate/reconciling items.',
             'cards':[card('Apple Mac','Mac product revenue; no product operating profit','AAPL_mac',target=True),card('Dell Client Solutions','PC/client hardware and related services','DELL_client_solutions',incomes['DELL']),card('HP Personal Systems','PC/computing segment','HPQ_personal_systems',incomes['HPQ'])]},
            {'title':'Apple Services vs ecosystem & subscription references','eyebrow':'Services & ecosystem','note':'Contextual revenue comparisons, not interchangeable businesses: Apple bundles multiple services; Google includes platforms/devices; Microsoft includes enterprise software; Netflix includes advertising. No standalone services operating profit is inferred.',
             'cards':[card('Apple Services','Reported Services category','AAPL_services',target=True),card('Google ecosystem','Subscriptions + platforms + devices','GOOGL_subscriptions_platforms_devices'),card('Microsoft 365 cloud','Enterprise and consumer cloud products','MSFT_m365'),card('Amazon subscriptions','Prime and other subscription services','AMZN_subscriptions'),card('Netflix','Total-company subscription + ad revenue proxy','NFLX_total',cur['metrics']['ebit']['value'])]}]
        tables=[table('Apple revenue mix reconciliation',[('Reported product/category','text'),('Quarter revenue, $B','bn')],
            [[label,current['values'][key]] for label,key in [('iPhone','iphone'),('Mac','mac'),('iPad','ipad'),('Wearables, Home & Accessories','wearables'),('Services','services')]]+[['Total Apple',current['total']]],
            f"Quarter ended {current['end']}. Components reconcile exactly to the existing shared financial package. iPhone has no clean separately traded US handset peer here; Dell/HP are Mac references, not iPhone substitutes. Samsung is not forced into this US-GAAP dataset."),
            table('Hardware segment reporting boundaries',[('Business','text'),('Quarter end','text'),('Revenue, $B','bn'),('Segment operating income, $B','bn')],
                [['Apple Mac',current['end'],current['values']['mac'],None],['Dell Client Solutions','2026-07-31',growth['DELL_client_solutions']['current'],incomes['DELL']],['HP Personal Systems','2026-07-31',growth['HPQ_personal_systems']['current'],incomes['HPQ']]],
                'Dell/HP management segment profit differs from consolidated GAAP EBIT and excludes separate reconciling items. Apple does not disclose Mac-only operating profit.')]
        growth_rows=[('iPhone','AAPL_iphone'),('Mac','AAPL_mac'),('iPad','AAPL_ipad'),('Wearables, Home & Accessories','AAPL_wearables'),('Services','AAPL_services')]
        limitations=['Apple product quarters reuse the existing revenue-mix derivation; Q4 is annual less nine months, not an invented standalone filing fact.',
            'Dell/HP periods end in July; Apple ends in September. Per-issuer fiscal dates and TTM ends are shown.',
            'Mac is compared with PC segments; no iPhone profit or pure US handset comparable is invented.',
            'Services benchmarks have different business mixes; Google/Netflix observations are explicitly broader proxies.',
            'Netflix cash PP&E capex excludes content investment; raw capex ratios are not complete reinvestment comparisons.',
            'EV/EBITDA, market inputs, share classifications and exit defaults remain unselected.']
    for t in peers:
        if t not in NAMES and t not in original['peers']:raise ValueError('Unknown peer')
    filing_checks=sum(json.loads((BASE/'prepared'/f'{t}.json').read_text())['validation']['matches'] for t in peers)
    business_checks=sum(json.loads((BASE/'business-review'/f'{t}.json').read_text())['matches'] for t in peers)
    used={c['growth_key'] for group in groups for c in group['cards']}|{key for _,key in growth_rows}
    for key in list(used):used.update(growth[key].get('components',[]))
    growth={key:value for key,value in growth.items() if key in used}
    return {'schema_version':1,'target':target,'as_of':AS_OF,'quarter_start':peers[target]['quarter_start'],
        'quarter_end':peers[target]['quarter_end'],'currency':'USD','peers':peers,'peer_order':ORDERS[target],
        'businesses':{},'growth':growth,'validation':{'selected_filing_checks':filing_checks,'business_reconciliations':business_checks},
        'limitations':limitations,'market':{'valuation_date':None,'prices':None,'multiples':None,'exit_default':None},
        'presentation':{'groups':groups,'growth_table_title':'Apple product revenue & growth' if target=='AAPL' else 'Advertising & platform revenue growth',
            'growth_rows':[{'label':name,'growth_key':key} for name,key in growth_rows], 'business_tables':tables},
        'provenance':provenance}

if __name__=='__main__':
    for target in ORDERS:
        data=build(target)
        write(ROOT/'frontend/public/features/trading-comparables'/f'{target}.json',data)
        print(json.dumps({'target':target,'peers':len(data['peers']),'growth_comparisons':len(data['growth']), 'checks':data['validation']}))
