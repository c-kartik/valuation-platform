"""Fixed V/INTC/WMT retained review. No activation, acquisition or policy expansion."""
import json,re,sys
from collections import Counter
from decimal import Decimal as D
import prepare_standard_review_batch as shared
import prepare_trillion_review_batch as peer
import prepare_large_company_review_batch as prior
from prepare_priority_review_batch import fiscal_focus
from prepare_msft_analyst_package import ROOT,digest,relevant,PROPOSED
from valuation_platform.analyst import retained_d_and_a as da_policy,retained_capex as capex_policy

BASELINE='fe4bb39f93fe05a50c48d2f64927d487a7e27cb1'
REVIEW_TIME='2026-10-17T20:19:34+00:00'
TICKERS=('V','INTC','WMT')
SUMMARY='docs/company-data-preparation/network-retail-review-batch.json'


def passages(f,t):
    markers={'V':('client incentives','Cash collateral','Restricted cash','Series B preferred','Series C preferred','non-U.S. pension','share-based compensation costs','retrospective responsibility'),
        'INTC':('useful lives','capital-related incentives','Proceeds from capital grants','Brookfield','Apollo','inventory','Restructuring and other','purchase obligations','non-cash transaction'),
        'WMT':('Supplier Financing Program Obligations','Depreciation and amortization expense','three-for-one','membership and other income','Acquisitions','discontinued operations')}[t]
    out=[]
    for marker in markers:
        hits=list(re.finditer(r'(?<!\w)'+re.escape(marker)+r'(?!\w)',f.text,re.I))
        for m in dict.fromkeys(hits[:2]+hits[-1:]):out.append(dict(marker=marker,offset=m.start(),exact_excerpt=f.text[max(0,m.start()-100):m.end()+2100],source_sha256=f.primary.artifact.sha256))
    return out


def build():
    cases,missing=shared.load(TICKERS);packages={}
    ledgers={n:json.loads((ROOT/('docs/'+n+'.json')).read_text()) for n in prior.LEDGERS+('retained-bridge-component-ledger','retained-tax-sbc-ledger')}
    store=capex_policy.artifacts()  # Existing typed original-byte catalog; no retrieval.
    for case in cases:
        t=case['ticker'];f=case['filing'];focus=fiscal_focus(case)
        case['tables']=shared.documents.parse(case['record'],improved=True)
        errors=shared.observe(case);prior.prepare_income(case,prior.ledger_row(ledgers['repaired-income-ledger'],case['identity'])[1])
        def bind(key,concept,instant=False,ns='us-gaap'):
            try:shared.monetary(case,key,concept,instant,ns)
            except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc),disposition='Unselected selector, not proof of missing disclosure or economic zero'))
        def displayed(key,co,captions,instant=False):
            try:
                if not peer.displayed_selection(case,key,co,captions,instant=instant):raise ValueError('Exact reviewed displayed population unavailable')
            except ValueError as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
        common={**prior.EXTRA,'short_afs':('AvailableForSaleSecuritiesDebtSecuritiesCurrent',True),
            'combined_da':('DepreciationAndAmortization',False),'da_accretion':('DepreciationAmortizationAndAccretionNet',False),
            'productive_cash':('PaymentsToAcquireProductiveAssets',False),'pension_recognized':('DefinedBenefitPensionPlanCurrentAndNoncurrentLiabilities',True),
            'supplier_finance':('SupplierFinanceProgramObligation',True),'litigation_current':('LitigationReserveCurrent',True),
            'grants_receivable':('GrantsReceivable',True),'impairment':('AssetImpairmentCharges',False),
            'restructuring':('RestructuringSettlementAndImpairmentProvisions',False),
            'preferred_outstanding':('PreferredStockValueOutstanding',True)}
        for key,(co,instant) in common.items():bind(key,co,instant)
        displayed('face_cash','CashAndCashEquivalentsAtCarryingValue',('Cash and cash equivalents',),True)
        if t=='INTC':
            # Earlier face uses a broader cash/restricted QName; retain that scope.
            if 'face_cash' not in f.facts:displayed('face_cash','CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents',('Cash and cash equivalents',),True)
            displayed('face_sbc','ShareBasedCompensation',('Share-based compensation',))
            displayed('face_short_debt','DebtCurrent',('Short-term debt',),True)
            for key,co,instant in [('capital_grant_cash','ProceedsFromCapitalGrants',False),('noncash_incentive','GovernmentIncentivesReceivedDuringNoncashTransaction',False),('grant_basis_reduction','PropertyPlantAndEquipmentAdditionsGrantsContraAccount',False)]:bind(key,co,instant,'intc')
        if t=='V':
            bind('investment_securities','AvailableForSaleSecuritiesDebtSecurities',True)
            bind('afs_current','AvailableForSaleSecuritiesCurrent',True)
            bind('afs_noncurrent','AvailableForSaleSecuritiesNoncurrent',True)
            for key,co in [('settlement_receivable','SettlementReceivable'),('settlement_payable','SettlementPayable'),('client_asset_current','ClientIncentivesAssetsCurrent'),('client_asset_noncurrent','ClientIncentivesAssetsNoncurrent'),('client_liability','ClientIncentivesLiabilitiesCurrent'),('litigation_escrow','RestrictedCashAndCashEquivalentsU.S.LitigationEscrow'),('client_cash_collateral','CashCollateralReceived')]:bind(key,co,True,'v')
        if t=='WMT':
            displayed('face_da','DepreciationAmortizationAndAccretionNet',('Depreciation and amortization',))
            displayed('face_sbc_expense','AllocatedShareBasedCompensationExpense',('Share-based compensation expense',))
            displayed('face_revenue','Revenues',('Total revenues',))
            bind('net_sales','RevenueFromContractWithCustomerExcludingAssessedTax')
            bind('membership_other','OtherIncome')
            displayed('face_short_borrowing','ShortTermBorrowings',('Short-term borrowings',),True)
        # Exact dimensioned preferred/benefit observations remain populations,
        # never an automatic class sum, conversion or pension adjustment.
        for node in f.root:
            co=node.tag.split('}')[-1]
            if co not in ('PreferredStockValueOutstanding','DefinedBenefitPlanFundedStatusOfPlan','DefinedBenefitPlanAssetsForPlanBenefitsNoncurrent','PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent'):continue
            ctx=f.contexts.get(node.get('contextRef'))
            if ctx is None:continue
            dims=tuple((x.get('dimension'),x.text) for x in ctx.iter() if x.tag.endswith('}explicitMember'))
            if not dims or len(dims)>2:continue
            key='claim:'+co+':'+digest(dims)[:8]
            if key in f.facts:continue
            try:f.fact(key,co,'Exact class/plan population, not additive to gross/net parents',instant=True,dimensions=dims)
            except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
        curated={}
        if t=='V':
            for name,replay in [('d_and_a',da_policy.resolve),('capex',capex_policy.replay)]:
                result,inspection,proof,*rest=replay(case['evidence'],store)
                gaps=rest[-1] if name=='d_and_a' else rest[0]
                if name=='d_and_a':gaps=rest[1]
                old=prior.ledger_row(ledgers['retained-d-and-a-ledger' if name=='d_and_a' else 'refreshed-capex-ledger'],case['identity'])[1]
                if gaps or not getattr(result,'policy_provenance',None):
                    errors.append(dict(input_id=name,value=None,reason='Existing curated approval failed exact replay',artifact_requirements=gaps))
                    missing.extend(dict(g,identity=case['identity'],ticker=t,field=name) for g in gaps)
                    continue
                if proof!=old['policy'] or D(str(result.value))!=abs(D(old['value_usd'])):raise ValueError('Visa immutable policy proof/value differs')
                curated[name]=dict(value=str(result.value),policy=proof,existing_approval=True,reviewed_scope_only=True)
        rec=shared.delivery.plain(shared.cfo.inspect_statement(case['evidence'],case['record'],version=shared.cfo.IMPROVED_VERSION))
        if rec!=case['proof']['reconciliation']:raise ValueError('Original displayed CFO proof changed')
        pop=rec['populations'][0];hierarchy=pop.get('hierarchy_proof')
        detail=(hierarchy['children'] if hierarchy else pop['rows'])
        # Explicit reviewed display captions include extensions and tax/combined
        # rows the generic standard-concept movement mapper intentionally rejects.
        # Keep original role/evidence unchanged; no new generic mapping policy.
        captions={'V':('Settlement receivable','Accounts receivable','Client incentives','Other assets','Accounts payable','Settlement payable','Accrued and other liabilities','Accrued litigation'),
            'INTC':('Accounts receivable','Inventories','Accounts payable','Accrued compensation and benefits','Income taxes','Other assets and liabilities'),
            'WMT':('Receivables, net','Inventories','Accounts payable','Accrued liabilities','Accrued income taxes')}[t]
        # Visa also has an earlier client-incentive amortization row with the
        # same caption. Only the change-in-balance occurrence is a movement.
        movements=[x for x in detail if x['caption'].strip() in captions and (t!='V' or x['concept'].startswith('IncreaseDecrease'))]
        def calc(key,ops,scope,origin='derived'):
            if any(k not in f.facts for k in ops):return
            f.entry(key,key,ops,status=PROPOSED,scope=scope,origin=origin,completeness='partial_named_population_only',rationale='Inactive exact company proposal, not a generic policy or completeness claim')
            f.entries[-1]['formula_version']='network-retail-review-v1'
        calc('limited_da_proxy',['depreciation','intangible_amortization'] if t=='INTC' else ['combined_da'] if t=='V' else ['face_da'],
            'INTC separate depreciation/intangible populations; WMT caption with accretion scope retained; Visa unchanged curated scope. Not additional CFO or complete expense D&A','proxy')
        calc('current_financial_captions',['face_cash','short_afs'] if 'short_afs' in f.facts else ['face_cash'],
            'Named face cash/current financial captions, not unrestricted/excess; INTC earlier includes restricted scope, Visa excludes separately captioned escrow/client funds')
        calc('named_financing',['face_short_debt','debt_long'] if t=='INTC' else ['face_short_borrowing','debt_current','debt_long','finance_lease'] if t=='WMT' else ['debt_current','debt_long'],
            'Named carrying captions only; current maturities included once, WMT separate finance parent added once; no combined exhaustive debt certification')
        # Revenue identity check is supporting arithmetic, not a generic conflict fix.
        revenue_check=None
        if t=='WMT' and all(k in f.facts for k in ('face_revenue','net_sales','membership_other')):
            revenue_check=dict(difference=str(D(f.facts['net_sales']['value'])+D(f.facts['membership_other']['value'])-D(f.facts['face_revenue']['value'])),
                operands=['net_sales','membership_other'],reported_total='face_revenue',scope='As-filed total revenues including membership/other; not generic equivalence with net sales')
        for k,v in f.facts.items():
            v.setdefault('origin','reported');v['role']='recognized_expense_observation' if k in ('sbc_expense','face_sbc_expense','depreciation','intangible_amortization') else 'cfo_reconciliation_observation' if k in ('face_sbc','sbc_addback','combined_da','da_accretion','face_da') else 'deferred_tax_note_observation' if k=='deferred_tax' else 'separate_reported_observation'
        references={}
        for name,ledger in ledgers.items():
            i,row=prior.ledger_row(ledger,case['identity']);references[name]=dict(reference='docs/'+name+'.json#/rows/'+str(i),record_sha256=digest(row))
        from valuation_platform.analyst.historical_inputs import Field
        policy={Field.REVENUE:'REV',Field.DA:'DA',Field.CAPEX:'INV',Field.CFO:'CF',Field.CF_WORKING_CAPITAL:'CF',Field.CFO_RESIDUAL:'CF',Field.DEFERRED_TAX:'CF',Field.SBC:'SBC',Field.TAX:'TAX',Field.CASH_INVESTMENTS:'CASH',Field.DEBT_LEASES:'FIN',Field.OTHER_BRIDGE:'CLAIMS',Field.SHARES:'SHARES'}
        checklist=[]
        for field in Field:
            required=[] if field==Field.EBIT or field==Field.REVENUE and t!='WMT' else [t+'-'+policy[field]]
            status='PROPOSED_PENDING_APPROVAL' if required else 'SOURCE_SUPPORTED'
            if field==Field.CFO and rec['status']!='SUPPORTED':status='ESSENTIAL_EXCEPTION'
            if t=='V' and field in (Field.DA,Field.CAPEX) and ('d_and_a' if field==Field.DA else 'capex') not in curated:status='ESSENTIAL_EXCEPTION'
            checklist.append(dict(field=field.value,status=status,pending_decisions=required,financial_complete=False))
        notes=prior.note_rows(case)
        caps=re.compile(r'^(Total revenues|Net sales|Membership|Share.based compensation|Client incentives|Settlement receivable|Settlement payable|Restricted|Investment securities|Accrued litigation|Preferred|Series [ABC]|Total adjustments|Capital.related|Government|Supplier|Outstanding payment obligations|Purchase obligations|Noncontrolling|Redeemable)',re.I)
        for ti,table in enumerate(case['tables']):
            for ri,row in enumerate(table):
                caption=row[0]['text'].strip() if row else ''
                if caps.search(caption):notes.append(dict(table=ti,row=ri,caption=caption,header=' | '.join(c['text'] for r in table[:3] for c in r),cells=row,source_sha256=f.primary.artifact.sha256,role='supporting source population, comparatives not registered selections'))
        period=dict(identity=case['identity'],fiscal_year=focus['fiscal_year'],fiscal_year_evidence=focus,selection_reference=case['manifest_reference'],prior_population_reference=case['proof_reference'],
            sources=case['sources'],facts=f.facts,calculations=f.entries,curated_policy_replays=curated,source_binding_exceptions=errors,
            cfo_reconciliation=rec,movement_rows=movements,supporting_note_rows=notes,passages=passages(f,t),preparation_ledger_evidence=references,
            alternatives={k:peer.candidates(case,k,co,inst) for k,co,inst in [('revenue_net_sales','RevenueFromContractWithCustomerExcludingAssessedTax',False),('revenue_total','Revenues',False),('cash','CashAndCashEquivalentsAtCarryingValue',True),('sbc','ShareBasedCompensation',False)]},
            revenue_display_identity=revenue_check,family_checklist=checklist,new_assumptions_active=False,analyst_complete=False,
            proposed_selections=dict(revenue='face_revenue' if t=='WMT' else 'revenue',sbc='face_sbc' if t=='INTC' else 'sbc_addback' if t=='V' else 'face_sbc_expense',capex='productive_cash' if t=='V' else 'cash_capex'),
            original_supporting_unknowns=dict(complete_expense_da=None,complete_reinvestment=None,additional_unidentified_borrowing=None,unknown_restrictions=None,operating_reserve=None,unidentified_claims=None,complete_lease_cash=None),
            cash_sign_multipliers={k:-1 for k in ('cash_capex','productive_cash','acquisition','cash_tax','cash_tax_gross','cash_interest','finance_principal_cash','finance_interest_cash','op_cash') if k in f.facts})
        if 'capital_grant_cash' in f.facts:period['cash_sign_multipliers']['capital_grant_cash']=1
        packages.setdefault(t,dict(schema='company-analyst-review-v1',version=1,ticker=t,source_commit=BASELINE,review_author='Retained company review, no user acceptance',review_recorded_at_utc=REVIEW_TIME,periods=[],new_assumptions_active=False,analyst_complete=False,phase1_closed=False,valuation_consumption_approved=False))['periods'].append(period)
    for t,p in packages.items():
        p['periods'].sort(key=lambda r:r['identity']['annual_end']);p.update(family_slots=70,outcomes=dict(Counter(c['status'] for r in p['periods'] for c in r['family_checklist'])),approval_table_reference=SUMMARY+'#/decisions',evidence_acquisition_requirements=[x for x in missing if x['ticker']==t]);p['review_revision']=digest(relevant(p))
    return packages,missing


def decisions(p):
    t=p['ticker']
    def nums(key,calc=False):
        values=[]
        for r in p['periods']:
            v=next((c for c in r['calculations'] if c['input_id']==key),{}) if calc else r['facts'].get(key,{})
            values.append(str(D(v['value'])/1000000) if v.get('value') is not None else 'unknown')
        return '/'.join(values)+' USDm'
    rows=[('CF','Retain original consolidated reported CFO and source cash movements; preserve hierarchy, no separate residual or second deduction.',nums('cfo'),
        'Not operating-only cash delta NWC or FCFF. Intel complete displayed adjustment children reconcile to the parent, not parent-plus-children. Visa settlement/client and Walmart tax/inventory rows retain source scope; mixed other rows unallocated. Alternative a narrower operating-only cash contract requires unsupported allocations.'),
        ('DA','Use unchanged Visa curated D&A; propose company-specific LIMITED Intel/Walmart historical proxies, never new generic D&A policy.',nums('limited_da_proxy',True),
        'Visa asset/technology/intangible scope is exactly approved;2025 rounded corroboration discrepancy is not a plug and client-incentive amortization is NOT D&A. Intel depreciation plus separately identified intangible amortization is a limited non-overlapping proxy, with capitalization/inventory timing, useful-life changes and incentive-reduced basis; no impairment/restructuring add-on. Walmart source caption retains accretion scope; finance amortization already reflected in source note perimeter, no second addition. Alternatives: retain raw observations and leave required expense D&A unresolved; no complete expense certification.'),
        ('INV','Select original gross cash-investment caption within existing exact approval/direct scope; keep incentives, noncash additions, creditors, acquisitions and proceeds separate.',nums('productive_cash' if t=='V' else 'cash_capex'),
        'Visa v3 operational software/property/technology scope only, no blanket software rule. Intel grant receipts '+nums('capital_grant_cash')+' and partner/noncash financing are not a reduction of gross cash PP&E or another lease debt. Walmart capex, noncash finance/operating ROU and acquired business consideration differ. No complete reinvestment or net-investment subtotal. Alternative explicitly defined net funding basis would need its own approved non-overlap/timing treatment; no default change.'),
        ('SBC','Select one labeled cost proxy, not duplicate expense plus CFO addback; preserve exact/rounded and missing reconciliation populations.',nums('face_sbc' if t=='INTC' else 'sbc_addback' if t=='V' else 'face_sbc_expense'),
        'Intel propose exact displayed CFO SBC over rounded note alternatives explicitly, not generic precedence; retain rounded candidates and NCI/parent allocations. Visa CFO SBC is proposed as a historical cost proxy where pure expense observation is not independently selected. Walmart propose exact displayed recognized expense, preserving rounded alternatives; pure CFO SBC remains unknown inside Other, not a manufactured addback. Alternative no proxy/retain expense-only where available; awards/capitalization remain separate.'),
        ('TAX','Retain source provision, pretax, reported accounting context and actual cash-tax scope separately; no future rate or normalization.',nums('tax')+'; cash net '+nums('cash_tax')+'; other cash '+nums('cash_tax_gross'),
        'Keep note tax expense, cash movements and deferred reconciliation distinct. Intel losses/valuation allowance and historical unusual rates are not clamped. Missing generic denominators/precision conflicts stay in original policy ledger. Alternative no future operating-tax assumption; any later rate requires a separately justified design.'),
        ('CASH','Select named face cash/current financial captions only, with source restrictions prominently retained and settlement/client funds separate.',nums('current_financial_captions',True),
        'Not unrestricted/excess cash. Visa selects the named cash caption only; investment securities stay a separately disclosed population, not assumed absent/free cash. Escrow/client collateral and settlement receivable are not corporate cash additions; do not subtract exclusions already outside the face caption twice. Intel earlier face QName includes restricted scope, not silently unrestricted. Walmart exact face cash is a company selection, preserving competing generic observations. Unknown reserves/restrictions stay unbounded. Alternative a broader securities-inclusive balance needs explicit maturity/coverage/non-overlap acceptance; no invented reserve or automatic addition.'),
        ('FIN','Operating leases service costs, finance leases asset financing; select named carrying financing with no additional unidentified-borrowing adjustment.',nums('named_financing',True),
        'Current maturities/parent captions counted once. Walmart adds separate finance parent once, not parent+current+noncurrent. Supplier-finance invoices remain in operating AP where source says so, not automatically added again as debt. Intel co-investment NCI/funding and commitments remain separate, not all termed debt; Visa settlement payable is not CP. Omission is potentially unbounded analyst assumption, not source zero/immateriality. Alternative retain unidentified operation unresolved.'),
        ('CLAIMS','Retain recognized preferred/NCI/benefit/litigation populations and their measurement overlaps; propose no additional unidentified adjustment beyond those named.',
        'Exact populations and dates in facts/note rows/claims ledger; unknown subamounts remain null.',
        'Visa participating convertible preferred and retrospective litigation recoveries require separate class/claim treatment, not ordinary fixed debt or unrestricted recovery cash. Intel co-investment NCI is a known claim, not omitted with pension assumption. Walmart NCI/redeemable populations retain separate presentations. No net funded/gross double count, exhaustive claims claim or valuation deduction. Unknown extra exposure unbounded; alternative leave omission operation unapproved.'),
        ('SHARES','Retain dated class-specific shares; choose fiscal-end common for Intel/Walmart and separate disclosed classes for Visa, without a class-conversion or diluted aggregate.',
        'Exact counts, original precision/dates/dimensions in facts/shares:*; no automatic class/award sum.',
        'Visa A/B/C and later B1/B2/preferred conversion rights are not one economically equivalent class. Walmart three-for-one2024 split changes reported populations; retain original selected presentation and later cover date, no invented restatement. Intel strategic issuance, subsidiary NCI and awards are not parent diluted closing shares. Alternative later-cover observations preserve their different dates, not fiscal-end replacement.')]
    if t=='WMT':rows.insert(0,('REV','Select as-filed Total revenues = Net sales + Membership and other income for the consolidated operating history; preserve generic economic conflict.',nums('face_revenue')+' versus net sales '+nums('net_sales')+'; difference '+nums('membership_other'),
        'Total revenues is the face-statement operating top line supporting reported EBIT, includes recurring membership/other operating income. Net sales-only is a meaningful narrower retail measure, not numerically equivalent; it would exclude the stated amounts and require a consistent expense/perimeter policy. No generic resolver precedence change, silent conflict clearance or splice of later comparatives.'))
    return [dict(decision_id=t+'-'+key,ticker=t,identities=[r['identity'] for r in p['periods']],recommendation=rec,numerical_effect=n,uncertainty_and_alternative=alt,status=PROPOSED,accepted=False,author=p['review_author'],recorded_at_utc=REVIEW_TIME,evidence_references=[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json#/periods/{i}' for i in range(5)]) for key,rec,n,alt in rows]


def outputs():
    import activate_company_review_batches as accepted
    packages,missing=build()
    summary=dict(schema='retained-network-retail-review-batch-v1',source_commit=BASELINE,tickers=list(TICKERS),selected_periods=15,family_slots=210,
        companies={t:dict(periods=5,outcomes=p['outcomes'],review_revision=p['review_revision']) for t,p in packages.items()},decisions=[d for t in TICKERS for d in decisions(packages[t])],
        evidence_acquisition_requirements=missing,new_sec_requests=0,new_assumptions_active=False,completed_company_packages=13,approved_partial_company_packages=2,pending_review_company_packages=3,broad_assessment_only=24,phase1_closed=False)
    packages={t:accepted.load_if_approved(f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json',p,summary['decisions']) for t,p in packages.items()}
    activation=accepted.summary_activation(packages)
    if activation:
        complete=sum(x['completed'] for x in activation['companies'].values())
        activation['current_company_counts']=dict(broadly_assessed=42,completed_scoped=13+complete,approved_partial=2+len(activation['companies'])-complete,pending_reviews=3-len(activation['companies']),assessment_only=24)
        summary['approval_activation']=activation
    return {**{f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json':p for t,p in packages.items()},SUMMARY:summary}


if __name__=='__main__':
    result=outputs()
    if '--check' in sys.argv:
        for path,p in result.items():
            if (ROOT/path).read_text()!=json.dumps(p,sort_keys=True,indent=2)+'\n':raise SystemExit('Network/retail batch differs: '+path)
        print('Exact V/INTC/WMT replay:15 selected annuals/210 families; current approval activation separately recorded')
    else:print(json.dumps(result,sort_keys=True,indent=2))
