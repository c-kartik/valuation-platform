"""Retained approved derivations only. No new equations or financial policies."""
from collections import Counter
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
import hashlib
import json
from . import historical_inputs as h, retained_income_sweep as sweep
from . import nvda_income_inputs as shared
from . import retained_components as inspection, retained_income_preparation as income
from ..normalization import operating_income_derivation as policy
from ..normalization.concepts import FinancialMetric
from ..normalization.models import DerivedHistoricalValue, MissingHistoricalMetric, MissingReason
from ..normalization.output import _serialize_operating_income_derivation
from ..sec.submissions import SECFiling
from ..sec.tickers import SECCompanyIdentity
from ..sec.filing_xbrl import parse_filing_xbrl_instance
from ..sec.annual_period import resolve_annual_period, ResolvedAnnualPeriod
from ..sec.fact_selection import FilingFactObservations

DATA='docs/approved-income-integration-bindings.json'
PROOF_FLAG='approved_operating_income_provenance:'


def bindings():
    data=json.loads((shared.ROOT/DATA).read_text())
    for path,digest in data['sources'].items():
        if hashlib.sha256((shared.ROOT/path).read_bytes()).hexdigest()!=digest:raise h.InputError('Retained integration source changed: '+path)
    for item in data['filings']:
        path,pointer=item['reference'].split('#');doc=json.loads((shared.ROOT/path).read_text())
        for key in pointer.strip('/').split('/'):doc=doc[int(key)] if isinstance(doc,list) else doc[key]
        if doc!=item['filing']:raise h.InputError('Filing metadata claim differs from retained source')
    for item in data['seed_identities']:
        path,line=item['reference'].rsplit(':',1);text=(shared.ROOT/path).read_text().splitlines()[int(line)-1]
        identity=item['identity']
        expected=f"| {item['issuer']} | {identity['annual_end']} | `{identity['accession']}` | {identity['annual_start']} | {identity['annual_end']} |"
        if text!=expected:raise h.InputError('Seed identity claim differs from reviewed resolver row')
    return data


def execute(evidence,metadata):
    """Replay actual body, annual resolver and immutable operating-income policy."""
    p=evidence.period
    if metadata['accession_number']!=p.accession or metadata['form']!=p.form or metadata['report_date']!=str(p.annual_end):
        raise h.InputError('Retained filing metadata/target mismatch')
    if not any(m['filing']==metadata for m in bindings()['filings']):raise h.InputError('Filing metadata lacks an exact retained source binding')
    filing=SECFiling(p.accession,p.form,date.fromisoformat(metadata['filing_date']),p.annual_end,metadata['primary_document'])
    receipt=evidence.instance
    if receipt is None:raise h.InputError('Verified retained instance required')
    stamp=datetime.fromisoformat(receipt.retrieved_at_utc)
    company=SECCompanyIdentity('RETAINED',p.cik,f'{p.cik:010d}','Exact retained registrant',receipt.artifact.url,stamp)
    xbrl=parse_filing_xbrl_instance(receipt.artifact.body,company=company,filing=filing,source_url=receipt.artifact.url,retrieved_at=stamp)
    annual=resolve_annual_period(xbrl)
    if not isinstance(annual,ResolvedAnnualPeriod) or (annual.start,annual.end)!=(p.annual_start,p.annual_end):
        raise h.InputError('Authoritative annual DEI identity differs')
    missing=MissingHistoricalMetric(FinancialMetric.OPERATING_INCOME,MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION,())
    result=policy.apply_curated_operating_income_derivation_policy(FilingFactObservations(filing,()),missing,p.cik,annual,xbrl)
    if isinstance(result,DerivedHistoricalValue):policy.validate_operating_income_derivation_provenance(result.derivation_provenance)
    return result


def package(annual,evidence,result):
    """Signed registered components + full existing policy proof, separately derived."""
    proof=result.derivation_provenance;p=annual.period
    entry=policy.operating_income_derivation_entry_for(p.cik,p.accession,p.annual_end,p.annual_start,p.annual_end)
    serialized=_serialize_operating_income_derivation(proof)
    refs={};used=set()
    for operand in proof.operands:
        refs[operand.operand_id]=[]
        for occurrence in (*operand.occurrences,*operand.reviewed_nonselected_occurrences):
            matches=[(f,i) for f,i in evidence.facts if i not in used and
                (f.namespace,f.concept,f.context_id,f.raw_value,f.decimals,f.unit_ref,f.start,f.end)==
                (occurrence.namespace,occurrence.concept,occurrence.context_id,occurrence.raw_value,occurrence.decimals,
                 occurrence.unit_ref,occurrence.start,occurrence.end)]
            if not matches:raise h.InputError('Policy occurrence cannot bind original root occurrence')
            f,i=matches[0];used.add(i)
            source=h.SourceReference(f'{p.accession}:approved-ebit:{operand.operand_id}:root-{i}',p,evidence.instance,
                json.dumps(dict(operand_id=operand.operand_id,policy_id=proof.policy_id,policy_version=proof.policy_version,
                    local_policy_ordinal=occurrence.occurrence_ordinal,original_root_ordinal=i,role=operand.economic_role),sort_keys=True),
                f.namespace,f.concept,f.context_id,i,f.start,f.end,'USD',f.raw_value,f.decimals,())
            refs[operand.operand_id].append((source,occurrence in operand.occurrences))
    inputs=[];operands=[]
    for term in entry.calculation_terms:
        definition=next(o for o in proof.operands if o.operand_id==term.operand_id)
        groups={}
        for source,selected in refs[term.operand_id]:
            if selected:groups.setdefault(source.decimals,[]).append(source)
        observations=[]
        for precision,sources in groups.items():
            observations.append(h.InputValue(f'approved-ebit:operand:{term.operand_id}:{precision}',h.Field.EBIT,p,None,
                term.coefficient*definition.expected_value,'USD',1,int(term.coefficient),precision,
                'support_only_signed_operating_component',h.Origin.REPORTED,h.Quality.SUPPORTED,definition.economic_role,
                h.Scope.OPERATING_ONLY,h.Completeness.COMPLETE,h.Review.REVIEWED,tuple(sources),None,None,(),
                'Exact registered operand; grouped confirming representations retain precision, not a new selection policy.',
                ('support_only_not_independent_ebit','registered_operating_component'),(),None,(term.operand_id,)))
        if not observations:raise h.InputError('Missing required calculation occurrence')
        item=replace(observations[0],alternatives=tuple(observations[1:]));inputs.append(item);operands.append(item.input_id)
    all_refs=tuple(source for pairs in refs.values() for source,_ in pairs)
    formula=h.Formula(entry.formula_id,int(proof.policy_version),h.FormulaKind.COMPONENT_TOTAL,
        ' + '.join(f'({t.coefficient})*{t.operand_id}' for t in entry.calculation_terms),tuple(operands),True,True,True,
        tuple(s.source_id for s in all_refs))
    derived=h.InputValue('approved-ebit:primitive',h.Field.EBIT,p,None,result.value,'USD',1,1,
        'derived_exact_from_registered_operand_precision','approved_derived_operating_income',h.Origin.DERIVED,h.Quality.SUPPORTED,
        entry.perimeter_id,h.Scope.OPERATING_ONLY,h.Completeness.COMPLETE,h.Review.REVIEWED,all_refs,None,formula,(),
        'Existing immutable exact-accession resolver verified operands, arithmetic and entry-specific bridge gates.',
        ('existing_derivation_only','no_financial_sufficiency_or_timing_approval',PROOF_FLAG+json.dumps(serialized,sort_keys=True,separators=(',',':'))),
        ('Future consumer-specific timing and financial sufficiency remain unassessed.',),None,('approved_ebit_primitive',))
    return replace(annual,inputs=tuple(v for v in annual.inputs if v.field is not h.Field.EBIT)+(derived,*inputs)),serialized


def build():
    ledger,histories=sweep.build();data=bindings();config,refs=sweep.sources()
    manifest=shared.pinned(shared.MANIFEST,shared.MANIFEST_SHA256)
    exceptions=[]
    for row in ledger['rows']:
        slot=next(f for f in row['fields'] if f['field']=='ebit')
        if slot['outcome']!='NO_ELIGIBLE_DIRECT_CONCEPT':continue  # Never replace conflicts or direct bindings.
        p=shared.period(row['identity'])
        entry=policy.operating_income_derivation_entry_for(p.cik,p.accession,p.annual_end,p.annual_start,p.annual_end)
        if entry is None:
            row['derivation_integration']=dict(status='UNREGISTERED',reason='No approved exact-accession derivation; no new equation.')
            continue
        metadata=next((m for m in data['filings'] if m['filing']['accession_number']==p.accession),None)
        if metadata is None:
            reason='Verified retained instance available, but exact filing_date/primary_document binding needed by existing FilingXBRLEvidence serialization is not retained; policy operands not executed.'
            row['derivation_integration']=dict(status='MISSING_FILING_METADATA',reason=reason,policy_id=policy.OPERATING_INCOME_DERIVATION_POLICY_ID,policy_version='1')
            exceptions.append(dict(identity=row['identity'],reason=reason));continue
        selection=next(r for r in manifest['rows'] if r['identity']==row['identity'])
        evidence,_,_,_=sweep.inspect_row(selection,refs,config)
        result=execute(evidence,metadata['filing'])
        if not isinstance(result,DerivedHistoricalValue):
            row['derivation_integration']=dict(status=type(result).__name__,reason='Existing resolver did not approve retained operands; no bypass.')
            continue
        history=histories[row['issuer']];annual=next(a for a in history.annuals if a.period==p)
        packaged,proof=package(annual,evidence,result)
        histories[row['issuer']]=replace(history,annuals=tuple(packaged if a.period==p else a for a in history.annuals))
        row['fields']=[dict(field='ebit',outcome='DERIVED',status='POPULATED_DERIVED',origin='derived',value_usd=str(result.value),
            unit='USD',scale=1,sign=1,precision='derived_exact_from_registered_operand_precision',provenance=proof,
            formula=dict(expression=next(v.formula.expression for v in packaged.inputs if v.formula),kind='signed_registered_component_total'),
            source_references=[dict(source_id=s.source_id,url=s.receipt.artifact.url,sha256=s.receipt.artifact.sha256,
                ordinal=s.occurrence_ordinal,context_id=s.context_id,raw_value=s.raw_value,precision=s.decimals) for s in next(v for v in packaged.inputs if v.formula).sources])
            if f['field']=='ebit' else f for f in row['fields']]
        row['derivation_integration']=dict(status='VERIFIED_DERIVED',metadata_reference=metadata['reference'])
    # Documented prior annual-resolver results establish identity candidates, not
    # fresh byte/receipt/DEI replay. No placeholder instance URL is manufactured.
    for row in ledger['rows']:
        if row['issuer'] not in ('META','COST'):continue
        matches=[s for s in data['seed_identities'] if s['issuer']==row['issuer'] and s['identity']['annual_end']==row['identity']['annual_end']]
        if not matches:continue
        row['identity']=matches[0]['identity'];row['identity_reference']=matches[0]['reference']
        row['identity_depth']='RETAINED_REVIEWED_ANNUAL_RESOLVER_RECORD; original body/receipt absent, not freshly replayed'
        row['fields']=[dict(field=f['field'],outcome='MISSING_RETAINED_BODY',status='UNAVAILABLE',
            unresolved_requirements=['Retained annual identity record exists; exact instance body/URL/digest/receipt required for shared direct fact inspection.']) for f in row['fields']]
    for name,summary in ledger['summary'].items():
        summary['outcomes']=dict(sorted(Counter(f['outcome'] for row in ledger['rows'] if row['issuer']==name for f in row['fields']).items()))
    ledger['outcomes']=dict(sorted(Counter(f['outcome'] for row in ledger['rows'] for f in row['fields']).items()))
    ledger['schema']='approved-income-integration-v1';ledger['integration_binding_sha256']=hashlib.sha256((shared.ROOT/DATA).read_bytes()).hexdigest()
    ledger['derivation_metadata_exceptions']=exceptions
    ledger['identity_backlog']=[r for r in ledger['identity_backlog'] if not any(s['issuer']==r['issuer'] and
        s['identity']['annual_end']==r['identity']['annual_end'] for s in data['seed_identities'])]
    ledger['seed_identity_exceptions']=[dict(identity=r['identity'],issuer=r['issuer'],fields=r['fields']) for r in ledger['rows'] if r['issuer'] in ('META','COST')]
    return ledger,histories


def validate_serialized_history(payload):
    """Generic models round-trip proof; this gate re-executes approved policy."""
    history=h.deserialize(payload);data=bindings()
    for annual in history.annuals:
        derived=[v for v in annual.inputs if v.origin is h.Origin.DERIVED]
        for value in derived:
            flags=[f[len(PROOF_FLAG):] for f in value.flags if f.startswith(PROOF_FLAG)]
            if len(flags)!=1:raise h.InputError('Full approved policy proof required')
            metadata=next(m['filing'] for m in data['filings'] if m['filing']['accession_number']==annual.period.accession)
            receipt=value.sources[0].receipt
            evidence=inspection.prepare(annual.period,(receipt,),(inspection.ArtifactBinding(receipt.artifact.url,receipt.artifact.sha256,'instance'),))
            result=execute(evidence,metadata)
            if not isinstance(result,DerivedHistoricalValue) or value.value!=result.value or json.loads(flags[0])!=_serialize_operating_income_derivation(result.derivation_provenance):
                raise h.InputError('Serialized approved policy value/proof differs')
            original=replace(annual,inputs=tuple(v for v in annual.inputs if v.field is not h.Field.EBIT)+
                (income.unavailable(annual.period,h.Field.EBIT,'Replay placeholder, never an approved value.',h.Review.UNREVIEWED),))
            # Repack exact inputs and compare formula, support operands and root
            # occurrence bindings, not just the supplied numerical result.
            expected,_=package(original,evidence,result)
            if tuple(v for v in expected.inputs if v.field is h.Field.EBIT)!=tuple(v for v in annual.inputs if v.field is h.Field.EBIT):
                raise h.InputError('Serialized operands/formula/source bindings differ')
    return history
