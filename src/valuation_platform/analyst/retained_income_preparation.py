"""Approved direct income semantics over prepared evidence; no issuer registry.

The caller owns the exact retained evidence and its limitations. This small
adapter never supplies other fields, derivations, scope fallbacks or readiness.
"""
from dataclasses import replace
from . import historical_inputs as h, retained_components as r
from ..normalization.concepts import REVENUE_POLICY, OPERATING_INCOME_POLICY

POLICIES = {h.Field.REVENUE: REVENUE_POLICY, h.Field.EBIT: OPERATING_INCOME_POLICY}


def inspect(evidence, field, limitations):
    if field not in POLICIES:
        raise h.InputError('Only existing approved direct Revenue/EBIT policies')
    namespace = evidence.namespaces.get('us-gaap')
    # An absent body still yields an exception, not a guessed taxonomy version.
    if namespace is None:
        return None
    if not namespace.startswith('http://fasb.org/us-gaap/'):
        raise h.InputError('Approved US-GAAP namespace required')
    return r.inspect(evidence, r.SelectionSpec(field.value,tuple(r.Selector(namespace,k.name,()) for k in POLICIES[field].candidates),
        'annual','USD','reported_revenue' if field is h.Field.REVENUE else 'reported_operating_income',
        'Approved direct US-GAAP nondimensional annual observation; no independent retained face-statement re-review.',limitations))


def choose(result, field):
    """Log policy-order representation choice only after all eligible values agree."""
    if result is None or not result.candidates:
        return None,'No eligible bound retained annual direct evidence; absence is not zero.'
    if (field not in POLICIES or result.specification.field_id!=field.value or result.specification.period_kind!='annual'
            or any(c.concept not in {k.name for k in POLICIES[field].candidates} or not c.namespace.startswith('http://fasb.org/us-gaap/')
                or any(o.dimensions for o in c.occurrences) for c in result.candidates)):
        raise h.InputError('Only inspected exact annual approved direct semantics can populate income')
    if result.competing_values:
        return None,'Competing eligible values remain unresolved; policy order cannot override a conflict.'
    if any(s.startswith('Missing retained') for s in result.unresolved_requirements):
        return None,'Required retained body/receipt binding is missing.'
    ranked=[i for key in POLICIES[field].candidates for i,c in enumerate(result.candidates) if c.concept==key.name]
    return ranked[0],('Existing approved direct concept policy order selects one representation after exact numeric agreement; '
        'all other candidates remain alternatives. Numeric equality does not prove a new concept equivalent.')


def annual(evidence, results, limitations):
    p=evidence.period;inputs=[]
    for field in h.Field:
        if field not in POLICIES:
            inputs.append(unavailable(p,field,'Outside this Revenue/EBIT-only pass: evidence and financial scope unassessed.',h.Review.UNREVIEWED));continue
        result=results[field];selected,reason=choose(result,field);observations=[]
        for c in (() if result is None else result.candidates):
            observations.append(h.InputValue(f'direct-income:{field.value}:{c.concept}:ordinal-{c.occurrences[0].ordinal}',field,p,None,
                c.value,'USD',1,1,c.precision,result.specification.role,h.Origin.REPORTED,h.Quality.LIMITED,
                result.specification.scope,h.Scope.CONSOLIDATED_REPORTED,h.Completeness.PARTIAL,h.Review.REVIEWED,
                c.evidence_references,None,None,(),reason,('direct_policy_only','no_aggregation_or_valuation_authorization',
                'independent_face_statement_not_retained'),result.unresolved_requirements,None,(field.value,)))
        if selected is not None:
            inputs.append(replace(observations[selected],alternatives=tuple(v for i,v in enumerate(observations) if i!=selected)))
        else:
            value=unavailable(p,field,reason,h.Review.REVIEWED)
            req=tuple(dict.fromkeys(value.unresolved_requirements+evidence.unresolved_requirements+
                (() if result is None else result.unresolved_requirements)))
            inputs.append(replace(value,alternatives=tuple(observations),quality=h.Quality.CONFLICTING if result and result.competing_values else h.Quality.LIMITED,
                unresolved_requirements=req))
    return h.AnnualBundle(f'retained-direct-income:{p.cik}:{p.accession}',1,p,tuple(inputs),limitations)


def unavailable(p,field,reason,review):
    as_of=p.annual_end if field in (h.Field.CASH_INVESTMENTS,h.Field.DEBT_LEASES,h.Field.OTHER_BRIDGE) else None
    return h.InputValue(f'direct-income:{field.value}:unresolved',field,p,as_of,None,'shares' if field is h.Field.SHARES else 'USD',
        1,1,'unknown','unavailable_or_unassessed_requirement',h.Origin.UNAVAILABLE,h.Quality.UNASSESSED,reason,h.Scope.UNKNOWN,
        h.Completeness.UNKNOWN,review,(),None,None,(),'No estimate, inferred zero or financial-scope acceptance.',
        ('required_value_unresolved','null_sign_scale_precision_are_not_observations','no_aggregation_or_valuation_authorization'),(reason,),reason,())
