"""Activate explicitly approved company reviews, not a generic policy.

Uses the existing package audit convention (ManualIdentity, relevant-content
revision, hash-linked immutable acceptance, separate current view). Reported
packages/proposals are preserved. No retrieval or valuation operations.
"""
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal as D
import json
from pathlib import Path
import re

from prepare_msft_analyst_package import ROOT, digest, relevant, ManualIdentity
from valuation_platform.analyst.analyst_overrides import _json

BASELINE='9bb110cb208ce3abcac0365c4ecf4820c498d60d'
TICKERS=('COST','CAT','KO','NVDA','AMZN','META')
LARGE_TICKERS=('AVGO','TSLA','LLY')
LARGE_BASELINE='4b5b93423fa84078dd6b19dcf68c52434ba9a6ac'
PRIORITY_TICKERS=('MU','AMD','JNJ')
NETWORK_TICKERS=('V','INTC','WMT')
PHARMA_TECH_TICKERS=('ABBV','MA','CSCO')
SEMICON_SOFTWARE_TICKERS=('LRCX','PLTR','AMAT')
ENERGY_PHARMA_STAPLES_TICKERS=('CVX','MRK','PG')
ENERGY_PHARMA_STAPLES_BASELINE='70d0feed195fcb605935c4849f3c371b7cbe9c34'
ENERGY_PHARMA_STAPLES_AUTHORITY='Current user explicitly approves all29 recommendations in docs/energy-pharma-staples-review-batch-results.md for exact CVX/MRK/PG frozen histories. CVX-PERIMETER remains OPEN: required EBIT null in all5 years, no substitute equation, zero or waiver. Approve CVX face Sales, depletion-inclusive DD&A, exact approved Capex, negative FY2023 SBC benefit and named financing/claims; MRK continuing panels, existing EBIT derivations, separate discontinued CFO and broader FY2021/22 investment proxies; PG exact Pretax extensions, face borrowing parents with unexplained component differences and retained ESOP preferred/pension overlaps. Preserve source unknowns, prior proposals and unbounded omission assumptions; no reported zeros, financial-sufficiency certification or Phase2 authority.'
SEMICON_SOFTWARE_BASELINE='7b06e5c88ac8d3763929680ce459eb837b742d1c'
SEMICON_SOFTWARE_AUTHORITY='Current user explicitly approves all27 recommendations in docs/semiconductor-software-review-batch-results.md for the exact frozen LRCX/PLTR/AMAT histories. LRCX limited D&A and broader combined PP&E/intangible investment proxy preserve pure-PP&E unknowns and separate plan claims/assets. PLTR face tax selections preserve rounded alternatives and original parser PARTIALs; zero named debt is not exhaustive zero financing. AMAT limited D&A/PP&E-software scope preserves incentive stocks, SBC expense660 versus add-back668 and finance-lease overlaps/missing subamounts. Approve the stated unbounded omission assumptions, not reported zeros, immateriality or Phase2 use.'
PHARMA_TECH_BASELINE='5332e07dca08e81ea499df8d4f41715e4cc0baf8'
PHARMA_TECH_AUTHORITY='Current user explicitly approves all28 recommendations in docs/pharma-network-tech-review-batch-results.md for exact ABBV/MA/CSCO frozen histories: limited ABBV/CSCO D&A proxies, MA face Net revenue and face D&A with exact curated Pretax, and CSCO FY2026 face financial components15918m with unresolved conflicting parent14297m/difference1621m. Preserve source unknowns, proposals, alternatives and all approved qualifications; no conflict clearance or Phase2 authority.'
NETWORK_BASELINE='5a0f606399893aa67b96f6660ef43a4fb4fdeafb'
NETWORK_AUTHORITY='Current user explicitly approves all28 recommendations in docs/network-retail-review-batch-results.md for V/INTC/WMT exact frozen histories, including curated Visa scope, exact Intel CFO SBC cost proxy and Walmart face Total revenues; preserve source unknowns and company-specific qualifications.'
PRIORITY_BASELINE='4234cb10e862c4bd95ccd017037f8db707263922'
PRIORITY_AUTHORITY='Current user explicitly approves all MU/AMD recommendations and JNJ original-as-filed historical selections in docs/priority-review-batch-results.md; JNJ continuing/consolidated scope mismatch remains an OPEN analyst-use requirement, not accepted completeness.'
JNJ_FLOW_FAMILIES=('revenue','ebit','depreciation_amortization','cash_capex','reported_cash_flow_working_capital_movements','deferred_taxes','stock_based_compensation','reported_cfo','reported_tax_context')
LARGE_AUTHORITY='Current user instruction explicitly approves all25 recommendations in docs/large-company-review-batch-results.md for the exact AVGO/TSLA/LLY frozen histories, preserving each company-specific qualification and source unknown.'
ADDITIONS=('history_approval','current_history')
AUTHORITY='Current user instruction explicitly approves all23 standard-review and all25 trillion-review recommendations; AMZN2021 expanded81427 including318; CAT separate industrial/Financial Products perimeters; KO held-sale alternative not selected.'
SCOPE='Accepted company-specific historical preparation only; no Phase2, complete debt/reinvestment or financial-sufficiency certification.'


def parent(package):return {k:v for k,v in package.items() if k not in ADDITIONS}


def cat_evidence(package):
    """Actual supplemental columns, with colspan-aware year bindings.

    Keep consolidating adjustments as reported, not as residuals calculated from
    industrial/Financial Products. Never use a prior-year or footnote column.
    """
    import prepare_standard_review_batch as s
    out=[];cache={}
    def cells(row):
        offset=0
        for i,c in enumerate(row):
            width=int(c['attrs'].get('colspan','1'));yield i,offset,width,c;offset+=width
    for period in package['periods']:
        source=next(v for v in period['sources'] if v['role']=='primary')
        doc=cache.setdefault(source['path'],_json((ROOT/source['path']).read_text()))
        a=doc['artifacts'][int(source['pointer'].split('/')[-1])]
        encoded=a['response_body_gzip_base64'];body=s.cash.gzip.decompress(s.cash.base64.b64decode(''.join(encoded) if isinstance(encoded,list) else encoded,validate=True))
        receipt=s.cash._receipt(dict(a,accession=period['identity']['accession']),body)
        if receipt.artifact.sha256!=source['sha256'] or receipt.artifact.url!=source['url']:raise ValueError('CAT supplemental source changed')
        record=dict(source,body=body,locator=source['pointer']);s.documents.verify_primary(record,period['identity'])
        tables=[];year=period['identity']['annual_end'][:4]
        for ti,table in enumerate(s.documents.parse(record,improved=True)):
            header=' '.join(c['text'] for r in table[:6] for c in r)
            if 'Supplemental Data for' not in header or 'ConsolidatingAdjustments' not in header or 'FinancialProducts' not in header:continue
            if not ('Results of Operations' in header or 'Financial Position' in header or 'Cash Flow' in header):continue
            years=[(ri,[(offset,width) for _,offset,width,c in cells(r) if c['text'].strip()==year]) for ri,r in enumerate(table[:7])]
            years=[(ri,coords) for ri,coords in years if len(coords)==4]
            if len(years)!=1:raise ValueError('Four exact current-year supplemental column groups required')
            yi,coords=years[0];rows=[]
            for ri,row in enumerate(table[yi+1:],yi+1):
                values={}
                for scope,(start,width) in zip(('consolidated','industrial','financial_products','eliminations'),coords):
                    numeric=[(ci,c) for ci,offset,_,c in cells(row) if start<=offset<start+width and re.fullmatch(r'\(?[\d,]+\)?|—|–|-',c['text'].strip())]
                    if not numeric:continue
                    if len(numeric)!=1:raise ValueError('Ambiguous supplemental monetary cell, not a selection by precedence')
                    ci,c=numeric[0];display=c['text'].strip()
                    values[scope]=dict(value=str(s.cfo.displayed(display,D(0))*1000000),unit='USD',precision='-6',origin='reported',
                        perimeter=scope,display=display,column=ci,grid_start=start,grid_width=width)
                if not values:continue
                if len(values)!=4:raise ValueError('Incomplete supplemental row, cannot manufacture a perimeter')
                rows.append(dict(caption=row[0]['text'].strip(),table=ti,row=ri,values=values,
                    source_url=source['url'],source_sha256=source['sha256'],source_reference=source['path']+'#'+source['pointer'],
                    consolidation_difference=str(sum((D(values[k]['value']) for k in ('industrial','financial_products','eliminations')),D(0))-D(values['consolidated']['value']))))
            kind='income' if 'Results of Operations' in header else 'balance' if 'Financial Position' in header else 'cash_flow'
            tables.append(dict(kind=kind,table=ti,header=header,current_year=year,rows=rows,
                scope='Reported supplemental consolidating columns with intercompany items, NOT standalone financial statements'))
        if {t['kind'] for t in tables}!={'income','balance','cash_flow'}:raise ValueError('CAT three supplemental statements required')
        out.append(dict(identity=period['identity'],source=source,tables=tables))
    return out


def approval(package,decisions,recorded_at_utc):
    p=parent(package);ticker=p['ticker']
    if ticker not in TICKERS+LARGE_TICKERS+PRIORITY_TICKERS+NETWORK_TICKERS+PHARMA_TECH_TICKERS+SEMICON_SOFTWARE_TICKERS+ENERGY_PHARMA_STAPLES_TICKERS or len(p['periods'])!=5:raise ValueError('Fixed approved company history required')
    selected=[deepcopy(d) for d in decisions if d['ticker']==ticker]
    energy=ticker in ENERGY_PHARMA_STAPLES_TICKERS
    open_review=None
    if energy and ticker=='CVX':
        exceptions=[d for d in selected if d['decision_id']=='CVX-PERIMETER']
        if (len(exceptions)!=1 or exceptions[0]['status']!='OPEN_ESSENTIAL_EXCEPTION'
                or exceptions[0]['accepted'] or exceptions[0]['identities']!=[r['identity'] for r in p['periods']]):
            raise ValueError('Exact OPEN CVX perimeter exception required; never an EBIT approval')
        open_review=exceptions[0]
        selected=[d for d in selected if d['decision_id']!='CVX-PERIMETER']
    if not selected or len({d['decision_id'] for d in selected})!=len(selected):raise ValueError('Exact approved decision set required')
    large=ticker in LARGE_TICKERS
    priority=ticker in PRIORITY_TICKERS
    network=ticker in NETWORK_TICKERS
    pharma=ticker in PHARMA_TECH_TICKERS
    semicon=ticker in SEMICON_SOFTWARE_TICKERS
    if large:
        suffixes=('CF','SBC','CASH','CLAIMS','SHARES','DA','INV','FIN')+(('TAX',) if ticker=='TSLA' else ())
        identities=[r['identity'] for r in p['periods']]
        if ({d['decision_id'] for d in selected}!={ticker+'-'+key for key in suffixes}
                or any(d['identities']!=identities for d in selected)):
            raise ValueError('All exact approved company decisions and periods required')
    if priority or network or pharma or semicon or energy:
        suffixes=('CF','DA','INV','SBC','TAX','CASH','FIN','CLAIMS','SHARES')+(('PERIMETER',) if ticker in ('JNJ','MRK') else ('REV',) if ticker in ('WMT','MA','CVX') else ())
        if ({d['decision_id'] for d in selected}!={ticker+'-'+key for key in suffixes}
                or any(d['identities']!=[r['identity'] for r in p['periods']] for d in selected)):
            raise ValueError('All exact approved company decisions and periods required')
    evidence=cat_evidence(p) if ticker=='CAT' else None
    record=dict(schema='company-treatment-acceptance-audit-v1',version=1,sequence=1,previous=None,
        action='ACCEPT_RETAINED_COMPANY_BATCH',ticker=ticker,author='User, explicit approval of the25 AVGO/TSLA/LLY recommendations' if large else 'User, explicit approval of the48 company-batch recommendations',
        recorded_at_utc=recorded_at_utc,rationale=LARGE_AUTHORITY if large else AUTHORITY,authority=LARGE_AUTHORITY if large else AUTHORITY,scope=SCOPE,source_commit=LARGE_BASELINE if large else BASELINE,
        source_revision=digest(relevant(p)),review_revision=p['review_revision'],proposal_revision=digest(relevant(selected)),
        decisions=selected,identities=[r['identity'] for r in p['periods']],additional_perimeter_evidence=evidence,
        financial_sufficiency='ONLY_APPROVED_HISTORICAL_PERIMETER',phase1_closed=False,valuation_consumption_approved=False)
    if priority:
        record.update(author='User, explicit MU/AMD approval and qualified JNJ historical-selection approval',
            authority=PRIORITY_AUTHORITY,rationale=PRIORITY_AUTHORITY,source_commit=PRIORITY_BASELINE,
            open_analyst_use_requirements=[dict(requirement_id='JNJ-ORIGINAL-AS-FILED-SCOPE',status='OPEN',
                affected_identities=[r['identity'] for r in p['periods']],affected_families=list(JNJ_FLOW_FAMILIES),
                reason='Original FY2021/22 Consumer Health-inclusive income versus later continuing income; consolidated cash/D&A/tax/investment populations cannot be assumed coterminous. Cross-year use remains unresolved.',
                resolution='Evidence-bound consistent continuing/discontinued allocations and cross-year bridge, OR explicit separately justified analyst-use treatment accepting/restricting the mismatched populations; no such resolution approved by this instruction.') ] if ticker=='JNJ' else [])
        if ticker=='JNJ':record['financial_sufficiency']='PARTIAL_OPEN_ANALYST_USE_REQUIREMENT'
    if network:
        record.update(author='User, explicit approval of all28 V/INTC/WMT recommendations',authority=NETWORK_AUTHORITY,rationale=NETWORK_AUTHORITY,source_commit=NETWORK_BASELINE)
    if pharma:
        record.update(author='User, explicit approval of all28 ABBV/MA/CSCO recommendations',authority=PHARMA_TECH_AUTHORITY,rationale=PHARMA_TECH_AUTHORITY,source_commit=PHARMA_TECH_BASELINE)
    if semicon:
        record.update(author='User, explicit approval of all27 LRCX/PLTR/AMAT recommendations',authority=SEMICON_SOFTWARE_AUTHORITY,rationale=SEMICON_SOFTWARE_AUTHORITY,source_commit=SEMICON_SOFTWARE_BASELINE)
    if energy:
        record.update(author='User, explicit approval of29 CVX/MRK/PG recommendations, excluding CVX-PERIMETER',
            authority=ENERGY_PHARMA_STAPLES_AUTHORITY,rationale=ENERGY_PHARMA_STAPLES_AUTHORITY,source_commit=ENERGY_PHARMA_STAPLES_BASELINE,
            open_analyst_use_requirements=[dict(requirement_id='CVX-EBIT-BUSINESS-PERIMETER',status='OPEN',
                affected_identities=[r['identity'] for r in p['periods']],affected_families=['ebit'],
                reason='BUSINESS_PERIMETER_UNRESOLVED: mixed-tax affiliate earnings, operating/nonoperating Other and incomplete benefit allocation; required EBIT remains unavailable.',
                review_decision=deepcopy(open_review),explicitly_not_approved=True,
                resolution='A defensible matched historical operating perimeter and evidence-bound EBIT selection with explicit approval; no substitute equation, zero or waiver is authorized.')] if ticker=='CVX' else [])
        if ticker=='CVX':record['financial_sufficiency']='PARTIAL_OPEN_ESSENTIAL_EBIT_REQUIREMENT'
    ManualIdentity(record['author'],record['recorded_at_utc'],record['rationale']);record['sha256']=digest(record)
    return record


def activate(package,decisions,record):
    """Closed revision-bound approval replay, matching existing company audits."""
    p=parent(package)
    if record.get('sha256')!=digest({k:v for k,v in record.items() if k!='sha256'}):raise ValueError('Malformed company audit digest')
    expected=approval(p,decisions,record.get('recorded_at_utc'))
    if record!=expected:raise ValueError('Stale or unregistered company approval; explicit revalidation required')
    result=deepcopy(p);result['history_approval']=deepcopy(record)
    result['current_history']=cat_view(p,record) if p['ticker']=='CAT' else large_view(p,record) if p['ticker'] in LARGE_TICKERS+PRIORITY_TICKERS+NETWORK_TICKERS+PHARMA_TECH_TICKERS+SEMICON_SOFTWARE_TICKERS+ENERGY_PHARMA_STAPLES_TICKERS else ordinary_view(p,record)
    return result


def load_if_approved(path,package,decisions):
    stored=_json((ROOT/path).read_text())
    if 'history_approval' not in stored:return package
    return activate(package,decisions,stored['history_approval'])


def fact(row,key,base,multiplier=1,origin='reported'):
    if key not in row['facts']:return None
    f=row['facts'][key]
    return dict(value=str(D(f['value'])*multiplier),raw_value=f['value'],unit=f['unit'],precision=f['precision'],
        precision_variants=f.get('precision_variants',[f['precision']]),origin=origin,source_origin='reported',sign_multiplier=multiplier,
        as_of=f.get('as_of'),source_reference=base+'/facts/'+key,scope=f.get('scope',f.get('location','Exact named source observation')))


def calculation(row,key,base,origin=None):
    found=[(i,c) for i,c in enumerate(row['calculations']) if c['input_id']==key]
    if len(found)!=1:raise ValueError('Missing/duplicate approved named calculation: '+key)
    i,c=found[0];out=deepcopy(c);out.update(status='ACCEPTED_FOR_STATED_HISTORICAL_SCOPE',source_reference=base+'/calculations/'+str(i))
    if origin:out['origin']=origin
    out['operand_precision']=c.get('operand_precision',[row['facts'][o]['precision'] for o in c.get('operands',[]) if o in row['facts']])
    return out


def large_view(package,record):
    """Effective values for this approved batch, using existing view/audit shape.

    No new equation or population acceptance: named calculations and proofs are
    the unchanged reviewed source package. Acknowledged nulls remain source nulls.
    """
    t=package['ticker'];periods=[];ids={d['decision_id'] for d in record['decisions']};priority=t in PRIORITY_TICKERS;network=t in NETWORK_TICKERS;pharma=t in PHARMA_TECH_TICKERS;semicon=t in SEMICON_SOFTWARE_TICKERS;energy=t in ENERGY_PHARMA_STAPLES_TICKERS
    for i,row in enumerate(package['periods']):
        base='/periods/'+str(i)
        f=lambda k,m=1,origin='reported':fact(row,k,base,m,origin)
        c=lambda k,origin=None:calculation(row,k,base,origin)
        proof=row['cfo_reconciliation'];pop=proof['populations'][0]
        manual=row.get('independent_display_check') if priority else None
        if manual:
            if manual['status']!='SUPPORTED' or D(manual['difference'])!=0 or D(manual['parent_difference'])!=0:raise ValueError('Exact independent CFO hierarchy required')
            target=manual['continuing_cfo'] or manual['cfo']
            if sum((D(x['value']) for x in manual['rows']),D(0))!=D(target['value']):raise ValueError('Displayed continuing reconciliation failed')
            if manual['continuing_cfo'] and D(manual['continuing_cfo']['value'])+D(manual['discontinued_cfo']['value'])!=D(manual['cfo']['value']):raise ValueError('Consolidated CFO hierarchy failed')
            proof=dict(status='SUPPORTED',populations=[dict(rows=manual['rows'],cfo=target)])
            pop=proof['populations'][0]
        displayed=row.get('independent_displayed_cfo') if semicon or energy else None
        if displayed:
            if (displayed['status']!='SUPPORTED' or D(displayed['difference'])!=0
                    or sum((D(x['value']) for x in displayed['rows']),D(0))!=D(displayed['cfo']['value'])
                    or D(displayed['cfo']['value'])!=D(row['facts']['selected_cfo' if energy else 'cfo']['value'])):raise ValueError('Exact independent displayed CFO proof required')
            # Local effective proof only: original parser PARTIAL remains in the
            # unchanged source package, never overwritten or called repaired.
            proof=dict(status='SUPPORTED',populations=[dict(rows=displayed['rows'],cfo=displayed['cfo'])]);pop=proof['populations'][0]
        precision_check=None
        if energy and t=='PG':
            # Replay the EXISTING displayed-precision rule, not a new tolerance
            # or relaxation of other companies' exact arithmetic requirements.
            from valuation_platform.analyst import cfo_statement_reconciliation as cfo_check
            precision_check=cfo_check.check_rows(pop['rows'],pop['cfo'],complete=True,non_overlapping=True,scope=pop['scope'])
            if (proof['status']!='SUPPORTED' or pop['status']!='SUPPORTED'
                    or any(precision_check[k]!=pop[k] for k in ('status','difference','tolerance','precision_rule'))
                    or precision_check['status']!='SUPPORTED'
                    or D(pop['cfo']['value'])!=D(row['facts']['selected_cfo']['value'])):
                raise ValueError('Unchanged supported PG displayed-precision proof required')
        elif (proof['status']!='SUPPORTED' or
                sum((D(x['value']) for x in pop['rows']),D(0))!=D(pop['cfo']['value'])):
            raise ValueError('Supported independent displayed CFO arithmetic required')
        ebit=None if energy and t=='CVX' else f('ebit')
        if t in ('LLY','JNJ','MRK'):
            ebit=deepcopy(row['derived_ebit'])
            if not ebit or ebit['origin']!='derived':raise ValueError('Existing registered EBIT proof required')
            ebit.update(source_reference=base+'/derived_ebit')
        if energy and t=='CVX':
            if row['proposed_selections']['ebit'] is not None or row['facts'].get('ebit') is not None or row['derived_ebit'] is not None:
                raise ValueError('CVX approved source retains EBIT null; no substitute permitted')
            ebit=dict(value=None,unit='USD',origin='unavailable',null_reason='OPEN_CVX_EBIT_BUSINESS_PERIMETER',
                source_reference=base+'/proposed_selections/ebit',not_reported_zero=True,
                open_requirement_reference='/history_approval/open_analyst_use_requirements/0')
        capex=f('productive_cash' if t in ('V','LRCX') else 'other_ppe_cash' if t=='LLY' else 'cash_capex',-1,origin='proxy' if t=='LRCX' else 'reported')
        if energy:
            if t=='CVX':
                replay=row['existing_capex_policy_replay'];policy=replay['policy'];scope=policy['capex_scope']
                selected=[o['fact'] for o in scope['occurrences'] if o['original_instance_ordinal'] in scope['confirming_original_ordinals']]
                if (not replay['existing_approval'] or replay['gaps'] or not selected
                        or any(D(x['numeric_value'])!=D(replay['value']) or x['accession_number']!=row['identity']['accession'] or x['start']!=row['identity']['annual_start'] or x['end']!=row['identity']['annual_end'] for x in selected)):
                    raise ValueError('Exact approved CVX Capex occurrence/policy binding required')
                capex=dict(value=str(-D(replay['value'])),raw_value=replay['value'],unit='USD',precision=selected[0]['decimals'],
                    precision_variants=sorted({x['decimals'] for x in selected}),origin='reported',source_origin='reported',sign_multiplier=-1,
                    source_reference=base+'/existing_capex_policy_replay',scope='Exact approved gross cash PP&E-equivalent scope only',
                    curated_policy_replay=dict(policy_id=policy['policy_id'],version=policy['version'],policy_sha256=digest(policy),existing_approval=True))
            elif t=='MRK' and row['fiscal_year']<2023:
                capex=f('productive_cash',-1,origin='proxy')
        if t=='LLY':
            generation=row['refreshed_capex']
            if (not generation or generation['original_byte_equivalence']!='UNPROVED'
                    or generation['acceptance_basis']!='INDEPENDENTLY_REVIEWED_REFRESH_NOT_ORIGINAL_DIGEST_VERIFICATION'
                    or len(generation['artifacts'])!=3 or D(generation['value_usd'])!=D(capex['value'])):
                raise ValueError('Exact reviewed refreshed-evidence Capex generation required')
            capex['refreshed_evidence']=deepcopy(generation)
        # Prefer the reviewed fiscal-end population when present; otherwise the
        # approved separately dated cover population. Neither is a diluted total.
        shares={k:f(k) for k in row['facts'] if k.startswith('shares:CommonStockSharesOutstanding:')}
        if not shares:shares={k:f(k) for k in row['facts'] if k.startswith('shares:EntityCommonStockSharesOutstanding:')}
        detail=pop['hierarchy_proof']['children'] if t=='INTC' and network else pop['rows']
        deferred_rows=[deepcopy(x) for x in detail if 'deferred' in x.get('caption',x.get('label','')).lower()]
        inputs=dict(
            revenue=f('face_revenue' if t in ('WMT','MA') else 'revenue'),ebit=ebit,depreciation_amortization=f('expense_da') if t=='MA' else c('limited_da_proxy','proxy'),cash_capex=capex,
            reported_cash_flow_working_capital_movements=dict(rows=deepcopy(row['movement_rows']),source_reference=base+'/cfo_reconciliation',additional_deduction_permitted=False,book_delta_nwc=False),
            deferred_taxes=dict(displayed_rows=deferred_rows,note_observation=f('deferred_tax'),other_observation=f('deferred_movement'),
                source_reference=base+'/cfo_reconciliation',separate_pure_operation='APPROVED_NO_SEPARATE_PURE_OPERATION_MIXED_ROW_PRESERVED' if t=='AVGO' else 'REPORTED_DISPLAYED_POPULATION',value_if_unavailable=None),
            stock_based_compensation=dict(selected=f(row['proposed_selections']['sbc'] if network or pharma or semicon or energy else 'sbc_expense',origin='proxy'),addback=f('face_sbc' if t=='INTC' else 'sbc_addback'),count_once=True),
            unclassified_cfo_reconciliation_residual=dict(value=None,disposition='APPROVED_NO_SEPARATE_OPERATION',not_reported_zero=True),
            reported_cfo=f('selected_cfo' if energy else 'cfo'),
            reported_tax_context=dict(provision=f(row['proposed_selections']['tax'] if semicon else 'tax' if priority or network or pharma else 'face_tax'),pretax=f('pretax'),reported_etr=None if row['facts'].get('reported_etr',{}).get('selection_status','').startswith('UNSELECTED') else f('reported_etr'),
                cash_taxes=f('cash_tax' if 'cash_tax' in row['facts'] else 'cash_tax_gross',-1),
                original_policy_context_reference=base+'/preparation_ledger_evidence/retained-reported-tax-context-ledger',
                original_generic_conflicts_preserved=True,no_new_ratio_computed=True,future_rate_approved=False),
            cash_investment_components=dict(selected=c('current_financial_captions' if network or pharma or semicon or energy else 'gross_current_financial'),unrestricted_or_excess_cash=False,unknown_restrictions=None,operating_reserve=None,
                other_balances={k:f(k) for k in ('restricted_current','restricted_noncurrent','restricted_cash','noncurrent_investments','marketable_long','equity_method','lessor_net_receivable','lessor_net_current','lessor_net_noncurrent') if k in row['facts']},
                parent_child_overlap_not_additive=True,other_populations_reference=base+'/supporting_note_rows'),
            debt_lease_components=dict(selected=c('named_financing'),additional_borrowing=None,no_additional_adjustment=dict(origin='analyst_assumption',approved=True,value=None,
                rationale='Explicitly approved omission of unquantified additional borrowing, not source zero or immateriality; potential amount unbounded'),
                complete_debt=False,current_maturities_already_included=True,finance_leases_already_included=True,
                operating_lease_treatment='service_cost',finance_lease_treatment='asset_financing',
                other_populations_reference=base+'/supporting_note_rows',finance_lease_observation=f('finance_lease')),
            other_equity_bridge_claims_assets=dict(known_populations={k:f(k) for k in row['facts'] if k in ('nci','redeemable_nci','preferred','benefit_liabilities','pension_net','pension_liability','unrecognized_tax_benefits','litigation_liability') or ':DefinedBenefitPlan' in k or ':PensionAndOtherPostretirement' in k},
                other_populations_reference=base+'/supporting_note_rows',net_funded_and_gross_claims_not_additive=True,
                additional_adjustment=dict(origin='analyst_assumption',approved=True,value=None,rationale='No additional unidentified preferred/NCI/pension adjustment beyond known disclosures; unbounded potential omission, not reported zero/immateriality'),
                pure_nol_economic_operation=False),
            point_in_time_shares=dict(selected_populations=shares,other_dates_classes_eps_awards_reference=base+'/facts',automatic_aggregation_or_dilution=False))
        inputs['cash_capex']['other_disclosures']={k:f(k,row.get('cash_sign_multipliers',{}).get(k,1)) for k in
            ('iprd_cash','iprd_expense','iprd_addback','acquisition','other_acquisition_cash','asset_acquisition_cash','noncash_finance_rou','noncash_operating_rou','capital_creditors','accrued_purchases') if k in row['facts']}
        inputs['cash_capex']['complete_reinvestment']=False
        inputs['cash_capex']['source_comparability_reference']=base+'/passages'
        inputs['depreciation_amortization'].update(complete_expense_da=None,additional_rou_addback=False,
            excluded_or_support_observations_reference=base+'/facts',
            qualification='Acquisition-amortization/dep ONLY, mixed ROU excluded' if t=='AVGO' else 'Impairment-inclusive manufacturing/energy/leasing CFO proxy, not pure expense D&A' if t=='TSLA' else 'Limited CFO D&A proxy; IPR&D/impairment not added')
        if t=='TSLA':
            inputs['debt_lease_components']['perimeter']='Consolidated manufacturing/energy/leasing including related financing assets and funding; no netted industrial carve-out'
            inputs['cash_capex']['scope']='Original selected PP&E cash caption with stated gross/net-of-sales perimeter; later differing comparatives not substituted'
        if network:
            inputs['depreciation_amortization']['qualification']={'V':'Existing exact curated D&A scope; client-incentive amortization excluded; rounded note discrepancy not plugged',
                'INTC':'Limited depreciation plus intangible amortization proxy; inventory capitalization/useful-life/incentive basis limitations; no impairment/restructuring add-on',
                'WMT':'Limited CFO depreciation/amortization/accretion proxy; accretion retained; no extra finance amortization'}[t]
            if t=='V':
                for family,key in (('depreciation_amortization','d_and_a'),('cash_capex','capex')):
                    replay=row['curated_policy_replays'][key]
                    if not replay['existing_approval'] or D(replay['value'])!=abs(D(inputs[family]['value'])):raise ValueError('Exact curated policy replay required')
                    inputs[family]['curated_policy_replay']=dict(value=replay['value'],existing_approval=True,reviewed_scope_only=replay['reviewed_scope_only'],
                        policy_id=replay['policy']['policy_id'],version=replay['policy']['version'],policy_sha256=digest(replay['policy']))
                    inputs[family]['curated_policy_reference']=base+'/curated_policy_replays/'+key
            if t=='INTC':
                hierarchy=pop['hierarchy_proof']
                if sum((D(x['value']) for x in hierarchy['children']),D(0))!=D(hierarchy['parent']['value']):raise ValueError('Intel bound adjustment hierarchy required')
                inputs['deferred_taxes'].update(hierarchy_reference=base+'/cfo_reconciliation/populations/0/hierarchy_proof')
            inputs['stock_based_compensation'].update(alternatives_reference=base+'/alternatives/sbc',
                selection_rationale='Exact approved company cost proxy; distinct from pure expense and original reconciliation role; count once')
            inputs['cash_investment_components']['other_balances'].update({k:f(k) for k in ('investment_securities','short_afs','cash_restricted_parent','settlement_receivable','client_asset_current','client_asset_noncurrent','litigation_escrow','client_cash_collateral') if k in row['facts']})
            inputs['debt_lease_components'].update(finance_leases_already_included=True if t=='WMT' else None,
                scope='Named carrying financing only; no inferred lease coverage or complete debt',
                supplier_finance=f('supplier_finance'),supplier_finance_already_in_operating_ap=t=='WMT')
            inputs['other_equity_bridge_claims_assets']['known_populations'].update({k:f(k) for k in row['facts'] if k.startswith('claim:') or k in ('preferred_outstanding','settlement_payable','client_liability','litigation_escrow','client_cash_collateral')})
            inputs['point_in_time_shares'].update(class_parent_overlap_not_additive=True,conversion_or_dilution_approved=False)
            inputs['cash_capex']['other_disclosures'].update({k:f(k,row.get('cash_sign_multipliers',{}).get(k,1)) for k in ('capital_grant_cash','noncash_incentive','grant_basis_reduction','supplier_finance') if k in row['facts']})
            if t=='WMT':inputs['revenue'].update(selection_rationale='Approved face Total revenues, including membership/other income; generic economic conflicts unchanged',
                original_conflicts_reference=base+'/alternatives',face_statement_identity_reference=base+'/revenue_display_identity')
        if pharma:
            inputs['depreciation_amortization']['qualification']={'ABBV':'Limited precise separate CFO depreciation/intangible proxy; impairment/IPRD/fair-value changes excluded; rounded note alternatives retained',
                'MA':'Selected reported face expense includes finance amortization; operating lease amortization in G&A; no customer-incentive or ROU addition; generic D&A policy unchanged',
                'CSCO':'Limited inherited-rounded PP&E plus impairment-inclusive total purchased-intangible proxy; not opex-only, pure complete D&A or mixed CFO-other; no balancing/ROU addition'}[t]
            inputs['cash_capex']['other_disclosures'].update({k:f(k,row.get('cash_sign_multipliers',{}).get(k,1)) for k in
                ('investment_cash','acquisition_net_divestitures','upfront_collaboration_adjustment','intangible_impairment','contingent_fair_value_change','contingent_cash_financing','contingent_cash_operating') if k in row['facts']})
            tax=inputs['reported_tax_context'];replay=row['reported_tax_policy_replay']
            tax['pretax']=f('pretax' if 'pretax' in row['facts'] else 'pretax_equity_scope')
            for key,role in (('provision','provision'),('pretax','pretax')):
                source=replay['fields'][role]
                if source['status']!='POPULATED' or not tax[key] or D(tax[key]['value'])!=D(source['value']):raise ValueError('Exact approved tax operand replay required')
                tax[key]['policy_provenance_reference']=base+'/reported_tax_policy_replay'
            tax.update(reported_etr=dict(deepcopy(replay['etr']),source_reference=base+'/reported_tax_policy_replay/etr'),
                original_reported_etr_observation=f('reported_etr'),policy_provenance_reference=base+'/reported_tax_policy_replay',generic_denominator_approval_changed=False)
            if t=='MA':
                inputs['revenue'].update(selection_rationale='Approved exact face Net revenue after rebates/incentives, not gross/net economic equivalence',generic_conflict_preserved=True,alternatives_reference=base+'/alternatives')
                tax['curated_pretax_provenance_reference']=base+'/reported_tax_policy_replay/proof'
            cash=inputs['cash_investment_components']
            cash['other_balances'].update({k:f(k) for k in ('current_investments','current_financial_investments','current_financial_parent','other_investments','strategic_equity','restricted_cash_current','restricted_noncurrent_cash','cash_restricted_parent','customer_collateral_asset','customer_collateral_liability','settlement_asset','settlement_liability','litigation_restricted') if k in row['facts']})
            cash['population_relationships_reference']=base+'/population_relationships'
            cash['unresolved_populations_reference']=base+'/source_binding_exceptions'
            if t=='CSCO' and row['fiscal_year']==2026:
                alternative=f('current_financial_parent');difference=D(cash['selected']['value'])-D(alternative['value'])
                if (D(cash['selected']['value']),D(alternative['value']),difference)!=(D('15918000000'),D('14297000000'),D('1621000000')):raise ValueError('Exact approved CSCO face/parent conflict required')
                cash['retained_conflict']=dict(status='UNRESOLVED_SOURCE_SCOPE_DIFFERENCE',selected_basis='Explicit face cash/current investment components',
                    conflicting_parent=alternative,difference_usd=str(difference),difference_role='Unexplained comparison, NOT adjustment or new input',no_plug=True,rounding_explanation=None,conflict_cleared=False)
            debt=inputs['debt_lease_components'];debt.update(finance_leases_already_included=True if t=='ABBV' else None,
                population_relationships_reference=base+'/population_relationships',other_reported_populations={k:f(k) for k in ('short_borrowing','cp','debt_parent','debt_carrying_parent','debt_carrying_combined','debt_finance_current','debt_finance_long','debt_current','debt_long','face_short_debt','finance_lease','financing_liability','op_lease') if k in row['facts']})
            if t=='ABBV':debt['embedded_population_limitation']='Finance lease/financing liability already in carrying captions; FY2024 additional short borrowing source remains null under approved omission, not reported zero'
            claims=inputs['other_equity_bridge_claims_assets']
            claims['known_populations'].update({k:f(k) for k in row['facts'] if k.startswith('claim:') or k in ('postemployment_liability','contingent_liability','contingent_current','contingent_noncurrent','litigation_current','strategic_equity')})
            claims['population_relationships_reference']=base+'/population_relationships'
            inputs['point_in_time_shares'].update(class_parent_overlap_not_additive=True,conversion_or_dilution_approved=False)
        if semicon:
            cf_reference=base+('/independent_displayed_cfo' if displayed else '/cfo_reconciliation')
            inputs['reported_cfo'].update(original_parser_status=row['cfo_reconciliation']['status'],independent_reconciliation_reference=cf_reference)
            inputs['reported_cash_flow_working_capital_movements'].update(source_reference=base+'/movement_rows',reconciliation_reference=cf_reference)
            inputs['deferred_taxes'].update(displayed_rows=[deepcopy(x) for x in detail if x.get('caption','').strip().lower().startswith('deferred income tax')],
                source_reference=cf_reference,separate_pure_operation='RETAIN_DISPLAYED_TAX_ROWS_ONLY_NO_NOTE_INSERTION',value_if_unavailable=None)
            inputs['depreciation_amortization']['qualification']={
                'LRCX':'Limited CFO D&A proxy; source finance amortization included with depreciation; no additional ROU, later unquantified components not zero',
                'PLTR':'Limited CFO D&A proxy; noncash operating-lease cost, impairment and investment losses separate, complete expense D&A unknown',
                'AMAT':'Limited manufacturing CFO D&A proxy; first-two direct observations preserved, later concept-scope negatives unchanged; inventory/timing, incentives and missing amortization remain'}[t]
            investment=inputs['cash_capex']
            investment.update(pure_cash_ppe=None if t=='LRCX' else None,
                investment_perimeter='BROADER_COMBINED_PPE_INTANGIBLES_APPROVED_PROXY' if t=='LRCX' else 'SOURCE_CASH_PPE_SCOPE_SOFTWARE_NOT_ALLOCATED',
                pure_ppe_scope_approved=False if t=='LRCX' else None)
            investment['other_disclosures'].update({k:f(k,row.get('cash_sign_multipliers',{}).get(k,1)) for k in ('inventory_transfers','investment_cash','investment_purchases','capitalized_software_cash','alternative_investment_cash','sale_ppe') if k in row['facts']})
            if t=='AMAT':investment['incentive_limitation']='PPE/tax incentive stock balances are not annual cash receipts; no netting against cash Capex'
            tax=inputs['reported_tax_context'];tax.update(original_policy_provenance_reference=base+'/reported_tax_policy_replay',
                original_policy_etr=deepcopy(row['reported_tax_policy_replay']['etr']),cash_tax_refund=f('cash_tax_refund'),face_provision_selected=t=='PLTR',
                alternatives_reference=base+'/alternatives/tax',generic_tax_conflicts_cleared=False,no_new_ratio_computed=True)
            cash=inputs['cash_investment_components'];cash['other_balances'].update({k:f(k) for k in ('face_investments','current_investments','marketable_current','restricted_note_current','restricted_note_noncurrent','restricted_cash','restricted_current','restricted_noncurrent','strategic_equity','deferred_plan_investments') if k in row['facts']})
            cash.update(population_relationships_reference=base+'/population_relationships',unresolved_populations_reference=base+'/source_binding_exceptions')
            debt=inputs['debt_lease_components'];debt.update(finance_leases_already_included=True if t=='LRCX' else None,
                scope='Named reported carrying/facility population with explicitly approved omission; NOT complete financing',
                population_relationships_reference=base+'/population_relationships',other_reported_populations={k:f(k) for k in ('debt_current','debt_long','debt_parent','debt_fair_value','debt_finance_current','debt_finance_long','face_short_debt','short_borrowing','cp','finance_lease','finance_current','finance_long','op_lease','op_current','op_long','facility_balance_explicit_none') if k in row['facts']})
            if t=='PLTR':debt['named_zero_scope']='Affirmative note population; FY2025 limited to2014 facility. Zero named balance plus approved no-additional adjustment is NOT exhaustive reported zero financing.'
            if t=='AMAT':debt['nonoverlap_limitation']='FY2024 short799 contains current maturities700; FY2023 separately disclosed finance102 included once; missing later finance subamounts remain unknown'
            claims=inputs['other_equity_bridge_claims_assets'];claims['known_populations'].update({k:f(k) for k in ('deferred_plan_obligation','deferred_plan_investments','accrued_compensation_caption','strategic_equity','postemployment_liability') if k in row['facts']})
            claims.update(population_relationships_reference=base+'/population_relationships',plan_assets_liabilities_not_automatically_netted=True,
                plan_obligation_is_not_broader_accrued_compensation=t=='LRCX')
            inputs['point_in_time_shares'].update(class_parent_overlap_not_additive=True,conversion_or_dilution_approved=False,source_comparability_reference=base+'/passages')
        if energy:
            cf_reference=base+('/independent_displayed_cfo' if displayed else '/cfo_reconciliation')
            perimeter='Original-as-filed continuing operations' if t=='MRK' and row['fiscal_year']<2024 else 'Original-as-filed consolidated/root presentation'
            inputs['revenue']=f('face_revenue' if t=='CVX' else 'revenue')
            if t=='CVX':inputs['revenue'].update(generic_conflict_preserved=True,alternatives_reference=base+'/alternatives/revenue',
                selection_rationale='Explicitly approved face Sales; broader Revenues is not economically equivalent and does not repair EBIT')
            inputs['reported_cfo'].update(perimeter=perimeter,original_parser_status=row['cfo_reconciliation']['status'],
                independent_reconciliation_reference=cf_reference,discontinued_observation=f('discontinued_cfo'))
            if precision_check:
                inputs['reported_cfo']['displayed_precision_check']=dict(precision_check,exact_arithmetic=D(precision_check['difference'])==0,
                    unchanged_existing_rule=True,no_plug=True,source_discrepancy_cause=None)
            inputs['reported_cash_flow_working_capital_movements'].update(perimeter=perimeter,source_reference=base+'/movement_rows',reconciliation_reference=cf_reference)
            # Do not misclassify CVX other deferred charges as deferred TAX.
            inputs['deferred_taxes'].update(displayed_rows=[deepcopy(x) for x in detail if x.get('caption','').strip().lower().startswith('deferred income tax')],
                source_reference=cf_reference,perimeter=perimeter,separate_pure_operation='RETAIN_DISPLAYED_TAX_ROWS_ONLY_NO_NOTE_INSERTION')
            inputs['depreciation_amortization']['qualification']={
                'CVX':'Depletion-inclusive consolidated energy DD&A proxy; no equivalence to industrial D&A or repair of unavailable EBIT',
                'MRK':'Limited continuing CFO depreciation plus amortization proxy; separate impairment excluded, accelerated/manufacturing/inventory scope retained',
                'PG':'Limited manufacturing/corporate CFO D&A proxy; no second intangible amortization, impairment or restructuring addition'}[t]
            inv=inputs['cash_capex'];inv.update(pure_cash_ppe=None,
                investment_perimeter='BROADER_CONTINUING_CAPITAL_EXPENDITURES_APPROVED_PROXY' if t=='MRK' and row['fiscal_year']<2023 else 'EXISTING_APPROVED_CASH_PPE_EQUIVALENT' if t=='CVX' else 'EXISTING_DIRECT_CASH_PPE_SCOPE',
                pure_ppe_scope_approved=False if t=='MRK' and row['fiscal_year']<2023 else None,
                prior_negative_findings_preserved=t=='MRK',other_cash_investment_reference=base+'/supporting_note_rows')
            inv['other_disclosures'].update({k:f(k,row.get('cash_sign_multipliers',{}).get(k,1)) for k in ('productive_cash','investment_acquisitions','investment_cash','other_ppe_cash','sale_ppe') if k in row['facts']})
            tax=inputs['reported_tax_context'];replay=row['reported_tax_policy_replay']
            pretax_key='pretax_extension' if t=='PG' and row['fiscal_year']<2024 else 'pretax_equity_scope' if t=='CVX' else 'pretax'
            tax.update(provision=f('tax'),pretax=f(pretax_key),reported_etr=f('reported_etr'),
                original_policy_etr=deepcopy(replay['etr']),original_policy_provenance_reference=base+'/reported_tax_policy_replay',
                generic_denominator_approval_changed=False,issuer_disclosure_not_new_ratio=True,perimeter=perimeter)
            if not tax['provision'] or D(tax['provision']['value'])!=D(replay['fields']['provision']['value']):raise ValueError('Exact reported provision binding required')
            if pretax_key=='pretax_extension':
                if replay['fields']['pretax']['status']!='UNAVAILABLE' or replay['etr']['value'] is not None or not tax['pretax']:
                    raise ValueError('PG company extension must preserve generic Pretax/ETR nulls')
                tax['pretax'].update(company_specific_selection=True,generic_extension_policy_changed=False)
            elif not tax['pretax'] or D(tax['pretax']['value'])!=D(replay['fields']['pretax']['value']):raise ValueError('Existing approved Pretax scope binding required')
            cash=inputs['cash_investment_components'];cash['other_balances'].update({k:f(k) for k in ('face_cash','current_investments','marketable_current','marketable_long','cash_restricted_parent','restricted_cash_current','restricted_current','restricted_noncurrent','equity_method','other_investments') if k in row['facts']})
            cash.update(population_relationships_reference=base+'/population_relationships',unresolved_populations_reference=base+'/source_binding_exceptions',
                face_cash_uses_broader_qname=t=='PG',restrictions_not_proven_absent=True)
            debt=inputs['debt_lease_components'];debt.update(finance_leases_already_included=True if t=='CVX' else None,
                scope='Named carrying captions only; missing subamounts and unquantified additional borrowing remain unknown',
                population_relationships_reference=base+'/population_relationships',other_reported_populations={k:f(k) for k in ('face_current_borrowing','short_borrowing','cp','other_short_borrowing','debt_current','debt_long','debt_parent','debt_finance_long','debt_fair_value','finance_lease','finance_current','finance_long','op_lease','op_current','op_long') if k in row['facts']})
            if t=='PG':
                components={k:f(k) for k in ('cp','debt_current','other_short_borrowing')};face=f('face_current_borrowing')
                total=sum((D(x['value']) for x in components.values()),D(0));difference=total-D(face['value'])
                debt['retained_component_check']=dict(components=components,face_parent=face,component_sum_usd=str(total),difference_usd=str(difference),
                    status='UNEXPLAINED_DIFFERENCE' if difference else 'EXACT',difference_role='Source comparison only, NOT an adjustment or accepted input',
                    face_parent_selected=True,no_plug=True,rounding_explanation=None,conflict_cleared=False)
            claims=inputs['other_equity_bridge_claims_assets']
            claims['known_populations'].update({k:f(k) for k in row['facts'] if k.startswith('claim:') or k in ('asset_retirement','pension_noncurrent','benefit_liabilities','retirement_expense','equity_method')})
            claims.update(population_relationships_reference=base+'/population_relationships',plan_assets_liabilities_not_automatically_netted=True,
                preferred_population_retained=t=='PG',other_source_observations_reference=base+'/facts')
            claims['additional_adjustment']['rationale']='Approved no additional unidentified claim adjustment BEYOND retained known preferred/NCI/pension/ARO populations; not a no-preferred assumption, reported zero or immateriality. Potential omitted amounts remain unbounded.'
            inputs['stock_based_compensation'].update(selection_rationale='Explicit company expense cost proxy, counted once; source expense and CFO add-back remain separate',
                negative_expense_benefit_preserved=True,alternatives_reference=base+'/alternatives/sbc')
            inputs['point_in_time_shares'].update(class_parent_overlap_not_additive=True,conversion_or_dilution_approved=False,source_comparability_reference=base+'/passages')
        if priority:
            inputs['reported_cfo']=f(row['proposed_cfo_fact'])
            cashflow_scope='Continuing operations' if t=='AMD' and row['fiscal_year']==2025 else 'Original consolidated reported population'
            inputs['reported_cfo'].update(scope=cashflow_scope,original_consolidated_observation=f('cfo'),
                discontinued_observation=f('discontinued_cfo'),independent_reconciliation_reference=base+('/independent_display_check' if manual else '/cfo_reconciliation'),original_parser_status=row['cfo_reconciliation']['status'])
            inputs['reported_cash_flow_working_capital_movements'].update(scope=cashflow_scope,source_reference=base+'/movement_rows',
                reconciliation_reference=base+('/independent_display_check' if manual else '/cfo_reconciliation'))
            inputs['deferred_taxes'].update(scope=cashflow_scope,source_reference=base+('/independent_display_check' if manual else '/cfo_reconciliation'))
            if not deferred_rows:inputs['deferred_taxes']['separate_pure_operation']='APPROVED_NO_SEPARATE_PURE_OPERATION_MIXED_ROW_PRESERVED'
            inputs['depreciation_amortization']['qualification']={'MU':'Limited manufacturing CFO proxy; inventory capitalization/release and incentive-reduced basis, not complete expense D&A',
                'AMD':'Exact approved source extension-backed CFO populations; separate amortization only FY2024/25; generic extension gates unchanged',
                'JNJ':'Limited original consolidated CFO D&A proxy; continuing/discontinued allocation unproved, analyst-use requirement OPEN'}[t]
            tax=inputs['reported_tax_context']
            tax.update(pretax=f('pretax_equity_scope') if t=='MU' else f('pretax'),generic_denominator_approval_changed=False,
                original_etr_observation=f('reported_etr'),issuer_disclosure_not_new_ratio=True)
            if t=='MU':tax['pretax']['scope']='Original before-equity pretax disclosure; not approval of generic positive-denominator ETR policy'
            inputs['cash_capex']['other_disclosures'].update({k:f(k,row.get('cash_sign_multipliers',{}).get(k,1)) for k in
                ('incentive_cash','acquisition_cash','iprd_face_impairment') if k in row['facts']})
            if t=='MU':inputs['cash_capex']['nondefault_incentive_net_alternative']=dict(next(x for x in row['calculations'] if x['input_id']=='net_incentive_cash_alternative'),selected=False)
            inputs['cash_investment_components']['other_balances'].update({k:f(k) for k in ('short_afs','current_investments','marketable_current','other_investments','cash_restricted_parent') if k in row['facts']})
            inputs['debt_lease_components']['finance_leases_already_included']=True if t=='MU' else None
            inputs['debt_lease_components']['embedded_finance_lease_scope']='MU combined face caption includes finance leases; no second addition' if t=='MU' else 'No complete finance-lease coverage proved; unknown additional populations remain source nulls'
            claims=inputs['other_equity_bridge_claims_assets']
            claims['known_populations'].update({k:f(k) for k in ('pension_recognized','other_postretirement_recognized','benefit_liabilities_noncurrent_parent','benefit_liabilities_current_parent','talc_carrying_reserve','talc_nominal_reserve','talc_reversal','retirement_expense') if k in row['facts']})
            claims.update(carrying_nominal_and_expense_not_additive=True,original_claims_ledger_reference=base+'/preparation_ledger_evidence/retained-claims-shares-ledger')
            if t=='JNJ':
                for key,value in inputs.items():value['panel']='ORIGINAL_AS_FILED_NOT_HOMOGENEOUS_CONTINUING_SERIES'
                claims['scope_requirement_reference']='/history_approval/open_analyst_use_requirements/0'
        for value in inputs.values():value.update(review='ACCEPTED_FOR_STATED_HISTORICAL_SCOPE',approval_reference='/history_approval')
        if energy and t=='CVX':inputs['ebit']['review']='OPEN_ESSENTIAL_REQUIREMENT_NOT_APPROVED'
        # Assess the existing operations, not a new demand for perfect disclosure.
        essentials={key:inputs[key] for key in ('revenue','ebit','depreciation_amortization','cash_capex','reported_cfo')}
        essentials.update(stock_based_compensation=inputs['stock_based_compensation']['selected'],
            cash_investment_components=inputs['cash_investment_components']['selected'],debt_lease_components=inputs['debt_lease_components']['selected'])
        gaps={key:'Existing approved scalar selection unavailable' for key,value in essentials.items() if not value or value.get('value') is None}
        if not all((inputs['reported_tax_context']['provision'],inputs['reported_tax_context']['pretax'])):gaps['reported_tax_context']='Reviewed provision/pretax selection unavailable'
        if not shares or any(not s.get('as_of') for s in shares.values()):gaps['point_in_time_shares']='Approved actual-date common population unavailable'
        if t=='JNJ':gaps.update({key:record['open_analyst_use_requirements'][0]['reason'] for key in JNJ_FLOW_FAMILIES})
        if energy and t=='CVX':gaps['ebit']=record['open_analyst_use_requirements'][0]['reason']
        checklist=[]
        if len(row['family_checklist'])!=14 or {x['field'] for x in row['family_checklist']}!=set(inputs):raise ValueError('Exact14-family accounting required')
        for old in row['family_checklist']:
            missing_ids=[key for key in old['pending_decisions'] if key not in ids]
            open_cvx_ebit=(energy and t=='CVX' and old['field']=='ebit' and old['status']=='ESSENTIAL_EXCEPTION' and missing_ids==['CVX-PERIMETER'])
            if missing_ids and not open_cvx_ebit:raise ValueError('Missing exact family authorization')
            key=old['field'];gap=gaps.get(key)
            checklist.append(dict(field=key,status='UNRESOLVED_ESSENTIAL_INPUT' if gap else 'SATISFIED_WITHIN_APPROVED_HISTORICAL_PERIMETER',reason=gap,
                approval_reference='/history_approval',effective_input_reference='/current_history/periods/'+str(i)+'/inputs/'+key))
        periods.append(dict(identity=row['identity'],inputs=inputs,checklist=checklist,passed_family_slots=14-len(gaps),analyst_complete=not gaps,
            remaining_essential_inputs=[dict(field=k,reason=v) for k,v in gaps.items()],original_supporting_unknowns=deepcopy(row['original_supporting_unknowns']),
            complete_expense_basis_da=None,complete_debt=False,complete_reinvestment=False,source_reference=base,accepted_limitations_reference='/history_approval/decisions'))
    view=dict(version=1,authoritative_current_view=True,new_assumptions_active=True,periods=periods,family_slots=70,
        passed_family_slots=sum(r['passed_family_slots'] for r in periods),company_completed_for_approved_historical_perimeter=all(r['analyst_complete'] for r in periods),
        approval_sha256=record['sha256'],active_decisions=[dict(decision_id=d['decision_id'],status='ACTIVE',accepted=True) for d in record['decisions']],
        historical_proposal_snapshot='/periods',phase1_closed=False,valuation_consumption_approved=False)
    if priority:
        view['open_analyst_use_requirements']=deepcopy(record['open_analyst_use_requirements'])
        if t=='JNJ':
            view['selected_values_approved']=True
            for d in view['active_decisions']:d['status']='ACTIVE_HISTORICAL_SELECTION_OPEN_ANALYST_USE_REQUIREMENT'
    if energy:
        view['open_analyst_use_requirements']=deepcopy(record['open_analyst_use_requirements'])
        if t=='CVX':view.update(selected_values_approved=True,joint_use_eligibility='NOT_ELIGIBLE_OPEN_EBIT_BUSINESS_PERIMETER')
    return view


def ordinary_view(package,record):
    t=package['ticker'];periods=[];ids={d['decision_id'] for d in record['decisions']}
    for i,row in enumerate(package['periods']):
        base='/periods/'+str(i);f=lambda k,m=1,origin='reported':fact(row,k,base,m,origin)
        c=lambda k,origin=None:calculation(row,k,base,origin)
        proof=row['cfo_reconciliation'];manual=row.get('independent_display_check')
        if proof['status']!='SUPPORTED' and not (t=='META' and manual and manual['status']=='SUPPORTED' and D(manual['difference'])==0):raise ValueError('No supported independent CFO check')
        da=c('limited_finance_inclusive_da_proxy','proxy') if t=='COST' else c('limited_expense_da_proxy','proxy') if t=='AMZN' else f('da',origin='proxy')
        capex=f('combined_investment',-1,'proxy') if t=='NVDA' else f('productive_cash',-1) if t=='AMZN' else f('cash_capex',-1)
        financing=c('known_facility_expanded_financing' if t=='AMZN' and row['identity']['annual_end']=='2021-12-31' else 'named_financing')
        shares={k:f(k) for k in row['facts'] if k.startswith('shares:CommonStockSharesOutstanding:')}
        if not all((f('revenue'),f('ebit'),da,capex,f('cfo'),shares)):raise ValueError('Approved scalar/share selection missing')
        deferred_rows=[deepcopy(r) for r in proof['populations'][0]['rows'] if r.get('concept') in ('DeferredIncomeTaxExpenseBenefit','IncreaseDecreaseInDeferredIncomeTaxes','DeferredIncomeTaxesAndTaxCredits')]
        # Keep mixed captions in the source proof, not an inferred pure zero.
        inputs=dict(revenue=f('revenue'),ebit=f('ebit'),depreciation_amortization=da,cash_capex=capex,
            reported_cash_flow_working_capital_movements=dict(rows=deepcopy(row['movement_rows']),source_reference=base+'/cfo_reconciliation',additional_deduction_permitted=False,book_delta_nwc=False),
            deferred_taxes=dict(displayed_rows=deferred_rows,note_observation=f('deferred_tax'),other_observation=f('deferred_movement'),
                separate_pure_operation='REPORTED_DISPLAYED_POPULATION' if deferred_rows else 'APPROVED_NO_SEPARATE_PURE_OPERATION_UNKNOWN_AMOUNT',value_if_unavailable=None,source_reference=base+'/cfo_reconciliation'),
            stock_based_compensation=dict(selected=c('gross_sbc_expense','proxy') if t=='COST' else f('sbc_expense',origin='proxy'),addback=f('sbc_addback'),count_once=True),
            unclassified_cfo_reconciliation_residual=dict(value=None,disposition='APPROVED_NO_SEPARATE_OPERATION',not_reported_zero=True),
            reported_cfo=f('cfo'),reported_tax_context=dict(provision=f('selected_tax' if t=='AMZN' else 'tax'),pretax=f('pretax_equity_scope' if t=='AMZN' else 'pretax'),
                reported_etr=f('reported_etr'),cash_taxes=f('selected_cash_tax' if t=='AMZN' else 'cash_tax' if 'cash_tax' in row['facts'] else 'cash_tax_gross',-1),
                generic_denominator_status='Unchanged approved generic rules; AMZN before-equity scope/loss restrictions preserved' if t=='AMZN' else 'Existing reported scope',future_rate_approved=False),
            cash_investment_components=dict(selected=c('gross_current_financial'),unrestricted_or_excess_cash=False,unknown_restrictions=None,operating_reserve=None,restrictions_and_other_holdings_reference=base+'/facts',additional_candidates_reference=base+'/preparation_ledger_evidence' if 'preparation_ledger_evidence' in row else base+'/passages'),
            debt_lease_components=dict(selected=financing,additional_borrowing=None,no_additional_adjustment=dict(origin='analyst_assumption',approved=True,value=None,
                rationale='Approved omission of unquantified additional borrowing, not reported zero or immateriality; amount unbounded'),complete_debt=False,current_maturities_already_included=True,
                operating_lease_treatment='service_cost',finance_lease_treatment='asset_financing',other_population_reference=base+'/facts'),
            other_equity_bridge_claims_assets=dict(known_population_reference=base+'/facts',additional_population_reference=base+'/preparation_ledger_evidence' if 'preparation_ledger_evidence' in row else base+'/passages',
                additional_adjustment=dict(origin='analyst_assumption',approved=True,value=None,rationale='No additional unidentified preferred/NCI/pension adjustment selected; potentially omitted claim unbounded, source nulls unchanged'),pure_nol_economic_operation=False),
            point_in_time_shares=dict(selected_populations=shares,other_dated_classes_eps_awards_reference=base+'/facts',automatic_aggregation_or_dilution=False))
        if t=='COST':inputs['depreciation_amortization']['accepted_non_overlap_assumption']='Separate finance amortization not already included; explicitly approved, not new source proof'
        if t=='NVDA':inputs['cash_capex'].update(scope='Combined PP&E/intangible purchases; explicitly approved extension years and standard-caption years, NOT pure PP&E',pure_ppe_cash=None)
        if t=='AMZN':inputs['depreciation_amortization']['prior_broad_da_status']='NEGATIVE_REVIEW_PRESERVED_SUPPORT_ONLY';inputs['debt_lease_components']['supplemental_comparative_reference']=base+'/supplemental_source_observations' if i==0 else None
        if t=='META':inputs['reported_cfo']['independent_display_check_reference']=base+'/independent_display_check' if manual else base+'/cfo_reconciliation'
        if t=='KO':
            held=next((j for j,x in enumerate(row['calculations']) if x['input_id']=='held_sale_named_borrowing'),None)
            inputs['debt_lease_components']['known_separate_held_sale']=c('held_sale_named_borrowing') if held is not None else None
            inputs['debt_lease_components']['known_separate_held_sale_treatment']='Visible recognized separate schedule; must not be silently omitted or added twice. Conditional expanded financing not selected.'
            inputs['debt_lease_components']['expanded_alternative_selected']=False
        for value in inputs.values():value.update(review='ACCEPTED_FOR_STATED_HISTORICAL_SCOPE',approval_reference='/history_approval')
        checklist=[]
        for old in row['family_checklist']:
            if any(k not in ids for k in old['pending_decisions']):raise ValueError('Missing exact family authorization')
            checklist.append(dict(field=old['field'],status='SATISFIED_WITHIN_APPROVED_HISTORICAL_PERIMETER',approval_reference='/history_approval',effective_input_reference='/current_history/periods/'+str(i)+'/inputs/'+old['field']))
        if len(checklist)!=14:raise ValueError('Fourteen existing families required')
        periods.append(dict(identity=row['identity'],inputs=inputs,checklist=checklist,passed_family_slots=14,analyst_complete=True,remaining_essential_inputs=[],
            original_supporting_unknowns=deepcopy(row['original_supporting_unknowns']),complete_expense_basis_da=None,complete_debt=False,complete_reinvestment=False,
            accepted_limitations_reference='/history_approval/decisions',source_reference=base))
    return dict(version=1,authoritative_current_view=True,new_assumptions_active=True,periods=periods,family_slots=70,passed_family_slots=70,
        company_completed_for_approved_historical_perimeter=True,approval_sha256=record['sha256'],active_decisions=[dict(decision_id=d['decision_id'],status='ACTIVE',accepted=True) for d in record['decisions']],
        historical_proposal_snapshot='/periods',phase1_closed=False,valuation_consumption_approved=False)


def cat_view(package,record):
    """Separate disclosed perimeters; acceptance cannot fill missing allocations."""
    periods=[]
    def find(table,captions,scope):
        rows=[r for r in table['rows'] if r['caption'] in captions]
        if len(rows)!=1:return None
        r=rows[0];return dict(r['values'][scope],caption=r['caption'],table=r['table'],row=r['row'],source_url=r['source_url'],source_sha256=r['source_sha256'],source_reference=r['source_reference'])
    for i,evidence in enumerate(record['additional_perimeter_evidence']):
        tables={t['kind']:t for t in evidence['tables']};scopes={}
        for scope in ('industrial','financial_products','eliminations'):
            get=lambda kind,*captions:find(tables[kind],captions,scope)
            start=next((j for j,r in enumerate(tables['cash_flow']['rows']) if r['caption'].startswith(('Profit (loss) of consolidated','Profit of consolidated'))),None)
            stop=next((j for j,r in enumerate(tables['cash_flow']['rows']) if r['caption']=='Net cash provided by (used for) operating activities'),None)
            if start is None or stop is None:raise ValueError('CAT displayed reconciliation boundaries required')
            terms=tables['cash_flow']['rows'][start:stop];cfo=get('cash_flow','Net cash provided by (used for) operating activities')
            difference=sum((D(r['values'][scope]['value']) for r in terms),D(0))-D(cfo['value'])
            proof=dict(status='SUPPORTED' if difference==0 else 'FAILED',difference=str(difference),tolerance='0',rows=terms,scope=scope,not_standalone=True)
            da=get('cash_flow','Depreciation and amortization')
            if da:da.update(origin='proxy',source_origin='reported',scope='Limited '+scope+' D&A proxy, not complete expense D&A; no extra ROU add-back')
            borrowing=[get('balance',label) for label in ('Short-term borrowings','Long-term debt due within one year','Long-term debt due after one year')]
            named=dict(value=str(sum((D(x['value']) for x in borrowing),D(0))),unit='USD',precision='-6',origin='derived',operands=borrowing,
                scope='Named '+scope+' external borrowing captions; intercompany borrowings and lessee leases separately retained, not complete debt') if all(borrowing) else None
            inputs=dict(revenue=get('income','Total sales and revenues'),ebit=get('income','Operating profit'),depreciation_amortization=da,
                cash_capex=get('cash_flow','Capital expenditures—excluding equipment leased to others','Capital expenditures - excluding equipment leased to others'),
                reported_cash_flow_working_capital_movements=dict(rows=[r for r in terms if r['caption'] in ('Receivables - trade and other','Inventories','Accounts payable','Accrued expenses','Accrued wages, salaries and employee benefits','Customer advances','Other assets—net','Other liabilities—net')],additional_deduction_permitted=False,scope=scope),
                deferred_taxes=get('cash_flow','Provision (benefit) for deferred income taxes'),stock_based_compensation=dict(value=None,scope=scope,reason='Consolidated recognized expense has no verified supplemental expense allocation; Other is not a pure SBC allocation'),
                unclassified_cfo_reconciliation_residual=dict(value=None,disposition='APPROVED_NO_SEPARATE_OPERATION',not_reported_zero=True),reported_cfo=cfo,
                reported_tax_context=dict(provision=get('income','Provision (benefit) for income taxes'),pretax=get('income','Consolidated profit before taxes'),reported_etr=None,generic_denominator_unchanged=True,future_rate_approved=False),
                cash_investment_components=dict(selected=get('balance','Cash and cash equivalents'),other_balances_source_reference='/history_approval/additional_perimeter_evidence/'+str(i),unrestricted_or_excess_cash=False,unknown_restrictions=None),
                debt_lease_components=dict(selected=named,lessee_lease_allocation=None,
                    supporting_limitation='Consolidated lessee detail unallocated; no subtraction/assignment or source-zero inference. Named funding, not complete debt, is the approved operation.',
                    no_additional_adjustment=dict(origin='analyst_assumption',approved=True,value=None,
                        rationale='CAT-FIN expressly approves no unidentified-borrowing adjustment within the separately approved perimeters; potentially omitted financing unbounded, not a reported zero'),
                    issuer_lease_support_reference='/periods/'+str(i)+'/facts',operating_lease_treatment='service_cost',finance_lease_treatment='asset_financing',complete_debt=False),
                other_equity_bridge_claims_assets=dict(nci=get('balance','Noncontrolling interests'),postemployment=get('balance','Liability for postemployment benefits'),
                    financing_assets_reference='/history_approval/additional_perimeter_evidence/'+str(i),no_unidentified_adjustment=dict(origin='analyst_assumption',approved=True,value=None,uncertainty='Potential omitted amounts unbounded; no source zero/immateriality finding')),
                point_in_time_shares=dict(issuer_common_reference='/periods/'+str(i)+'/facts',scope='Shared parent-issuer dated shares/awards, not manufactured segment shares',no_perimeter_allocation=True))
            checklist=[]
            for family in package['periods'][i]['family_checklist']:
                key=family['field'];gap=None
                if key=='stock_based_compensation':gap=inputs[key]['reason']
                elif key=='debt_lease_components' and named is None:gap='Named perimeter funding sources unavailable'
                elif key=='reported_cfo' and difference!=0:gap='Supplemental displayed CFO check failed'
                elif inputs[key] is None:gap='Exact supplemental source row unavailable for '+key
                elif key=='reported_tax_context' and not all((inputs[key]['provision'],inputs[key]['pretax'])):gap='Supplemental tax/pretax scope source incomplete'
                checklist.append(dict(field=key,status='UNRESOLVED_ESSENTIAL_PERIMETER_INPUT' if gap else 'SATISFIED_WITHIN_APPROVED_HISTORICAL_PERIMETER',reason=gap))
            if scope=='eliminations':
                checklist=[dict(field=x['field'],status='CONSOLIDATING_SUPPORT_ONLY_NOT_ASSESSED',reason='Not a separately approved company perimeter') for x in checklist]
            scopes[scope]=dict(inputs=inputs,cfo_reconciliation=proof,checklist=checklist,passed_family_slots=None if scope=='eliminations' else sum(x['reason'] is None for x in checklist),
                analyst_complete=False,scope='Directly disclosed supplemental '+scope+' column; intercompany relationships not removed',
                investing_support_reference='/history_approval/additional_perimeter_evidence/'+str(i),
                remaining_essential_inputs=[] if scope=='eliminations' else [dict(field=x['field'],reason=x['reason']) for x in checklist if x['reason']])
        periods.append(dict(identity=evidence['identity'],perimeters=scopes,analyst_complete=False,consolidated_observations_reference='/periods/'+str(i),consolidated_descriptive_only=True))
    return dict(version=1,authoritative_current_view=True,new_assumptions_active=True,periods=periods,company_completed_for_approved_historical_perimeter=False,
        approved_perimeters=['industrial','financial_products'],eliminations_are_separate_not_a_standalone_company=True,approval_sha256=record['sha256'],
        active_decisions=[dict(decision_id=d['decision_id'],accepted=True,status='APPROVED_EFFECTIVE_VALUE_BLOCKED_BY_PERIMETER_ALLOCATION' if d['decision_id']=='CAT-SBC' else 'ACTIVE_WITH_EXPLICIT_PERIMETER_LIMITATIONS') for d in record['decisions']],
        phase1_closed=False,valuation_consumption_approved=False)


def summary_activation(packages):
    approved=[p for p in packages.values() if 'current_history' in p]
    if not approved:return None
    return dict(companies={p['ticker']:dict(completed=p['current_history']['company_completed_for_approved_historical_perimeter'],active_decisions=p['current_history']['active_decisions'],approval_sha256=p['history_approval']['sha256']) for p in approved},
        original_proposals_retained=True,phase1_closed=False)
