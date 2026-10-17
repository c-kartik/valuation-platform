"""Fixed retained ABBV/MA/CSCO review; proposals, not financial acceptance.

Uses existing receipt/identity, explicit primary-row and policy replay helpers.
No extraction policy, approval registry, retrieval or effective-view change.
"""
import json,re,sys
from collections import Counter
from decimal import Decimal as D
import prepare_standard_review_batch as shared
import prepare_trillion_review_batch as peer
import prepare_large_company_review_batch as prior
from prepare_priority_review_batch import fiscal_focus
from prepare_msft_analyst_package import ROOT,digest,relevant,PROPOSED
from valuation_platform.analyst import retained_reported_tax as tax_policy

BASELINE='94b40c1753c5ed354933028793248ca31052b3db'
REVIEW_TIME='2026-10-17T20:52:33+00:00'
TICKERS=('ABBV','MA','CSCO')
SUMMARY='docs/company-data-preparation/pharma-network-tech-review-batch.json'


def passages(f,t):
    markers={'ABBV':('Amortization expense','depreciation expense','contingent consideration','acquired IPR','in-process research','finance lease','Cerevel','ImmunoGen','pension'),
        'MA':('rebates and incentives','no borrowings outstanding','customer funds','cash and certificates','not recorded','finance lease amortization','operating lease amortization','litigation'),
        'CSCO':('expenses for property and equipment','including impairment charges','Splunk','commercial paper','restructuring charges','restricted cash','52 weeks','53 weeks','defined contribution')}[t]
    out=[]
    # Start at the statements rather than treating hidden XBRL contexts as prose.
    for marker in markers:
        hits=[m for m in re.finditer(re.escape(marker),f.text,re.I) if m.start()>len(f.text)//3]
        for m in dict.fromkeys(hits[:2]+hits[-1:]):out.append(dict(marker=marker,offset=m.start(),exact_excerpt=f.text[max(0,m.start()-100):m.end()+1800],source_sha256=f.primary.artifact.sha256))
    return out


def csco_amortization(case):
    """Exact purchased-intangible TOTAL note, not the smaller opex-only fact.

    Earlier notes explicitly dimension cost-of-sales/opex combined; later notes
    use unclassed competing values. Retain real dimensions and all confirmations.
    """
    found=[]
    for ti,table in enumerate(case['tables']):
        if not any(c['text'].strip()=='Amortization of purchased intangible assets:' for row in table for c in row):continue
        for ri,row in enumerate(table):
            if not row or row[0]['text'].strip()!='Total':continue
            for ci,cell in enumerate(row):
                for item in cell['facts']:
                    if item['attrs']['name'].split(':')[-1]!='AmortizationOfIntangibleAssets':continue
                    try:found.append(peer.primary_fact(case,item,ti,ri,ci,'Total purchased intangible amortization, including source impairment scope'))
                    except ValueError:continue
    if not found or len({D(x['value']) for x in found})!=1:raise ValueError('Exact purchased-intangible total note not bound')
    case['filing'].facts['purchased_amortization_total']=dict(found[0],confirming_primary_tables=[x['primary_table'] for x in found])


def build():
    cases,missing=shared.load(TICKERS);packages={}
    ledgers={n:json.loads((ROOT/('docs/'+n+'.json')).read_text()) for n in prior.LEDGERS+('retained-bridge-component-ledger','retained-tax-sbc-ledger')}
    for case in cases:
        t=case['ticker'];f=case['filing'];focus=fiscal_focus(case)
        case['tables']=shared.documents.parse(case['record'],improved=True)
        errors=shared.observe(case);prior.prepare_income(case,prior.ledger_row(ledgers['repaired-income-ledger'],case['identity'])[1])
        def bind(key,co,instant=False,ns='us-gaap'):
            try:shared.monetary(case,key,co,instant,ns)
            except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc),disposition='Unselected selector, not an economic zero or proof of unavailable disclosure'))
        def displayed(key,co,captions,instant=False):
            try:
                if not peer.displayed_selection(case,key,co,captions,instant=instant):raise ValueError('Exact reviewed displayed population unavailable')
            except ValueError as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
        common={**prior.EXTRA,'combined_da':('DepreciationAndAmortization',False),'da_accretion':('DepreciationAmortizationAndAccretionNet',False),
            'debt_current_parent':('DebtCurrent',True),'debt_carrying_parent':('DebtAndCapitalLeaseObligations',True),
            'debt_carrying_combined':('DebtLongtermAndShorttermCombinedAmount',True),'impairment':('AssetImpairmentCharges',False),
            'contingent_liability':('BusinessCombinationContingentConsiderationLiability',True),
            'contingent_cash_financing':('PaymentForContingentConsiderationLiabilityFinancingActivities',False),
            'contingent_cash_operating':('PaymentForContingentConsiderationLiabilityOperatingActivities',False),
            'contingent_current':('BusinessCombinationContingentConsiderationLiabilityCurrent',True),
            'contingent_noncurrent':('BusinessCombinationContingentConsiderationLiabilityNoncurrent',True),
            'contingent_fair_value_change':('BusinessCombinationContingentConsiderationArrangementsChangeInAmountOfContingentConsiderationLiability1',False),
            'intangible_impairment':('ImpairmentOfIntangibleAssetsExcludingGoodwill',False),
            'strategic_equity':('EquitySecuritiesWithoutReadilyDeterminableFairValueAmount',True),
            'restricted_noncurrent_cash':('RestrictedCashAndCashEquivalentsNoncurrent',True),
            'preferred_outstanding':('PreferredStockValueOutstanding',True)}
        for key,(co,instant) in common.items():bind(key,co,instant)
        if t=='ABBV':
            displayed('cfo_intangible_amortization','AmortizationOfIntangibleAssets',('Amortization of intangible assets',))
            displayed('investment_cash','PaymentsToAcquireOtherInvestments',('Other acquisitions and investments','Other acquisitions and investments, net of cash acquired'))
            bind('iprd_expense','ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff')
            displayed('iprd_expense','ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff',('Acquired IPR&D','Acquired IPR&D and milestones'))
            for key,co,instant in [('upfront_collaboration_adjustment','UpfrontCostsRelatedToCollaborations',False),('financing_liability','NoncurrentFinancingLiability',True),('mixed_litigation_adjustment','NonCashLitigationReserveAdjustmentsNetOfCashPayments',False)]:bind(key,co,instant,'abbv')
        if t=='MA':
            displayed('face_revenue','Revenues',('Net revenue',))
            displayed('expense_da','DepreciationAndAmortization',('Depreciation and amortization',))
            for key,co,instant in [('current_financial_investments','Investments',True),('customer_collateral_asset','DepositsAssetsCurrent',True),('customer_collateral_liability','ContractWithCustomerLiabilityCurrent' if f.year<=2022 else 'DepositLiabilityCurrent',True),('settlement_asset','SettlementAssets',True),('settlement_liability','SettlementObligations',True),('litigation_current','LitigationReserveCurrent',True)]:bind(key,co,instant)
            bind('rebates','RevenueRebatesAndIncentives',ns='ma')
            bind('gross_revenue','RevenueFromContractWithCustomerExcludingAssessedTax')
            bind('settlement_asset','SettlementDueFromCustomers',True,'ma')
            bind('settlement_liability','SettlementDueToCustomers',True,'ma')
            bind('litigation_restricted','RestrictedCashAndCashEquivalentsAtCarryingValue',True)
        if t=='CSCO':
            bind('mixed_cfo_da','DepreciationAmortizationAndOther',ns='csco')
            bind('acquisition_net_divestitures','PaymentsToAcquireBusinessesNetOfCashAcquiredAndNetOfDivestitures')
            try:csco_amortization(case)
            except ValueError as exc:errors.append(dict(input_id='purchased_amortization_total',value=None,reason=str(exc)))
            displayed('face_short_debt','DebtCurrent',('Short-term debt',),True)
        # Exact plan populations remain separate from net/gross parent captions.
        for node in f.root:
            co=node.tag.split('}')[-1]
            if co not in ('DefinedBenefitPlanFundedStatusOfPlan','DefinedBenefitPlanAmountsRecognizedInBalanceSheet','PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent','DefinedBenefitPlanAssetsForPlanBenefitsNoncurrent','BusinessCombinationContingentConsiderationLiability'):continue
            ctx=f.contexts.get(node.get('contextRef'));dims=tuple((x.get('dimension'),x.text) for x in ctx.iter() if x.tag.endswith('}explicitMember')) if ctx is not None else ()
            if not dims or len(dims)>2:continue
            key='claim:'+co+':'+digest(dims)[:8]
            if key in f.facts:continue
            try:f.fact(key,co,'Exact plan funded/gross population; overlapping amounts not additive',instant=True,dimensions=dims)
            except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
        rec=shared.delivery.plain(shared.cfo.inspect_statement(case['evidence'],case['record'],version=shared.cfo.IMPROVED_VERSION))
        if rec!=case['proof']['reconciliation']:raise ValueError('Original displayed CFO proof changed')
        pop=rec['populations'][0];detail=(pop.get('hierarchy_proof') or {}).get('children',pop['rows'])
        captions={'ABBV':('Accounts receivable','Inventories','Prepaid expenses and other assets','Accounts payable and other liabilities','Income tax assets and liabilities, net'),
            'MA':('Accounts receivable','Income taxes receivable','Settlement assets','Prepaid expenses','Accrued litigation and legal settlements','Restricted security deposits held for customers','Accounts payable','Settlement obligations','Accrued expenses','Long-term taxes payable','Net change in other assets and liabilities'),
            'CSCO':('Accounts receivable','Inventories','Financing receivables','Other assets','Accounts payable','Income taxes, net','Accrued compensation','Deferred revenue','Other liabilities')}[t]
        movements=[x for x in detail if x['caption'] in captions]
        tax_result,tax_replay=tax_policy.package(case['evidence'])
        tax_replay['issuer']=t
        old_tax=prior.ledger_row(ledgers['retained-reported-tax-context-ledger'],case['identity'])[1]
        if tax_replay!=old_tax:
            def differences(x,y,path=''):
                if type(x)!=type(y):return [path+': type']
                if isinstance(x,dict):return [path+': keys'] if set(x)!=set(y) else [v for k in x for v in differences(x[k],y[k],path+'/'+k)]
                if isinstance(x,list):return [path+': length'] if len(x)!=len(y) else [v for i in range(len(x)) for v in differences(x[i],y[i],path+'/'+str(i))]
                return [] if x==y else [path+': '+str(x)[:80]+' != '+str(y)[:80]]
            raise ValueError('Existing tax policy replay differs '+t+str(f.year)+' '+str(differences(tax_replay,old_tax)[:5]))
        def calc(key,ops,scope,origin='derived',coefficients=None):
            if any(k not in f.facts for k in ops):return
            f.entry(key,key,ops,coefficients,status=PROPOSED,scope=scope,origin=origin,completeness='partial_named_population_only',rationale='Inactive exact company proposal, not a generic policy or completeness approval')
            f.entries[-1]['formula_version']='pharma-network-tech-review-v1'
        calc('limited_da_proxy',['depreciation','cfo_intangible_amortization'] if t=='ABBV' else ['expense_da'] if t=='MA' else ['da','purchased_amortization_total'],
            'ABBV precise separate CFO components; MA face expense; CSCO rounded PPE expense plus total purchased amortization including source impairment. No extra ROU/other add-back; not complete expense certification','proxy')
        calc('current_financial_captions',['cash','current_investments'] if t!='MA' else ['cash','current_financial_investments'],
            'Named gross current corporate cash/investment captions, not unrestricted/excess; restricted/strategic and customer collateral populations separate')
        financing=['debt_finance_current','debt_finance_long']+(['short_borrowing'] if 'short_borrowing' in f.facts else []) if t=='ABBV' else ['debt_current','debt_long'] if t=='MA' else ['face_short_debt','debt_long']
        calc('named_financing',financing,'Named carrying captions; current maturities/embedded finance once; ABBV2024 unidentified short scope remains unknown, not zero; no complete debt certification')
        for k,v in f.facts.items():
            v.setdefault('origin','reported');v['role']='cfo_reconciliation_observation' if k in ('cfo_intangible_amortization','sbc_addback','mixed_cfo_da','da_accretion','deferred_movement') else 'recognized_expense_observation' if k in ('expense_da','sbc_expense','purchased_amortization_total','iprd_expense') else 'separate_reported_observation'
            if k=='depreciation' and t=='ABBV':v['role']='cfo_reconciliation_observation'
            if k=='da' and t=='CSCO':v['role']='rounded_property_expense_observation'
        references={}
        for name,ledger in ledgers.items():
            i,row=prior.ledger_row(ledger,case['identity']);references[name]=dict(reference='docs/'+name+'.json#/rows/'+str(i),record_sha256=digest(row))
        from valuation_platform.analyst.historical_inputs import Field
        policy={Field.REVENUE:'REV',Field.DA:'DA',Field.CAPEX:'INV',Field.CFO:'CF',Field.CF_WORKING_CAPITAL:'CF',Field.CFO_RESIDUAL:'CF',Field.DEFERRED_TAX:'CF',Field.SBC:'SBC',Field.TAX:'TAX',Field.CASH_INVESTMENTS:'CASH',Field.DEBT_LEASES:'FIN',Field.OTHER_BRIDGE:'CLAIMS',Field.SHARES:'SHARES'}
        checklist=[]
        for field in Field:
            required=[] if field==Field.EBIT or field==Field.REVENUE and t!='MA' else [t+'-'+policy[field]]
            status='PROPOSED_PENDING_APPROVAL' if required else 'SOURCE_SUPPORTED'
            if field==Field.CFO and rec['status']!='SUPPORTED':status='ESSENTIAL_EXCEPTION'
            if field==Field.DA and not any(c['input_id']=='limited_da_proxy' for c in f.entries):status='ESSENTIAL_EXCEPTION'
            checklist.append(dict(field=field.value,status=status,pending_decisions=required,financial_complete=False))
        notes=prior.note_rows(case)
        caps=re.compile(r'^(Net revenue|Gross revenue|Rebates|Settlement|Customer|Restricted|Deposits|Contingent|Acquired|In.process|Impairment|Total debt|Long.term debt|Short.term debt|Amortization|Total|Cost of sales|Operating expenses|Pension|Noncontrolling)',re.I)
        for ti,table in enumerate(case['tables']):
            for ri,row in enumerate(table):
                caption=row[0]['text'].strip() if row else ''
                if caps.search(caption):notes.append(dict(table=ti,row=ri,caption=caption,header=' | '.join(c['text'] for r in table[:3] for c in r),cells=row,source_sha256=f.primary.artifact.sha256,role='Supporting source table incl comparatives/dimensions, not automatic selected facts'))
        period=dict(identity=case['identity'],fiscal_year=focus['fiscal_year'],fiscal_year_evidence=focus,selection_reference=case['manifest_reference'],prior_population_reference=case['proof_reference'],
            sources=case['sources'],facts=f.facts,calculations=f.entries,source_binding_exceptions=errors,cfo_reconciliation=rec,movement_rows=movements,
            reported_tax_policy_replay=tax_replay,supporting_note_rows=notes,passages=passages(f,t),preparation_ledger_evidence=references,
            alternatives={k:peer.candidates(case,k,co,inst) for k,co,inst in [('revenue_contract','RevenueFromContractWithCustomerExcludingAssessedTax',False),('revenue_total','Revenues',False),('intangible_amortization','AmortizationOfIntangibleAssets',False),('cash','CashAndCashEquivalentsAtCarryingValue',True),('sbc','ShareBasedCompensation',False)]},
            family_checklist=checklist,new_assumptions_active=False,analyst_complete=False,
            proposed_selections=dict(revenue='face_revenue' if t=='MA' else 'revenue',sbc='sbc_expense' if 'sbc_expense' in f.facts else 'sbc_addback',capex='cash_capex'),
            original_supporting_unknowns=dict(complete_expense_da=None,complete_reinvestment=None,additional_unidentified_borrowing=None,unknown_restrictions=None,operating_reserve=None,unidentified_claims=None,complete_lease_cash=None),
            cash_sign_multipliers={k:-1 for k in ('cash_capex','acquisition','acquisition_net_divestitures','iprd_cash','cash_tax','cash_tax_gross','finance_principal_cash','op_cash') if k in f.facts})
        period['cash_sign_multipliers'].update({k:-1 for k in ('investment_cash','contingent_cash_financing','contingent_cash_operating') if k in f.facts})
        period['population_relationships']=[dict(parent='debt_carrying_parent',components=['debt_finance_current','debt_finance_long'],relationship='confirming_partition_not_additive_to_parent'),
            dict(parent='debt_carrying_parent',components=['finance_lease','financing_liability'],relationship='already_included_where_disclosed_do_not_add'),
            dict(parent='contingent_fair_value_parent',components=[k for k in f.facts if k.startswith('claim:BusinessCombinationContingentConsiderationLiability')]+['contingent_current','contingent_noncurrent'],relationship='measurement_and_current_noncurrent_overlap_no_new_sum')] if t=='ABBV' else [
            dict(parent='debt_carrying_combined',components=['debt_current','debt_long'],relationship='confirming_partition_not_additive_to_parent'),
            dict(parent='customer_collateral_asset',components=['customer_collateral_liability'],relationship='offsetting_customer_population_not_free_corporate_cash_or_extra_debt'),
            dict(parent='expense_da',components=['finance_amortization'],relationship='finance_amortization_already_included_no_second_addition')] if t=='MA' else [
            dict(parent='face_short_debt',components=['debt_current','cp'],relationship='current_maturities_CP_overlap_do_not_add'),
            dict(parent='purchased_amortization_total',components=['intangible_amortization'],relationship='opex_only_or_competing_note_population_not_additive'),
            dict(parent='current_financial_parent',components=['cash','current_investments'],relationship='different_reported_scope_or_conflicting_parent_not_assumed_equivalent',status='SUPPORTING_REVIEW_LIMITATION')]
        packages.setdefault(t,dict(schema='company-analyst-review-v1',version=1,ticker=t,source_commit=BASELINE,review_author='Retained company review, no user acceptance',review_recorded_at_utc=REVIEW_TIME,periods=[],new_assumptions_active=False,analyst_complete=False,phase1_closed=False,valuation_consumption_approved=False))['periods'].append(period)
    for t,p in packages.items():
        p['periods'].sort(key=lambda r:r['identity']['annual_end']);p.update(family_slots=70,outcomes=dict(Counter(c['status'] for r in p['periods'] for c in r['family_checklist'])),approval_table_reference=SUMMARY+'#/decisions',evidence_acquisition_requirements=[x for x in missing if x['ticker']==t]);p['review_revision']=digest(relevant(p))
    return packages,missing


def decisions(p):
    t=p['ticker']
    def nums(key,calc=False):
        out=[]
        for r in p['periods']:
            v=next((x for x in r['calculations'] if x['input_id']==key),{}) if calc else r['facts'].get(key,{})
            out.append(str(D(v['value'])/1000000) if v.get('value') is not None else 'unknown')
        return '/'.join(out)+' USDm'
    da={'ABBV':('Select separate precise CFO depreciation + intangible amortization as a LIMITED historical proxy; exclude separate impairment/IPR&D/fair-value changes.',
        'Exact CF amortization differs from rounded note expense; explicit reviewed caption selection, not a tolerance. Internal software included in depreciation; complete expense D&A/finance amortization remains unknown. Alternative rounded note amortization gives a different lower-precision proxy; no rounding plug or finance ROU addition.'),
        'MA':('Select face-statement D&A expense under its exact scope, not the equal-value accretion-inclusive CFO concept as an interchangeable generic policy.',
        'Source expressly includes finance amortization here and operating lease amortization in G&A. No extra ROU or customer-incentive amortization. Alternative CFO caption retains broader semantic scope; equality is not general equivalence. Complete all-population expense coverage not certified.'),
        'CSCO':('Select rounded PP&E D&A expense + reviewed total purchased-intangible amortization as a LIMITED impairment-inclusive historical proxy.',
        'Purchased-intangible note total includes cost-of-sales and opex, and explicitly includes impairment charges. Nondimensional opex-only amortization is NOT the total. Rounded PP&E includes software; proposed non-overlap follows separate asset populations, not a claim of pure/complete D&A. Retain broad CFO Depreciation, amortization, and other as support only. Alternative that broader CFO proxy '+nums('mixed_cfo_da')+' includes unallocated other costs; do not infer the difference is amortization, remove impairments by guess, or add either proxy to CFO.')}
    inv={'ABBV':'Keep PP&E '+nums('cash_capex')+', business acquisitions '+nums('acquisition')+', investing other investments '+nums('investment_cash')+', acquired-IPR&D expense '+nums('iprd_expense')+' and collaboration reconciliation '+nums('upfront_collaboration_adjustment')+' distinct. FY2021 collaboration caption is broader; later comparatives must not replace it.2024 acquisitions and2025 investing-caption net-of-acquired-cash boundary remain. Contingent fair-value changes are noncash; operating/financing payments and liability measurements differ.',
         'MA':'Cash PP&E is distinct from business acquisitions, capitalized software, customer incentives, and collateral/settlement movements. Customer-incentive amortization is a revenue/cost-perimeter observation, not D&A or an extra investment deduction.',
         'CSCO':'Keep cash PP&E, acquisition cash net of divestitures in early years versus later net-of-cash-acquired captions, restricted escrow, noncash ROU and purchased intangibles distinct. Splunk FY2024 changes scope/financing and amortization; no recast splice or normalized acquisition subtraction.'}
    cash={'ABBV':'Separate strategic nonmarketable holdings and restrictions. No unrestricted/excess claim or invented operating reserve.',
          'MA':'Exclude separately captioned customer collateral and litigation/other restricted funds from additions to corporate cash. Customer cash/CD collateral fully offsets its liability; settlement receivables/payables are operating-network populations, not free cash/debt. Litigation restricted cash alone misses other restricted22/31/32m in2021–23. Do not subtract captions already outside selected cash twice.',
          'CSCO':'Current Investments are classified by availability for operations, not proof all mature within one year. Separate nonmarketable/strategic holdings, customer financing and restricted escrow; broad CFO cash/restricted parent is NOT the face cash selection.'}
    fin={'ABBV':'Current/noncurrent carrying parent already contains finance leases34/34/42/40/41 and later financing liability328/378. Contractual maturity principal and fair-value observations are alternatives, not additional debt. Include separately reported short borrowing14/1/0/unknown/2499 where bound;2025 CP499 plus term loan2000 is already within2499. FY2024 unquantified short borrowing is an expressly proposed omission, not CP-zero proof of broader absence.',
         'MA':'Named debt current+noncurrent equals note carrying parent. All five filings affirm no outstanding CP/credit-facility borrowing within those named programs; this is not proof of no other financing or complete finance-lease coverage. Operating liabilities remain separate, finance amortization already in expense D&A. Client deposits/settlement obligations are not another corporate borrowing addition.',
         'CSCO':'Face DebtCurrent contains current maturities and CP; do not add note current long-term debt or CP a second time. Named face current+noncurrent carrying subtotal, with source lease liabilities separate. Missing separately quantified finance leases is not zero or proved inclusion. Restricted escrow and acquisition funding differ; no cash-flow-net-to-ending-balance inference.'}
    claims={'ABBV':'Retain contingent fair-value parents14887/16384/19890/21666/25374, current/noncurrent and Level3 confirmations without addition; FY2021 current subamount unavailable, not a subtraction-derived fact. Noncurrent pension/OPEB3153/1638/1538/1234/1410, NCI28/33/37/39/42 and litigation/settlement overlaps remain. Fair-value CFO adjustment is neither the ending claim nor cash payment.',
            'MA':'Retain litigation840/1094/723/930/800, NCI71/58/46/30/9 and separately reported redeemable populations. Pension surplus92/38/29/44/47 does not erase underfunded individual plans; gross assets/liabilities and OPEB overlap, never a net deduction. Later OPEB described immaterial is not a zero or valuation materiality finding. Client collateral paired liabilities are separate from litigation claims.',
            'CSCO':'Retain pension/retirement disclosures, unrecognized tax benefits, litigation, customer-financing receivables, guarantees and investment populations with source measurement/overlap. No unidentified preferred/NCI/pension deduction beyond named claims is a proposed omission, not absence proved by authorization, non-disclosure or an audit opinion.'}
    rows=[('CF','Use reported CFO and independently reconciled displayed movements; no separate residual operation or second movement deduction.',nums('cfo'),
        'CFO is consolidated, not organic/unlevered cash or cash delta NWC. Preserve mixed/acquisition/tax/client populations and signs; no allocation, residual plug or requirement for reconstructed complete book NWC. Alternative operating-only rows require unavailable allocations; retain their nulls.'),
        ('DA',da[t][0],nums('limited_da_proxy',True),da[t][1]),
        ('INV','Select narrow cash PP&E outflow; keep acquisition/noncash/other investing populations separate.',nums('cash_capex')+' payment magnitudes, effective cash sign -1',
         inv[t]+' No complete reinvestment sum or inferred allocation. Alternative broader investment perimeter requires separately approved allocation/timing, not an automatically netted amount.'),
        ('SBC','Select recognized expense as a labeled historical cost proxy once, with source CFO add-back retained separately.',nums('sbc_expense')+' expense; addback '+nums('sbc_addback'),
         'Preserve source differences, capitalization/awards and withholding cash. No duplicate charge, rounding plug, award valuation or automatic dilution. If pure expense cannot bind, leave the proxy unresolved rather than silently use another role.'),
        ('TAX','Retain reported provision, actual cash taxes and unchanged policy-replayed Pretax/ETR as historical accounting context.',nums('tax')+' provision; cash net '+nums('cash_tax')+'; gross '+nums('cash_tax_gross'),
         'MA first three exact curated Pretax approvals replay with original metadata/review requirements; later direct scope stays separate. This does not approve generic equity-method scope equivalence. Tax provision, deferred reconciliation, tax cash movements and cash payments differ; no new rate, clamp or forecast assumption. Alternative leave future operating tax entirely deferred.'),
        ('CASH','Select named gross corporate current financial captions, not unrestricted/excess cash.',nums('current_financial_captions',True),cash[t]+' Unknown restrictions/reserves remain unbounded. Alternative a narrower cash-only population '+nums('cash')+' excludes the stated investment component; no invented reserve or blanket maturity equivalence.'),
        ('FIN','Operating leases as service costs; finance leases as asset financing; select named carrying financing with no additional unidentified borrowing adjustment only if approved.',nums('named_financing',True),
         fin[t]+' Omitted exposure remains unquantified/unbounded, not a reported zero or immateriality finding. Alternative retain additional operation unresolved; no complete-debt certification.'),
        ('CLAIMS','Retain named claims/assets with measurement and parent/child overlaps; propose no additional unidentified/pension adjustment beyond named source populations.',
         'Known disclosed claims remain visible, no valuation deduction or new numerical zero.',claims[t]+' Potential undisclosed claim size is unbounded. Alternative leave omission operation unapproved; no arbitrary materiality threshold or exhaustive claims assertion.'),
        ('SHARES','Select actual fiscal-end common populations where bound; otherwise actual cover-date classes, retaining all class/date/EPS/award populations separately.',
         'Exact counts/dates/classes and precision in facts/shares:*; no automatic class or award sum.',
         'Not weighted-average or diluted closing shares. MA A/B economic and conversion distinctions survive; ABBV class dimensions and CSCO exact fiscal-calendar/cover dates remain. No forecast dilution/award valuation. Alternative later cover date is not a fiscal-end replacement.')]
    if t=='MA':rows.insert(0,('REV','Select exact face Net revenue after rebates/incentives for consolidated history; preserve gross/rebate alternatives and generic ambiguity.',nums('face_revenue')+' versus gross '+nums('gross_revenue')+'; rebates '+nums('rebates'),
        'FY2021 gross29845 less rebates10961 = face18884. Face net is consistent with reported EBIT and recognition policy. Gross is a meaningful network-volume/rebate perimeter, not equivalent Revenue; would require a consistent gross-cost presentation. No generic conflict cleared or resolver precedence changed.'))
    return [dict(decision_id=t+'-'+key,ticker=t,identities=[r['identity'] for r in p['periods']],recommendation=rec,numerical_effect=n,uncertainty_and_alternative=alt,
        status=PROPOSED,accepted=False,author=p['review_author'],recorded_at_utc=REVIEW_TIME,evidence_references=[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json#/periods/{i}' for i in range(5)]) for key,rec,n,alt in rows]


def outputs():
    import activate_company_review_batches as accepted
    packages,missing=build()
    summary=dict(schema='retained-pharma-network-tech-review-batch-v1',source_commit=BASELINE,tickers=list(TICKERS),selected_periods=15,family_slots=210,
        companies={t:dict(periods=5,outcomes=p['outcomes'],review_revision=p['review_revision']) for t,p in packages.items()},decisions=[d for t in TICKERS for d in decisions(packages[t])],
        evidence_acquisition_requirements=missing,new_sec_requests=0,new_assumptions_active=False,completed_company_packages=16,approved_partial_company_packages=2,pending_review_company_packages=3,broad_assessment_only=21,phase1_closed=False)
    packages={t:accepted.load_if_approved(f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json',p,summary['decisions']) for t,p in packages.items()}
    activation=accepted.summary_activation(packages)
    if activation:
        complete=sum(x['completed'] for x in activation['companies'].values())
        activation['current_company_counts']=dict(broadly_assessed=42,completed_scoped=16+complete,approved_partial=2+len(activation['companies'])-complete,pending_reviews=3-len(activation['companies']),assessment_only=21)
        summary['approval_activation']=activation
    return {**{f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json':p for t,p in packages.items()},SUMMARY:summary}


if __name__=='__main__':
    result=outputs()
    if '--check' in sys.argv:
        for path,payload in result.items():
            if (ROOT/path).read_text()!=json.dumps(payload,sort_keys=True,indent=2)+'\n':raise SystemExit('Company review differs: '+path)
        print('Exact ABBV/MA/CSCO replay:15 annuals/210 families; current approval activation separately recorded')
    else:print(json.dumps(result,sort_keys=True,indent=2))
