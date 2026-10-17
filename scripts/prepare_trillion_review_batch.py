"""Fixed NVDA/AMZN/META retained review; proposals are not accepted overlays.

Reuses the existing standard-batch source/inspection path. Explicit primary-row
selections below are review data, not a new financial resolver or approval rule.
"""
import json
import re
import sys
from dataclasses import asdict
from decimal import Decimal as D

import prepare_standard_review_batch as shared
from prepare_msft_analyst_package import ROOT, digest, relevant, PROPOSED

BASELINE = 'afd1a2598a790826be5dd1f4beebaf0ea412467a'
REVIEW_TIME = '2026-10-17T17:50:43+00:00'
TICKERS = ('NVDA', 'AMZN', 'META')
SUMMARY = 'docs/company-data-preparation/trillion-review-batch.json'
EXTRA = {
    'productive_cash': ('PaymentsToAcquireProductiveAssets', False),
    'financing_current': ('FinancingObligationsCurrent', True),
    'financing_long': ('FinancingObligationsNoncurrent', True),
    'debt_discount': ('DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet', True),
    'nonmarketable': ('NonmarketableEquitySecuritiesCarryingValue', True),
    'financing_principal_cash': ('RepaymentsOfFinancingObligations', False),
}


def primary_fact(case, item, table, row, column, caption):
    """Bind an actually displayed population, including explicit class dimensions.

    No selection by first tag/value/precision. Callers specify the displayed row
    population; competing observations remain in separate candidate payloads.
    """
    f = case['filing']; a = item['attrs']; prefix, concept = a['name'].split(':')
    context = f.contexts[a['contextref']]; xi = shared.cash._XI
    start = context.findtext(xi+'period/'+xi+'startDate')
    end = context.findtext(xi+'period/'+xi+'endDate') or context.findtext(xi+'period/'+xi+'instant')
    entity = context.findtext('.//'+xi+'identifier')
    if int(entity) != f.period.cik or end != str(f.period.annual_end):
        raise ValueError('Primary population is not selected issuer/year end')
    if start != str(f.period.annual_start):
        raise ValueError('Primary population is not exact annual duration')
    if a.get('format') in ('ixt:fixed-zero','ixt:zerodash'):
        # Explicit tagged/displayed zero only, subsequently matched to a real
        # instance occurrence. Never an absent-value default.
        value=shared.cfo.displayed(item['text'],D(0))
        if value!=0:raise ValueError('Invalid explicit-zero display')
    else:value = shared.inline_amount(a, item['text'])
    if not value.is_finite():raise ValueError('Nonfinite displayed observation')
    matches = [(i,n) for i,n in enumerate(f.root)
        if n.tag == '{'+f.namespaces[prefix]+'}'+concept
        and n.get('contextRef') == a['contextref'] and n.get('unitRef') == a['unitref']
        and n.get('decimals') == a['decimals'] and n.text and D(n.text) == value]
    if not matches: raise ValueError('Displayed population has no exact instance confirmation')
    unit = f.units[a['unitref']]
    measure=unit[0].text if len(unit)==1 and unit[0].tag==shared.cash._XI+'measure' else ''
    prefix_unit,_,local_unit=measure.partition(':')
    if local_unit!='USD' or f.namespaces.get(prefix_unit)!='http://www.xbrl.org/2003/iso4217':
        raise ValueError('Displayed monetary review requires USD')
    dims = [[x.get('dimension'),x.text] for x in context.iter() if x.tag.endswith('}explicitMember')]
    return dict(value=str(value),unit='USD',precision=a['decimals'],origin='reported',
        namespace=f.namespaces[prefix],concept=concept,as_of=end if not start else None,
        scope=caption,occurrence_count=len(matches),occurrences=[dict(ordinal=i,xml_id=n.get('id'),
            context_id=a['contextref'],unit_id=a['unitref'],raw_value=n.text,precision=a['decimals'],
            start=start,end=end,dimensions=dims,primary_locator='inline#'+a['id'],
            primary_display=item['text'],primary_scale=int(a.get('scale','0')),primary_sign=a.get('sign','+'),primary_format=a.get('format')) for i,n in matches],
        primary_table=dict(table=table,row=row,column=column,caption=caption),
        primary_source='primary',instance_source='instance')


def displayed_selection(case, key, concept, captions):
    """Exact reviewed caption/annual population, not automatic precedence."""
    selections=[]; f=case['filing']
    for ti,t in enumerate(case['tables']):
        for ri,row in enumerate(t):
            caption=row[0]['text'].strip() if row else ''
            if caption not in captions: continue
            for ci,cell in enumerate(row):
                for item in cell['facts']:
                    if item['attrs']['name'].split(':')[-1]!=concept: continue
                    try: fact=primary_fact(case,item,ti,ri,ci,caption)
                    except ValueError: continue
                    if any(o['dimensions'] for o in fact['occurrences']): continue
                    selections.append(fact)
    if not selections: return False
    if len({D(x['value']) for x in selections})!=1: raise ValueError('Competing displayed row selections: '+key)
    fact=selections[0];fact['confirming_primary_tables']=[x['primary_table'] for x in selections]
    fact['selection_rationale']='Reviewed exact named statement/note row; not a generic precedence or scope policy'
    f.facts[key]=fact
    return True


def candidates(case, key, concept, instant=False, namespace='us-gaap'):
    f=case['filing']; ns=f.namespaces.get(namespace,namespace)
    result=shared.inspect.inspect(case['evidence'],shared.inspect.SelectionSpec(key,
        (shared.inspect.Selector(ns,concept,()),),'instant' if instant else 'annual','USD',
        'unselected_source_observation','Exact candidate population; economic role/completeness not inferred',()))
    return dict(field_id=key,role=result.specification.role,scope=result.specification.scope,
        candidates=[dict(namespace=c.namespace,concept=c.concept,value=str(c.value),precision=c.precision,
            occurrences=[dict(asdict(o),start=str(o.start) if o.start else None,end=str(o.end),dimensions=list(o.dimensions)) for o in c.occurrences],
            evidence_references=shared.delivery.plain(c.evidence_references)) for c in result.candidates],
        competing_values=[str(v) for v in result.competing_values],unresolved_requirements=list(result.unresolved_requirements))


def manual_meta_reconciliation(case, original):
    """Independent displayed-row check; never changes the shared PARTIAL proof.

    Source explicitly separates restructuring populations by row/caption/dimension.
    Retain those populations, rather than collapsing same-QName facts together.
    """
    if original['status']!='PARTIAL': return None
    pop=original['populations'][0];table=case['tables'][pop['table']];f=case['filing']
    first=next(i for i,r in enumerate(table) if r and r[0]['text'].strip().startswith('Net income'))
    last=next(i for i,r in enumerate(table) if r and r[0]['text'].strip()=='Net cash provided by operating activities')
    rows=[]
    for ri in range(first,last+1):
        row=table[ri]; bound=[]
        for ci,cell in enumerate(row):
            for item in cell['facts']:
                ctx=f.contexts[item['attrs']['contextref']];xi=shared.cash._XI
                if (ctx.findtext(xi+'period/'+xi+'startDate'),ctx.findtext(xi+'period/'+xi+'endDate'))!=(str(f.period.annual_start),str(f.period.annual_end)):continue
                fact=primary_fact(case,item,pop['table'],ri,ci,row[0]['text'].strip())
                # Each displayed current-period cell is its own population; no
                # use of unrelated current-period facts elsewhere in the report.
                display=shared.cfo.displayed(cell['text'],D(0))*D(10)**int(item['attrs'].get('scale','0'))
                bound.append(dict(caption=row[0]['text'].strip(),value=str(display),fact=fact))
        if not bound: continue  # section headings have no monetary facts
        if len(bound)!=1: raise ValueError('Manual displayed row still has multiple populations')
        rows.extend(bound)
    if not rows or rows[-1]['caption']!='Net cash provided by operating activities':raise ValueError('Displayed CFO boundary absent')
    total=sum((D(x['value']) for x in rows[:-1]),D(0));difference=total-D(rows[-1]['value'])
    return dict(status='SUPPORTED' if difference==0 else 'FAILED',basis='Independent selected primary table row inspection, not replacement shared parser result',
        rows=rows[:-1],cfo=rows[-1],row_sum=str(total),difference=str(difference),tolerance='0',
        scope='Consolidated; distinct facilities/data-center restructuring captions retained; no normalization or residual plug')


def passages(f):
    markers=['Depreciation expense includes','Depreciation and amortization expense on property',
        'The following table summarizes','Finance leases are included','Principal repayments of financing obligations',
        'Excluding interest, current financing obligations','no borrowings outstanding','Commercial Paper Programs',
        'stock split','ten-for-one','20 -for-1','four-for-one','useful lives of','Prior Period Reclassifications',
        'restricted cash','retirement','preferred stock','noncontrolling','Groq','non-marketable equity',
        'commercial paper','other short-term credit facilities','borrowings outstanding',
        'Impairment charges for','amortization expense associated with intangible','Finance lease assets']
    result=[]
    for marker in markers:
        matches=list(re.finditer(r'(?<!\w)'+re.escape(marker)+r'(?!\w)',f.text,re.I))
        for m in dict.fromkeys(matches[:2]+matches[-2:]):result.append(dict(marker=marker,offset=m.start(),exact_excerpt=f.text[max(0,m.start()-80):m.end()+1800],source_sha256=f.primary.artifact.sha256))
    return result


def build():
    cases,missing=shared.load(TICKERS);packages={}
    income=json.loads((ROOT/'docs/repaired-income-ledger.json').read_text())
    ledgers={name:json.loads((ROOT/('docs/'+name+'.json')).read_text()) for name in
        ['refreshed-capex-ledger','retained-d-and-a-ledger','retained-reported-tax-context-ledger','retained-claims-shares-ledger']}
    for case in cases:
        f=case['filing'];ticker=case['ticker'];case['tables']=shared.documents.parse(case['record'],improved=True)
        errors=shared.observe(case); alternatives={}
        for key,(co,instant) in EXTRA.items():
            try:shared.monetary(case,key,co,instant,'amzn' if ticker=='AMZN' and key in ('financing_current','financing_long') else 'us-gaap')
            except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
        row=next(r for r in income['rows'] if r['identity']==case['identity'])
        for slot in row['fields']:
            if slot['status'] in ('POPULATED','POPULATED_REPORTED_DIRECT'):
                candidate=slot['candidates'][slot['selected']]
                shared.monetary(case,slot['field'],candidate['concept'],namespace=candidate['namespace'])
        if ticker=='NVDA':
            for key,co,ns,instant in [('combined_investment','PurchasesOfPropertyAndEquipmentAndIntangibleAssets','nvda',False),
                ('marketable_mixed','MarketableSecuritiesAndEquitySecuritiesFVNI','nvda',True),
                ('groq_payment','PaymentsToAcquireBusinessTwoNetOfCashAcquired','us-gaap',False)]:
                try:shared.monetary(case,key,co,instant,ns)
                except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
        if ticker=='AMZN':
            for key,co,dims,as_of in [
                ('cp_note','CommercialPaper',(('us-gaap:DebtInstrumentAxis','us-gaap:CommercialPaperMember'),),None),
                ('working_credit','ShortTermBorrowings',(('us-gaap:DebtInstrumentAxis','amzn:ShortTermCreditFacilitiesWorkingCapitalPurposesMember'),),None),
                ('prior_working_credit','ShortTermBorrowings',(('us-gaap:DebtInstrumentAxis','amzn:ShortTermCreditFacilitiesWorkingCapitalPurposesMember'),),'2021-12-31')]:
                if key=='prior_working_credit' and f.year!=2022:continue
                try:f.fact(key,co,'Disclosed instrument-specific borrowing; not facility capacity or investment asset',instant=True,dimensions=dims,as_of=as_of)
                except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
            for key,co,captions in [
                ('ppe_da','Depreciation',('Consolidated',)),
                ('selected_tax','IncomeTaxExpenseBenefit',('Provision for income taxes','Provision (benefit) for income taxes','Provision (benefit) for income taxes, net','Provision for income taxes, net')),
                ('selected_cash_tax','IncomeTaxesPaidNet',('Cash paid for income taxes, net of refunds',))]:
                displayed_selection(case,key,co,captions);alternatives[key]=candidates(case,key,co)
            for key,co in [('combined_acquisitions','PaymentsToAcquireBusinessesNetOfCashAcquiredAndOther'),
                ('combined_acquisitions_later','PaymentsToAcquireBusinessesNetOfCashAcquiredAndPaymentsToAcquireNonmarketableSecuritiesAndOther'),
                ('debt_cash_interest','InterestPaidOnLongTermDebt')]:
                try:shared.monetary(case,key,co,namespace='amzn')
                except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
        # Source variations remain alternatives even when a narrower displayed
        # row is explicitly selected for this review. Never patch prior ledgers.
        for key in ['da','depreciation','finance_amortization','tax','cash_tax','nonmarketable']:
            co,inst=EXTRA[key] if key in EXTRA else shared.SPECS[key]
            alternatives[key]=candidates(case,key,co,inst)
        rec=shared.delivery.plain(shared.cfo.inspect_statement(case['evidence'],case['record'],version=shared.cfo.IMPROVED_VERSION))
        if rec!=case['proof']['reconciliation']:raise ValueError('Original CFO replay changed')
        manual=manual_meta_reconciliation(case,rec) if ticker=='META' else None
        def calc(key,operands,scope,origin='derived'):
            if any(k not in f.facts for k in operands):return
            f.entry(key,key,operands,status=PROPOSED,origin=origin,scope=scope,rationale='Explicit company review proposal; no user approval or complete population claim')
            f.entries[-1]['formula_version']='retained-trillion-review-v1'
        if ticker=='NVDA':
            if 'combined_investment' not in f.facts and 'productive_cash' in f.facts:f.facts['combined_investment']=dict(f.facts['productive_cash'],scope='PP&E and intangible cash, NOT pure PP&E')
            current='marketable_current' if 'marketable_current' in f.facts else 'marketable_mixed'
            calc('gross_current_financial',['cash',current],'Current financial captions; not excess/unrestricted cash')
            calc('named_financing',['debt_current','debt_long'],'Named term carrying only; finance/license/other financing coverage unproved')
        elif ticker=='AMZN':
            calc('gross_current_financial',['cash','marketable_current'],'Current financial captions, not excess/unrestricted cash')
            calc('limited_expense_da_proxy',['ppe_da','intangible_amortization'],'PP&E depreciation/amortization including finance assets + named intangible expense; content and other scope not exhaustive','proxy')
            calc('named_financing',['debt_current','debt_long','finance_lease','financing_current','financing_long']+(['cp_note'] if 'cp_note' in f.facts else [])+(['working_credit'] if 'working_credit' in f.facts else ['short_borrowing'] if 'short_borrowing' in f.facts else []),
                'Named net term carrying + finance liabilities + separate facility financing + disclosed short borrowing; excludes unbounded unidentified borrowing. Rounded financing note component retained')
        else:
            # Early cash+marketable caption is explicitly reported as its own
            # population; do not reconstruct it from restricted-cash parents.
            try:shared.monetary(case,'current_financial_parent','CashCashEquivalentsAndMarketableSecuritiesAtCarryingValue',True,'fb' if 'fb' in f.namespaces else 'meta')
            except (ValueError,KeyError):pass
            if 'marketable_current' in f.facts:calc('gross_current_financial',['cash','marketable_current'],'Current financial captions, not excess/unrestricted cash')
            else:calc('gross_current_financial',['current_financial_parent'],'Reported current cash and marketable population; restrictions separate')
            calc('named_financing',(['debt_long'] if 'debt_long' in f.facts else [])+['finance_lease'],
                'Named net term carrying where reported + finance lease parent; no missing-to-zero term/debt assumption. FY2021 finance-only is a partial observation')
        ledger_refs={}
        ledger_refs['repaired-income-ledger']=dict(reference='docs/repaired-income-ledger.json#/rows/'+str(income['rows'].index(row)),source_record=row)
        for name,ledger in ledgers.items():
            matches=[(i,r) for i,r in enumerate(ledger['rows']) if r.get('identity')==case['identity']]
            if len(matches)!=1:raise ValueError('Exact preparation ledger join required '+name)
            ledger_refs[name]=dict(reference='docs/'+name+'.json#/rows/'+str(matches[0][0]),source_record=matches[0][1])
        from valuation_platform.analyst.historical_inputs import Field
        decisions_by_family={Field.DA:'DA',Field.CAPEX:'INV',Field.SBC:'SBC',Field.CFO_RESIDUAL:'CF',Field.CF_WORKING_CAPITAL:'CF',Field.CFO:'CF',Field.TAX:'TAX',Field.CASH_INVESTMENTS:'CASH',Field.DEBT_LEASES:'FIN',Field.OTHER_BRIDGE:'CLAIMS',Field.SHARES:'SHARES'}
        checklist=[]
        for field in Field:
            decision=decisions_by_family.get(field)
            status='PROPOSED_PENDING_APPROVAL' if decision else 'SOURCE_SUPPORTED'
            if field is Field.CAPEX and ticker!='NVDA':status='SOURCE_SUPPORTED';decision=None
            if field is Field.TAX and ticker!='AMZN':status='SOURCE_SUPPORTED';decision=None
            if manual and manual['status']!='SUPPORTED' and field in (Field.CFO,Field.CFO_RESIDUAL):status='ESSENTIAL_EXCEPTION'
            keys={Field.REVENUE:['revenue'],Field.EBIT:['ebit'],Field.DA:['da','depreciation','ppe_da','intangible_amortization','finance_amortization'],
                Field.CAPEX:['cash_capex','productive_cash','combined_investment','groq_payment','capital_creditors','noncash_finance_rou','noncash_operating_rou'],
                Field.CF_WORKING_CAPITAL:[],Field.DEFERRED_TAX:['deferred_tax','deferred_movement'],Field.SBC:['sbc_expense','sbc_addback'],
                Field.CFO_RESIDUAL:[],Field.CFO:['cfo'],Field.TAX:['tax','selected_tax','pretax','pretax_equity_scope','reported_etr','cash_tax','selected_cash_tax'],
                Field.CASH_INVESTMENTS:['cash','marketable_current','marketable_mixed','current_financial_parent','nonmarketable','restricted_cash','cash_restricted_parent','equity_method'],
                Field.DEBT_LEASES:['cp_note','working_credit','debt_current','debt_long','debt_parent','debt_discount','short_borrowing','finance_lease','financing_current','financing_long','op_lease','finance_principal_cash'],
                Field.OTHER_BRIDGE:['preferred','nci','pension_net','pension_liability','retirement_expense','nonmarketable','equity_method','equity','total_equity'],
                Field.SHARES:[k for k in f.facts if k.startswith('shares:') or k.startswith('weighted_')]}[field]
            refs=['/facts/'+k for k in keys if k in f.facts]
            refs+=['/preparation_ledger_evidence','/cfo_reconciliation']
            if field in (Field.CFO,Field.CF_WORKING_CAPITAL,Field.CFO_RESIDUAL,Field.DEFERRED_TAX):refs+=['/independent_display_check']
            checklist.append(dict(field=field.value,status=status,pending_decisions=[ticker+'-'+decision] if decision else [],financial_complete=False,evidence_references=refs))
        for key,fact in f.facts.items():
            fact.setdefault('origin','reported')
            fact['role']=('cfo_reconciliation_observation' if key in ('da','sbc_addback','deferred_tax','deferred_movement') else
                'recognized_expense_observation' if key in ('depreciation','intangible_amortization','ppe_da','finance_amortization','sbc_expense') else
                'point_in_time_or_award_observation' if key.startswith('shares:') else 'separate_reported_observation')
            if fact.get('unit')=='pure':fact['display_unit']='ratio'
        for error in errors:
            error['disposition']='superseded_by_exact_review_binding' if error['input_id'] in f.facts else 'unselected_or_unavailable_selector; not proof the financial population is absent'
        period=dict(identity=case['identity'],selection_reference=case['manifest_reference'],prior_population_reference=case['proof_reference'],sources=case['sources'],facts=f.facts,
            calculations=f.entries,source_binding_exceptions=errors,alternatives=alternatives,passages=passages(f),
            preparation_ledger_evidence=ledger_refs,cfo_reconciliation=rec,independent_display_check=manual,
            movement_rows=[x for x in rec['populations'][0]['rows'] if x.get('role')=='displayed_movement'],
            family_checklist=checklist,new_assumptions_active=False,analyst_complete=False,
            original_supporting_unknowns=dict(complete_expense_da=None,pure_ppe_cash=None if ticker=='NVDA' else 'See individually verified cash purchase observation',complete_reinvestment=None,additional_unidentified_borrowing=None,unknown_restrictions=None,operating_reserve=None,unidentified_claims=None),
            cash_sign_multipliers={k:-1 for k in ['cash_capex','productive_cash','combined_investment','groq_payment','acquisition','combined_acquisitions','combined_acquisitions_later','cash_tax','selected_cash_tax','cash_interest','debt_cash_interest','op_cash','finance_interest_cash','finance_principal_cash','financing_principal_cash'] if k in f.facts})
        packages.setdefault(ticker,dict(schema='company-analyst-review-v1',version=1,ticker=ticker,source_commit=BASELINE,review_author='Retained-evidence company review; not user approval',review_recorded_at_utc=REVIEW_TIME,periods=[],new_assumptions_active=False,analyst_complete=False,phase1_closed=False,valuation_consumption_approved=False))['periods'].append(period)
    # The selected2022 report explicitly quantifies the2021 facility balance.
    # Keep this later comparative's source identity, not fabricated2021 provenance.
    amazon=packages['AMZN']['periods'];old=next(r for r in amazon if r['identity']['annual_end']=='2021-12-31');later=next(r for r in amazon if r['identity']['annual_end']=='2022-12-31')
    if 'prior_working_credit' in later['facts']:
        fact=later['facts']['prior_working_credit'];old['supplemental_source_observations']=[dict(fact=fact,source_identity=later['identity'],sources=later['sources'],scope='Later selected filing explicitly reports2021-end facility; not substituted original-period metadata')]
        base=next((x for x in old['calculations'] if x['input_id']=='named_financing'),None)
        if base:old['calculations'].append(dict(input_id='known_facility_expanded_financing',value=str(D(base['value'])+D(fact['value'])),unit='USD',origin='derived',status=PROPOSED,
            operands=['/calculations/named_financing','/supplemental_source_observations/0/fact'],formula='LINEAR_COMPONENTS',formula_version='retained-trillion-review-v1',
            operand_precision=[base.get('precision','See individual source operands'),fact['precision']],scope='Named borrowing plus separately disclosed318 facility; rounded long facility note still limits precision; not complete debt'))
    for t,p in packages.items():
        p['periods'].sort(key=lambda r:r['identity']['annual_end']);p['family_slots']=70
        p['approval_table_reference']=SUMMARY+'#/decisions';p['evidence_acquisition_requirements']=[x for x in missing if x['ticker']==t]
        p['outcomes']={s:sum(c['status']==s for r in p['periods'] for c in r['family_checklist']) for s in ['SOURCE_SUPPORTED','PROPOSED_PENDING_APPROVAL','ESSENTIAL_EXCEPTION']}
        p['review_revision']=digest(relevant(p))
    return packages,missing


def decisions(p):
    t=p['ticker'];rows=p['periods']
    def nums(key,calc=False):
        values=[]
        for r in rows:
            x=next((x for x in r['calculations'] if x['input_id']==key),{}) if calc else r['facts'].get(key,{})
            values.append(str(D(x['value'])/1000000) if x.get('value') is not None else 'unknown')
        return '/'.join(values)+' USDm'
    common=[
        ('CF','Use displayed reported cash movements and independently checked consolidated CFO; no separate residual operation and no second movement deduction.',nums('cfo'),
            'Not operating-only/organic cash or book delta NWC. Preserve mixed/acquisition/FX/reclassification scopes; alternative require separately supported allocations, not balancing items. META original parser remains PARTIAL2022–24; independent caption/dimension-specific display check is separate, no altered legacy result.'),
        ('SBC','Use recognized expense as a labeled historical cost proxy once, preserving CFO add-back differences and awards separately.',nums('sbc_expense'),
            'No double charge, rounded difference adjustment, exercise-cash substitution or forecast dilution. Alternative retain observations without cost-proxy selection.'),
        ('CASH','Select gross current financial captions only; retain restricted, strategic/nonmarketable and long-term holdings separately.',nums('gross_current_financial',True),
            'Not unrestricted/excess cash; unknown restrictions/reserves remain unbounded. Do not add restricted-cash parents to included cash. Alternative defer financial-balance selection until operating reserve policy is designed.'),
        ('CLAIMS','Retain specifically recorded claims/strategic assets and retirement disclosures; propose no additional unidentified preferred/NCI/pension adjustment.',
            'Known source populations and nulls remain separate in facts, candidate and claims-ledger payloads; no invented amount.',
            'Presentation-based analyst omission, not reported zero or immateriality. Potential omitted claims unbounded. Alternative leave that operation unresolved. Combined loss/credit DTA is not a pure-NOL economic asset.'),
        ('SHARES','Select actual dated fiscal-end common populations/classes separately; retain cover counts, EPS denominators and awards without automatic addition.',
            'Exact dates/classes/precision in facts shares:* and claims-shares source records; no new dilution number.',
            'NVDA original2022–24 counts precede2024 ten-for-one split;2022 already reflects2021 four-for-one. AMZN2021 predates2022 twenty-for-one; META A/B voting classes remain separate. Alternative a separately approved comparison restatement; none computed here.')]
    if t=='NVDA':specific=[
        ('DA','Use reported CFO D&A as a limited historical proxy, preserving expense depreciation and finite-lived amortization separately.',nums('da'),
            'Depreciation note includes finance assets; no extra finance add-back.2023 component844+699=1543 versus CFO1544;2025 rounded1300+593=1893 versus1864;2026 rounded2400+488=2888 versus2843. Do not plug differences or certify expense completeness. Alternative retain component observations without an approved complete D&A operation.'),
        ('INV','Approve combined PP&E/intangible purchases as a specifically broader historical investment proxy, NOT pure PP&E cash.',nums('combined_investment'),
            '2022–23 issuer extensions need explicit separate approval as well as2024–26 standard captions. Prior NO-GO for pure PP&E remains. Missing split cannot be inferred from unpaid258/374/170/525/820, assets or acquisition cash263/49/83/1007/1535. FY2026 Groq13000 cash is separate; no sum or acquisition allocation. Alternative pure PP&E remains unresolved with no defensible split.'),
        ('FIN','Retain named net term carrying as financing input, operating leases service; keep license/finance/other populations separate and propose no unidentified borrowing adjustment.',nums('named_financing',True),
            'Finance/license liability allocation and exhaustive borrowing not proved. CP source0 where explicitly tagged cannot establish broader zero. No addition of op lease885/1078/1347/1807/2944 or undiscounted/principal/fair-value alternatives. Alternative require full liability split; no complete-debt claim.')]
    elif t=='AMZN':specific=[
        ('DA','Select PP&E depreciation/amortization plus separately named finite-lived intangible expense as a LIMITED historical expense proxy.',nums('limited_expense_da_proxy',True),
            'PP&E segment-note22909/24924/30225/32067/41860 already includes finance depreciation. Add named intangible512/604/706/838/817 once; no operating ROU/content/other inclusion claim or new frozen equation. Broad CFO34296/41921/48663/52795/65756 remains negatively reviewed/support-only. Alternative rounded PP&E note22900/24900/30200/32100/41900 has different precision; broad CFO is NOT acceptable pure D&A. Content cost/amortization remains in service/content operating perimeter, proposed exclusion from this limited investment proxy; not proved complete expense D&A.'),
        ('INV','Retain approved gross cash equipment purchases separately from proceeds/incentives, cash acquisition/other, finance-lease additions and facility financing.',nums('productive_cash'),
            'Gross, not company non-GAAP net purchases. Proceeds/incentives remain separate source observations, never guessed or netted. No add of financed equipment7061/675/642/854/2911 to cash; no complete reinvestment or content proxy. Alternative explicit later investment perimeter, not a residual.'),
        ('TAX','Select exact displayed provision/cash-tax populations and separately retain before-tax scope/issuer ETR; no generic denominator override.',nums('selected_tax')+'; cash '+nums('selected_cash_tax'),
            'Preserve rounded competing candidates and original generic tax conflicts/nulls; source statement population, not precedence. Pretax38151/-5936/37557/68614/97311 is before-equity-method scope. FY2022 loss denominator does not permit existing positive-denominator ETR. No future rate/clamp; alternative keep all generic required values unresolved.'),
        ('FIN','Use current+noncurrent NET term carrying, finance lease parent, separately recognized facility financing and known short borrowing; exclude operating leases as service.',nums('named_financing',True),
            'Use2021 expanded81427 including318 facility explicitly quantified in the selected2022 comparative; keep that later source identity. Named2021 base81109 excludes318. CP725/6800 then explicit note-zero scope, plus facility1200/147/151/455 in2022–25 remain separate. Do not use gross term parent50553/70542/67182/58000/68836 on top of net components or add finance children again. Facility financing196+6200/266+6700/271+6600/312+7100/358+7800 has rounded long components; include separately, not maturity/interest totals. Unidentified borrowing omission remains proposed/unbounded. Alternative keep financing incomplete; no net-flow inference.')]
    else:specific=[
        ('DA','Use CFO D&A as a limited historical proxy, without extra finance ROU amortization.',nums('da'),
            'Finance assets in PP&E; note expense and CFO differences remain. Finance amortization344/380/349/387/549 is supporting, not incremental. Facilities/data-center impairments are separate mixed populations, not added to D&A. Useful-life changes affect comparisons. Alternative note components remain partial, no subtraction-based amortization.'),
        ('INV','Select gross cash PP&E separately from proceeds, noncash additions, capital creditors and acquisition/investment cash.',nums('cash_capex'),
            '2021 original18567 is not later restated comparative18690. Capital creditors3404/3319/4105/7127/9331 are not cash. Finance principal677/850/1058/1969/2524 not added to cash purchase. Known strategic investments include2025 equity-method7448 and nonmarketable27524; no exhaustive allocation/net reinvestment. Alternative net cash only after explicit proceeds scope, not selected here.'),
        ('FIN','Select named net term carrying where reported plus finance lease parent; operating leases service; propose no additional unidentified borrowing adjustment.',nums('named_financing',True),
            '2021 named581 is finance-only; no debt tag is NOT source zero.2022–25 net term9923/18385/28826/58744 differs from principal10000/18500/29000/59000 by77/115/174/256 issuance costs/discount. Do not add both. Other borrowing unbounded; no present complete-debt certification. Alternative leave incomplete financing operation open.')]
    return [dict(decision_id=t+'-'+key,ticker=t,identities=[r['identity'] for r in rows],recommendation=rec,numerical_effect=number,
        uncertainty_and_alternative=limit,status=PROPOSED,accepted=False,author=p['review_author'],recorded_at_utc=REVIEW_TIME,
        evidence_references=[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json#/periods/{i}' for i in range(5)]) for key,rec,number,limit in common+specific]


def outputs():
    packages,missing=build()
    summary=dict(schema='retained-trillion-review-batch-v1',source_commit=BASELINE,tickers=list(TICKERS),selected_periods=15,family_slots=210,
        companies={t:dict(periods=5,outcomes=p['outcomes'],review_revision=p['review_revision']) for t,p in packages.items()},
        decisions=[x for t in TICKERS for x in decisions(packages[t])],evidence_acquisition_requirements=missing,
        new_sec_requests=0,new_assumptions_active=False,completed_company_packages=3,reviewed_pending_company_packages=6,broad_assessment_only=33,phase1_closed=False)
    return {**{f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json':p for t,p in packages.items()},SUMMARY:summary}


if __name__=='__main__':
    result=outputs()
    if '--check' in sys.argv:
        for path,payload in result.items():
            if (ROOT/path).read_text()!=json.dumps(payload,sort_keys=True,indent=2)+'\n':raise SystemExit('Batch package replay differs: '+path)
        print('Exact NVDA/AMZN/META replay:15 periods/210 families; no new approvals')
    else:print(json.dumps(result,sort_keys=True,indent=2))
