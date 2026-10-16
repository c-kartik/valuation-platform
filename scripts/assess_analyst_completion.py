"""Retained-result planning assessment only: no extraction, approval or repair.

Replay: PYTHONPATH=src .venv/bin/python scripts/assess_analyst_completion.py --check
Output defaults to the machine-checkable JSON companion on stdout.
"""
from collections import Counter
import hashlib
import json
from functools import lru_cache
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
BASELINE='46a0b5729887e1b5fc2b54fafe840578f4c3abb7'
OUTPUT='docs/analyst-complete-historical-assessment.json'
MARKDOWN='docs/analyst-complete-historical-assessment.md'
COVERAGE='docs/preparation-coverage-results.json'
POPULATIONS='docs/reported-population-delivery-ledger.json'
ASSEMBLY='docs/prepared-assembly-summary.json'
VALIDATION='docs/universe/phase-1h5-issuer-validation.json'
DISPOSITION='docs/phase1-issuer-preparation-disposition.json'

# Planning tasks, not approved exclusions, extraction rules or financial estimates.
TASKS={
 'S0':dict(name='Required-perimeter decision and completion acceptance checklist',category='company_specific_financial_selection',dependencies=[],
  action='Specify each required historical field/population and demonstrate why any exclusion genuinely makes it unnecessary; CFO alone cannot waive D&A, investment or financing requirements.',
  acceptance='Every required field has a supported selection or a defensible explicitly approved estimate/classification/exclusion, with evidence, scope, uncertainty and no required null.',
  stop='If an essential input has neither evidence nor a defensible alternative, retain INCOMPLETE; do not shrink the target to fit available data.'),
 'S1':dict(name='Exact source/selection integration and audit controls',category='reusable_extraction_mapping_or_evidence_repair',dependencies=['S0'],
  action='Reuse existing package/audit/overlay infrastructure; integrate only reviewed missing joins or mappings identified by exact ledger diagnostics. Review notes before deciding any fresh evidence dependency.',
  acceptance='Exact accession/date/unit/precision/source binding, non-overlap, immutable alternatives, persisted revision-bound decisions and stale/dependency rejection pass; no source changes.',
  stop='No blanket new extractor. Unavailable evidence is not a repository defect; list exact required evidence/decision and stop.'),
 'S2':dict(name='Income total selection and existing approved EBIT scope',category='company_specific_financial_selection',dependencies=['S0'],
  action='Resolve exact Revenue/EBIT conflicts against existing face-statement scope; preserve approved derivations and operands. Review five CVX EBIT gaps without inventing an equation.',
  acceptance='Selected population economically matches requested Revenue/operating EBIT, all alternatives retained; no precedence-only winner.',
  stop='No supported choice/equation means unresolved; any new financial treatment requires separate authorization.'),
 'S3':dict(name='Expense D&A perimeter and timing disposition',category='company_specific_financial_selection',dependencies=['S0'],
  action='Distinguish policy values from complete expense D&A, CFO support and combined captions; retain seven negative reviews. Propose only evidence-supported classifications or a defensible approved exclusion under S0.',
  acceptance='Required D&A has proved expense scope or an explicit defensible analyst basis; no residual amortization or unproved component sum. Accepted MSFT inclusion assumption stays labeled assumption.',
  stop='Unavailable amortization/inventory/lease overlap with no defensible basis remains blocking; do not infer zero or reopen exhausted research.'),
 'S4':dict(name='Cash investment scope and unavailable allocations',category='unavailable_disclosure_requiring_justified_alternative',dependencies=['S0'],
  action='Review approved cash Capex alongside unapproved broader captions, acquisition/intangible spending, creditors and noncash additions. A policy amount is not complete reinvestment.',
  acceptance='Required purchase perimeter selected with complete/non-overlap evidence or an explicitly justified accepted alternative; allocations remain separate if not required by the approved perimeter.',
  stop='No disclosed allocation and no defensible alternative means incomplete for the broader requested perimeter; no estimate from residuals.'),
 'S5':dict(name='CFO reconciliation roles and historical tax/SBC/movement decisions',category='company_specific_financial_selection',dependencies=['S0'],
  action='Classify exact movement/tax/SBC rows, preserve signs and acquisition/FX/reclassification scope; resolve supported/partial/failed displayed CFO checks. Determine whether a remainder is required and retain its unclassified role.',
  acceptance='Selected required rows and omissions have approved rationale; any reconciliation has independently bound operands, no balancing plug, no book-delta substitution, no duplicate SBC. Provision/pretax/ETR/cash/deferred roles remain separate.',
  stop='MCD failed check cannot pass by widening tolerance; unresolved hierarchy or undisclosed allocations remain blocking if required. No future tax rate.'),
 'S6':dict(name='Financial balances, borrowing/lease, claims and dated-share selection',category='company_specific_financial_selection',dependencies=['S0'],
  action='Use current bridge observations/partitions to select required named populations and exclusions; resolve carrying/principal/fair-value, class/date, restricted/strategic and parent-child scope. Do not force a combined total.',
  acceptance='No knowingly double-counted debt/lease/claims; every required population/class/date accounted for, or a defensible explicit alternative accepted. Narrow totals retain labels; no excess-cash or dilution claim.',
  stop='Unknown short debt, restrictions, claims or class coverage is not zero. Named subtotal approval alone does not exclude unknown populations.'),
 'S7':dict(name='Full available-history extension and comparability',category='history_comparability_boundary',dependencies=['S1','S2','S3','S4','S5','S6'],
  action='After one-period completion, repeat exact evidence/decisions over remaining selected annuals, checking acquisitions, FX, reclassification, leases and stock-versus-cash boundaries; do not extend a pilot approval implicitly.',
  acceptance='Every available selected annual independently satisfies the completion checklist; opening/movement scope proved only when required and evidenced. Missing target slots separately dispositioned.',
  stop='Standalone/predecessor or empty registrant history cannot be filled by invented periods. Additional evidence/continuity approval is an external dependency, not scheduled completion.'),
}
FIELD_TASK={
 'revenue':'S2','ebit':'S2','depreciation_amortization':'S3','cash_capex':'S4',
 'reported_cash_flow_working_capital_movements':'S5','deferred_taxes':'S5',
 'stock_based_compensation':'S5','unclassified_cfo_reconciliation_residual':'S5',
 'reported_cfo':'S5','reported_tax_context':'S5','cash_investment_components':'S6',
 'debt_lease_components':'S6','other_equity_bridge_claims_assets':'S6','point_in_time_shares':'S6'}
DETAIL_SOURCES={
 'cash_capex':'docs/refreshed-capex-ledger.json','depreciation_amortization':'docs/retained-d-and-a-ledger.json',
 'reported_cash_flow_working_capital_movements':'docs/retained-working-capital-ledger.json',
 'deferred_taxes':'docs/retained-tax-sbc-ledger.json','stock_based_compensation':'docs/retained-tax-sbc-ledger.json',
 'cash_investment_components':'docs/retained-bridge-component-ledger.json','debt_lease_components':'docs/retained-bridge-component-ledger.json',
 'other_equity_bridge_claims_assets':'docs/retained-claims-shares-ledger.json','point_in_time_shares':'docs/retained-claims-shares-ledger.json',
 'reported_tax_context':'docs/retained-reported-tax-context-ledger.json'}
FIELD_REQUIREMENT={
 'revenue':'Select the consolidated operating revenue population; resolve differing eligible totals, not by policy order alone.',
 'ebit':'Select operating-only income or verify the exact approved derivation/operands; no silent treatment of derived income as direct.',
 'depreciation_amortization':'Establish required expense/timing scope; CFO add-backs, impairment/accretion and lease amortization observations are not automatically complete D&A.',
 'cash_capex':'Select the required cash purchase perimeter; PP&E/intangible/acquisition/netting/creditor/noncash roles need separate disposition, not a complete reinvestment claim.',
 'reported_cash_flow_working_capital_movements':'Decide which displayed cash-contribution rows are required and prove parent/child coverage; preserve tax/noncurrent/acquisition scope, never call them book delta NWC.',
 'deferred_taxes':'Select deferred-tax CFO reconciliation role separately from provision, balances, credits and cash; absence is not zero.',
 'stock_based_compensation':'Select expense proxy versus CFO reconciliation add-back once, preserve rounding and awards; no duplicate economic cost.',
 'unclassified_cfo_reconciliation_residual':'If required, retain a source-bound versioned reconciliation remainder and classified operands; it is not independent validation or an economic adjustment.',
 'reported_cfo':'Retain consolidated subtotal and exact independent displayed reconciliation disposition; partial/failed checks require resolution or a defensible genuinely unnecessary requirement.',
 'reported_tax_context':'Select provision, eligible pretax and policy ETR as separate historical roles; cash/deferred taxes and future operating rates are not substitutes.',
 'cash_investment_components':'Select required current/long-term/restricted/strategic populations and no-overlap boundaries; narrow liquidity does not prove unrestricted or excess availability.',
 'debt_lease_components':'Account for required term/short/CP/lease populations, carrying versus principal/fair value and overlap; named financing subtotal does not establish unknown short debt zero.',
 'other_equity_bridge_claims_assets':'Disposition required preferred/NCI/pension/NOL/investment/other claims with inclusion relationships; absent tag or partial scope is not zero or immaterial.',
 'point_in_time_shares':'Select required dated issuer/class population with explicit coverage; source aggregate versus separate classes, cover dates, EPS and awards stay distinct, no forecast dilution.'}


@lru_cache(maxsize=None)
def load(path):return json.loads((ROOT/path).read_text())
def ref(path,pointer=''):return dict(path=path,pointer=pointer)
def seal(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def build():
    coverage=load(COVERAGE);pop=load(POPULATIONS);assembly=load(ASSEMBLY)
    validation=load(VALIDATION);disposition=load(DISPOSITION)
    cohort={r['execution_ticker']:r for r in validation['rows'] if r['classification']!='SPECIALIZED_METHODOLOGY_REQUIRED'}
    assert set(cohort)==set(coverage['issuer_slots'])==set(assembly['issuers'])
    old={r['ticker']:(i,r) for i,r in enumerate(disposition['rows'])}
    sources={p:seal(p) for p in (COVERAGE,POPULATIONS,ASSEMBLY,VALIDATION,DISPOSITION,
        'docs/dcf-input-contract.md','docs/phase1-delivery-acceptance-report.md',
        'docs/phase1-preparation-pilot-gap-assessment.md','docs/d-and-a-independent-scope-dispositions.json',
        'docs/preparation-independent-results.json','docs/preparation-workflow-summary.json')}
    for path in set(DETAIL_SOURCES.values()):sources[path]=seal(path)
    rows=[]
    for ticker in sorted(cohort):
        selected=coverage['issuer_slots'][ticker];frozen=cohort[ticker]
        record='docs/company-data-preparation/'+('supported-seeds/' if ticker in ('META','COST') else '')+ticker+'.md'
        text=(ROOT/record).read_text();assert text.startswith('# '+ticker)
        sources[record]=seal(record)
        cr=[(i,r) for i,r in enumerate(coverage['rows']) if r['ticker']==ticker]
        pr=[(i,r) for i,r in enumerate(pop['rows']) if r['ticker']==ticker]
        assert len(cr)==selected['selected']*14 and len(pr)==selected['selected']
        ends=sorted({r['annual_end'] for _,r in cr});assert ends==sorted(frozen['selected_annual_end_dates'])
        assert selected['cik']==frozen['cik']
        latest=ends[-1] if ends else None
        byfield={f:[(i,r) for i,r in cr if r['field']==f] for f in FIELD_TASK}
        requirements=[]
        for f,items in byfield.items():
            latest_rows=[r for _,r in items if r['annual_end']==latest]
            detail=[]
            if f in DETAIL_SOURCES:
                path=DETAIL_SOURCES[f]
                for i,r in enumerate(load(path)['rows']):
                    if r['issuer']!=ticker:continue
                    focus=r['fields'].get(f,r) if isinstance(r.get('fields'),dict) else r
                    detail.append(dict(source=ref(path,'/rows/'+str(i)),
                        status=focus.get('status'),coverage=focus.get('coverage'),
                        requirements=focus.get('unresolved_requirements',[]),errors=focus.get('errors',focus.get('evidence_errors',[])),
                        approved_entry_evidence_gaps=r.get('approved_entry_evidence_gaps',[])))
            requirements.append(dict(requirement_id=ticker+':'+f,field=f,task_id=FIELD_TASK[f],
                category=TASKS[FIELD_TASK[f]]['category'],status='REQUIRES_COMPANY_COMPLETENESS_REVIEW',
                reason=FIELD_REQUIREMENT[f],
                available_history_counts={k:sum(bool(r[k]) for _,r in items) for k in
                    ('valued','policy_prepared','approved_complete_total','partial_support','conflicting','invalid_evidence','required_value_unavailable')},
                latest_selected_outcome={k:latest_rows[0][k] for k in
                    ('valued','policy_prepared','approved_complete_total','partial_support','conflicting','invalid_evidence','required_value_unavailable')} if latest_rows else None,
                exact_field_period_references=[ref(COVERAGE,'/rows/'+str(i)) for i,r in items],
                retained_detail=detail,
                conditional_work_categories=['analyst_assumption_requiring_approval','unavailable_disclosure_requiring_justified_alternative'],
                category_caveat='Financial review must establish whether a supported selection suffices, a defensible assumption is needed, or evidence is unavailable; these are possible routes, not diagnosed missing disclosures or approved estimates.',
                depends_on=['S0'],action_reference='/shared_tasks/'+FIELD_TASK[f],
                approval='PROPOSED_ONLY',cause_certainty='Observed ledger flags; missing alone does not prove unavailable disclosure or extraction defect.'))
        periods=[]
        for i,r in pr:
            ident=r['identity']['fields'];assert ident['cik']==selected['cik']
            end=ident['annual_end']['date'];assert end in ends
            periods.append(dict(identity=ident,source=ref(POPULATIONS,'/rows/'+str(i)),
                cfo_status=r['reconciliation']['status'],cfo_reason=r['reconciliation']['reason'],
                bridge_requirements=r['bridge']['requirements'],
                invalid_primary_binding_diagnostics=len(r['bridge']['invalid_bindings']),
                invalid_binding_interpretation='Includes ineligible/nonmonetary/nil rows; not all are defective accepted values or repair tasks. Inspect exact proof before classifying.',
                observed_roles=sorted({x['role'] for x in r['inputs'] if x.get('value') is not None})))
        periods.sort(key=lambda r:r['identity']['annual_end']['date'])
        pilot=None
        if ticker in ('MSFT','AAPL','GOOGL'):
            path='docs/company-data-preparation/'+ticker.lower()+'-analyst-input-package.json'
            package=load(path);view=package['accepted_view'];sources[path]=seal(path)
            audit='docs/company-data-preparation/'+ticker.lower()+'-analyst-treatment-acceptance.json';sources[audit]=seal(audit)
            approved_ends=['2025-06-30','2026-06-30'] if ticker=='MSFT' else [package['identity']['annual_end']]
            pilot=dict(approved_annual_ends=approved_ends,scope='Named partial selections and historical classifications only, not analyst completeness.',
                package=ref(path,'/accepted_view'),audit=ref(audit),
                original_unresolved=package.get('unresolved_requirements',[]) if ticker!='MSFT' else [
                    dict(annual_end=p['identity']['annual_end'],requirements=p['unresolved_requirements']) for p in package['periods']],
                accepted_short_borrowing=view['periods'][1]['additional_short_borrowing'] if ticker=='MSFT' else None,
                assumptions='Finance amortization included in rounded D&A is approved but unproved, not source-confirmed; residual-caption capital estimate is non-default.' if ticker=='MSFT' else 'No finance-amortization inclusion assumption; complete expense D&A remains null.',
                latest_selected_approved=latest in approved_ends,
                completion_obstacles='See exact package unresolved requirements and named-subtotal limitations; acceptance does not make undisclosed populations unnecessary.')
        hard_latest=any(r['latest_selected_outcome'] and
            (r['latest_selected_outcome']['conflicting'] or
             (r['field'] in ('revenue','ebit','depreciation_amortization','cash_capex') and r['latest_selected_outcome']['required_value_unavailable'])) for r in requirements)
        if selected['selected']<5:band='HISTORY_BOUNDARY';readiness='HISTORY_LIMITED_INCOMPLETE'
        elif pilot:band='FOCUSED_HARD_GAPS';readiness='APPROVED_PARTIAL_PILOT_INCOMPLETE'
        elif hard_latest or any(r['cfo_status']!='SUPPORTED' for r in periods):band='COMPLEX_REVIEW';readiness='COMPLEX_SELECTION_INCOMPLETE'
        else:band='STANDARD_REVIEW';readiness='RETAINED_REVIEW_CANDIDATE_INCOMPLETE'
        financial={'FOCUSED_HARD_GAPS':[2,4,8],'STANDARD_REVIEW':[2,4,7],
            'COMPLEX_REVIEW':[4,8,15],'HISTORY_BOUNDARY':[4,8,15]}[band] if periods else None
        full={'FOCUSED_HARD_GAPS':[8,16,30],'STANDARD_REVIEW':[6,12,22],
            'COMPLEX_REVIEW':[12,25,45],'HISTORY_BOUNDARY':[6,12,22]}[band] if periods else None
        reasons=['S0 required-field perimeter/defensible exclusions','S1 exact audit/source integration','S6 bridge/claims/class/date decisions','S7 period-by-period extension']
        if pilot:reasons.append('Existing company package reduces setup, but unavailable disclosures/approved partial populations still prevent completeness')
        if hard_latest:reasons.append('Latest selected scalar scope/null/conflict or component conflict evidenced in field references')
        if any(r['cfo_status']!='SUPPORTED' for r in periods):reasons.append('Exact partial/failed source reconciliation periods require financial/source disposition')
        if not periods:reasons.append('No selected current-CIK annual exists in retained scope; numerical completion cannot be scheduled')
        rows.append(dict(ticker=ticker,cik=selected['cik'],frozen_classification=frozen['classification'],record=ref(record),
            history=dict(available_selected=selected['selected'],target_slots=5,target_deficit=5-selected['selected'],annual_ends=ends,
                latest_selected=latest,missing_slot_dates=None,proven_unavailable_preexistence_slot_count=None,
                distinction=('Empty current-CIK history, not proof of issuer nonexistence; no predecessor identity inferred.' if ticker=='XOM' else
                    'Two selected standalone/carve-out histories; three unfilled target slots are not proved nonexistent business years. Predecessor comparability is unapproved.' if ticker in ('GEV','SNDK') else
                    'Five selected annuals; continuity/comparability still requires review.'),
                exceptions=selected['exceptions']),
            review_depth='Retained field/policy replay and displayed-source population checks; no new source review in this assessment. '+('Company-specific partial analyst package reviewed only for listed approved periods.' if pilot else 'No equivalent consolidated analyst-complete package approval established.'),
            pilot=pilot,analyst_complete_latest=False,analyst_complete_full_available_history=False,
            readiness=readiness,effort_band=band,financial_review_person_days_low_base_high=financial,
            full_available_history_financial_review_person_days_low_base_high=full,
            engineering_person_days_low_base_high=([0.5,1,2] if band!='COMPLEX_REVIEW' else [1,2,4]) if periods else None,
            full_available_history_engineering_person_days_low_base_high=([1,2,4] if band!='COMPLEX_REVIEW' else [2,4,7]) if periods else None,
            estimate_basis=reasons,effort_confidence='MEDIUM on task boundaries, LOW on closure feasibility' if pilot else 'LOW: company-specific exclusions/alternatives not independently resolved',
            completion_elapsed_time='NOT_ESTIMABLE until essential alternatives/evidence and approvals exist',
            requirements=requirements,period_limitations=periods,
            original_frozen_gaps_reference=ref(DISPOSITION,'/rows/'+str(old[ticker][0])) if ticker in old else ref(VALIDATION,'/rows/'+str(validation['rows'].index(frozen))),
            prior_research_routing=old[ticker][1]['retained_research'] if ticker in old else [],
            original_blockers_unchanged=True,specialized_escalation='NOT_ESTABLISHED: no new evidence supports reclassification in this retained assessment',
            independent_sample=dict(counts=dict(Counter(r['status'] for r in load('docs/preparation-independent-results.json')['rows'] if r['ticker']==ticker)),
                exact_references=[ref('docs/preparation-independent-results.json','/rows/'+str(i)) for i,r in enumerate(load('docs/preparation-independent-results.json')['rows']) if r['ticker']==ticker],
                limitation='A bounded field sample, not independent whole-history/company completeness; no sample means unassessed, not failed.'),
            review_queue_reference=ref('docs/preparation-workflow-summary.json','/per_issuer/'+ticker),
            review_queue_limit='Retained assembly snapshot separates primary/nested/informational diagnostics; it predates local analyst view approvals and is not a count of financial inputs still missing.',
            history_action=dict(task_id='S7',category='history_comparability_boundary',depends_on=['S0'],
                acceptance='Separately prove comparability of all available annuals; explicit target-history exclusion needs justification and approval, not invented years.',
                stop='Retain exact missing slots with null identities; no automatic predecessor or acquisition research.'),
            stopping_condition='No required unresolved input may be called complete; stop on unavailable essential evidence/no defensible alternative. Proposed tasks are not execution authority.'))
    # Priority is an explainable work sequence, not calibrated financial confidence.
    order={'MSFT':0,'AAPL':1,'GOOGL':2}
    rows.sort(key=lambda r:(order.get(r['ticker'],3),{'STANDARD_REVIEW':0,'COMPLEX_REVIEW':1,'HISTORY_BOUNDARY':2,'FOCUSED_HARD_GAPS':0}[r['effort_band']],r['ticker']))
    for i,r in enumerate(rows):r['priority_rank']=i+1
    tasks={k:dict(v,benefiting_issuers=[r['ticker'] for r in rows if r['history']['available_selected'] and
        (k in ('S0','S1','S7') or any(x['task_id']==k for x in r['requirements']))],approval='PROPOSED_NOT_AUTHORIZED') for k,v in TASKS.items()}
    batches=[dict(batch_id='B0',targets=['MSFT:2026-06-30'],purpose='Smallest end-to-end latest-period completion attempt',
        dependencies=['S0'],acceptance='Every required field selected/approved with defensible basis or genuinely unnecessary under an approved exclusion; no required null or unresolved scope. Persist exact audit and prove serialization/staleness, preserving source facts.',
        stop='One retained review of the listed MSFT gaps only. If FY2026 short debt or another essential population has no defensible alternative, return INCOMPLETE with exact unmet requirement; no automatic research.',
        financial_review_person_days_low_base_high=[2,4,8],engineering_person_days_low_base_high=[0.5,1,2],
        complete_by_date='NOT_ESTIMABLE; approval and unavailable-evidence dependencies remain'),
        dict(batch_id='B1',targets=['MSFT:2025-06-30','AAPL:2025-09-27','GOOGL:2024-12-31'],
            purpose='Apply demonstrated completion checklist to the other already-reviewed periods, independently; Alphabet FY2025 is not included or approved.',
            dependencies=['B0'],stop='Stop each period at an essential unavailable amount with no defensible alternative; do not transfer financial assumptions.'),
        dict(batch_id='B1-LATEST',targets=['GOOGL:2025-12-31'],dependencies=['B1'],
            purpose='Separate latest-selected Alphabet attempt; FY2024 approval and classifications do not extend to FY2025.',
            stop='One retained review; stop incomplete on essential unsupported evidence or no defensible alternative before history extension.')]
    for band in ('STANDARD_REVIEW','COMPLEX_REVIEW'):
        tickers=[r['ticker'] for r in rows if r['effort_band']==band]
        for n in range(0,len(tickers),3):
            batches.append(dict(batch_id=band+'-'+str(n//3+1),targets=[t+':'+next(r['history']['latest_selected'] for r in rows if r['ticker']==t) for t in tickers[n:n+3]],
                purpose='Latest-selected-period review using shared S1/S3/S5/S6 controls; independently approve each company perimeter.',dependencies=['B0','S0','S1'],
                stop='Three issuer packages maximum, one bounded retained inspection each; unresolved alternative blocks completion, not an automatic follow-up queue.'))
    batches.extend([dict(batch_id='HISTORY',targets=['GEV','SNDK','XOM'],dependencies=['S0'],
        purpose='Decide admissible available-history/predecessor boundary only; no numerical reconstruction. XOM has no latest period to package.',
        stop='No identity, date or pre-existence assumption; missing target slots remain unless defensible boundary explicitly approved.'),
        dict(batch_id='HISTORY-AVAILABLE',targets=['GEV:2025-12-31','SNDK:2026-07-03'],dependencies=['HISTORY','S0'],
            purpose='Latest available selected input review after history boundary decision; not five-year or predecessor reconstruction.',
            stop='One retained review of each available perimeter; required unsupported standalone/comparable data remains incomplete.'),
        dict(batch_id='EXTEND',targets=[r['ticker'] for r in rows if r['history']['available_selected']],dependencies=['S7'],
            purpose='Only after individual latest completion, extend selected histories in the same finite groups; include GOOGL FY2025 as a separate unreviewed selection.',
            stop='No implied prior-year approval. Stop on comparability or essential unavailable evidence; no promise of 210 completed target slots.')])
    return dict(schema='retained-analyst-completion-assessment-v1',baseline=BASELINE,
        target_definition='Every required input selected with evidence, defensible approved estimate/classification, or genuinely necessary approved methodological exclusion; acknowledged gaps are not complete.',
        source_sha256=sources,issuer_count=len(rows),selected_periods=sum(r['history']['available_selected'] for r in rows),
        target_slots=5*len(rows),target_deficits=sum(r['history']['target_deficit'] for r in rows),
        field_period_slots=len(coverage['rows']),field_families=list(FIELD_TASK),
        analyst_complete_issuers=0,approved_pilot_periods=sum(len(r['pilot']['approved_annual_ends']) for r in rows if r['pilot']),
        readiness_counts=dict(Counter(r['readiness'] for r in rows)),effort_counts=dict(Counter(r['effort_band'] for r in rows)),
        shared_tasks=tasks,shared_engineering_person_days_low_base_high=[8,15,25],
        financial_review_latest_person_days_low_base_high=[sum(r['financial_review_person_days_low_base_high'][i] for r in rows if r['financial_review_person_days_low_base_high']) for i in range(3)],
        financial_review_full_available_person_days_low_base_high=[sum(r['full_available_history_financial_review_person_days_low_base_high'][i] for r in rows if r['full_available_history_financial_review_person_days_low_base_high']) for i in range(3)],
        issuer_engineering_latest_person_days_low_base_high=[sum(r['engineering_person_days_low_base_high'][i] for r in rows if r['history']['available_selected']) for i in range(3)],
        issuer_engineering_full_available_person_days_low_base_high=[sum(r['full_available_history_engineering_person_days_low_base_high'][i] for r in rows if r['history']['available_selected']) for i in range(3)],
        proposed_batches=batches,
        schedule_is_conditional_workload_not_completion_promise=True,external_evidence_wait='NOT_ESTIMABLE',
        financial_approvals_added=0,source_repairs_executed=0,phase_closed=False,rows=rows)


def validate(d):
    assert (d['issuer_count'],d['selected_periods'],d['target_slots'],d['target_deficits'])==(42,199,210,11)
    assert d['field_period_slots']==199*14 and d['approved_pilot_periods']==4
    assert len({r['cik'] for r in d['rows']})==len({r['ticker'] for r in d['rows']})==42
    assert sum(d['readiness_counts'].values())==sum(d['effort_counts'].values())==42
    identities=[p['identity']['accession'] for r in d['rows'] for p in r['period_limitations']]
    assert len(set(identities))==199
    assert {r['ticker']:r['history']['target_deficit'] for r in d['rows'] if r['history']['target_deficit']}=={'GEV':3,'SNDK':3,'XOM':5}
    def walk(x):
        if isinstance(x,dict):
            if set(x)=={'path','pointer'}:
                path=ROOT/x['path'];assert path.exists(),x
                if x['pointer']:
                    value=load(x['path'])
                    for token in x['pointer'].split('/')[1:]:
                        token=token.replace('~1','/').replace('~0','~')
                        value=value[int(token)] if isinstance(value,list) else value[token]
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(d)
    for key,t in d['shared_tasks'].items():
        assert len(t['benefiting_issuers'])==len(set(t['benefiting_issuers']))
        assert all(dep in d['shared_tasks'] for dep in t['dependencies'])
        assert all(t[k] for k in ('action','acceptance','stop'))
    for r in d['rows']:
        assert set(x['field'] for x in r['requirements'])==set(FIELD_TASK)
        assert all(x['task_id'] in d['shared_tasks'] for x in r['requirements'])
    targets={target for b in d['proposed_batches'] for target in b['targets']}
    assert all(r['ticker']+':'+r['history']['latest_selected'] in targets for r in d['rows'] if r['history']['latest_selected'])
    return d


if __name__=='__main__':
    result=validate(build());text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if '--check' in sys.argv:
        assert (ROOT/OUTPUT).read_text()==text,'Assessment replay differs'
        print('42 issuers / 199 selected / 210 target / 11 deficits / 2786 field slots; references and replay pass')
    else:print(text,end='')
