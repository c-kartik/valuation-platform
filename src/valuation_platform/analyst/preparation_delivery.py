"""Separately versioned reported-population delivery; legacy assembly is untouched.

Complete here describes an exact reported population, never a company's financial
sufficiency. Display checks and residuals are separate: a remainder cannot prove
the independent reconciliation that supplied its operands.
"""
from collections import Counter
from dataclasses import dataclass, replace
from decimal import Decimal
import json

from . import historical_inputs as h, prepared_assembly as a, statement_delivery as docs
from . import usable_bridge as bridge, cfo_statement_reconciliation as cfo
from . import analyst_overrides as overrides, preparation_review as review

LEGACY_SCHEMA='reported-population-delivery-v1'
SCHEMA='reported-population-delivery-v2'
LEDGER='docs/reported-population-delivery-ledger.json'
SUMMARY='docs/reported-population-delivery-summary.json'
QUALIFIED=frozenset(('reported_current_liquidity','issuer_common_shares','independently_reconciled_reported_cfo'))


def plain(value):
    if isinstance(value,dict):return {k:plain(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [plain(v) for v in value]
    if isinstance(value,h.SourceReference):return a.source_payload(value)
    return value


def row_input(row,period):
    return h.InputValue('displayed-cfo:'+str(row['table'])+':'+str(row['row'])+':'+str(row['ordinal']),
        h.Field.CFO_RESIDUAL,period,None,Decimal(row['value']),'USD',1,row['sign'],row['precision'],
        row.get('role','displayed_cfo_subtotal'),h.Origin.REPORTED,h.Quality.SUPPORTED,
        'Exact displayed indirect-CFO statement row; not a D&A primitive, SBC expense, book delta NWC or economic charge.',
        h.Scope.CONSOLIDATED_REPORTED,h.Completeness.PARTIAL,h.Review.REVIEWED,tuple(row['sources']),None,None,(),
        'Independent primary display and exact instance context agree; source-specific cash contribution sign retained.',
        ('support_only_displayed_reconciliation','not_fcff_adjustment'),(),None,(row['concept']+':'+row['context_id'],))


def reconciliation_inputs(result,period):
    # Multiple statements/scopes and incomplete populations remain proof-only.
    if result['status']!='SUPPORTED':return ()
    population=result['populations'][0]
    if population['scope']!='CONSOLIDATED':return ()
    rows=population['rows'];inputs=[row_input(r,period) for r in rows]
    root=row_input(population['cfo'],period);inputs.append(root)
    inputs.append(replace(root,input_id=root.input_id+':confirmed-subtotal',field=h.Field.CFO,
        role='independently_reconciled_reported_cfo',completeness=h.Completeness.COMPLETE,
        scope='Exact reported consolidated CFO; complete independently displayed reconciliation, not organic cash flow or FCFF.',
        flags=('independent_displayed_cfo_reconciliation','reported_population_only'),
        coverage_keys=('reported_consolidated_cfo',)))
    from . import retained_working_capital as wc
    known={r.concept for r in wc.RULES}|set(cfo.STARTS)|{
        'DepreciationDepletionAndAmortization','DepreciationDepletionAndAmortizationPropertyPlantAndEquipment',
        'Depreciation','AmortizationOfIntangibleAssets','ShareBasedCompensation','DeferredIncomeTaxExpenseBenefit'}
    operands=[v for v,r in zip(inputs,rows) if r['namespace'].startswith('http://fasb.org/us-gaap/') and r['concept'] in known]
    if not operands:return tuple(inputs)
    f=h.Formula('displayed-cfo-unclassified-remainder',1,h.FormulaKind.CFO_REMAINDER,
        root.input_id+' - ('+' + '.join(v.input_id for v in operands)+')',
        (root.input_id,*(v.input_id for v in operands)),False,False,True,
        tuple(s.source_id for s in root.sources if s.occurrence_ordinal is None))
    remainder=replace(root,input_id='displayed-cfo:unclassified-remainder',
        value=root.value-sum((v.value for v in operands),Decimal(0)),origin=h.Origin.DERIVED,
        role='unclassified_cfo_reconciliation_remainder',sources=(),formula=f,sign=1,
        precision='derived_from_explicit_reported_precision',
        selection_rationale='CFO minus exact identified starting/adjustment/movement operands; remaining displayed rows stay separately observable.',
        flags=('unclassified_reconciliation_remainder','not_independent_validation','not_fcff_adjustment'),
        unresolved_requirements=('Remainder is unclassified, not a complete working-capital or approved economic adjustment.',),
        coverage_keys=('unclassified_remainder',))
    children=tuple(replace(row_input(r,period),flags=('support_only_displayed_reconciliation','hierarchy_child_not_summed_with_parent','not_fcff_adjustment'))
        for r in (population.get('hierarchy_proof') or {}).get('children',()))
    return (*inputs,*children,remainder)


@dataclass(frozen=True)
class AnnualDelivery:
    period:h.Period
    primary:h.Receipt|None
    inputs:tuple[h.InputValue,...]
    bridge_json:str
    reconciliation_json:str
    binding_receipts:tuple[h.Receipt,...]=()

    def __post_init__(self):
        h._typed(self.inputs,h.InputValue)
        h._typed(self.binding_receipts,h.Receipt)
        if any(r.artifact.accession!=self.period.accession for r in self.binding_receipts):raise h.InputError('Cross-accession statement binding receipt')
        if any(v.period!=self.period for v in self.inputs):raise h.InputError('Cross-period delivery')
        for text in (self.bridge_json,self.reconciliation_json):
            if a.canonical(json.loads(text))!=text:raise h.InputError('Canonical exact population proof required')
        if self.primary is not None and self.primary.artifact.accession!=self.period.accession:raise h.InputError('Primary/accession differs')
        by_id={v.input_id:v for v in self.inputs}
        if len(by_id)!=len(self.inputs):raise h.InputError('Duplicate population')
        for v in self.inputs:
            if v.formula:
                operands=[by_id[k] for k in v.formula.operands]
                expected=(operands[0].value-sum((x.value for x in operands[1:]),Decimal(0))
                    if v.formula.kind is h.FormulaKind.CFO_REMAINDER else sum((x.value for x in operands),Decimal(0)))
                if v.value!=expected:raise h.InputError('Exact formula arithmetic differs')


def inspect(annual,record,legacy=False):
    e=a.cfo.prepare(annual)
    if record is None:
        bp=dict(version=bridge.VERSION if legacy else bridge.IMPROVED_VERSION,status='UNRESOLVED',requirements=['Exact primary metadata/body/receipt unavailable; no inferred filename.'],populations=[])
        cr=dict(version=cfo.VERSION if legacy else cfo.IMPROVED_VERSION,status='NOT_ASSESSED',reason=bp['requirements'][0],populations=[])
        return AnnualDelivery(annual.period,None,(),a.canonical(bp),a.canonical(cr))
    values,bp=bridge.inspect(e,record,bridge.VERSION if legacy else bridge.IMPROVED_VERSION)
    cr=cfo.inspect_statement(e,record,cfo.VERSION if legacy else cfo.IMPROVED_VERSION)
    receipts=tuple(docs.receipt(record[k],annual.period) for k in ('filing_primary','index_record')) if record.get('document_type') in ('EX-13','EX-13.1') else ()
    return AnnualDelivery(annual.period,docs.receipt(record,annual.period),
        (*values,*reconciliation_inputs(cr,annual.period)),a.canonical(plain(bp)),a.canonical(plain(cr)),receipts)


def combine(parent,annuals):
    if tuple(v.period for v in parent.bundle.annuals)!=tuple(v.period for v in annuals):raise h.InputError('Exact selected-period delivery required')
    bindings=json.loads(parent.bindings_json);out=[]
    for old,extra in zip(parent.bundle.annuals,annuals):
        operands={k for v in extra.inputs if v.formula for k in v.formula.operands}
        proof=dict(bridge=json.loads(extra.bridge_json),cfo=json.loads(extra.reconciliation_json))
        for v in extra.inputs:
            relevant_proof=proof['cfo'] if v.field in (h.Field.CFO,h.Field.CFO_RESIDUAL) else field_proof(proof['bridge'],v.field)
            bindings.append(dict(accession=v.period.accession,input_id=v.input_id,field=v.field.value,
                channel=LEGACY_SCHEMA if json.loads(extra.reconciliation_json)['version']==cfo.VERSION else SCHEMA,category='derivation_operand' if v.input_id in operands else
                'prepared_value' if v.role in QUALIFIED else 'support_observation',
                population_proof=relevant_proof,usable_population=v.role not in ('displayed_adjustment','displayed_movement','starting_subtotal','displayed_cfo_subtotal','unclassified_cfo_reconciliation_remainder'),
                field_complete=v.role in QUALIFIED))
        out.append(h.AnnualBundle('reported-populations:'+old.period.accession,1,old.period,(*old.inputs,*extra.inputs),
            (*old.limitations,'Separate reported populations and independent checks; source parents stay unchanged.')))
    return h.HistoryBundle('reported-populations:'+str(parent.bundle.cik),1,parent.bundle.cik,tuple(out),parent.bundle.history_exceptions),a.canonical(bindings)


def field_proof(proof,field):
    """Revisions bind this population, not unrelated reconciliation metadata."""
    if field is h.Field.SHARES:
        return dict(source=proof.get('source'),populations=[p for p in proof.get('populations',[]) if p['role']=='issuer_common_shares'])
    names=({'CashAndCashEquivalentsAtCarryingValue','MarketableSecuritiesCurrent','CashCashEquivalentsAndMarketableSecurities','ShortTermInvestments'}
        if field is h.Field.CASH_INVESTMENTS else bridge.POPULATIONS-{'CashAndCashEquivalentsAtCarryingValue','MarketableSecuritiesCurrent','CashCashEquivalentsAndMarketableSecurities','ShortTermInvestments'})
    return dict(source=proof.get('source'),version=proof['version'],
        candidates=[r for r in proof.get('candidates',[]) if r['concept'] in names],
        invalid_bindings=[r for r in proof.get('invalid_bindings',[]) if r.get('name','').split(':')[-1] in names],
        populations=[p for p in proof.get('populations',[]) if p['role']=='reported_current_liquidity'] if field is h.Field.CASH_INVESTMENTS else [])


@dataclass(frozen=True)
class DeliveryHistory:
    parent:a.PreparedHistory
    annuals:tuple[AnnualDelivery,...]
    bundle:h.HistoryBundle
    bindings_json:str
    serialization_schema:str=SCHEMA

    def __post_init__(self):
        h._typed(self.annuals,AnnualDelivery)
        if self.serialization_schema not in (SCHEMA,LEGACY_SCHEMA):raise h.InputError('Unknown delivery history schema')
        expected=(cfo.VERSION,bridge.VERSION) if self.serialization_schema==LEGACY_SCHEMA else (cfo.IMPROVED_VERSION,bridge.IMPROVED_VERSION)
        if any((json.loads(v.reconciliation_json)['version'],json.loads(v.bridge_json)['version'])!=expected for v in self.annuals):raise h.InputError('Inspection/schema version mismatch; no implicit migration')
        if self.serialization_schema==LEGACY_SCHEMA and any(v.binding_receipts for v in self.annuals):raise h.InputError('Legacy envelope cannot hide added binding receipts')
        if (self.bundle,self.bindings_json)!=combine(self.parent,self.annuals):raise h.InputError('Delivery differs from exact source assembly')

    @property
    def ticker(self):return self.parent.ticker
    @property
    def aliases(self):return self.parent.aliases
    @property
    def original(self):return self.parent.original
    @property
    def diagnostics_json(self):return self.parent.diagnostics_json
    @property
    def ledger_seals(self):return self.parent.ledger_seals


def deliver(parent,records):
    annuals=tuple(inspect(annual,records.get(annual.period.accession)) for annual in parent.bundle.annuals)
    bundle,bindings=combine(parent,annuals)
    return DeliveryHistory(parent,annuals,bundle,bindings)


def overlay(prepared,store):
    """Same-period transitive dependencies are invalidated, never recalculated."""
    result=overrides.overlay(prepared,store)
    invalid=set(result.dependent_review)
    for annual in prepared.bundle.annuals:
        sources=[v.alternatives[0] for v in result.values if v.period==annual.period]
        changed={v.input_id for v in sources}
        for source in sources:
            aliases=population_aliases(annual,source)
            changed.update(aliases);invalid.update(annual.period.accession+'#'+k for k in aliases)
        while True:
            more={v.input_id for v in annual.inputs if v.formula and set(v.formula.operands)&changed}-changed
            if not more:break
            changed.update(more);invalid.update(annual.period.accession+'#'+k for k in more)
    # The legacy API's unqualified dependencies are retained only for original
    # callers. Delivery uses exact period-qualified identities for every formula.
    return replace(result,dependent_review=tuple(sorted(x for x in invalid if '#' in x)))


def population_aliases(annual,source):
    """Exact source aliases, not numerical equivalence or expense/add-back fusion."""
    from . import retained_tax_sbc as tax_sbc
    def keys(v):
        return {(s.receipt.artifact.sha256,s.namespace,s.concept,s.context_id,s.dimensions,
                 s.start,s.end,s.unit,s.raw_value) for s in v.sources if s.occurrence_ordinal is not None}
    if source.value is None:return set()
    out=set();source_keys=keys(source)
    for v in annual.inputs:
        if v.input_id==source.input_id or not v.input_id.startswith(('usable-bridge:','displayed-cfo:')):continue
        compatible=(v.field==source.field and source.field in (h.Field.CASH_INVESTMENTS,h.Field.DEBT_LEASES)) or (
            source.field is h.Field.CFO and v.role in ('displayed_cfo_subtotal','independently_reconciled_reported_cfo')) or (
            v.field is h.Field.CFO_RESIDUAL and (source.role in tax_sbc.RECONCILIATION_ROLES or
                source.role in ('reported_cash_flow_movement','reported_operating_capital_total')))
        if compatible and v.value==source.value and v.unit==source.unit and v.as_of==source.as_of and source_keys & keys(v):out.add(v.input_id)
    return out


def inspection_payload(prepared,view='full',store=None):
    payload=review.inspection_payload(prepared,view)
    if store is None:return payload
    patches=overlay(prepared,store)
    by_key={(v.period.accession,v.alternatives[0].input_id):v for v in patches.values}
    for annual in payload['bundle']['annuals']:
        p=h._decode(annual['period'])
        for row in annual['inputs']:
            patch=by_key.get((p.accession,row['input_id']))
            if patch is not None:row.update(effective=a.click(patch),effective_basis='SEPARATE_ANALYST_OVERLAY')
            if p.accession+'#'+row['input_id'] in patches.dependent_review:
                row['effective']={**row['effective'],'value':None,'origin':'unavailable','formula':None,
                    'null_reason':'A related source/component was overridden; original selection/formula remains source history. No recomputation authorized.',
                    'requirements':row['effective']['requirements']+['Dependent population requires explicit revalidation.']}
                row['effective_basis']='DEPENDENT_POPULATION_INVALIDATED'
    payload['delivery_overlay']=json.loads(overrides.serialize_overlay(patches))
    return payload


def serialize_overlay(value):return overrides.serialize_overlay(value)


def deserialize_overlay(payload,prepared,store):
    result=overlay(prepared,store)
    if overrides._json(payload)!=overrides._json(serialize_overlay(result)):
        raise h.InputError('Delivery overlay differs from exact audit/source dependencies')
    return result


def serialize(value):
    bodies={}
    def annual(v):
        out=dict(period=a.parent._encode(v.period,bodies),primary=a.parent._encode(v.primary,bodies),
            inputs=a.parent._encode(v.inputs,bodies),bridge_json=v.bridge_json,reconciliation_json=v.reconciliation_json)
        if value.serialization_schema==SCHEMA:out['binding_receipts']=a.parent._encode(v.binding_receipts,bodies)
        return out
    extras=[annual(v) for v in value.annuals]
    return a.canonical(dict(schema=value.serialization_schema,parent=a.serialize(value.parent),annuals=extras,original_bodies=bodies))


def deserialize(payload):
    doc=overrides._json(payload)
    if set(doc)!= {'schema','parent','annuals','original_bodies'} or doc['schema'] not in (SCHEMA,LEGACY_SCHEMA):raise h.InputError('Closed delivery envelope required')
    parent=a.deserialize(doc['parent']);bodies={};used=set()
    for key,encoded in doc['original_bodies'].items():
        raw=h._decode(encoded)
        if type(raw) is not bytes or a.sha256(raw).hexdigest()!=key:raise h.InputError('Changed delivery body')
        bodies[key]=raw
    annuals=[];repaired=None
    for entry,original in zip(doc['annuals'],parent.bundle.annuals):
        keys={'period','primary','inputs','bridge_json','reconciliation_json'}
        if doc['schema']==SCHEMA:keys.add('binding_receipts')
        if set(entry)!=keys:raise h.InputError('Closed annual delivery required')
        extra=AnnualDelivery(a.parent._decode(entry['period'],bodies,used),a.parent._decode(entry['primary'],bodies,used),
            a.parent._decode(entry['inputs'],bodies,used),entry['bridge_json'],entry['reconciliation_json'],
            a.parent._decode(entry['binding_receipts'],bodies,used) if doc['schema']==SCHEMA else ())
        record=None if extra.primary is None else dict(json.loads(extra.bridge_json)['source'],body=extra.primary.artifact.body,
            retrieved_at_utc=extra.primary.retrieved_at_utc,http_status=extra.primary.http_status,
            retrieval_mode=extra.primary.retrieval_mode)
        # Recompute exact scope/selection from retained evidence, not trust a
        # serialized completeness assertion or changed derived expected number.
        if record is not None and doc['schema']==SCHEMA and extra.binding_receipts:
            if repaired is None:
                scope,catalog,_=docs.scope();repaired=docs.repaired_records(scope,catalog)
            bound=repaired.get(extra.period.accession)
            if bound is not None and bound.get('document_type') in ('EX-13','EX-13.1'):
                if (bound['url'],bound['sha256'])!=(record['url'],record['sha256']):raise h.InputError('Incorporated document serialization identity differs')
                for role in ('filing_primary','index_record'):
                    if bound[role]['sha256'] not in bodies:raise h.InputError('Required incorporated-document binding body missing')
                record={**bound,**record}
        if inspect(original,record,legacy=doc['schema']==LEGACY_SCHEMA)!=extra:raise h.InputError('Delivery proof/source replay differs')
        annuals.append(extra)
    if used!=set(bodies) or len(annuals)!=len(parent.bundle.annuals) or len(doc['annuals'])!=len(annuals):raise h.InputError('Exact body/annual accounting differs')
    bundle,bindings=combine(parent,tuple(annuals))
    return DeliveryHistory(parent,tuple(annuals),bundle,bindings,doc['schema'])


def build():
    prior,parents=a.build();scope,catalog,errors=docs.scope()
    records=docs.repaired_records(scope,catalog)
    histories={t:deliver(p,records) for t,p in parents.items()}
    rows=[]
    for t,p in histories.items():
        for annual in p.annuals:
            rows.append(dict(ticker=t,identity=h._encode(annual.period),bridge=json.loads(annual.bridge_json),
                reconciliation=json.loads(annual.reconciliation_json),inputs=[a.click(v) for v in annual.inputs]))
    ledger=dict(schema=SCHEMA,rows=rows,primary_scope=scope,receipt_diagnostics=errors)
    summary=coverage(histories)
    summary['original_assembly']=prior
    return ledger,histories,summary


def coverage(histories):
    fields={};bands={}
    recent_selected=sum(min(3,len(p.bundle.annuals)) for p in histories.values())
    older_selected=sum(max(0,len(p.bundle.annuals)-3) for p in histories.values())
    if (len(histories),recent_selected,older_selected)!=(42,121,78):raise h.InputError('Frozen delivery denominator differs')
    for field in h.Field:
        outcomes=[]
        for p in histories.values():
            for rank,annual in enumerate(reversed(p.bundle.annuals),1):
                bindings={b['input_id']:b for b in json.loads(p.bindings_json) if b['accession']==annual.period.accession}
                vv=[v for v in annual.inputs if v.field is field]
                complete=[v for v in vv if v.value is not None and v.completeness is h.Completeness.COMPLETE and
                    (bindings[v.input_id].get('field_complete') or (field in a.PRIMARY and bindings[v.input_id]['category']=='prepared_value'))]
                newly_confirmed=[v for v in complete if v.role in QUALIFIED]
                if newly_confirmed:complete=newly_confirmed
                outcomes.append(dict(band='recent' if rank<=3 else 'older',usable=len(complete)==1,
                    valued=any(v.value is not None for v in vv),partial=any(v.value is not None and v.completeness is not h.Completeness.COMPLETE for v in vv),
                    conflicting=any(v.quality is h.Quality.CONFLICTING for v in vv),null=any(v.value is None for v in vv)))
        fields[field.value]={k:sum(v[k] for v in outcomes) for k in ('usable','valued','partial','conflicting','null')}
        fields[field.value]['bands']={band:dict(selected_denominator=recent_selected if band=='recent' else older_selected,target_denominator=3*len(histories) if band=='recent' else 2*len(histories),
            usable=sum(v['usable'] for v in outcomes if v['band']==band),target='90%' if band=='recent' else '80%') for band in ('recent','older')}
    annuals=[v for p in histories.values() for v in p.annuals]
    return dict(schema=SCHEMA,histories=len(histories),selected_annuals=len(annuals),target_annuals=210,history_deficits=210-len(annuals),
        fields=fields,cfo_checks=dict(Counter(json.loads(v.reconciliation_json)['status'] for v in annuals)),
        populations=dict(Counter(v.role for y in annuals for v in y.inputs if v.input_id.startswith('usable-bridge:'))),
        financial_sufficiency='NOT_ASSESSED',phase_closed=False)
