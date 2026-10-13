"""Bounded deferred-tax/SBC reconciliation observations; no economic treatment."""
from collections import Counter
from dataclasses import dataclass, replace, asdict
from . import historical_inputs as h, retained_components as r
from . import retained_cfo_preparation as cfo, retained_working_capital as movements
from . import retained_income_preparation as missing, pilot_historical_inputs as pilot


@dataclass(frozen=True)
class Rule:
    field: h.Field
    concept: str
    role: str
    definition: str
    reconciliation: bool
    combined: bool = False
    sign: int = 1


# Explicit element meanings, not substring discovery or issuer approvals.
# Deferred expense/benefit is a provision element: only existing reviewed pilot
# evidence may establish its CFO placement. Never infer that role from equality.
RULES = (
    Rule(h.Field.DEFERRED_TAX, 'DeferredIncomeTaxesAndTaxCredits', 'cfo_deferred_tax_adjustment_combined_credits',
        'Deferred income taxes AND tax credits in the reported noncash reconciliation; not a certified pure deferred-tax component.', True, True),
    Rule(h.Field.DEFERRED_TAX, 'DeferredIncomeTaxExpenseBenefit', 'deferred_tax_provision',
        'Deferred income-tax expense/benefit; provision observation alone does not establish CFO placement.', False),
    Rule(h.Field.DEFERRED_TAX, 'DeferredIncomeTaxExpenseBenefitContinuingOperations', 'continuing_deferred_tax_provision',
        'Deferred expense/benefit for continuing operations, not consolidated CFO adjustment.', False),
    Rule(h.Field.DEFERRED_TAX, 'DeferredIncomeTaxExpenseBenefitDiscontinuedOperations', 'discontinued_deferred_tax_provision',
        'Deferred expense/benefit for discontinued operations, not consolidated CFO adjustment.', False),
    Rule(h.Field.SBC, 'ShareBasedCompensation', 'sbc_cfo_addback',
        'Reported noncash share-based compensation reconciliation observation; not grant/award value or withholding cash.', True),
    Rule(h.Field.SBC, 'AllocatedShareBasedCompensationExpense', 'sbc_note_expense',
        'Allocated recognized compensation expense, separate from CFO reconciliation and outstanding awards.', False),
    Rule(h.Field.DEFERRED_TAX, 'OtherNoncashIncomeExpense', 'unallocated_other_noncash_support',
        'Mixed other noncash income/expense; no assumption that it contains deferred tax or any allocatable amount.', False, True, -1),
    Rule(h.Field.SBC, 'OtherNoncashIncomeExpense', 'unallocated_other_noncash_support',
        'Mixed other noncash income/expense; no assumption that it contains SBC or any allocatable amount.', False, True, -1),
)
FIELDS = (h.Field.DEFERRED_TAX, h.Field.SBC)
RECONCILIATION_ROLES = frozenset(v.role for v in RULES if v.reconciliation) | frozenset({
    'cfo_deferred_adjustment_with_provision_confirmation', 'cfo_deferred_tax_adjustment'})
# Diagnostic list is closed and role-specific too; no substring matching.
EXCLUDED = {
    'IncomeTaxExpenseBenefit': 'TAX_PROVISION_NOT_DEFERRED_RECONCILIATION',
    'IncomeTaxesPaidNet': 'CASH_TAX_NOT_DEFERRED_RECONCILIATION',
    'IncomeTaxesPaid': 'CASH_TAX_NOT_DEFERRED_RECONCILIATION',
    'DeferredIncomeTaxAssetsNet': 'DEFERRED_TAX_BALANCE_NOT_ADJUSTMENT',
    'DeferredIncomeTaxLiabilitiesNet': 'DEFERRED_TAX_BALANCE_NOT_ADJUSTMENT',
    'DeferredTaxAssetsNet': 'DEFERRED_TAX_BALANCE_NOT_ADJUSTMENT',
    'DeferredTaxAssetsLiabilitiesNet': 'DEFERRED_TAX_BALANCE_NOT_ADJUSTMENT',
    'IncreaseDecreaseInDeferredIncomeTaxes': 'DEFERRED_TAX_ACCOUNT_MOVEMENT_ROLE_UNREVIEWED',
    'IncreaseDecreaseInAccruedIncomeTaxesPayable': 'WORKING_CAPITAL_TAX_MOVEMENT_NOT_ADJUSTMENT',
    'IncreaseDecreaseInIncomeTaxes': 'WORKING_CAPITAL_TAX_MOVEMENT_NOT_ADJUSTMENT',
    'PaymentsRelatedToTaxWithholdingForShareBasedCompensation': 'WITHHOLDING_CASH_NOT_SBC_EXPENSE_OR_ADDBACK',
    'PaymentsForRepurchaseOfCommonStock': 'BUYBACK_CASH_NOT_SBC_ADDBACK',
    'EmployeeServiceShareBasedCompensationTaxBenefitFromCompensationExpense': 'TAX_BENEFIT_NOT_SBC_ADDBACK',
    'ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsGrantsInPeriodGross': 'AWARDS_NOT_RECOGNIZED_EXPENSE',
    'ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsGrantsInPeriodWeightedAverageGrantDateFairValue': 'AWARD_FAIR_VALUE_NOT_EXPENSE',
}
LIMITATIONS = (
    'Observation availability is not complete CFO reconciliation, consolidated/continuing scope certification or financial sufficiency.',
    'Provision/balance/cash/working-capital tax roles are not interchangeable; no allocation, rate or tax adjustment.',
    'SBC expense and reconciliation are non-additive representations; no second charge, rounding adjustment or economic treatment.',
    'Mixed captions retain their full scope; no decomposition, absent component zero, residual or sum.',
    'Acquisition/FX/reclassification and timing effects remain unestablished outside unchanged reviewed evidence.',
)


def inspect(evidence, field):
    if field not in FIELDS: raise h.InputError('Explicit deferred-tax or SBC field required')
    ns=evidence.namespaces.get('us-gaap',''); values=[]; rows=[]
    if not ns.startswith('http://fasb.org/us-gaap/'):
        return (), [], ('Exact standard US-GAAP namespace unavailable.',)
    errors=[]
    for rule in (v for v in RULES if v.field is field):
        spec=r.SelectionSpec(field.value+':'+rule.concept,(r.Selector(ns,rule.concept,()),),
            'annual','USD',rule.role,rule.definition,LIMITATIONS)
        try: result=r.inspect(evidence,spec)
        except h.InputError as exc:
            reason=rule.concept+': '+str(exc);errors.append(reason)
            value=missing.unavailable(evidence.period,field,reason,h.Review.REVIEWED)
            values.append(replace(value,input_id='retained-tax-sbc:invalid:'+field.value+':'+rule.concept,
                role=rule.role,flags=('invalid_evidence',)))
            continue
        if not result.candidates: continue
        candidates=tuple(h.InputValue('retained-tax-sbc:'+field.value+':'+rule.concept+':'+str(c.occurrences[0].ordinal),
            field,evidence.period,None,c.value*rule.sign,'USD',1,rule.sign,c.precision,rule.role,
            h.Origin.REPORTED,h.Quality.LIMITED,rule.definition,h.Scope.MIXED if rule.combined else h.Scope.RESTRICTED,
            h.Completeness.PARTIAL,h.Review.REVIEWED,c.evidence_references,None,None,(),
            'Explicit element role only; provision/expense support does not approve reconciliation or economic use.',
            ('rule_version:1','no_sum_or_economic_adjustment','statement_scope_not_independently_reviewed',
             'combined_caption' if rule.combined else 'separate_role_observation'),LIMITATIONS,None,(rule.role,))
            for c in result.candidates)
        if result.competing_values:
            value=missing.unavailable(evidence.period,field,'Unequal eligible values for '+rule.concept+'; no precedence or rounding tolerance.',h.Review.REVIEWED)
            values.append(replace(value,input_id='retained-tax-sbc:conflict:'+field.value+':'+rule.concept,
                role=rule.role,quality=h.Quality.CONFLICTING,alternatives=candidates))
        else: values.append(replace(candidates[0],alternatives=candidates[1:]))
        rows.append(dict(concept=rule.concept,role=rule.role,reconciliation=rule.reconciliation,combined=rule.combined,
            definition=rule.definition,sign=rule.sign,status='CONFLICTING' if result.competing_values else 'OBSERVED',
            candidates=[dict(raw_value=str(c.value),value_usd=str(c.value*rule.sign),scale=1,precision=c.precision,
                namespace=c.namespace,occurrences=[dict(ordinal=o.ordinal,context_id=o.context_id,unit_id=o.unit_id,
                    raw_value=o.raw_value,precision=o.decimals,dimensions=list(o.dimensions)) for o in c.occurrences]) for c in result.candidates]))
    return tuple(values),rows,tuple(errors)


def outcome(values):
    primary=[v for v in values if v.role in RECONCILIATION_ROLES]
    if any(v.quality is h.Quality.CONFLICTING for v in primary): return 'CONFLICTING'
    if any('invalid_evidence' in v.flags for v in primary): return 'UNAVAILABLE'
    return 'POPULATED' if any(v.value is not None for v in primary) else 'UNAVAILABLE'


def package(evidence, field):
    values,rows,errors=inspect(evidence,field);status=outcome(values)
    if status=='UNAVAILABLE':
        gap=missing.unavailable(evidence.period,field,
            'No adequately bound CFO reconciliation observation in the bounded mapping; provision/expense/mixed support cannot substitute or establish zero.',h.Review.REVIEWED)
        values=(replace(gap,input_id='retained-tax-sbc:required:'+field.value,unresolved_requirements=gap.unresolved_requirements+errors+LIMITATIONS),*values)
    return values,dict(status=status,observations=rows,errors=list(errors),coverage='PARTIAL_UNKNOWN',
        unresolved_requirements=list(LIMITATIONS),not_observed_concepts=[v.concept for v in RULES if v.field is field and not any(v.concept==row['concept'] for row in rows)])


def diagnostics(evidence):
    names=set(EXCLUDED)|{v.concept for v in RULES};rows=[]
    for f,i in evidence.facts:
        if f.concept not in names: continue
        c=evidence.contexts[f.context_id];dims=r.dimensions(c)
        if (c.start,c.end)!=(evidence.period.annual_start,evidence.period.annual_end) and not (c.start is None and c.end==evidence.period.annual_end):
            continue  # Comparatives remain in the original body, not new registrations.
        reason=('UNSUPPORTED_EXTENSION' if f.namespace!=evidence.namespaces.get('us-gaap') else
            'DIMENSIONED_POPULATION' if dims else 'OTHER_PERIOD_OR_INSTANT' if (c.start,c.end)!=(evidence.period.annual_start,evidence.period.annual_end)
            else EXCLUDED.get(f.concept,'MAPPED_ANNUAL_ROLE_CANDIDATE'))
        rows.append(dict(concept=f.concept,namespace=f.namespace,ordinal=i,context_id=c.context_id,
            start=None if c.start is None else str(c.start),end=str(c.end),dimensions=list(dims),entity=c.entity_identifier,
            raw_value=f.raw_value,precision=f.decimals,nil=f.is_nil,unit_id=f.unit_ref,
            unit=None if f.unit is None else dict(numerator=[dict(namespace=q.namespace,name=q.local_name) for q in f.unit.numerator_measures],
                denominator=[dict(namespace=q.namespace,name=q.local_name) for q in f.unit.denominator_measures]),disposition=reason))
    return rows


def build():
    baseline,histories=movements.build();rows=[];out={};summary={}
    pilots={a.period for name in ('MSFT','AAPL','GOOGL') for a in pilot.load_history(name).annuals}
    for name,history in histories.items():
        annuals=[]
        for annual in history.annuals:
            evidence=cfo.prepare(annual);fields={};new=[]
            for field in FIELDS:
                values,entry=package(evidence,field)
                if annual.period in pilots:
                    values=tuple(v for v in annual.inputs if v.field is field)
                    entry['status']=outcome(values);entry['preserved_pilot_roles']=[dict(input_id=v.input_id,role=v.role,
                        value_usd=None if v.value is None else str(v.value),precision=v.precision) for v in values]
                fields[field.value]=entry;new.extend(values)
            if annual.period not in pilots:
                annual=replace(annual,inputs=tuple(v for v in annual.inputs if v.field not in FIELDS)+tuple(new))
            annuals.append(annual)
            receipt=evidence.instance
            rows.append(dict(issuer=name,identity=dict(cik=annual.period.cik,accession=annual.period.accession,
                form=annual.period.form,annual_start=str(annual.period.annual_start),annual_end=str(annual.period.annual_end)),
                original_pilot_preserved=annual.period in pilots,fields=fields,diagnostics=diagnostics(evidence),
                receipt=dict(url=receipt.artifact.url,sha256=receipt.artifact.sha256,representation=receipt.artifact.representation,
                    digest_type=receipt.artifact.digest_type,retrieved_at_utc=receipt.retrieved_at_utc,http_status=receipt.http_status,retrieval_mode=receipt.retrieval_mode)))
        out[name]=replace(history,history_id='retained-tax-sbc:'+name,annuals=tuple(annuals))
        selected=[v for v in rows if v['issuer']==name]
        summary[name]=dict(periods=len(selected),fields={f.value:dict(Counter(v['fields'][f.value]['status'] for v in selected)) for f in FIELDS})
    ledger=dict(schema='retained-tax-sbc-reconciliation-v1',rule_version=1,rules=[dict(asdict(v),field=v.field.value) for v in RULES],
        selected_periods=len(rows),issuer_count=len(out),summary=summary,
        outcomes={f.value:dict(Counter(v['fields'][f.value]['status'] for v in rows)) for f in FIELDS},
        observation_counts={f.value:dict(Counter(o['role'] for v in rows for o in v['fields'][f.value]['observations'])) for f in FIELDS},
        limitations=list(LIMITATIONS),history_exceptions=baseline['history_exceptions'],rows=rows,
        unchanged_income_outcomes=baseline['income_outcomes'],unchanged_cfo_outcomes=baseline['cfo_outcomes'],
        unchanged_movement_outcomes=baseline['period_outcomes'])
    return ledger,out


def validate_history(payload):
    history=h.deserialize(payload)
    pilots={a.period:a for name in ('MSFT','AAPL','GOOGL') for a in pilot.load_history(name).annuals}
    for annual in history.annuals:
        evidence=cfo.prepare(annual)
        for field in FIELDS:
            actual=tuple(v for v in annual.inputs if v.field is field)
            expected=(tuple(v for v in pilots[annual.period].inputs if v.field is field) if annual.period in pilots else package(evidence,field)[0])
            if actual!=expected: raise h.InputError('Reconciliation role/value/precision/source differs from retained replay')
    return history
