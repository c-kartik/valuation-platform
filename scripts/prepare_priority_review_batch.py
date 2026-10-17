"""One retained MU/AMD/JNJ review, no activation/new financial policy."""
import json,re,sys
from collections import Counter
from decimal import Decimal as D
import prepare_standard_review_batch as shared
import prepare_trillion_review_batch as peer
import prepare_large_company_review_batch as prior
from prepare_msft_analyst_package import ROOT,digest,relevant,PROPOSED

BASELINE='29baa8a1d5248d5219ffbd229295e5ccad096eba'
REVIEW_TIME='2026-10-17T19:42:09+00:00'
TICKERS=('MU','AMD','JNJ')
SUMMARY='docs/company-data-preparation/priority-review-batch.json'


def fiscal_focus(case):
    f=case['filing'];items=[]
    for i,n in enumerate(f.root):
        if not n.tag.endswith('}DocumentFiscalYearFocus') or not n.tag.startswith('{http://xbrl.sec.gov/dei/'):continue
        ctx=f.contexts[n.get('contextRef')];xi=shared.cash._XI
        if ctx.findtext('.//'+xi+'identifier') not in (str(f.period.cik),str(f.period.cik).zfill(10)):continue
        end=ctx.findtext(xi+'period/'+xi+'endDate') or ctx.findtext(xi+'period/'+xi+'instant')
        if end!=str(f.period.annual_end) or any(x.tag.endswith('}explicitMember') for x in ctx.iter()):continue
        items.append(dict(ordinal=i,context_id=n.get('contextRef'),raw_value=n.text,source_sha256=f.instance.artifact.sha256))
    if len({x['raw_value'] for x in items})!=1:raise ValueError('Exact fiscal-year focus must be established, not inferred from end date')
    f.year=int(items[0]['raw_value'])
    return dict(fiscal_year=f.year,concept='DocumentFiscalYearFocus',occurrences=items)


def amd_display(case):
    """Independently bind every displayed current-year row and CFO hierarchy.

    Preserve the shared PARTIALs.2022 inventory step-up is its own dimensioned
    population;2025 continuing reconciliation and discontinued CFO are separate.
    No formula from a residual or changed parser tolerance.
    """
    f=case['filing'];table_id=case['proof']['reconciliation']['populations'][0]['table'];table=case['tables'][table_id]
    first=next(i for i,r in enumerate(table) if r and r[0]['text'].strip()=='Net income')
    final=next(i for i,r in enumerate(table) if r and r[0]['text'].strip()=='Net cash provided by operating activities')
    rows=[]
    headings=('Adjustments to reconcile net income to net cash provided by operating activities:','Changes in operating assets and liabilities:')
    for ri in range(first,final+1):
        row=table[ri];caption=row[0]['text'].strip()
        if caption in headings:continue
        bound=[]
        for ci,cell in enumerate(row):
            for item in cell['facts']:
                ctx=f.contexts[item['attrs']['contextref']];xi=shared.cash._XI
                if (ctx.findtext(xi+'period/'+xi+'startDate'),ctx.findtext(xi+'period/'+xi+'endDate'))!=(str(f.period.annual_start),str(f.period.annual_end)):continue
                fact=peer.primary_fact(case,item,table_id,ri,ci,caption)
                value=shared.cfo.displayed(cell['text'],D(0))*D(10)**int(item['attrs'].get('scale','0'))
                bound.append(dict(caption=caption,value=str(value),fact=fact,row=ri))
        if len(bound)!=1:raise ValueError('Unbound/ambiguous displayed AMD monetary row: '+caption)
        rows.extend(bound)
    total=rows[-1]
    if f.year==2025:
        continuing=next(x for x in rows if x['caption']=='Net cash provided by operating activities of continuing operations')
        discontinued=next(x for x in rows if x['caption']=='Net cash provided by operating activities of discontinued operations')
        terms=[x for x in rows if x['row']<continuing['row']]
        difference=sum((D(x['value']) for x in terms),D(0))-D(continuing['value'])
        parent_difference=D(continuing['value'])+D(discontinued['value'])-D(total['value'])
    else:
        continuing=None;discontinued=None;terms=rows[:-1]
        difference=sum((D(x['value']) for x in terms),D(0))-D(total['value']);parent_difference=D(0)
    return dict(status='SUPPORTED' if difference==0 and parent_difference==0 else 'FAILED',
        basis='Separate exact caption/dimension-specific review, original shared proof unchanged',
        rows=terms,cfo=total,continuing_cfo=continuing,discontinued_cfo=discontinued,
        difference=str(difference),parent_difference=str(parent_difference),tolerance='0',table=table_id)


def passages(f):
    markers=('Government Incentives','Cost includes depreciation','Depreciation expense was','depreciation and amortization expense included in operating income',
        'Interest capitalized','cash received from incentives','capacity','Xilinx','Pensando','ZT Systems','discontinued operations','Kenvue',
        'talc litigation','talc-related','Talc','litigation accrual','Funded status','acquired in-process','finance leases')
    out=[]
    for marker in markers:
        hits=list(re.finditer(r'(?<!\w)'+re.escape(marker)+r'(?!\w)',f.text,re.I))
        # First occurrences include financial-note discussion, not just exhibit lists.
        for m in dict.fromkeys(hits[:3]+hits[-1:]):
            out.append(dict(marker=marker,offset=m.start(),exact_excerpt=f.text[max(0,m.start()-100):m.end()+1700],source_sha256=f.primary.artifact.sha256))
    return out


def build():
    cases,missing=shared.load(TICKERS)
    ledgers={n:json.loads((ROOT/('docs/'+n+'.json')).read_text()) for n in prior.LEDGERS}
    packages={}
    common={**prior.EXTRA,'short_afs':('AvailableForSaleSecuritiesDebtSecuritiesCurrent',True),
        'other_da':('OtherDepreciationAndAmortization',False),'separate_amortization':('AdjustmentForAmortization',False),
        'continuing_cfo':('NetCashProvidedByUsedInOperatingActivitiesContinuingOperations',False),
        'discontinued_cfo':('CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations',False),
        'pension_recognized':('DefinedBenefitPensionPlanCurrentAndNoncurrentLiabilities',True),
        'other_postretirement_recognized':('OtherPostretirementDefinedBenefitPlanLiabilitiesCurrentAndNoncurrent',True),
        'benefit_liabilities_noncurrent_parent':('PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent',True),
        'benefit_liabilities_current_parent':('PensionAndOtherPostretirementDefinedBenefitPlansCurrentLiabilities',True),
        'litigation_reserve':('LitigationReserve',True),'accrued_litigation':('AccruedLitigation',True),
        'capitalized_interest':('InterestCostsCapitalized',False),'inventory_write_down':('InventoryWriteDown',False)}
    for case in cases:
        t=case['ticker'];f=case['filing'];focus=fiscal_focus(case)
        case['tables']=shared.documents.parse(case['record'],improved=True)
        errors=shared.observe(case)
        income=prior.ledger_row(ledgers['repaired-income-ledger'],case['identity'])[1]
        prior.prepare_income(case,income,include_repairs=t=='JNJ')
        def bind(key,co,instant=False,ns='us-gaap'):
            try:shared.monetary(case,key,co,instant,ns)
            except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc),disposition='Unselected/missing/conflicting selector is not a financial zero'))
        for key,(co,instant) in common.items():bind(key,co,instant)
        if t=='MU':
            bind('incentive_cash','ProceedsFromGovernmentIncentives',ns='mu') if f.year==2022 else bind('incentive_cash','ProceedsFromGovernmentAssistance',ns='mu')
        if t=='AMD':
            for key,co in [('acq_amort_cogs','AmortizationOfAcquisitionRelatedIntangiblesCOGS' if f.year>=2025 else 'AmortizationOfAcquisitionRelatedIntangibles'),
                ('acq_amort_opex','AmortizationOfAcquisitionRelatedIntangibles_Opex'),('acquisition_cash','AcquisitionsNetOfCashAcquiredAllOthers')]:bind(key,co,ns='amd')
            peer.displayed_selection(case,'other_da','OtherDepreciationAndAmortization',('Depreciation and amortization',))
        if t=='JNJ':
            for key,co in [('iprd_cash','PaymentsToAcquiredInProcessResearchAndDevelopmentAssets'),('talc_legacy_reserve','AccruedLitigation'),('litigation_expense','LitigationSettlementExpense')]:bind(key,co,ns='jnj')
            bind('iprd_face_impairment','ResearchAndDevelopmentInProcess1' if f.year>=2023 else 'ResearchAndDevelopmentInProcess',ns='jnj' if f.year>=2023 else 'us-gaap')
            for key,co,instant,ns in [('talc_carrying_reserve','LossContingencyAccrualAtCarryingValue',True,'us-gaap'),('talc_nominal_reserve','LossContingencyAccrualNominalValue',True,'jnj'),('talc_reversal','LitigationSettlementReversalOfFeeExpense',False,'jnj')]:
                try:f.fact(key,co,'Exact talc litigation population; nominal/carrying/expense are NOT additive',instant=instant,namespace=ns,dimensions=(('srt:LitigationCaseAxis','jnj:TalcMember'),))
                except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
        for member in ('PensionPlansDefinedBenefitMember','OtherPostretirementBenefitPlansDefinedBenefitMember'):
            for co in ('DefinedBenefitPlanFundedStatusOfPlan','PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent','DefinedBenefitPlanAssetsForPlanBenefitsNoncurrent'):
                key=member+':'+co
                try:f.fact(key,co,'Exact benefit-plan population, not additive to gross/net parents',instant=True,dimensions=(('us-gaap:RetirementPlanTypeAxis','us-gaap:'+member),))
                except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
        rec=shared.delivery.plain(shared.cfo.inspect_statement(case['evidence'],case['record'],version=shared.cfo.IMPROVED_VERSION))
        if rec!=case['proof']['reconciliation']:raise ValueError('Original displayed CFO proof changed')
        manual=amd_display(case) if t=='AMD' and rec['status']=='PARTIAL' else None
        effective_proof=manual or rec
        def calc(key,ops,scope,origin='derived',coefficients=None):
            if any(k not in f.facts for k in ops):return
            f.entry(key,key,ops,coefficients,status=PROPOSED,scope=scope,origin=origin,completeness='partial_named_population_only',rationale='Company-specific proposal only, not a new frozen policy or accepted complete total')
            f.entries[-1]['formula_version']='retained-priority-review-v1'
        calc('limited_da_proxy',['other_da','separate_amortization'] if t=='AMD' and f.year>=2024 else ['other_da'] if t=='AMD' else ['da'],
            'Limited source CFO D&A proxy; no ROU/impairment/IPRD/financing additions, no expense completeness claim','proxy')
        calc('gross_current_financial',['cash','short_afs' if t=='MU' else 'current_investments' if t=='AMD' else 'marketable_current'],
            'Gross named current financial captions, not unrestricted/excess cash; strategic/long-term/restricted populations separate')
        calc('named_financing',['borrowing_current','debt_finance_long'] if t=='MU' else ['short_borrowing','debt_long'],
            'Source face current + noncurrent carrying borrowing captions; embedded current maturities/finance populations not added twice, unidentified exposure unbounded')
        if t=='MU':calc('net_incentive_cash_alternative',['cash_capex','incentive_cash'],
            'NONDEFAULT cash PP&E outflow plus separately received incentives; not a complete reinvestment or gross-basis normalization',coefficients=[-1,1])
        for key,value in f.facts.items():
            value.setdefault('origin','reported')
            value['role']='deferred_tax_expense_note_observation' if key=='deferred_tax' else 'cfo_reconciliation_observation' if key in ('da','other_da','separate_amortization','deferred_movement','sbc_addback') else 'recognized_expense_observation' if key in ('depreciation','intangible_amortization','acq_amort_cogs','acq_amort_opex','sbc_expense','iprd_face_impairment') else 'dated_shares_or_awards' if key.startswith('shares:') else 'separate_reported_observation'
        if t=='AMD' and f.year==2023 and 'reported_etr' in f.facts:
            f.facts['reported_etr']['selection_status']='UNSELECTED_TAGGED_68_PURE_REPRESENTATION_NOT_NORMALIZED_TO_RATIO'
        refs={}
        for name,ledger in ledgers.items():
            i,row=prior.ledger_row(ledger,case['identity']);refs[name]=dict(reference='docs/'+name+'.json#/rows/'+str(i),record_sha256=digest(row),status=row.get('status'),value_usd=row.get('value_usd'))
        from valuation_platform.analyst.historical_inputs import Field
        policy={Field.DA:'DA',Field.CAPEX:'INV',Field.CFO:'CF',Field.CF_WORKING_CAPITAL:'CF',Field.CFO_RESIDUAL:'CF',Field.DEFERRED_TAX:'CF',Field.SBC:'SBC',Field.TAX:'TAX',Field.CASH_INVESTMENTS:'CASH',Field.DEBT_LEASES:'FIN',Field.OTHER_BRIDGE:'CLAIMS',Field.SHARES:'SHARES'}
        checklist=[]
        for field in Field:
            required=([t+'-PERIMETER'] if t=='JNJ' else [])+([t+'-'+policy[field]] if field in policy else [])
            status='PROPOSED_PENDING_APPROVAL' if required else 'SOURCE_SUPPORTED'
            if field in (Field.CFO,Field.CFO_RESIDUAL) and effective_proof['status']!='SUPPORTED':status='ESSENTIAL_EXCEPTION'
            checklist.append(dict(field=field.value,status=status,pending_decisions=required,financial_complete=False,evidence_references=['/facts','/cfo_reconciliation','/independent_display_check','/preparation_ledger_evidence']))
        note=prior.note_rows(case)
        extra_caps=re.compile(r'^(Loans and notes payable|Total.*litigation|Accrued.*litigation|Litigation|Net.*funded|Pension benefits|Retirement|Other benefit|Short.term investments|Proceeds from government|Capital expenditures|Net cash.*discontinued|Net cash.*continuing)',re.I)
        for ti,table in enumerate(case['tables']):
            for ri,row in enumerate(table):
                cap=row[0]['text'].strip() if row else ''
                if extra_caps.search(cap):note.append(dict(table=ti,row=ri,caption=cap,header=' | '.join(c['text'] for r in table[:3] for c in r),cells=row,source_sha256=f.primary.artifact.sha256,role='Supporting displayed source population; comparatives/classes not automatic selections'))
        movements=[x for x in (manual['rows'] if manual else rec['populations'][0]['rows']) if x.get('role')=='displayed_movement' or (manual and x['caption'] in ('Accounts receivable, net','Inventories','Receivables from related parties','Prepaid expenses and other assets','Payables to related parties','Accounts payable','Accrued liabilities and other','Accrued and other liabilities'))]
        period=dict(identity=case['identity'],fiscal_year=focus['fiscal_year'],fiscal_year_evidence=focus,selection_reference=case['manifest_reference'],prior_population_reference=case['proof_reference'],
            sources=case['sources'],facts=f.facts,calculations=f.entries,derived_ebit=case.get('derived_ebit'),source_binding_exceptions=errors,
            cfo_reconciliation=rec,independent_display_check=manual,movement_rows=movements,supporting_note_rows=note,passages=passages(f),
            alternatives={k:peer.candidates(case,k,co,inst) for k,(co,inst) in [('tax',('IncomeTaxExpenseBenefit',False)),('other_da',('OtherDepreciationAndAmortization',False)),('depreciation',('Depreciation',False)),('short_borrowing',('ShortTermBorrowings',True))]},
            preparation_ledger_evidence=refs,family_checklist=checklist,proposed_cfo_fact='continuing_cfo' if t=='AMD' and f.year==2025 else 'cfo',
            original_supporting_unknowns=dict(complete_expense_da=None,complete_reinvestment=None,additional_unidentified_borrowing=None,unknown_restrictions=None,operating_reserve=None,unidentified_claims=None,complete_lease_cash=None),
            cash_sign_multipliers={k:-1 for k in ('cash_capex','acquisition','acquisition_cash','iprd_cash','other_acquisition_cash','cash_tax','cash_tax_gross','cash_interest','finance_principal_cash','finance_interest_cash','op_cash') if k in f.facts},
            new_assumptions_active=False,analyst_complete=False)
        if 'incentive_cash' in f.facts:period['cash_sign_multipliers']['incentive_cash']=1
        packages.setdefault(t,dict(schema='company-analyst-review-v1',version=1,ticker=t,source_commit=BASELINE,review_author='Retained company review, no user acceptance',review_recorded_at_utc=REVIEW_TIME,periods=[],new_assumptions_active=False,analyst_complete=False,phase1_closed=False,valuation_consumption_approved=False))['periods'].append(period)
    for t,p in packages.items():
        p['periods'].sort(key=lambda r:r['identity']['annual_end']);p.update(family_slots=70,approval_table_reference=SUMMARY+'#/decisions',outcomes=dict(Counter(c['status'] for r in p['periods'] for c in r['family_checklist'])),evidence_acquisition_requirements=[x for x in missing if x['ticker']==t]);p['review_revision']=digest(relevant(p))
    return packages,missing


def decisions(p):
    t=p['ticker']
    common_concept='EntityCommonStockSharesOutstanding' if t=='JNJ' else 'CommonStockSharesOutstanding'
    selected_shares=[]
    for r in p['periods']:
        matches=[v for k,v in r['facts'].items() if k.startswith('shares:'+common_concept+':') and not v['occurrences'][0]['dimensions']]
        if len(matches)!=1:raise ValueError('One exact proposed common-share observation required')
        v=matches[0];selected_shares.append(v['value']+' shares @ '+v['as_of']+' (decimals '+v['precision']+')')
    def nums(key,calc=False):
        out=[]
        for r in p['periods']:
            item=next((x for x in r['calculations'] if x['input_id']==key),{}) if calc else r['facts'].get(key,{})
            out.append(str(D(item['value'])/1000000) if item.get('value') is not None else 'unknown')
        return '/'.join(out)+' USDm'
    rows=[
        ('CF','Retain source movements and independent displayed CFO; no second movement deduction or separate residual operation.',nums('cfo'),
         'Not operating-only cash delta NWC or FCFF. '+('2025 propose continuing CFO6493, with discontinued1216 and consolidated7709 retained separately;2022/2025 independent display checks do not replace original PARTIAL parser results.' if t=='AMD' else 'Mixed/deferred/other adjustments remain source populations; pure tax note does not substitute for a mixed CFO row.')),
        ('DA','Select a labeled LIMITED historical D&A proxy with the explicit company-specific scope below.',nums('limited_da_proxy',True),
         {'MU':'Manufacturing D&A/expense versus inventory capitalization/release timing and incentive-reduced basis remain. Rounded depreciation plus amortization need not equal CFO, no rounding plugs; finance amortization not incremental. Alternative expense-note observations only, not complete expense certification.',
          'AMD':'2021–23 OtherDepreciationAndAmortization already includes acquisition amortization;2024–25 add only separate CFO AdjustmentForAmortization2393/2254 to base671/750. Do not add COGS/opex acquisition captions again, operating ROU or inventory step-up189. Exact five extension/scope approvals remain pending; frozen gates/negative findings unchanged. Alternative expense/depreciation-only remains partial; no generic fallback.',
          'JNJ':'Consolidated CFO proxy can include discontinued-business D&A; do not add rounded intangible expense4700/4300/4500/4500/4600 or IPR&D impairments again. Expense/continuing-only allocation unproved. Alternative uniformly continuing expense D&A remains unavailable without a supported allocation; no subtraction-based balancing amount.'}[t]),
        ('INV','Keep original cash PP&E as separate input, with acquisitions/IPR&D, noncash additions, capital creditors and source incentives separately visible.',nums('cash_capex'),
         {'MU':'Gross cash PP&E is default proposal. Separate cash incentives '+nums('incentive_cash')+'; nondefault PP&E-net-of-receipts alternative '+nums('net_incentive_cash_alternative',True)+'. Government cash timing/basis reduction/receivables/earned benefits differ; no complete reinvestment, incentive forecast or gross depreciation normalization. Manufacturing inventory write-downs/idle capacity are not capex.',
          'AMD':'Xilinx/Pensando/ZT acquisitions and inventory step-up are not ordinary PP&E. Separate noncash lease additions, unpaid capex72/157/106/144/129 and discontinued-business cash where reported; no manufactured pure acquisition split. Alternative broader investment perimeter requires separately approved sourced non-overlap, not a new sum.',
          'JNJ':'IPR&D impairment is an expense in approved EBIT; acquired-IPR&D/milestone cash and acquisition cash are separate and may differ. Do not reverse EBIT or add charged IPR&D again. Kenvue separation/continuing versus consolidated cash perimeter is explicit, not an organic normalized investment history.'}[t]),
        ('SBC','Use named recognized SBC expense as a once-only labeled cost proxy; preserve CFO addback, tax benefits and awards separately.',nums('sbc_expense')+'; addback '+nums('sbc_addback'),
         'No duplicate charge, rounding adjustment or capitalized/unrecognized-award cost assumed expensed. '+('MU capitalization/inventory recognition differs: expense and CFO SBC differ across all five years.' if t=='MU' else 'Original expense/addback/scope differences remain; no numerical dilution/award valuation.')),
        ('TAX','Retain provision, exact original pretax scope and issuer/accounting tax context separately from cash/deferred taxes; no future rate.',nums('tax')+'; cash net '+nums('cash_tax')+'; other cash tag '+nums('cash_tax_gross'),
         'No clamp, tax-shield or new ratio equation. '+('Before-equity pretax '+nums('pretax_equity_scope')+' is not the generic approved denominator; issuer ETR including2023 loss-year−3.1% remains a disclosure, not a derived positive-denominator override.' if t=='MU' else 'AMD2023 tagged pure value68 is an unselected representation anomaly, not a68x rate or silently repaired−0.68; existing policy ETR/operands remain in the ledger.2025 note deferred252 versus CFO248 differ without a plug.' if t=='AMD' else 'Original continuing tax context and consolidated cash taxes are different scopes around Kenvue; no unsupported operating-tax allocation or tax rate approval.')),
        ('CASH','Select gross named current financial captions; keep restrictions, noncurrent/strategic holdings, grant receivables and parent totals separate.',nums('gross_current_financial',True),
         'Not unrestricted/excess cash. Unknown reserves/restrictions remain unbounded; no cash-restricted parent addition. Alternative defer reserve-adjusted selection, no default reserve amount.'),
        ('FIN','Select named face carrying current/noncurrent financing; operating leases service, finance leases asset financing with no additional unidentified-borrowing adjustment.',nums('named_financing',True),
         {'MU':'Current Debt plus noncurrent debt/finance caption already includes embedded gas/supply finance leases. Do not add finance parent886/1281/2054/3044/2387 again or use gross principal/fair value.2026 current491 is finance current, not an additional bond maturity.',
          'AMD':'ShortTermBorrowings is captioned current portion of long-term debt, not incremental CP; add noncurrent carrying only.2025 DebtCurrent874 confirms, not another874. Unquantified finance/other funding stays unknown; no source-zero inference.',
          'JNJ':'Loans/notes payable is the current face parent; term-current maturities are included, not added again alongside noncurrent carrying. Operating leases/rounded finance/other funding remain distinct; no complete debt claim.'}[t]+' Approved omission would be an analyst assumption of potentially unbounded exposure, not reported zero/immateriality. Alternative leave unidentified borrowing operation unresolved.'),
        ('CLAIMS','Retain known pension/benefit, litigation/tax, NCI and strategic populations without net/gross overlap; propose no additional unidentified preferred/NCI/pension adjustment.',
         ('Pension recognized '+nums('pension_recognized')+'; talc carrying '+nums('talc_carrying_reserve')+'; nominal '+nums('talc_nominal_reserve')+'; reversal '+nums('talc_reversal') if t=='JNJ' else 'Exact known populations in facts, note rows and claims ledger; missing subamounts remain unknown.'),
         'Omission would be an explicit unbounded analyst assumption, not reported zero or immateriality. '+('JNJ pension funded status and recognized liabilities are distinct; talc reserve, related reversal/settlement expenses and other litigation may overlap already recorded liabilities. No aggregate claim sum or valuation deduction; leave unknown additional exposure unbounded.' if t=='JNJ' else 'Do not net pension assets/liabilities or infer absent claims zero. Alternative retain that operation unresolved; no materiality estimate.')),
        ('SHARES','Select fiscal-end unclassed common counts for MU/AMD, actual later cover counts for JNJ; retain other dated common populations, award classes, EPS denominators and acquisition issuance separately.',
         '; '.join(selected_shares),
         'Fiscal-end MU/AMD counts retain reported million-share precision; the alternative later cover counts have different dates, not greater same-date accuracy. JNJ later cover counts are not fiscal-end counts. No award aggregation, EPS substitution, dilution estimate or automatic comparative restatement.')]
    if t=='JNJ':rows.insert(0,('PERIMETER','Approve original-as-filed historical panels, NOT a homogeneous continuing-business cash/earnings series.',
        'FY2021/22 original sales93775/94943 include Consumer Health;2023–25 continuing sales85159/88821/94193. Consolidated CFO23410/21194/22791/24266/24530 retained;2023 gain on Kenvue separation20984 is a separate CFO reversal.',
        'This preserves actual selected presentations without splicing later recast comparatives. Continuing-income/combined-cash boundaries and related claims/tax/D&A allocations remain supporting limitations, not silently matched. Alternative a uniformly continuing-only five-year contract needs independently supported allocations absent from this reviewed package; not solved by subtracting sale gains or CFO. Entire JNJ checklist remains pending this substantive perimeter decision.'))
    return [dict(decision_id=t+'-'+key,ticker=t,identities=[r['identity'] for r in p['periods']],recommendation=rec,numerical_effect=n,uncertainty_and_alternative=alt,status=PROPOSED,accepted=False,author=p['review_author'],recorded_at_utc=REVIEW_TIME,evidence_references=[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json#/periods/{i}' for i in range(5)]) for key,rec,n,alt in rows]


def outputs():
    packages,missing=build()
    summary=dict(schema='retained-priority-review-batch-v1',source_commit=BASELINE,tickers=list(TICKERS),selected_periods=15,family_slots=210,
        companies={t:dict(periods=5,outcomes=p['outcomes'],review_revision=p['review_revision']) for t,p in packages.items()},decisions=[d for t in TICKERS for d in decisions(packages[t])],
        evidence_acquisition_requirements=missing,new_sec_requests=0,new_assumptions_active=False,completed_company_packages=11,approved_partial_company_packages=1,pending_review_company_packages=3,broad_assessment_only=27,phase1_closed=False)
    return {**{f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json':p for t,p in packages.items()},SUMMARY:summary}


if __name__=='__main__':
    result=outputs()
    if '--check' in sys.argv:
        for path,p in result.items():
            if (ROOT/path).read_text()!=json.dumps(p,sort_keys=True,indent=2)+'\n':raise SystemExit('Priority batch replay differs: '+path)
        print('Exact MU/AMD/JNJ review replay:15 selected annuals/210 families; all judgments inactive')
    else:print(json.dumps(result,sort_keys=True,indent=2))
