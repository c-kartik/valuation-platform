"""One retained LRCX/PLTR/AMAT review; company proposals, never acceptance.

Source receipt, exact population, arithmetic and policy checks reuse prior batch
helpers. No retrieval, new normalization policy or effective overlay is added.
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

BASELINE='67545e76752a42c4800aa32b10445441a09366f1'
REVIEW_TIME='2026-10-17T21:23:08+00:00'
TICKERS=('LRCX','PLTR','AMAT')
SUMMARY='docs/company-data-preparation/semiconductor-software-review-batch.json'

MARKERS={
 'LRCX':('amortization of finance lease','amortization is included','capital expenditures and intangible','deferred compensation plan','participants','no outstanding borrowings','ten-for-one','stock split','53 weeks','not material','postretirement','Government Assistance'),
 'PLTR':('capitalization','Software Development Costs','Strategic Commercial Contracts','privately-held','gold bars','no outstanding debt','no debt outstanding','voting rights','convertible','49.999999','Legal Proceedings','restricted cash','financing component','stock-based compensation'),
 'AMAT':('depreciation expense','amortization expense','Capital expenditure related incentives','Government Assistance','software','finance leases','No amounts were outstanding','commercial paper','defined and postretirement','postretirement benefit','non-marketable','strategic','53 weeks','inventory','inventories')}

def passages(f,t):
    out=[]
    for marker in MARKERS[t]:
        hits=list(re.finditer(re.escape(marker),f.text,re.I))
        for m in dict.fromkeys(hits[:1]+hits[-2:]):
            out.append(dict(marker=marker,offset=m.start(),exact_excerpt=f.text[max(0,m.start()-100):m.end()+1700],source_sha256=f.primary.artifact.sha256))
    return out


def build():
    cases,missing=shared.load(TICKERS);packages={}
    ledgers={n:json.loads((ROOT/('docs/'+n+'.json')).read_text()) for n in prior.LEDGERS+('retained-bridge-component-ledger','retained-tax-sbc-ledger')}
    for case in cases:
        t=case['ticker'];f=case['filing'];focus=fiscal_focus(case)
        case['tables']=shared.documents.parse(case['record'],improved=True)
        errors=shared.observe(case)
        prior.prepare_income(case,prior.ledger_row(ledgers['repaired-income-ledger'],case['identity'])[1])
        def bind(key,co,instant=False,ns='us-gaap'):
            try:shared.monetary(case,key,co,instant,ns)
            except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc),disposition='Unselected/absent selector; not an economic zero or claim of absent disclosure'))
        def displayed(key,co,captions,instant=False):
            try:
                if not peer.displayed_selection(case,key,co,captions,instant=instant):raise ValueError('Exact reviewed displayed population unavailable')
            except ValueError as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
        extra={**prior.EXTRA,'combined_da':('DepreciationAndAmortization',False),
          'productive_cash':('PaymentsToAcquireProductiveAssets',False),'face_investments':('Investments',True),
          'strategic_equity':('EquitySecuritiesWithoutReadilyDeterminableFairValueAmount',True),
          'cash_tax_refund':('IncomeTaxesRefunded',False),'debt_fair_value':('LongTermDebtFairValue',True),
          'investment_purchases':('PaymentsToAcquireInvestments',False),'inventory_transfers':('InventoryTransferredToPropertyPlantAndEquipment',False),
          'benefit_liabilities':('PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent',True),
          'capitalized_software_cash':('PaymentsToDevelopSoftware',False),
          'accrued_compensation_caption':('DeferredCompensationLiabilityCurrent',True)}
        for k,(co,inst) in extra.items():bind(k,co,inst)
        if t=='LRCX':
            displayed('sbc_note_expense','ShareBasedCompensation',('Equity-based compensation expense',))
            bind('inventory_transfers','TransferOfInventoryToPropertyAndEquipment',ns='lrcx')
            end=f.period.annual_end;date_text=end.strftime('%B')+' '+str(end.day)+', '+str(end.year)
            for key,phrase in [('deferred_plan_obligation','the liability of the Company to the plan participants was'),('deferred_plan_investments','the Company had investments in the aggregate amount of')]:
                matches=list(re.finditer(r'As of '+re.escape(date_text)+r'.{0,150}?'+re.escape(phrase)+r' \$ ([\d,.]+) million',f.text,re.I))
                if len(matches)!=1:raise ValueError('Exact selected-date deferred-plan prose not unique '+key+str(f.year))
                m=matches[0];raw=m.group(1).replace(',','');value=D(raw)*1000000
                f.facts[key]=dict(value=str(value),unit='USD',precision='-5',as_of=str(end),origin='reported',representation='primary_note_prose_not_XBRL',occurrences=[],occurrence_count=0,display_value=raw,display_unit='USD millions',
                    scope='Note16 unfunded plan liability across accrued/other liabilities' if key=='deferred_plan_obligation' else 'Note16 correlated investments within Other assets, not free current cash',
                    note_evidence=dict(offset=m.start(),exact_excerpt=m.group(),source_url=f.primary.artifact.url,source_sha256=f.primary.artifact.sha256,raw_display=raw,display_scale=6))
        if t=='PLTR':
            displayed('face_tax','IncomeTaxExpenseBenefit',('Provision for (benefit from) income taxes','Provision for income taxes'))
            # Actual face row is explicit; preserve rounded same-context note
            # alternatives and unchanged generic tax conflict independently.
            displayed('face_debt','LongTermDebtNoncurrent',('Long-term debt',),True)
            if 'face_debt' not in f.facts:displayed('face_debt','LongTermDebt',('Long-term debt',),True)
            bind('noncash_operating_cost','NoncashOperatingLeaseCost',ns='pltr')
            bind('alternative_investment_cash','PurchasesOfAlternativeInvestments',ns='pltr')
            for key,captions in [('restricted_note_current',('Restricted cash','Restricted cash included in prepaid expenses and other current assets')),('restricted_note_noncurrent',('Restricted cash, noncurrent','Restricted cash included in other assets'))]:
                found=[]
                for ti,table in enumerate(case['tables']):
                    for ri,row in enumerate(table):
                        if not row or row[0]['text'].strip() not in captions:continue
                        caption=row[0]['text'].strip()
                        for ci,cell in enumerate(row):
                            for item in cell['facts']:
                                if item['attrs']['name'].split(':')[-1] not in ('RestrictedCash','RestrictedCashCurrent','RestrictedCashNoncurrent'):continue
                                try:found.append(peer.primary_fact(case,item,ti,ri,ci,caption,instant=True))
                                except ValueError:continue
                if not found or len({D(v['value']) for v in found})!=1:raise ValueError('Exact restricted placement missing/conflicting '+key+str(f.year))
                f.facts[key]=dict(found[0],confirming_primary_tables=[v['primary_table'] for v in found])
            matches=list(re.finditer(r'As of December 31, '+str(f.year)+r', (?:the Company|we) had no outstanding debt balances(?: under the 2014 Credit Facility)?',f.text,re.I))
            if not matches:raise ValueError('Exact selected-year affirmative debt note absent '+str(f.year))
            m=matches[-1]
            f.facts['facility_balance_explicit_none']=dict(value='0',unit='USD',precision='verbal_explicit_none',as_of=str(f.period.annual_end),origin='reported',representation='primary_note_prose_not_XBRL',occurrences=[],occurrence_count=0,
                scope='Exact source debt-balance statement; FY2025 expressly limited to2014 facility, not complete financing',note_evidence=dict(offset=m.start(),exact_excerpt=m.group(),source_url=f.primary.artifact.url,source_sha256=f.primary.artifact.sha256))
        if t=='AMAT':
            displayed('face_short_debt','ShortTermBorrowings',('Short-term debt',),True)
            displayed('cfo_da','DepreciationAndAmortization',('Depreciation and amortization',))
        rec=shared.delivery.plain(shared.cfo.inspect_statement(case['evidence'],case['record'],version=shared.cfo.IMPROVED_VERSION))
        if rec!=case['proof']['reconciliation']:raise ValueError('Original CFO proof changed')
        manual=peer.manual_meta_reconciliation(case,rec) if t=='PLTR' else None
        if manual and manual['status']!='SUPPORTED':raise ValueError('Independent PLTR displayed CFO failed')
        pop=rec['populations'][0];detail=(pop.get('hierarchy_proof') or {}).get('children',pop['rows'])
        if manual:detail=manual['rows']
        # Bounded reviewed row labels, not arbitrary IncreaseDecrease matching.
        movement_captions={
          'LRCX':('Accounts receivable','Accounts receivable, net of allowance','Inventories','Prepaid expenses and other assets','Trade accounts payable','Accrued expenses and other liabilities','Deferred profit','Other operating assets and liabilities','Accounts payable','Accrued expenses and other current liabilities'),
          'PLTR':('Accounts receivable','Accounts receivable, net','Prepaid expenses and other current assets','Prepaid expenses and other assets','Other assets','Accounts payable','Accounts payable and accrued liabilities','Accrued liabilities','Deferred revenue, current and noncurrent','Customer deposits, current and noncurrent','Operating lease liabilities, current and noncurrent','Other noncurrent liabilities','Deferred revenue','Customer deposits','Contract liabilities','Other liabilities'),
          'AMAT':('Accounts receivable, net','Inventories','Other assets','Other current and non-current assets','Accounts payable and accrued expenses','Contract liabilities','Income taxes payable','Other liabilities','Accounts receivable','Accounts payable','Accrued expenses','Customer deposits and deferred revenue')}
        movements=[x for x in detail if x['caption'] in movement_captions[t]]
        tax_result,tax_replay=tax_policy.package(case['evidence']);tax_replay['issuer']=t
        if tax_replay!=prior.ledger_row(ledgers['retained-reported-tax-context-ledger'],case['identity'])[1]:raise ValueError('Existing tax replay changed '+t+str(f.year))
        def calc(key,ops,scope,origin='derived'):
            if not ops or any(k not in f.facts for k in ops):return
            f.entry(key,key,ops,status=PROPOSED,scope=scope,origin=origin,completeness='partial_named_population_only',rationale='Inactive company-specific proposal; no complete population or generic financial approval')
            f.entries[-1]['formula_version']='semiconductor-software-review-v1'
        da='combined_da' if t=='LRCX' else 'da' if t=='PLTR' or f.year<2023 else 'cfo_da'
        calc('limited_da_proxy',[da],'Limited consolidated CFO D&A historical proxy, not complete expense D&A; separate ROU, impairments and manufacturing timing remain',origin='proxy')
        cash_ops=['cash']+(['face_investments'] if t=='LRCX' and f.year<2024 else ['marketable_current'] if t=='PLTR' and 'marketable_current' in f.facts else ['current_investments'] if t=='AMAT' else [])
        calc('current_financial_captions',cash_ops,'Named gross face financial captions only; not unrestricted/excess or all strategic holdings')
        fin_ops=['debt_finance_current','debt_finance_long'] if t=='LRCX' else ['facility_balance_explicit_none'] if t=='PLTR' else ['debt_long']+(['face_short_debt'] if 'face_short_debt' in f.facts else [])
        if t=='AMAT' and 'face_short_debt' not in f.facts and 'debt_current' in f.facts:fin_ops+=['debt_current']
        # AMAT short debt contains its current note maturities; never add both.
        if t=='AMAT' and 'finance_lease' in f.facts:fin_ops+=['finance_lease']
        calc('named_financing',fin_ops,'Named carrying captions and separately disclosed finance liability where nonoverlapping; unidentified financing remains unknown')
        for k,v in f.facts.items():
            v.setdefault('origin','reported');v['role']='cfo_reconciliation_observation' if k in ('da','combined_da','cfo_da','sbc_addback','deferred_tax','deferred_movement','noncash_operating_cost') else 'recognized_expense_observation' if k in ('sbc_expense','sbc_note_expense','depreciation','intangible_amortization') else 'separate_reported_observation'
        references={}
        for n,ledger in ledgers.items():
            i,row=prior.ledger_row(ledger,case['identity']);references[n]=dict(reference='docs/'+n+'.json#/rows/'+str(i),record_sha256=digest(row))
        from valuation_platform.analyst.historical_inputs import Field
        policy={Field.DA:'DA',Field.CAPEX:'INV',Field.CFO:'CF',Field.CF_WORKING_CAPITAL:'CF',Field.CFO_RESIDUAL:'CF',Field.DEFERRED_TAX:'CF',Field.SBC:'SBC',Field.TAX:'TAX',Field.CASH_INVESTMENTS:'CASH',Field.DEBT_LEASES:'FIN',Field.OTHER_BRIDGE:'CLAIMS',Field.SHARES:'SHARES'}
        checklist=[dict(field=field.value,status='SOURCE_SUPPORTED' if field in (Field.REVENUE,Field.EBIT) else 'PROPOSED_PENDING_APPROVAL',pending_decisions=[] if field in (Field.REVENUE,Field.EBIT) else [t+'-'+policy[field]],financial_complete=False) for field in Field]
        for c in checklist:
            if c['field']==Field.DA.value and not any(x['input_id']=='limited_da_proxy' for x in f.entries):c['status']='ESSENTIAL_EXCEPTION'
            if c['field']==Field.CFO.value and rec['status']!='SUPPORTED' and not manual:c['status']='ESSENTIAL_EXCEPTION'
        notes=prior.note_rows(case)
        for ti,table in enumerate(case['tables']):
            for ri,row in enumerate(table):
                caption=row[0]['text'].strip() if row else ''
                if re.match(r'^(Total|Class [ABF]|Depreciation|Amortization|Deferred|Restricted|Non.cash|Capital|Equity.based|Stock.based|Long.term|Short.term|Defined|Pension|Proceeds|Repayments|Purchases|Inventories|Software|Other investments)',caption,re.I):notes.append(dict(table=ti,row=ri,caption=caption,header=' | '.join(c['text'] for rr in table[:3] for c in rr),cells=row,source_sha256=f.primary.artifact.sha256,role='Supporting displayed population, including comparatives/dimensions; not automatic selection'))
        r=dict(identity=case['identity'],fiscal_year=focus['fiscal_year'],fiscal_year_evidence=focus,selection_reference=case['manifest_reference'],prior_population_reference=case['proof_reference'],sources=case['sources'],facts=f.facts,calculations=f.entries,source_binding_exceptions=errors,cfo_reconciliation=rec,independent_displayed_cfo=manual,movement_rows=movements,reported_tax_policy_replay=tax_replay,supporting_note_rows=notes,passages=passages(f,t),preparation_ledger_evidence=references,
          alternatives={k:peer.candidates(case,k,co,inst) for k,co,inst in [('tax','IncomeTaxExpenseBenefit',False),('intangible_amortization','AmortizationOfIntangibleAssets',False),('combined_da','DepreciationAndAmortization',False),('cash','CashAndCashEquivalentsAtCarryingValue',True),('sbc','ShareBasedCompensation',False)]},
          family_checklist=checklist,new_assumptions_active=False,analyst_complete=False,
          original_supporting_unknowns=dict(complete_expense_da=None,complete_reinvestment=None,additional_unidentified_borrowing=None,unknown_restrictions=None,operating_reserve=None,unidentified_claims=None,complete_lease_cash=None,pure_cash_ppe=None),
          proposed_selections=dict(revenue='revenue',ebit='ebit',da='limited_da_proxy',sbc='sbc_note_expense' if t=='LRCX' else 'sbc_expense',capex='productive_cash' if t=='LRCX' else 'cash_capex',tax='face_tax' if t=='PLTR' else 'tax'),
          cash_sign_multipliers={k:-1 for k in ('cash_capex','productive_cash','acquisition','cash_tax','cash_tax_gross','finance_principal_cash','finance_interest_cash','op_cash','investment_purchases','investment_cash','alternative_investment_cash') if k in f.facts},
          population_relationships=[dict(parent='debt_finance_current+debt_finance_long' if t=='LRCX' else 'face_short_debt' if t=='AMAT' else 'face_debt',components=['debt_current','cp','finance_lease'],relationship='Check exact source inclusion; LRCX finance embedded, AMAT short contains current maturities; not extra parent additions'),dict(parent='current_financial_captions',components=['restricted_current','restricted_noncurrent','strategic_equity','noncurrent_investments'],relationship='Separate scope, never automatically additive or netted'),dict(parent='limited_da_proxy',components=['finance_amortization','intangible_amortization','noncash_operating_cost'],relationship='No second ROU/amortization addition; no completeness inferred from equal/partial components')])
        packages.setdefault(t,dict(schema='company-analyst-review-v1',version=1,ticker=t,source_commit=BASELINE,review_author='Retained company review, no user acceptance',review_recorded_at_utc=REVIEW_TIME,periods=[],new_assumptions_active=False,analyst_complete=False,phase1_closed=False,valuation_consumption_approved=False))['periods'].append(r)
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
    da={'LRCX':'Finance amortization is explicitly included with depreciation under the source policy: do not add7.439/7.899/5.175m again. Separate depreciation/intangible notes are rounded/incomplete later. Alternative strict pure operating expense D&A remains unresolved; no source zero for later not-material amortization.',
        'PLTR':'Keep noncash operating-lease expense, impairment and investment losses separate. Alternative pure expense D&A requires complete scope not established by CFO; do not infer amortization by subtraction.',
        'AMAT':'First two direct-policy observations remain source verified; later combined CFO caption515/392/435 is a proposed limited proxy, not reversal of frozen concept-scope denial. Manufacturing depreciation may be inventoried before sale; amortization described not material is not zero. No extra finance ROU or component sum.'}
    inv={'LRCX':'Approve an explicitly BROADER combined PP&E/intangible cash-investment proxy; strict pure-PP&E split stays null and prior negative component-completeness findings unchanged. Unpaid capital80.296/31.899/60.826/80.799/119.605 and inventory transfers75.068/76.856/71.267/90.873/125.691 are separate noncash/timing observations, not a split equation. Alternative reject broader perimeter and keep required narrow investment unresolved.',
        'PLTR':'Select direct cash PP&E; keep marketable/private investments, strategic commercial customer agreements and gold purchases/disposal separate. Customer/investee cash may be commercially related, not an invented loan population or ordinary Capex. Alternative broader investment requires a separately defined scope; no double deduction with CFO.',
        'AMAT':'Select direct cash PP&E with source software scope, not a manufactured pure tangible split. Retain acquisitions, capital creditors, finance additions and incentives separately. FY2025 capex incentives reduce recorded gross PPE by1200m and tax-related balances by781m (233current/548noncurrent); these stock measures are not annual cash receipts to net against2260m Capex. Inventory timing and grant contra-depreciation remain; alternative net economic investment requires unavailable cash allocation.'}
    fin={'LRCX':'Current/noncurrent debt-plus-finance captions include finance leases once; borrowing-only carrying parent is an alternative, not additional. Explicit no CP at year end covers CP only. Finance liability separately43.371/46.176/15.973 then unquantified, not zero. Carrying, principal, fair value and maturity schedules are different measurements.',
        'PLTR':'Source explicitly says no debt outstanding after2021 repayment and in later liquidity notes. Select the disclosed named debt population only; retain undrawn facilities, operating leases and customer deposits separately. Do not infer debt from mis-tagged FY2021 financing cash rows or net flows. Unquantified additional/finance obligations remain unknown.',
        'AMAT':'Face short debt contains current note maturities (FY2024 799 includes700) and CP; do not add them twice. FY2023 separately disclosed102 finance lease added once to named borrowings; later repayment102 and current finance0 do not prove exhaustive noncurrent absence. Missing finance/short subamounts remain unknown; bank facilities/CP and principal/fair-value observations remain separate.'}
    claims={'LRCX':'Preserve unfunded deferred-plan obligation280/318/385.5/423.9/498.5 and correlated Other-assets investments291.3/318.1/393.5/438.8/511.8 separately, never automatically netted. Accrued-compensation tag is broader, not that plan. Known pension/OPEB, tax and warranty obligations overlap captions.',
        'PLTR':'Preserve NCI, legal/tax/customer claims, investment commitments and strategic holdings. Preferred authorization and incorrectly tagged share counts do not prove outstanding preferred value; face preferred dollar row and equity note control the proposed scope. No separate pension claim is a proposed omission, not source absence.',
        'AMAT':'Retain defined/postretirement liabilities, pension funded populations, deferred-compensation investments, uncertain taxes and legal commitments without double addition to accrued/other liabilities. Strategic/equity-method investments are not free cash; no netting plan assets against obligations by default.'}
    cash={'LRCX':'Cash plus disclosed current Investments FY2022/23; cash-only thereafter, NOT a claim absent investments are zero. Restricted cash251.534/250.316/2.947/16.997/18.772 and correlated plan holdings remain separate.',
        'PLTR':'FY2021/22 current marketable securities are public equities, later balances include Treasury securities: preserve composition change and private/strategic/gold scope. Restricted CDs and customer relationships remain outside gross face selection; do not subtract already excluded restrictions again.',
        'AMAT':'Current cash and short-term investments only; long-term available-for-sale, strategic/equity holdings, restricted cash and deferred-plan assets remain separate. Restricted cash106/105/101/91/71 is not part of face cash, not a second deduction.'}
    rows=[('CF','Use reported movement detail and independently reconciled CFO; no separately calculated residual and no second movement deduction.',nums('cfo'),'Consolidated reported CFO is not FCFF, organic cash or cash delta NWC. PLTR four original PARTIAL results remain, alongside independently exact displayed-row checks. Mixed tax/noncurrent/lease/customer populations retained; no residual plug.'),
      ('DA','Select a labeled limited historical CFO D&A proxy, not complete expense-basis D&A.',nums('limited_da_proxy',True),da[t]),
      ('INV',inv[t],nums('productive_cash' if t=='LRCX' else 'cash_capex')+' payment magnitudes; cash sign -1','Acquisitions, software/intangibles, noncash ROU and capital-creditor timing stay separate. No complete reinvestment subtotal or policy/registry expansion.'),
      ('SBC','Select expense as a labeled cost proxy once, keeping CFO add-back, APIC recognition, capitalization and awards distinct.',nums('sbc_note_expense' if t=='LRCX' else 'sbc_expense')+' expense; add-back '+nums('sbc_addback'),'LRCX note expense uses ShareBasedCompensation rather than an inferred Allocated expense; AMAT FY2025 expense660 versus add-back668. PLTR APIC recognition is not expense. No duplicate cost, rounding adjustment or dilution assumption.'),
      ('TAX','Retain historical provision, cash taxes, deferred rows and existing policy Pretax/ETR separately; select PLTR face provision explicitly.',nums('face_tax' if t=='PLTR' else 'tax')+' provision; cash net '+nums('cash_tax')+'; gross '+nums('cash_tax_gross'),'PLTR rounded prose alternatives10.1/19.7/21.3/22.7 retain original generic conflicts versus face10.067/19.716/21.255/22.724. No automatic ratio from selected provision or negative pretax; no forecast rate. AMAT cash refunds/tax incentives differ from provision/deferred movements.'),
      ('CASH','Select named gross current financial captions; no unrestricted/excess-cash assertion.',nums('current_financial_captions',True),cash[t]+' Unknown restrictions/reserves stay unknown. Alternative cash only '+nums('cash')+' changes known perimeter, not an operating-reserve estimate.'),
      ('FIN','Operating leases as service costs, finance leases as asset financing; select named carrying subtotal with no additional unidentified-borrowing adjustment only if approved.',nums('named_financing',True),fin[t]+' Omitted exposure remains unquantified/unbounded. Alternative leave additional operation unresolved; not reported zero or complete debt.'),
      ('CLAIMS','Retain disclosed named claims/assets, with no additional unidentified/preferred/NCI/pension adjustment beyond bound populations only if approved.','Named observations remain visible; no valuation deduction or new source zero.',claims[t]+' Potential undisclosed claim size is unbounded; no financial-statement or valuation immateriality inference. Alternative keep omission unapproved.'),
      ('SHARES','Use actual fiscal-end common populations/classes and retain separately dated covers, EPS denominators and awards.','Exact source counts, dates, dimensions and precision in shares:*; no automatic sum.','LRCX October2024 ten-for-one split and FY2024 53weeks remain original-as-filed boundaries. PLTR A/B/F retain1/10/founder voting, F-to-B conversion and separate reported aggregate; no class equivalence or award/dilution sum. AMAT fiscal52/53weeks/cover dates preserved. Alternative cover dates are not year-end replacements.')]
    return [dict(decision_id=t+'-'+k,ticker=t,identities=[r['identity'] for r in p['periods']],recommendation=rec,numerical_effect=num,uncertainty_and_alternative=alt,status=PROPOSED,accepted=False,author=p['review_author'],recorded_at_utc=REVIEW_TIME,evidence_references=[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json#/periods/{i}' for i in range(5)]) for k,rec,num,alt in rows]


def outputs():
    packages,missing=build()
    summary=dict(schema='retained-semiconductor-software-review-batch-v1',source_commit=BASELINE,tickers=list(TICKERS),selected_periods=15,family_slots=210,companies={t:dict(periods=5,outcomes=p['outcomes'],review_revision=p['review_revision']) for t,p in packages.items()},decisions=[d for t in TICKERS for d in decisions(packages[t])],evidence_acquisition_requirements=missing,new_sec_requests=0,new_assumptions_active=False,completed_company_packages=19,approved_partial_company_packages=2,pending_review_company_packages=3,broad_assessment_only=18,phase1_closed=False,valuation_consumption_approved=False)
    return {**{f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json':p for t,p in packages.items()},SUMMARY:summary}

if __name__=='__main__':
    result=outputs()
    if '--check' in sys.argv:
        for path,payload in result.items():
            if (ROOT/path).read_text()!=json.dumps(payload,sort_keys=True,indent=2)+'\n':raise SystemExit('Review differs: '+path)
        print('Exact LRCX/PLTR/AMAT replay:15 annuals/210 families;27 inactive proposals')
    else:print(json.dumps(result,sort_keys=True,indent=2))
