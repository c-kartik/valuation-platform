"""Exact reviewed evidence generations, isolated from legacy Capex attestations."""
from dataclasses import dataclass, fields, replace
from datetime import date
from decimal import Decimal
import hashlib
import json

from . import historical_inputs as h, capex_evidence_repair as prior
from . import lly_capex_refresh_review as review, retained_capex as capex
from . import retained_components as inspection, retained_cfo_preparation as cfo
from .cash_flow_inputs import Receipt
from .nwc import Artifact
from ..normalization.models import AmbiguousHistoricalMetric, NormalizedHistoricalValue

SCHEMA = 'historical-input-preparation-v2'
REFRESH_VERSION = 'lly-capex-preparation-refresh-v1'
REVIEW_SHA = '060bdfe1cd38c764ad76b9518db18b47100f6bf203f3836343276ca6e750cf0d'
REGISTRY_SHA = '34684ae93ed81bfb454ad43cf9ff3510c8dbc9714a09b11a27e547a36bdd5606'
MARKER = 'preparation_capex_refresh:'
LEDGER = 'docs/refreshed-capex-ledger.json'
REQUIRED = ('CURRENT_CASH_AMOUNT','AUTHORITATIVE_ANNUAL_PERIOD','EXACT_OPERAND_OCCURRENCES',
    'CONSOLIDATED_INVESTING_SCOPE','PPE_PHYSICAL_ASSET_SCOPE','ACQUISITION_IPRD_SEPARATION',
    'NO_NONCASH_LEASE_PROCEEDS_INCENTIVE_OR_INTEREST_ADJUSTMENT')
HISTORICAL_STATUS = 'ORIGINAL_BODY_UNAVAILABLE_BYTE_EQUIVALENCE_UNESTABLISHED'
BASIS = 'INDEPENDENTLY_REVIEWED_REFRESH_NOT_ORIGINAL_DIGEST_VERIFICATION'


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def registered_review():
    raw=(review.ROOT/review.RECORD).read_bytes()
    if review.sha(raw)!=REVIEW_SHA or review.sha((review.ROOT/review.REGISTRY).read_bytes())!=REGISTRY_SHA:
        raise h.InputError('Unregistered refresh review or changed original financial registry')
    return json.loads(raw)


def matching(period):
    record=registered_review()
    row=next((r for r in record['entries'] if (r['identity']['cik'],r['identity']['accession'],
        r['identity']['annual_start'],r['identity']['annual_end'],r['identity']['form'])==
        (period.cik,period.accession,str(period.annual_start),str(period.annual_end),period.form)),None)
    entry=next((e for e in capex.curated.CAPEX_SCOPE_EQUIVALENCE_POLICY.entries if
        (e.company_cik,e.accession_number,e.annual_start,e.annual_end,e.form)==
        (period.cik,period.accession,period.annual_start,period.annual_end,period.form)),None)
    if row is None or entry is None or entry.company_cik!=59478:
        raise h.InputError('Unregistered exact LLY refresh entry/period')
    if (row['content_review']!='SUPPORTED_EXISTING_FINANCIAL_SCOPE' or row['checks']['contradicted']
            or tuple(row['checks']['supported'])!=REQUIRED or len(row['reports'])!=3):
        raise h.InputError('Required independent refresh assertions missing or contradicted')
    return row,entry


@dataclass(frozen=True)
class RefreshedArtifact:
    historical_sha256: str
    historical_digest_type: str
    historical_status: str
    refreshed_receipt: Receipt
    receipt_document_sha256: str
    receipt_path: str
    receipt_locator: str
    report_json: str
    supported_requirements: tuple[str,...]

    def __post_init__(self):
        if (type(self.refreshed_receipt) is not Receipt or self.historical_status!=HISTORICAL_STATUS
                or self.historical_digest_type!='sha256_sec_response_body_bytes'
                or self.historical_sha256==self.refreshed_receipt.artifact.sha256):
            raise h.InputError('Separate unavailable-original and refreshed receipt required')
        h._strings(self.supported_requirements)


@dataclass(frozen=True)
class RefreshAudit:
    refresh_id: str
    refresh_version: str
    period: h.Period
    input_id: str
    financial_policy_id: str
    financial_policy_version: str
    original_entry_json: str
    original_entry_sha256: str
    review_path: str
    review_version: str
    review_sha256: str
    review_entry_json: str
    supported_requirements: tuple[str,...]
    artifacts: tuple[RefreshedArtifact,...]
    original_byte_equivalence: str = 'UNPROVED'
    acceptance_basis: str = BASIS

    def __post_init__(self):
        if type(self.period) is not h.Period:raise h.InputError('Exact refresh period required')
        row,entry=matching(self.period)
        if (self.refresh_id!=REFRESH_VERSION+':'+entry.accession_number or self.refresh_version!=REFRESH_VERSION
                or self.input_id!='refreshed-capex:'+entry.accession_number
                or (self.financial_policy_id,self.financial_policy_version)!=('capex_scope_equivalence','1')
                or self.original_entry_json!=entry.reviewed_entry_json
                or self.original_entry_sha256!=row['financial_policy']['entry_sha256']
                or (self.review_path,self.review_version,self.review_sha256)!=(review.RECORD,review.VERSION,REVIEW_SHA)
                or self.review_entry_json!=canonical(row) or self.supported_requirements!=REQUIRED
                or self.original_byte_equivalence!='UNPROVED' or self.acceptance_basis!=BASIS):
            raise h.InputError('Refresh acceptance identity, requirements or original history differs')
        h._typed(self.artifacts,RefreshedArtifact)
        if len(self.artifacts)!=3:raise h.InputError('Exactly three reviewed refreshed reports required')
        for a,r in zip(self.artifacts,row['reports']):
            receipt=a.refreshed_receipt;actual=receipt.artifact
            if (actual.url!=r['source_url'] or actual.accession!=entry.accession_number
                    or actual.sha256!=r['refreshed_sha256'] or len(actual.body)!=r['byte_length']
                    or (receipt.retrieved_at_utc,receipt.http_status)!=(r['retrieved_at_utc'],r['http_status'])
                    or receipt.retrieval_mode!='new_authorized_fixed_capex_binding_repair'
                    or a.historical_sha256!=r['historical_sha256']
                    or a.historical_digest_type!=r['historical_digest_type']
                    or a.receipt_document_sha256!=r['receipt_document_sha256']
                    or (a.receipt_path,a.receipt_locator)!=(r['receipt_path'],r['receipt_locator'])
                    or a.report_json!=canonical(r['report']) or a.supported_requirements!=tuple(r['supports'])):
                raise h.InputError('Exact reviewed old/new artifact, receipt, role or requirement binding differs')


def audits():
    record=registered_review()
    review.validate(record)  # Same independent report/DEI/operand review, no requests.
    payload=json.loads((review.ROOT/prior.OUTPUT).read_text())
    out=[]
    for row in record['entries']:
        i=row['identity'];period=h.Period(i['cik'],i['accession'],date.fromisoformat(i['annual_start']),date.fromisoformat(i['annual_end']),i['form'])
        _,entry=matching(period);reports=[]
        for r in row['reports']:
            a=payload['artifacts'][int(r['receipt_locator'].rsplit('/',1)[1])]
            receipt=Receipt(Artifact(a['source_url'],a['accession'],a['representation'],a['digest_type'],a['sha256'],prior.body(a)),
                a['byte_length'],a['retrieved_at_utc'],a['http_status'],a['retrieval_mode'])
            reports.append(RefreshedArtifact(r['historical_sha256'],r['historical_digest_type'],r['historical_status'],receipt,
                r['receipt_document_sha256'],r['receipt_path'],r['receipt_locator'],canonical(r['report']),tuple(r['supports'])))
        out.append(RefreshAudit(REFRESH_VERSION+':'+entry.accession_number,REFRESH_VERSION,period,
            'refreshed-capex:'+entry.accession_number,'capex_scope_equivalence','1',entry.reviewed_entry_json,
            row['financial_policy']['entry_sha256'],review.RECORD,review.VERSION,REVIEW_SHA,canonical(row),REQUIRED,tuple(reports)))
    return tuple(out)


def package(evidence,audit):
    """Reviewed exact-entry preparation path, not legacy digest attestation."""
    if type(audit) is not RefreshAudit or evidence.period!=audit.period:
        raise h.InputError('Exact reviewed refresh and preparation identity required')
    audit.__post_init__();row,entry=matching(audit.period)
    if evidence.instance is None or evidence.instance.artifact.url!=entry.instance_url or evidence.instance.artifact.sha256!=entry.instance_digest:
        raise h.InputError('Original approved instance remains mandatory; no instance refresh')
    actual=inspection.prepare(evidence.period,(evidence.instance,),
        (inspection.ArtifactBinding(entry.instance_url,entry.instance_digest,'instance'),))
    if (actual.facts!=evidence.facts or actual.contexts!=evidence.contexts or actual.namespaces!=evidence.namespaces):
        raise h.InputError('Competing or malformed evidence differs from the verified original instance')
    direct,_=capex.direct_result(evidence)
    if isinstance(direct,AmbiguousHistoricalMetric) or (isinstance(direct,NormalizedHistoricalValue) and Decimal(str(direct.value))!=entry.expected_value):
        raise h.InputError('Conflicting eligible financial evidence cannot be replaced by a refresh')
    result=capex.inspect(evidence,entry.concept)
    if not result.candidates or {c.value for c in result.candidates}!={entry.expected_value}:
        raise h.InputError('Reviewed approved operand absent or conflicting')
    expected_precision=row['observations']['operand_occurrences'][0]['decimals']
    if any(c.precision!=expected_precision for c in result.candidates):raise h.InputError('Reviewed operand precision differs')
    if isinstance(direct,NormalizedHistoricalValue):raise h.InputError('Existing direct result must remain on its unchanged direct path')
    sources=tuple(s for c in result.candidates for s in c.evidence_references)
    support=capex.supplementary(evidence)
    # Support remains raw, not additive and not extra approved Capex operands.
    support=tuple(v for v in support if (v.sources[0].namespace,v.sources[0].concept)!=(entry.namespace,entry.concept))
    return h.InputValue(audit.input_id,h.Field.CAPEX,evidence.period,None,-entry.expected_value,'USD',1,-1,expected_precision,
        'approved_reported_cash_capex_outflow_refreshed_evidence',h.Origin.REPORTED,h.Quality.SUPPORTED,entry.economic_scope,
        h.Scope.RESTRICTED,h.Completeness.PARTIAL,h.Review.ACCEPTED,sources,None,None,support,
        'Exact original financial approval and independently reviewed refreshed reports; not verification of historical report digests.',
        (MARKER+audit.refresh_id,'original_report_bytes_unavailable','original_byte_equivalence_unproved',BASIS,'no_aggregation'),
        capex.LIMITATIONS+tuple(row['checks']['unverified']),None,(entry.concept,))


@dataclass(frozen=True)
class RefreshedHistory:
    bundle: h.HistoryBundle
    refresh_audits: tuple[RefreshAudit,...]

    def __post_init__(self):
        if type(self.bundle) is not h.HistoryBundle:raise h.InputError('Original immutable history model required')
        review.validate(registered_review())
        h._typed(self.refresh_audits,RefreshAudit)
        if not self.refresh_audits or len({a.refresh_id for a in self.refresh_audits})!=len(self.refresh_audits):
            raise h.InputError('Nonempty unique exact refresh audits required')
        used=[]
        for annual in self.bundle.annuals:
            for value in annual.inputs:
                def no_nested(v):
                    for alt in v.alternatives:
                        if any(f.startswith(MARKER) for f in alt.flags):raise h.InputError('Refresh provenance belongs to the selected input only')
                        no_nested(alt)
                no_nested(value)
                markers=[f for f in value.flags if f.startswith(MARKER)]
                if not markers:continue
                candidates=[a for a in self.refresh_audits if MARKER+a.refresh_id in markers]
                if len(markers)!=1 or len(candidates)!=1:raise h.InputError('Missing or ambiguous typed refresh provenance')
                a=candidates[0]
                if value!=package(cfo.prepare(annual),a):raise h.InputError('Refreshed value/provenance differs from exact independent replay')
                used.append(a.refresh_id)
        if tuple(used)!=tuple(a.refresh_id for a in self.refresh_audits):raise h.InputError('Orphaned, duplicated or reordered refresh audit')


_EXTRA={c.__name__:c for c in (RefreshedArtifact,RefreshAudit,RefreshedHistory)}

def _encode(value,bodies=None):
    if type(value) is bytes and bodies is not None:
        digest=review.sha(value);bodies.setdefault(digest,h._encode(value))
        return dict(body_reference=digest)
    types=(*_EXTRA.values(),*h._TYPES.values()) if bodies is not None else tuple(_EXTRA.values())
    if type(value) in types:
        return dict(type=type(value).__name__,fields={f.name:_encode(getattr(value,f.name),bodies) for f in fields(value)})
    if type(value) is tuple:return [_encode(v,bodies) for v in value]
    return h._encode(value)


def _decode(value,bodies,used):
    if type(value) is list:return tuple(_decode(v,bodies,used) for v in value)
    if type(value) is dict and set(value)=={'body_reference'}:
        digest=value['body_reference']
        if digest not in bodies:raise h.InputError('Missing serialized original body')
        used.add(digest);return bodies[digest]
    types={**h._TYPES,**_EXTRA}
    if type(value) is dict and value.get('type') in types:
        cls=types[value['type']]
        if (set(value)!={'type','fields'} or type(value['fields']) is not dict
                or set(value['fields'])!={f.name for f in fields(cls)}):
            raise h.InputError('Exact refresh schema fields required')
        return cls(**{k:_decode(v,bodies,used) for k,v in value['fields'].items()})
    return h._decode(value)


def serialize(history):
    if type(history) is h.HistoryBundle:return h.serialize(history)  # Original bytes/version.
    if type(history) is not RefreshedHistory:raise h.InputError('Typed refresh history required')
    history.__post_init__()
    bodies={};encoded=_encode(history,bodies)
    return canonical(dict(schema=SCHEMA,history=encoded,original_bodies=bodies))


def deserialize(payload):
    try:
        def unique(pairs):
            d={}
            for k,v in pairs:
                if k in d:raise h.InputError('Duplicate serialized key')
                d[k]=v
            return d
        doc=json.loads(payload,object_pairs_hook=unique)
        if type(doc) is not dict:raise h.InputError('Closed preparation envelope required')
        if doc.get('schema')==h.SCHEMA:return h.deserialize(payload)
        if set(doc)!={'schema','history','original_bodies'} or doc['schema']!=SCHEMA:raise h.InputError('Unsupported refresh serialization version')
        if type(doc['original_bodies']) is not dict:raise h.InputError('Closed original-body table required')
        bodies={};used=set()
        for digest,encoded in doc['original_bodies'].items():
            raw=h._decode(encoded)
            if type(raw) is not bytes or review.sha(raw)!=digest:raise h.InputError('Tampered serialized original bytes')
            bodies[digest]=raw
        result=_decode(doc['history'],bodies,used)
        if used!=set(bodies):raise h.InputError('Unused or missing serialized original bodies')
        if type(result) is not RefreshedHistory:raise h.InputError('Typed refresh history required')
        return result
    except (ValueError,KeyError,TypeError) as exc:raise h.InputError('Invalid refreshed preparation serialization') from exc


def validate_history(payload):
    result=deserialize(payload)
    if type(result) is h.HistoryBundle:return prior.validate_history(payload)
    return result  # Typed wrapper replays each refreshed value at construction.


def build():
    ledger,histories=prior.build();accepted=audits();rows={r['identity']['accession']:r for r in ledger['rows'] if r['issuer']=='LLY'}
    history=histories['LLY'];annuals=[]
    for annual in history.annuals:
        audit=next(a for a in accepted if a.period==annual.period)
        evidence=cfo.prepare(annual);value=package(evidence,audit)
        annuals.append(replace(annual,bundle_id='retained-refreshed-capex:'+annual.period.accession,version=2,
            inputs=tuple(value if v.field is h.Field.CAPEX else v for v in annual.inputs)))
        old_gaps=rows[annual.period.accession]['approved_entry_evidence_gaps']
        _,entry=matching(annual.period);result=capex.inspect(evidence,entry.concept)
        diagnostic=capex.support(evidence)
        for item in diagnostic:
            if (item['namespace'],item['concept'])==(entry.namespace,entry.concept) and not item['dimensions'] and not item['nil']:
                item['acceptance']='ACCEPTED_EXACT_REVIEWED_REFRESH_OPERAND_NOT_BLANKET_SCOPE'
        rows[annual.period.accession].update(status='CURATED_REFRESH',value_usd=str(value.value),approved_entry_evidence_gaps=[],
            unresolved_requirements=list(value.unresolved_requirements),preparation_refresh=_encode(audit),
            original_legacy_evidence_gaps=old_gaps,support=diagnostic,
            candidates=[dict(concept=c.concept,namespace=c.namespace,raw_value=str(c.value),sign=-1,scale=1,precision=c.precision,
                occurrences=[dict(ordinal=o.ordinal,context_id=o.context_id,unit_id=o.unit_id,raw_value=o.raw_value,precision=o.decimals) for o in c.occurrences]) for c in result.candidates],
            policy=dict(original_financial_policy_id=audit.financial_policy_id,original_financial_policy_version='1',
                        acceptance_basis=BASIS,legacy_attestation='NOT_SATISFIED_OR_CLAIMED'))
    refreshed=RefreshedHistory(replace(history,history_id='retained-refreshed-capex:LLY',version=2,annuals=tuple(annuals)),accepted)
    histories['LLY']=refreshed
    from collections import Counter
    ledger.update(schema='retained-refreshed-capex-v1',outcomes=dict(Counter(r['status'] for r in ledger['rows'])),
        refresh_version=REFRESH_VERSION,refresh_review_sha256=REVIEW_SHA,
        summary={name:dict(periods=len((v.bundle if type(v) is RefreshedHistory else v).annuals),
                 outcomes=dict(Counter(r['status'] for r in ledger['rows'] if r['issuer']==name))) for name,v in histories.items()})
    return ledger,histories
