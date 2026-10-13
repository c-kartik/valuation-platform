"""Retained approved Capex replay; no new scope or financial policy."""
from collections import Counter
from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
import base64
import gzip
import hashlib
import json
from . import historical_inputs as h, retained_components as r, retained_cfo_preparation as cfo
from . import retained_tax_sbc as previous, retained_income_preparation as missing
from . import pilot_historical_inputs as pilot, nvda_income_inputs as shared
from ..normalization import capex_scope as curated
from ..normalization.concepts import CAPEX_POLICY, FinancialMetric
from ..normalization.historical import _resolve_metric
from ..normalization.models import NormalizedHistoricalValue, AmbiguousHistoricalMetric, EvidenceSourceKind
from ..normalization.output import _serialize_policy, _policy_reference
from ..sec.company_facts import SECFactObservation
from ..sec.fact_selection import FilingFactObservations, SelectedFactObservation, ObservationRelationship
from ..sec.submissions import SECFiling
from ..sec.tickers import SECCompanyIdentity
from ..sec.filing_xbrl import parse_filing_xbrl_instance
from ..sec.annual_period import resolve_annual_period, ResolvedAnnualPeriod

DIRECT=CAPEX_POLICY.candidates[0].name
PROOF='retained_capex_policy:'
LIMITATIONS=('Cash Capex is not complete reinvestment, a cash/accrual bridge or valuation consumption approval.',
    'Broader software/intangible/productive-asset captions require existing exact approvals; no blanket software rule.',
    'Noncash additions, capital creditors, lease principal/liabilities, acquisitions and proceeds remain non-additive separate populations.',
    'Future consumer timing/scope sufficiency remains unassessed; no absence-to-zero or component sum.')
SUPPORT={
    'PaymentsToAcquireProductiveAssets':'BROAD_PRODUCTIVE_ASSET_SCOPE_UNAPPROVED',
    'PaymentsToAcquireOtherPropertyPlantAndEquipment':'OTHER_PPE_SCOPE_UNAPPROVED',
    'PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets':'COMBINED_PPE_INTANGIBLE_SCOPE_UNAPPROVED',
    'PaymentsToAcquireIntangibleAssets':'SEPARATE_INTANGIBLE_PURCHASE_NOT_PPE_APPROVAL',
    'PaymentsToAcquireSoftware':'SOFTWARE_PURCHASE_NOT_BLANKET_APPROVAL',
    'PaymentsToAcquireOtherProductiveAssets':'OTHER_PRODUCTIVE_ASSET_SCOPE_UNAPPROVED',
    'PurchasesOfPropertyAndEquipmentAndIntangibleAssets':'ISSUER_COMBINED_PPE_INTANGIBLE_SCOPE_UNAPPROVED',
    'PaymentsToAcquireBusinessesNetOfCashAcquired':'ACQUISITION_CONSIDERATION_NOT_CAPEX',
    'PaymentsToAcquireBusinessesGross':'ACQUISITION_CONSIDERATION_NOT_CAPEX',
    'PaymentsForFinancedPropertyPlantAndEquipmentFinancingActivities':'FINANCING_PAYMENT_NOT_INVESTING_PURCHASE',
    'ProceedsFromSaleOfPropertyPlantAndEquipment':'PROCEEDS_NOT_GROSS_PURCHASES',
    'FinanceLeasePrincipalPayments':'FINANCING_PRINCIPAL_NOT_INVESTING_PURCHASE',
    'LongTermDebtAndFinanceLeaseObligationsCurrent':'DEBT_LEASE_BALANCE_NOT_CASH_PURCHASE',
    'RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability':'NONCASH_LEASE_ADDITION',
    'RightofUseAssetsObtainedinExchangeforOperatingandFinanceLeaseLiabilities':'NONCASH_LEASE_ADDITION',
    'CapitalExpendituresIncurredButNotYetPaid':'CAPITAL_CREDITOR_NOT_CASH_PURCHASE',
    'PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable':'CAPITAL_CREDITOR_NOT_CASH_PURCHASE',
}


def artifacts():
    """Read only documented committed body collections, not /tmp guesses."""
    paths=list(json.loads((shared.ROOT/'docs/retained-income-sweep-sources.json').read_text()))+[
        'docs/evidence/cvx-capex-perimeter-response-bodies.json','tests/fixtures/capex_amzn_response_bodies.json',
        'tests/fixtures/capex_index_responses.json']
    out={}
    for path in dict.fromkeys(paths):
        raw=(shared.ROOT/path).read_bytes();doc=json.loads(raw)
        aa=doc if isinstance(doc,list) else doc.get('artifacts',[])
        for index,a in enumerate(aa):
            encoded=a.get('response_body_gzip_base64') or a.get('body_gzip_base64')
            if encoded:
                if a.get('representation')!='sec_response_body_bytes' or a.get('digest_type')!='sha256_sec_response_body_bytes':
                    raise h.InputError('Retained body has missing/unsupported original-byte representation: '+path)
                if isinstance(encoded,list):encoded=''.join(encoded)
                body=gzip.decompress(base64.b64decode(encoded,validate=True))
            elif a.get('response_body_base64'):
                if path!='tests/fixtures/capex_index_responses.json':
                    raise h.InputError('Unregistered untyped response fixture')
                # Existing LLY correction contract separately verifies this
                # original response field/digest versus retained JSON bytes.
                body=base64.b64decode(a['response_body_base64'],validate=True)
            else:continue
            digest=a.get('sha256') or a.get('response_digest')
            if hashlib.sha256(body).hexdigest()!=digest:raise h.InputError('Retained artifact declared digest mismatch: '+path)
            url=a['source_url'];key=(url,digest)
            ref=dict(path=path,locator=('/'+str(index) if isinstance(doc,list) else '/artifacts/'+str(index)),
                document_sha256=hashlib.sha256(raw).hexdigest(),source_url=url,sha256=digest,
                representation='sec_response_body_bytes',digest_type='sha256_sec_response_body_bytes',
                retrieved_at_utc=a.get('retrieved_at_utc') or a.get('retrieved_at') or a.get('original_retrieval_at_utc'),
                http_status=a.get('http_status') or a.get('original_http_status'),
                metadata_limit='Actual retained metadata only; missing original fields not recovered.')
            out.setdefault(key,(body,ref))
    return out


def inspect(evidence,concept):
    ns=evidence.namespaces.get('us-gaap','')
    if not ns.startswith('http://fasb.org/us-gaap/'):raise h.InputError('Exact standard taxonomy required')
    return r.inspect(evidence,r.SelectionSpec('capex:'+concept,(r.Selector(ns,concept,()),),
        'annual','USD','reported_cash_purchase_candidate','Exact candidate scope requires existing direct or curated approval.',LIMITATIONS))


def direct_result(evidence):
    """Project inspected signatures into the existing numeric selector ONLY.

    This is not a Company Facts receipt/observation import. Never emit the
    selector's Company-Facts-labelled evidence: rebind to actual filing evidence.
    Collapse equal numeric signatures for selection, keeping every raw occurrence
    and precision in the original inspection/packaging. No float conversion.
    Unknown filing-date metadata stays None in this ephemeral selector projection.
    """
    result=inspect(evidence,DIRECT);p=evidence.period
    filing=SimpleNamespace(accession_number=p.accession,form=p.form,report_date=p.annual_end)
    projected=[]
    for value in dict.fromkeys(c.value for c in result.candidates):
        if value!=value.to_integral_value():raise h.InputError('Existing numeric selector cannot represent exact fractional USD without float conversion')
        observation=SECFactObservation('USD',int(value),p.annual_start,p.annual_end,p.accession,None,None,p.form,None,None)
        projected.append(SelectedFactObservation('us-gaap',DIRECT,observation,ObservationRelationship.CURRENT))
    resolved=_resolve_metric(FilingFactObservations(filing,tuple(projected)),CAPEX_POLICY,evidence.instance.artifact.url,None)
    # Replace transient selector provenance; no fictional Company Facts source.
    refs=tuple(__compact(c,evidence) for c in result.candidates)
    if isinstance(resolved,NormalizedHistoricalValue):resolved=replace(resolved,chosen_source=refs[0],confirming_sources=refs[1:])
    elif isinstance(resolved,AmbiguousHistoricalMetric):resolved=replace(resolved,candidates=refs)
    return resolved,result


def __compact(candidate,evidence):
    from ..normalization.models import FactEvidence
    p=evidence.period
    return FactEvidence(EvidenceSourceKind.FILING_XBRL,evidence.instance.artifact.url,'us-gaap',candidate.concept,
        candidate.value,'USD',p.annual_start,p.annual_end,p.accession,p.form,None,None,None,None)


def replay(evidence,store):
    direct,result=direct_result(evidence);p=evidence.period
    proof=dict(policy_id='CAPEX_POLICY',version=None,version_status='existing_unversioned_direct_policy',
        candidates=[dict(taxonomy=c.taxonomy,concept=c.name) for c in CAPEX_POLICY.candidates],
        resolver='normalization.historical._resolve_metric',source_kind='filing_xbrl',
        selection_projection='Ephemeral exact integer signatures only; no Company Facts provenance emitted.')
    policy_entry=next(((policy,entry) for policy in curated.CAPEX_SCOPE_POLICY_CATALOG.policies for entry in policy.entries
        if (entry.company_cik,entry.accession_number,entry.annual_start,entry.annual_end)==(p.cik,p.accession,p.annual_start,p.annual_end)),None)
    if isinstance(direct,AmbiguousHistoricalMetric):
        if policy_entry:proof.update(registered_policy_id=policy_entry[0].policy_id,registered_version=policy_entry[0].version,
            registered_replay='Not applied: existing direct ambiguity cannot be overridden.')
        return direct,result,proof,[],policy_entry[1] if policy_entry else None
    if not policy_entry:return direct,result,proof,[],None
    policy,entry=policy_entry;proof.update(registered_policy_id=policy.policy_id,registered_version=policy.version)
    missing_artifacts=[dict(url=url,sha256=digest,reason='Registered original response body absent from documented retained collections.',
        available_other_representations=[ref for (u,d),(body,ref) in store.items() if u==url and d!=digest])
        for url,digest in entry.artifact_digests if (url,digest) not in store and (url,digest)!=(evidence.instance.artifact.url,evidence.instance.artifact.sha256)]
    if evidence.instance.artifact.sha256!=entry.instance_digest:
        missing_artifacts.append(dict(url=entry.instance_url,sha256=entry.instance_digest,reason='Verified preparation instance differs from registered instance digest; no silent refresh/rebinding.'))
    if missing_artifacts:return direct,result,proof,missing_artifacts,entry
    filing=SECFiling(p.accession,p.form,entry.filed,p.annual_end,entry.primary_document)
    receipt=evidence.instance;stamp=datetime.fromisoformat(receipt.retrieved_at_utc)
    company=SECCompanyIdentity('RETAINED',p.cik,f'{p.cik:010d}','Exact retained registrant',receipt.artifact.url,stamp)
    x=parse_filing_xbrl_instance(receipt.artifact.body,company=company,filing=filing,source_url=receipt.artifact.url,retrieved_at=stamp)
    annual=resolve_annual_period(x)
    if not isinstance(annual,ResolvedAnnualPeriod) or (annual.start,annual.end)!=(p.annual_start,p.annual_end):raise h.InputError('Registered authoritative annual period mismatch')
    bodies={url:(receipt.artifact.body if url==receipt.artifact.url else store[url,digest][0]) for url,digest in entry.artifact_digests}
    attestation=curated.verify_capex_artifacts(entry,bodies,x)
    resolved=curated.apply_curated_capex_scope_policy(FilingFactObservations(filing,()),direct,p.cik,annual,x,attestation,policy=policy)
    if isinstance(resolved,NormalizedHistoricalValue) and resolved.policy_provenance:
        curated.validate_capex_scope_provenance(resolved.policy_provenance)
        proof=dict(_serialize_policy(_policy_reference(resolved.policy_provenance,filing)),
            artifact_bindings=[store[url,digest][1] if url!=receipt.artifact.url else dict(source_url=url,sha256=digest,
                representation=receipt.artifact.representation,digest_type=receipt.artifact.digest_type,
                retrieved_at_utc=receipt.retrieved_at_utc,http_status=receipt.http_status,source='unchanged_verified_preparation_receipt')
                for url,digest in entry.artifact_digests])
        result=inspect(evidence,entry.concept)
    return resolved,result,proof,[],entry


def support(evidence):
    rows=[]
    for fact,i in evidence.facts:
        if fact.concept not in SUPPORT:continue
        c=evidence.contexts[fact.context_id]
        if c.end!=evidence.period.annual_end or c.start not in (None,evidence.period.annual_start):continue
        rows.append(dict(namespace=fact.namespace,concept=fact.concept,ordinal=i,context_id=fact.context_id,
            start=None if c.start is None else str(c.start),end=str(c.end),dimensions=list(r.dimensions(c)),
            unit_id=fact.unit_ref,raw_value=fact.raw_value,precision=fact.decimals,nil=fact.is_nil,
            unit=None if fact.unit is None else dict(numerator=[dict(namespace=q.namespace,name=q.local_name) for q in fact.unit.numerator_measures],
                denominator=[dict(namespace=q.namespace,name=q.local_name) for q in fact.unit.denominator_measures]),
            role=SUPPORT[fact.concept],acceptance='SUPPORT_ONLY_UNLESS_EXACT_CURATED_REPLAY_SUCCEEDS'))
    return rows


def supplementary(evidence):
    """Annual USD support preserves raw signs, never an accepted replacement.

    Instant balances/noncash liabilities stay diagnostics: the unchanged annual
    Capex model must not disguise an instant as an annual cash observation.
    """
    values=[]
    for concept,role in SUPPORT.items():
        try: result=inspect(evidence,concept)
        except h.InputError: continue  # Raw invalid/excluded populations remain diagnostic.
        for c in result.candidates:
            values.append(h.InputValue('retained-capex:support:'+concept+':'+str(c.occurrences[0].ordinal),h.Field.CAPEX,
                evidence.period,None,c.value,'USD',1,1,c.precision,'support_only_raw_noncapex_population',h.Origin.REPORTED,
                h.Quality.LIMITED,role,h.Scope.RESTRICTED,h.Completeness.PARTIAL,h.Review.REVIEWED,c.evidence_references,
                None,None,(),'Raw support observation; not approved cash Capex, not additive and not a substitute.',
                ('support_only','raw_sign_not_cash_contribution','no_aggregation'),LIMITATIONS,None,(concept,)))
    return tuple(values)


def package(evidence,store):
    proof={};gaps=[];entry=None
    try:
        resolved,result,proof,gaps,entry=replay(evidence,store)
        candidates=tuple(h.InputValue('retained-capex:'+c.concept+':'+str(c.occurrences[0].ordinal),h.Field.CAPEX,
            evidence.period,None,c.value*-1,'USD',1,-1,c.precision,'support_only_cash_purchase_candidate',h.Origin.REPORTED,
            h.Quality.LIMITED,'Unapproved until exact existing policy replay.',h.Scope.RESTRICTED,h.Completeness.PARTIAL,
            h.Review.REVIEWED,c.evidence_references,None,None,(),'Retained exact candidate, not a new financial scope approval.',
            ('no_aggregation','not_complete_reinvestment'),LIMITATIONS,None,(c.concept,)) for c in result.candidates)
        if isinstance(resolved,NormalizedHistoricalValue) and Decimal(str(resolved.value))>=0:
            chosen=next(v for v in candidates if v.value==Decimal(str(resolved.value))*-1)
            status='CURATED' if resolved.policy_provenance else 'DIRECT'
            value=replace(chosen,role='approved_reported_cash_capex_outflow',scope=(entry.economic_scope if status=='CURATED' else 'Existing approved direct cash PP&E purchase semantics.'),
                quality=h.Quality.SUPPORTED,alternatives=tuple(v for v in candidates if v is not chosen),
                flags=chosen.flags+(PROOF+json.dumps(proof,sort_keys=True,separators=(',',':')),),
                selection_rationale='Existing policy resolver replay; only cash outflow sign is normalized. No new scope interpretation.')
        else:
            status=('CONFLICTING' if isinstance(resolved,AmbiguousHistoricalMetric) else 'EVIDENCE_GAP' if gaps else 'UNAPPROVED_SCOPE' if support(evidence) else 'UNAVAILABLE')
            reason=('Unequal eligible approved candidates; no silent selection.' if status=='CONFLICTING' else
                'Registered approval cannot replay mandatory original artifacts.' if gaps else
                'Negative reported payment magnitude cannot be labeled a negative cash outflow; no absolute-value transformation.' if isinstance(resolved,NormalizedHistoricalValue) else
                'Existing policy does not approve retained scope; no absent component zero or fallback.')
            value=replace(missing.unavailable(evidence.period,h.Field.CAPEX,reason,h.Review.REVIEWED),alternatives=candidates,
                quality=h.Quality.CONFLICTING if status=='CONFLICTING' else h.Quality.LIMITED)
        diagnostic=support(evidence)
        qualified={(s.namespace,s.concept) for s in value.sources} if value.value is not None else set()
        for row in diagnostic:
            if (row['namespace'],row['concept']) in qualified and not row['dimensions'] and not row['nil']:
                row['acceptance']='ACCEPTED_EXACT_CURATED_OPERAND_ONLY_NOT_BLANKET_SCOPE'
        value=replace(value,alternatives=value.alternatives+tuple(v for v in supplementary(evidence)
            if (v.sources[0].namespace,v.sources[0].concept) not in qualified),
            flags=value.flags+('retained_capex_support:'+json.dumps(diagnostic,sort_keys=True,separators=(',',':')),))
        return value,dict(status=status,value_usd=None if value.value is None else str(value.value),policy=proof,
            approved_entry_evidence_gaps=gaps,unresolved_requirements=list(value.unresolved_requirements),support=diagnostic,
            candidates=[dict(concept=c.concept,namespace=c.namespace,raw_value=str(c.value),sign=-1,scale=1,precision=c.precision,
                occurrences=[dict(ordinal=o.ordinal,context_id=o.context_id,unit_id=o.unit_id,raw_value=o.raw_value,precision=o.decimals) for o in c.occurrences]) for c in result.candidates])
    except (ValueError,KeyError) as exc:
        reason='Retained policy/evidence replay failed: '+type(exc).__name__+': '+str(exc)
        value=missing.unavailable(evidence.period,h.Field.CAPEX,reason,h.Review.REVIEWED)
        return value,dict(status='EVIDENCE_GAP',value_usd=None,policy=proof,approved_entry_evidence_gaps=gaps,
            unresolved_requirements=[reason],support=support(evidence),candidates=[])


def build():
    baseline,histories=previous.build();store=artifacts();rows=[];out={}
    pilots={a.period for name in ('MSFT','AAPL','GOOGL') for a in pilot.load_history(name).annuals}
    for name,history in histories.items():
        aa=[]
        for annual in history.annuals:
            evidence=cfo.prepare(annual);value,row=package(evidence,store)
            if annual.period in pilots:
                original=next(v for v in annual.inputs if v.field is h.Field.CAPEX)
                if value.value!=original.value:raise h.InputError('Replayed Capex differs from reviewed pilot')
                row['original_pilot_preserved']=True
            else:annual=replace(annual,inputs=tuple(value if v.field is h.Field.CAPEX else v for v in annual.inputs))
            aa.append(annual);receipt=evidence.instance
            rows.append(dict(row,issuer=name,identity=dict(cik=annual.period.cik,accession=annual.period.accession,
                form=annual.period.form,annual_start=str(annual.period.annual_start),annual_end=str(annual.period.annual_end)),
                receipt=dict(url=receipt.artifact.url,sha256=receipt.artifact.sha256,representation=receipt.artifact.representation,
                    digest_type=receipt.artifact.digest_type,retrieved_at_utc=receipt.retrieved_at_utc,http_status=receipt.http_status)))
        out[name]=replace(history,history_id='retained-capex:'+name,annuals=tuple(aa))
    ledger=dict(schema='retained-approved-capex-v1',selected_periods=len(rows),issuer_count=len(out),outcomes=dict(Counter(v['status'] for v in rows)),
        curated_versions=dict(Counter(v['policy'].get('version') for v in rows if v['status']=='CURATED')),
        summary={name:dict(periods=len(hist.annuals),outcomes=dict(Counter(v['status'] for v in rows if v['issuer']==name))) for name,hist in out.items()},
        history_exceptions=baseline['history_exceptions'],limitations=list(LIMITATIONS),rows=rows)
    return ledger,out


def validate_history(payload):
    history=h.deserialize(payload);store=artifacts()
    pilots={a.period:a for name in ('MSFT','AAPL','GOOGL') for a in pilot.load_history(name).annuals}
    for a in history.annuals:
        actual=next(v for v in a.inputs if v.field is h.Field.CAPEX)
        expected=(next(v for v in pilots[a.period].inputs if v.field is h.Field.CAPEX) if a.period in pilots else package(cfo.prepare(a),store)[0])
        if actual!=expected:raise h.InputError('Capex policy/value/sign/precision/provenance differs from replay')
    return history
