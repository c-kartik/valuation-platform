"""Dated CAPM/WACC starting assumptions; not observed issuer capital costs.

Derive cost of equity from the SAME saved operands already used for preload
WACC. No market refresh, financing projection or automatic adoption occurs.
"""
from decimal import Context, Decimal, localcontext, ROUND_HALF_EVEN
from copy import deepcopy
from valuation_platform.preload.profile import validate_profile, select_observation
from valuation_platform.valuation.fcfe import equity_cost
from valuation_platform.preload.rules import wacc
from valuation_platform.preload.issuers import registration


def discount_inputs(profile, ticker):
    validate_profile(profile)
    econ=profile['economic'];field=econ['fields']['wacc']
    spec=registration(ticker)
    if (econ['anchor']['kind']!=spec['kind'] or econ['anchor']['cik']!=spec['cik']
            or econ['issuer']['ticker']!=ticker or econ['issuer']['cik']!=spec['cik']):
        raise ValueError('Discount profile and requested issuer differ')
    base={'schema_version':'saved-discount-inputs-v1','ticker':ticker,'economic_hash':profile['economic_hash'],
          'information_review':econ['dates']['information_review'], 'model_origin':econ['dates']['model_origin'],
          'automatic_adoption':False,'scenario_wacc_offset_applied_to_cost_of_equity':False,
          'status':'UNAVAILABLE','cost_of_equity':None,'cost_of_equity_percent':None,
          'base_wacc':field['value'],'operands':{},'observed_macro_inputs':[], 'sources':[],
          'limitations':['These are saved starting assumptions, not live market estimates or filing-reported capital costs.',
             'Beta, credit spread, target weights and tax shield are configured assumptions, not measured issuer beta or market capital weights.',
             'Bear/Bull WACC diagnostic offsets do not automatically change CAPM cost of equity.',
             'This supplies no missing historical interest, financing, minority ownership or per-share input.']}
    if field['status'] not in ('AVAILABLE_ESTIMATE','CONFIGURED_CONVENTION'):
        base['limitations'].append('Saved WACC field is missing, incompatible or stale; enter and review cost of equity manually.')
        return base
    if field['rule']!='target-weight-wacc-v1':
        raise ValueError('Unsupported saved discount-rate rule')
    operands=field['operands'];expected={'risk_free','erp','beta','spread','equity_weight','debt_weight','tax_shield'}
    if set(operands)!=expected:raise ValueError('Exact saved discount-rate operands required')
    for operand,configuration in (('beta','beta'),('spread','credit_spread'),('equity_weight','equity_weight'),('debt_weight','debt_weight'),('tax_shield','debt_tax_shield')):
        if Decimal(operands[operand])!=Decimal(econ['configuration'][configuration]):
            raise ValueError('Discount operand differs from its declared policy configuration')
    with localcontext(Context(prec=50,rounding=ROUND_HALF_EVEN)):
        ke=equity_cost(operands['risk_free'],operands['beta'],operands['erp'])
        actual=wacc(*(operands[k] for k in ('risk_free','erp','beta','spread','equity_weight','debt_weight','tax_shield')))
        if Decimal(actual)!=Decimal(field['value']):raise ValueError('Saved WACC operands do not reproduce the displayed field')
        if not Decimal(0)<ke<=1:raise ValueError('Saved CAPM inputs imply unsupported cost of equity')
        base.update(status='CONFIGURED_CONVENTION',cost_of_equity=str(ke),cost_of_equity_percent=str(ke*100),operands=deepcopy(operands),
                    pre_tax_cost_of_debt=str(Decimal(operands['risk_free'])+Decimal(operands['spread'])))
    sources={s['id']:s for s in econ['sources']}
    base['sources']=[{k:sources[key].get(k) for k in ('id','title','url','sha256','published_at','observation_date','retrieved_at')} for key in field['sources']]
    for key in ('treasury_10y','implied_erp'):
        o=select_observation(econ['observations'],key,definition='treasury-par-yield' if key=='treasury_10y' else 'implied-erp-over-treasury',unit='fraction',cutoff=econ['dates']['information_review'])
        if o['value']!=operands['risk_free' if key=='treasury_10y' else 'erp'] or o['end'] not in {p['end'] for p in field['periods']} or o['scope']!='macro':
            raise ValueError('Saved macro operands differ from their source observations')
        if o['source'] not in field['sources'] or o['source_sha256']!=sources[o['source']]['sha256']:
            raise ValueError('Macro observation source differs from saved evidence')
        base['observed_macro_inputs'].append({k:deepcopy(o.get(k)) for k in ('id','key','value','unit','end','available_at','published_at','source','source_sha256')})
    return base
