"""Alphabet mapping and a small auditable input generator; engine remains unchanged."""
from copy import deepcopy
from datetime import datetime, timezone, date
from pathlib import Path
from .rules import number, fade, growth, wacc, incremental_cash_ratio, cagr, isolated, diagnostic_axes
from .profile import read_json, read_sources, select_observation, digest, validate_profile

RELATIVE = Path('data/preload/googl-v1')
ANNUAL = ('revenue_growth','operating_margin','forecast_tax_rate','d_and_a_percent_revenue',
          'capex_percent_revenue','change_in_operating_nwc_percent_revenue')
LIMITS = {
 'revenue_growth':'Quarter-momentum extension, not guidance; seasonality/acquisition perimeter not normalized.',
 'operating_margin':'Includes SBC/service leases/Other Bets once; acquisition and infrastructure cost mix may change.',
 'forecast_tax_rate':'Normalized operating convention; reported ETR, credits and tax-payment timing are not substituted.',
 'd_and_a_percent_revenue':'Configured expense estimate including finance depreciation/intangibles once; no complete vintage/useful-life calibration.',
 'capex_percent_revenue':'Cash PP&E plus separately estimated new financed operating assets; excludes principal/acquisitions and duplicate capital-creditor settlements; software included within cash PP&E estimate.',
 'change_in_operating_nwc_percent_revenue':'20% incremental-sales convention converted to full revenue; excludes taxes/capital creditors/financial collateral/acquisitions/financing; mixed CFO not reused.',
}


def resolve_listing(ticker):
    if ticker.upper() not in ('GOOG','GOOGL'):raise ValueError('UNSUPPORTED_PREPARATION: only Alphabet preload implemented')
    return {'issuer':'Alphabet Inc.','cik':1652044,'ticker':ticker.upper(),
            'listing_class':'A' if ticker.upper()=='GOOGL' else 'C','class_equivalence':'NOT_SELECTED'}


@isolated
def generate(root, *, dataset=None, policy_path=None, ticker='GOOGL', generated_at=None):
    root=Path(root);directory=Path(dataset) if dataset else root/RELATIVE
    policy=read_json(policy_path or directory/'policy.json');config=policy['configuration']
    sources=read_sources(directory/'sources');observations=read_json(directory/'observations.json')
    source_ids={s['id'] for s in sources}
    if len({o['id'] for o in observations})!=len(observations):raise ValueError('Duplicate observation identity')
    for o in observations:
        if o['source'] not in source_ids:raise ValueError('Unknown extraction source')
        source=next(s for s in sources if s['id']==o['source'])
        if o['source_sha256']!=source['sha256']:raise ValueError('Extraction/body hash mismatch')
        if not o.get('locator') or not o.get('precision') or not o.get('mapping_version'):
            raise ValueError('Missing extraction metadata')
    cutoff=policy['review_date'];date.fromisoformat(cutoff)
    template=read_json(root/'examples/valuation/googl-fy2025-unset.json')
    fields={};selected={};support=[];diagnostics=[]
    def fact(key,definition='consolidated-reported',unit='USD'):
        row=select_observation(observations,key,definition=definition,unit=unit,cutoff=cutoff)
        expected=policy['selection'].get(key)
        if not expected or any(row.get(k)!=v for k,v in expected.items()):raise TypeError('INCOMPATIBLE_DEFINITION: period/issuer/dimensions/scope '+key)
        selected[key]=row
        return number(row['value'])
    def param(key):
        value=config.get(key)
        if value is None:raise LookupError('MISSING_EVIDENCE: explicit configuration '+key)
        return number(value)
    def put(path,value,rule,operands,keys=(),configured=False,limitation=None):
        rows=[selected[k] for k in keys]
        context_ids=['q3-2026-call','q3-2026-10q'] if path.endswith('.capex_percent_revenue') else ['q3-2026-10q'] if path.endswith(('.d_and_a_percent_revenue','.forecast_tax_rate')) else ['q3-2026-release'] if path.endswith('.change_in_operating_nwc_percent_revenue') else []
        fields[path]={'context_sources':context_ids,'context_role':'Definition/scope background only; not automatic historical calibration','configuration_selected_at':policy['configuration_provenance']['selected_at'],'value':None if value is None else format(number(str(value)) if isinstance(value,str) else value,'f'),'unit':'multiple' if path=='exit_ev_ebit_multiple' else 'fraction',
          'status':'CONFIGURED_CONVENTION' if configured else 'AVAILABLE_ESTIMATE',
          'classification':['FORECAST_ESTIMATE','MODELING_CONVENTION'] if configured else ['FORECAST_ESTIMATE','DERIVED_FROM_REPORTED_OBSERVATIONS','CONFIGURED_TRANSFORMATION'],
          'basis':'EXPLICIT_VERSIONED_CONFIGURATION' if configured else 'REPORTED_OBSERVATIONS_AND_FORECAST_RULE',
          'configuration_reference':policy['version']+'/configuration',
          'sources':sorted({r['source'] for r in rows}),'periods':[{'start':r.get('start'),'end':r['end'],'published_at':r['published_at'],'available_at':r.get('available_at',r['published_at'])} for r in rows],
          'rule':rule,'operands':operands,'limitation':limitation or LIMITS.get(path.split('.')[-1], 'Explicit long-run estimate; not independently approved or complete financial calibration.')}
    def gap(paths,exc):
        status='INCOMPATIBLE_DEFINITION' if isinstance(exc,TypeError) else 'MISSING_EVIDENCE'
        for path in paths:
            put(path,None,'unavailable-v1',{'reason':str(exc)},configured=True,limitation=str(exc))
            fields[path]['status']=status
    # All required values can independently remain missing; unaffected fields survive.
    revenue=[];growths=[]
    try:
        anchor=fact('fy2025_revenue')
        if str(anchor)!= '402836000000':raise ValueError('Retained GOOGL anchor mismatch; no automatic promotion')
        projected=fact('ytd2026_revenue')+fact('q42025_revenue')*fact('q32026_revenue')/fact('q32025_revenue')
        growths=fade(str(projected/anchor-1),str(param('growth_endpoint')))
        previous=anchor
        for i,g in enumerate(growths):
            value=previous*(1+number(g));revenue.append(value)
            put(f'forecast_years[{i}].revenue_growth',g,'quarter-extension-growth-fade-v1',
                {'fy2026_revenue_estimate':str(projected),'start':growths[0],'endpoint':config['growth_endpoint'],'index':i,'denominator':'4'},
                ('fy2025_revenue','ytd2026_revenue','q42025_revenue','q32026_revenue','q32025_revenue'))
            previous=value
    except (LookupError,TypeError,ZeroDivisionError) as exc:gap([f'forecast_years[{i}].revenue_growth' for i in range(5)],exc)
    try:
        start=fact('q32026_ebit')/fact('q32026_revenue')
        margins=fade(str(start),str(param('margin_endpoint')))
        for i,m in enumerate(margins):put(f'forecast_years[{i}].operating_margin',m,'reported-margin-fade-v1',{'start':str(start),'endpoint':config['margin_endpoint'],'index':i,'denominator':'4'},('q32026_ebit','q32026_revenue'))
    except (LookupError,TypeError,ZeroDivisionError) as exc:gap([f'forecast_years[{i}].operating_margin' for i in range(5)],exc)
    try:
        taxes=fade(str(param('tax_start')),str(param('tax_endpoint')))
        for i,tax in enumerate(taxes):put(f'forecast_years[{i}].forecast_tax_rate',tax,'operating-tax-fade-v1',{'start':config['tax_start'],'endpoint':config['tax_endpoint'],'index':i},configured=True)
    except LookupError as exc:gap([f'forecast_years[{i}].forecast_tax_rate' for i in range(5)],exc)
    investments=[]
    try:
        cash=param('cash_ppe_start_usd');financed_fraction=param('new_financed_fraction_cash_ppe')
        changes=config.get('cash_ppe_growth')
        if changes is None:raise LookupError('MISSING_EVIDENCE: cash_ppe_growth configuration')
        if not isinstance(changes,list) or len(changes)!=4:raise ValueError('Four cash PP&E growth configurations required')
        for i in range(5):
            if i:cash*=1+number(changes[i-1])
            financed=cash*financed_fraction;investment=cash+financed;investments.append(investment)
            if not revenue:raise LookupError('Investment ratio requires available forecast revenue')
            put(f'forecast_years[{i}].capex_percent_revenue',investment/revenue[i], 'cash-ppe-plus-new-financed-v1',
                {'cash_ppe_usd':str(cash),'new_financed_assets_usd':str(financed),'revenue_usd':str(revenue[i]),'cash_growth':None if not i else changes[i-1],'principal':'EXCLUDED; cash PP&E definition already excludes financing principal'},configured=True)
    except LookupError as exc:gap([f'forecast_years[{i}].capex_percent_revenue' for i in range(5)],exc)
    try:
        da=param('expense_da_start_usd');commissioning=param('commissioning_allowance')
        if not revenue or len(investments)!=5:raise LookupError('D&A ratios need forecast revenue and scoped investment')
        for i in range(5):
            previous_da=da
            if i:da+=investments[i-1]*commissioning
            put(f'forecast_years[{i}].d_and_a_percent_revenue',da/revenue[i], 'expense-commissioning-allowance-v1',
                {'expense_da_usd':str(da),'previous_expense_da_usd':str(previous_da),'previous_investment_usd':None if not i else str(investments[i-1]),'commissioning_allowance':str(commissioning),'revenue_usd':str(revenue[i])},configured=True)
    except LookupError as exc:gap([f'forecast_years[{i}].d_and_a_percent_revenue' for i in range(5)],exc)
    try:
        coefficient=param('incremental_wc')
        if not growths:raise LookupError('WC cash ratio requires forecast growth')
        for i,g in enumerate(growths):put(f'forecast_years[{i}].change_in_operating_nwc_percent_revenue',incremental_cash_ratio(g,str(coefficient)),
                'incremental-to-full-revenue-wc-v1',{'growth':g,'incremental_fraction':str(coefficient),'formula':'coefficient*g/(1+g)'},configured=True)
    except LookupError as exc:gap([f'forecast_years[{i}].change_in_operating_nwc_percent_revenue' for i in range(5)],exc)
    try:
        rf=fact('treasury_10y','treasury-par-yield','fraction');erp=fact('implied_erp','implied-erp-over-treasury','fraction')
        values=[str(rf),str(erp),*(str(param(k)) for k in ('beta','credit_spread','equity_weight','debt_weight','debt_tax_shield'))]
        value=wacc(*values)
        put('wacc',value,'target-weight-wacc-v1',dict(zip(('risk_free','erp','beta','spread','equity_weight','debt_weight','tax_shield'),values)),('treasury_10y','implied_erp'),True,
            'Dated 10y Treasury par proxy plus monthly Treasury-based ERP; configured beta/spread/target weights/shield, not measured issuer market weights. No intermediate rounding.')
        for key in ('treasury_10y','implied_erp'):
            if (date.fromisoformat(cutoff)-date.fromisoformat(selected[key]['end'])).days>policy['source_max_age_days']:
                fields['wacc']['status']='STALE';diagnostics.append('WACC source beyond explicitly configured review-age window')
    except (LookupError,TypeError) as exc:gap(['wacc'],exc)
    for path,key in [('terminal_growth','terminal_growth'),('terminal.operating_margin','terminal_margin'),('terminal.operating_tax_rate','terminal_tax'),('terminal.d_and_a_percent_revenue','terminal_da'),('terminal.investment_percent_revenue','terminal_investment')]:
        try:put(path,param(key),'independent-terminal-configuration-v1',{'configuration_key':key,'value':config[key]},configured=True)
        except LookupError as exc:gap([path],exc)
    try:put('terminal.working_capital_cash_requirement_percent_revenue',incremental_cash_ratio(str(param('terminal_growth')),str(param('incremental_wc'))),'terminal-incremental-to-full-wc-v1',{'growth':config['terminal_growth'],'incremental_fraction':config['incremental_wc']},configured=True)
    except LookupError as exc:gap(['terminal.working_capital_cash_requirement_percent_revenue'],exc)
    if config.get('exit_ev_ebit_multiple') is None:gap(['exit_ev_ebit_multiple'],LookupError('No supported mature EV/EBIT exit selection; enter an explicit assumption to use exit'))
    elif not policy['configuration_provenance'].get('exit'):gap(['exit_ev_ebit_multiple'],LookupError('An explicit exit selection needs a documented configuration_provenance.exit rationale/basis'))
    else:put('exit_ev_ebit_multiple',param('exit_ev_ebit_multiple'),'explicit-exit-configuration-v1',{'value':config['exit_ev_ebit_multiple'],'rationale':policy['configuration_provenance']['exit']},configured=True)
    scenarios={}
    for label in ('Base','Bear','Bull'):
        rates={path:f['value'] for path,f in fields.items()}
        if label!='Base':
            for path,value in list(rates.items()):
                offset=scenario_offset(config,label,path)
                if value is not None and offset is not None:rates[path]=str(number(value)+number(offset))
        scenarios[label]=rates
    if revenue:
        diagnostics.append('Five-year forecast revenue CAGR = '+cagr('402836000000',str(revenue[-1]),5)+'; not any individual annual rate')
    try:
        net=param('terminal_investment')-param('terminal_da')+number(fields['terminal.working_capital_cash_requirement_percent_revenue']['value'])
        nopat=param('terminal_margin')*(1-param('terminal_tax'))
        diagnostics.append('Terminal net reinvestment/revenue = '+str(net))
        diagnostics.append('Implied incremental return diagnostic g*NOPAT/net reinvestment = '+str(param('terminal_growth')*nopat/net)+'; NOT observed ROIC')
        if net<=0 and param('terminal_growth')>0:diagnostics.append('INCONSISTENCY: positive growth without positive net reinvestment')
    except (LookupError,ValueError,ZeroDivisionError):diagnostics.append('Terminal consistency diagnostic unavailable')
    diagnostics+=['Reported FY2025 YTD plus Q4 revenue differs from the annual anchor by1m; no residual correction or precision improvement.',
                  'Acquisition cash/perimeter not reconciled: operating PV conditional; exclusions are not zero claims or assets.',
                  'Expense D&A and commissioning are estimates; source PP&E/CFO proxies remain incomplete.',
                  'Terminal expense D&A16% is independent of the commissioning path; transition/retirement economics are not modeled. Review the discontinuity, not a proven vintage reconciliation.',
                  'Terminal dependence must be reviewed after explicit engine execution; no financial approval.']
    economic={'issuer':resolve_listing(ticker),'anchor':template['anchor'],'anchor_revenue':'402836000000',
      'dates':{'anchor_period':'2025-01-01/2025-12-31','model_origin':'2025-12-31','information_review':cutoff,'timing':'Fiscal-end analytical origin using later-filed information; not a contemporaneous backtest or current-date fair value'},
      'policy':{k:v for k,v in policy.items() if k not in ('configuration','configuration_provenance')},
      'configuration':config,'configuration_provenance':policy['configuration_provenance'],
      'sources':sources,'observations':observations,'fields':fields,'scenarios':scenarios,
      'scenario_policy':'diagnostic-offset-v1; unchanged RATIOS inherit Base, including WC; 20% incremental WC rule describes Base only, not stressed revenue. No probabilities or guaranteed ordering',
      'optional_bridge':{'status':'UNSUPPORTED_PREPARATION','assets':None,'claims':None,'shares':None,'reason':'Eligibility/claims/settlement/class/award selections unapproved; omissions potentially unbounded'},
      'diagnostics':diagnostics,'case_template':template}
    return validate_profile({'schema_version':'preload-profile-v1','generated_at':generated_at or datetime.now(timezone.utc).isoformat(),
      'economic_hash':digest(economic),'economic':economic})


def scenario_offset(config,label,path):
    if label=='Base':return None
    key='growth' if path.startswith('forecast_years') and path.endswith('.revenue_growth') else 'margin' if path.startswith('forecast_years') and path.endswith('.operating_margin') else 'wacc' if path=='wacc' else None
    return config.get(label.lower()+'_'+key+'_offset') if key else None


def engine_request(profile,label='Base',method='perpetual_growth'):
    """Only input adaptation; execution is always the pre-existing engine."""
    validate_profile(profile)
    if label not in ('Base','Bear','Bull') or method not in ('perpetual_growth','exit_multiple'):raise ValueError('Unsupported scenario/method')
    economic=profile['economic'];rates=economic['scenarios'][label]
    required=[p for p in rates if p!='exit_ev_ebit_multiple' and not (method=='exit_multiple' and (p=='terminal_growth' or p.startswith('terminal.')))]
    if method=='exit_multiple':required.append('exit_ev_ebit_multiple')
    gaps=[p+': '+economic['fields'][p]['limitation'] for p in required if rates[p] is None or economic['fields'][p]['status'] not in {'AVAILABLE_ESTIMATE','CONFIGURED_CONVENTION','USER_OVERRIDE'}]
    if gaps:raise ValueError('Unavailable required inputs: '+'; '.join(gaps))
    doc=deepcopy(economic['case_template']);doc['schema_version']='analyst-case-v3';doc['calculation_scope']='ENTERPRISE_VALUE'
    doc['case_name']=f"{economic['issuer']['ticker']} proposed starting estimate · {label}"
    doc['analyst']={'author':'AI-assisted versioned preload policy; not a verified human identity','timestamp_utc':profile['generated_at'],
       'rationale':'Proposed estimates generated by '+economic['policy']['version']+'; economic hash '+profile['economic_hash']+'; explicit configuration is analyst judgment, not user-supplied or approved facts.'}
    doc['scope']=economic['dates']['timing']+'; information reviewed through '+economic['dates']['information_review']+'; consolidated operating EV only.'
    doc['limitations']=[s for s in doc['limitations'] if not s.startswith('All 37') and not s.startswith('Fiscal-end analytical')]+economic['diagnostics']
    for i,row in enumerate(doc['forecast_years']):
        for key in ANNUAL:row[key]=rates[f'forecast_years[{i}].{key}']
    doc['wacc']=rates['wacc'];doc.pop('terminal_growth');terminal=doc.pop('terminal')
    for key in terminal:terminal[key]=rates['terminal.'+key]
    gordon={'method':'perpetual_growth','terminal_growth':rates['terminal_growth'],'terminal':terminal}
    exit_method={'method':'exit_multiple','exit_ev_ebit_multiple':rates['exit_ev_ebit_multiple']}
    doc['conventions']['discounting']='fiscal-end-annual-gordon-v1' if method=='perpetual_growth' else 'fiscal-end-year-five-ev-ebit-v1'
    doc['terminal_valuation']=gordon if method=='perpetual_growth' else exit_method
    doc['comparison_terminal_valuation']=exit_method if method=='perpetual_growth' and rates['exit_ev_ebit_multiple'] is not None else gordon if method=='exit_multiple' else None
    from valuation_platform.valuation.case_inputs import read_case
    read_case(__import__('json').dumps(doc))
    return doc
