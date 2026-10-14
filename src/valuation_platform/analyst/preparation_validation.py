"""Retained evidence validation/reporting only; no policy acceptance or closure."""
from collections import Counter
from decimal import Decimal
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re

from . import historical_inputs as h, prepared_assembly as a
from .lly_capex_refresh_review import Report
from .cash_interest_annotations import _text

SPOT_ISSUERS=tuple('META COST AAPL MSFT GOOGL WMT AMZN MA CVX LLY HD VZ ORCL NVDA AVGO'.split())
SPOT_FIELDS=(h.Field.REVENUE,h.Field.EBIT,h.Field.DA,h.Field.CAPEX,h.Field.CF_WORKING_CAPITAL,
             h.Field.CASH_INVESTMENTS,h.Field.DEBT_LEASES,h.Field.SHARES)
SCALARS=frozenset((h.Field.REVENUE,h.Field.EBIT,h.Field.DA,h.Field.CAPEX,h.Field.CFO))
FIXTURES='docs/preparation-independent-fixtures.json'


class StatementTables(Report):
    """Visible primary/report cells, not numeric XBRL attributes or instance facts."""
    def handle_starttag(self,tag,attrs):
        if tag=='table' and not self.active:
            attrs=[(k,v) for k,v in attrs if k!='class']+[('class','report')]
        super().handle_starttag(tag,attrs)
        if self.cell is not None and tag=='ix:nonfraction':
            self.cell.setdefault('names',[]).append(dict(attrs).get('name',''))

    def handle_endtag(self,tag):
        names=self.cell.get('names',[]) if self.cell is not None else []
        is_cell=tag in ('td','th') and self.depth==1 and self.cell is not None
        super().handle_endtag(tag)
        if is_cell and self.row:self.row[-1]['names']=names


def statement_artifacts(root=a.ROOT):
    """Fixed committed body collections; do not probe /tmp or fetch URLs."""
    out=[]
    paths=sorted((root/'docs/evidence').glob('*.json'))+sorted((root/'tests/fixtures').glob('capex*json'))
    for path in paths:
        doc=json.loads(path.read_bytes());entries=doc if isinstance(doc,list) else doc.get('artifacts',[])
        if type(entries) is not list:continue
        for index,entry in enumerate(entries):
            url=entry.get('source_url','')
            if not re.search(r'\.html?(?:$|\?)',url,re.I):continue
            encoded=entry.get('response_body_gzip_base64') or entry.get('body_gzip_base64')
            if not encoded:continue
            if entry.get('representation')!='sec_response_body_bytes' or entry.get('digest_type')!='sha256_sec_response_body_bytes':
                raise h.InputError('Unverified statement body representation')
            body=gzip.decompress(base64.b64decode(''.join(encoded) if isinstance(encoded,list) else encoded,validate=True))
            if hashlib.sha256(body).hexdigest()!=entry.get('sha256'):raise h.InputError('Statement body digest mismatch')
            parser=StatementTables();parser.feed(body.decode());parser.close()
            out.append(dict(path=str(path.relative_to(root)),locator=f'/artifacts/{index}',url=url,
                accession=entry.get('accession') or entry.get('accession_number'),sha256=entry['sha256'],
                retrieved_at_utc=entry.get('retrieved_at_utc') or entry.get('retrieved_at') or entry.get('original_retrieval_at_utc'),
                http_status=entry.get('http_status') or entry.get('original_http_status'),
                rows=parser.rows,text=_text(body)))
    return out


def coverage(histories,spot=None):
    """Newest 3 selected ordinals are recent; remaining 2 target ordinals are older.

    Missing ordinals are deficiencies, not fabricated annual dates or continuity.
    Complete coverage is existing declared complete policy-prepared scalar totals.
    Component/role families have no approved complete-field contract here.
    """
    report=dict(schema='preparation-coverage-v1',definition='DECLARED_COMPLETE_POLICY_SCALAR_TOTAL',
        recent='newest three selected ordinal positions; target three per issuer',
        older='selected ordinal positions four/five; target two per issuer',
        phase_closure=False,financial_sufficiency='NOT_ASSESSED',fields={},issuer_slots={})
    failed={(r['ticker'],r['accession'],r['field']) for r in (spot or {}).get('rows',[]) if r['status']=='FAILED'}
    per=[]
    for ticker,prepared in sorted(histories.items()):
        binding={(b['accession'],b['input_id']):b for b in json.loads(prepared.bindings_json)}
        annuals=list(reversed(prepared.bundle.annuals))
        report['issuer_slots'][ticker]=dict(cik=prepared.bundle.cik,selected=len(annuals),
            recent_selected=min(3,len(annuals)),older_selected=max(0,len(annuals)-3),
            recent_target_missing=3-min(3,len(annuals)),older_target_missing=2-max(0,len(annuals)-3),
            exceptions=list(prepared.bundle.history_exceptions))
        errors=json.loads(prepared.diagnostics_json)
        for rank,annual in enumerate(annuals,1):
            for field in h.Field:
                values=[v for v in annual.inputs if v.field is field]
                policy=[v for v in values if binding[(v.period.accession,v.input_id)]['category']=='prepared_value' and v.value is not None
                        and v.origin not in (h.Origin.PROXY,h.Origin.OVERRIDE)]
                complete=[v for v in policy if field in SCALARS and v.completeness is h.Completeness.COMPLETE
                          and v.quality is not h.Quality.CONFLICTING and v.review is not h.Review.UNREVIEWED
                          and v.scope_status not in (h.Scope.UNKNOWN,h.Scope.MIXED)
                          and v.origin not in (h.Origin.PROXY,h.Origin.OVERRIDE)]
                invalid=any(d['accession']==annual.period.accession and d['errors'].get(field.value) for d in errors)
                conflict=any(v.quality is h.Quality.CONFLICTING for v in values)
                # Data/scope decisions, versus mechanical inventory and pending independent confirmation.
                independent_failure=(ticker,annual.period.accession,field.value) in failed
                required=invalid or conflict or independent_failure or (not policy if field in SCALARS else not complete)
                per.append(dict(ticker=ticker,accession=annual.period.accession,annual_end=str(annual.period.annual_end),
                    band='recent' if rank<=3 else 'older',field=field.value,valued=any(v.value is not None for v in values),
                    policy_prepared=bool(policy),approved_complete_total=len(complete)==1 and not independent_failure,
                    partial_support=any(v.value is not None and (v.completeness is not h.Completeness.COMPLETE or
                        binding[(v.period.accession,v.input_id)]['category']!='prepared_value') for v in values),
                    conflicting=conflict,unavailable=not any(v.value is not None for v in values),
                    required_value_unavailable=not policy if field in SCALARS else not complete,
                    manual_override=any(v.origin is h.Origin.OVERRIDE for v in values),
                    proxy=any(v.origin is h.Origin.PROXY for v in values),invalid_evidence=bool(invalid),independent_failure=independent_failure,
                    substantive_review_required=bool(required),independent_confirmation_pending=not required,
                    valued_input_count=sum(v.value is not None for v in values),
                    support_observation_count=sum(v.value is not None and binding[(v.period.accession,v.input_id)]['category']
                        in ('support_observation','component_observation') for v in values),
                    null_entry_count=sum(v.value is None for v in values),
                    origins=dict(Counter(v.origin.value for v in values))))
    flags=('valued','policy_prepared','approved_complete_total','partial_support','conflicting','unavailable',
        'required_value_unavailable','manual_override','proxy','invalid_evidence','substantive_review_required','independent_confirmation_pending')
    for field in h.Field:
        report['fields'][field.value]={}
        for band,target,threshold in (('recent',3,90),('older',2,80)):
            rows=[r for r in per if r['field']==field.value and r['band']==band];denom=len(rows);target_denom=target*len(histories)
            counts={key:sum(row[key] for row in rows) for key in flags}
            report['fields'][field.value][band]=dict(selected_denominator=denom,target_denominator=target_denom,
                missing_target_slots=target_denom-denom,counts=counts,
                approved_complete_selected_percent=str(Decimal(100)*counts['approved_complete_total']/denom) if denom else None,
                approved_complete_target_percent=str(Decimal(100)*counts['approved_complete_total']/target_denom) if target_denom else None,
                proposed_target_percent=threshold,
                complete_selected_target_met=bool(denom and counts['approved_complete_total']*100>=threshold*denom),
                complete_target_slots_target_met=bool(target_denom and counts['approved_complete_total']*100>=threshold*target_denom),
                policy_prepared_selected_target_met=bool(denom and counts['policy_prepared']*100>=threshold*denom))
    report['rows']=per
    report['totals']=dict(issuers=len(histories),selected_periods=sum(len(p.bundle.annuals) for p in histories.values()),
        target_periods=5*len(histories),selected_field_inventory=len(per),target_field_inventory=5*len(histories)*len(h.Field),
        substantive_review_required=sum(r['substantive_review_required'] for r in per),
        confirmation_pending_only=sum(r['independent_confirmation_pending'] for r in per),manual_overrides=sum(r['manual_override'] for r in per))
    return report


def primary_references(root=a.ROOT):
    paths=('docs/approved-income-integration-bindings.json','docs/evidence/income-binding-repair.json',
        'docs/evidence/selected-filing-identity-acquisition.json','docs/capex-inventory.json',
        'docs/depreciation-amortization-inventory.json','docs/analyst-operating-nwc-inventory.json')
    result={}
    def visit(node,path,locator):
        if type(node) is dict:
            accession=node.get('accession_number') or node.get('accession');name=node.get('primary_document')
            if accession and name:result.setdefault(accession,[]).append(dict(filename=name,path=path,locator=locator))
            for key,value in node.items():visit(value,path,locator+'/'+key)
        elif type(node) is list:
            for index,value in enumerate(node):visit(value,path,locator+'/'+str(index))
    for path in paths:visit(json.loads((root/path).read_text()),path,'')
    return result


def spot_checks(histories,fixtures,artifacts):
    """Check literal independently reviewed cells/paragraphs against source inputs.

    A passed observation sample is not a complete field or a financial approval.
    XML-only evidence never qualifies as independent statement confirmation.
    """
    results=[];backlog=[];primary=primary_references()
    for ticker in SPOT_ISSUERS:
        prepared=histories[ticker];annual=prepared.bundle.annuals[-1]
        acc=annual.period.accession;available=[x for x in artifacts if x['accession']==acc]
        for field in SPOT_FIELDS:
            checks=[f for f in fixtures if f['ticker']==ticker and f['accession']==acc and f['field']==field.value]
            values=[v for v in annual.inputs if v.field is field];failures=[];established=[]
            for fixture in checks:
                artifact=next((x for x in available if (x['url'],x['sha256'],x['path'],x['locator'])==
                    (fixture['url'],fixture['sha256'],fixture['path'],fixture['locator'])),None)
                if artifact is None:failures.append('Missing exact independently reviewed body binding');continue
                if fixture['evidence_kind']!='rendered_statement_or_note':failures.append('Instance replay is not independent confirmation');continue
                if fixture['annual_start']!=str(annual.period.annual_start) or fixture['annual_end']!=str(annual.period.annual_end):
                    failures.append('Fixture annual identity differs');continue
                if any(phrase not in artifact['text'] for phrase in fixture['required_text']):
                    failures.append('Reviewed date/unit/scope/class passage missing');continue
                header=fixture.get('column_period_evidence',{})
                if 'row' in header and [c['text'] for c in artifact['rows'][header['row']]]!=header['cells']:
                    failures.append('Independent fiscal-column header changed');continue
                equation=fixture.get('independent_equation')
                if equation and (sum(equation['operands_millions'])*1000000!=Decimal(fixture['expected_value']) or
                    equation['pretax_bridge_millions'][0]+equation['pretax_bridge_millions'][1]!=equation['pretax_bridge_millions'][2]):
                    failures.append('Independent approved-equation arithmetic differs');continue
                if fixture['row'] is not None:
                    row=artifact['rows'][fixture['row']]
                    cells=[c['text'] for c in row]
                    if cells!=fixture['cells']:failures.append('Independent rendered row changed');continue
                    token=''.join(cells[i] for i in fixture['value_cells']).replace('$','').replace(',','').replace(' ','')
                    displayed=Decimal('-'+token[1:-1] if token.startswith('(') and token.endswith(')') else token)*Decimal(fixture['scale'])
                    if displayed!=Decimal(fixture['displayed_value']):failures.append('Independent display/sign/scale fixture inconsistent');continue
                expected=Decimal(fixture['expected_value'])
                candidates=values if fixture['match']=='support_or_value' else [v for v in values if v.value is None]
                if fixture['match']=='conflicting_alternative':
                    def descendants(value):
                        return [value]+[entry for alternative in value.alternatives for entry in descendants(alternative)]
                    candidates=[entry for value in values if value.quality is h.Quality.CONFLICTING
                                for entry in descendants(value)]
                if fixture['match']=='required_null':
                    bindings={(b['accession'],b['input_id']):b for b in json.loads(prepared.bindings_json)}
                    match=any(v.unresolved_requirements for v in candidates) and not any(v.value is not None and
                        bindings[(acc,v.input_id)]['category']=='prepared_value' for v in values)
                else:
                    match=any(v.value==expected and v.unit==fixture['unit'] and
                        (str(v.as_of) if v.as_of is not None else None)==fixture['as_of'] and
                        v.role in fixture['roles'] and any(s.concept in fixture['concepts'] and
                            (list(s.dimensions)==fixture['dimensions'] if fixture.get('dimensions') is not None else
                             any(d.rsplit('}',1)[-1]==fixture['class_member'] for d in s.dimensions)) for s in v.sources) for v in candidates)
                if not match:failures.append('Value/date/class/unit/role/source scope differs from reviewed fixture')
                else:established.append(fixture['fixture_id'])
                if fixture.get('expected_conflict') and not any(v.quality is h.Quality.CONFLICTING for v in values):
                    failures.append('Expected unresolved conflicting candidates not retained')
                if fixture.get('required_value_unresolved'):
                    bindings={(b['accession'],b['input_id']):b for b in json.loads(prepared.bindings_json)}
                    if not any(v.value is None and v.unresolved_requirements for v in values) or any(v.value is not None and
                        bindings[(acc,v.input_id)]['category']=='prepared_value' for v in values):
                        failures.append('Scope-disqualified D&A incorrectly populates required value')
                if fixture.get('exclude_from_primitive'):
                    bindings={(b['accession'],b['input_id']):b for b in json.loads(prepared.bindings_json)}
                    if any(v.value is not None and bindings[(acc,v.input_id)]['category']=='prepared_value'
                           and any(s.concept in fixture['concepts'] for s in v.sources) for v in values):
                        failures.append('APPROVED_PRIMITIVE_SCOPE_'+fixture.get('scope_issue_type','CONTRADICTED')+': '+fixture['scope_note'])
            status='FAILED' if failures else 'CHECKED' if checks else 'NOT_VERIFIED'
            reason=None if checks else ('No retained exact-accession statement/cover/note body.' if not available else
                'Retained bodies do not independently establish this exact field/population; no expected value forced.')
            unbound=json.loads((a.ROOT/FIXTURES).read_text()).get('unbound_observations',[])
            unresolved=[f for f in unbound if (f['ticker'],f['accession'],f['field'])==(ticker,acc,field.value)]
            if not checks and available and unresolved:reason=unresolved[0]['binding_limitation']
            results.append(dict(ticker=ticker,accession=acc,annual_start=str(annual.period.annual_start),annual_end=str(annual.period.annual_end),
                field=field.value,status=status,fixture_ids=established,failures=failures,reason=reason,
                source_value_available=any(v.value is not None for v in values),source_conflicting=any(v.quality is h.Quality.CONFLICTING for v in values),
                independent_complete_field=False,unbound_statement_observations=unresolved,
                available_artifacts=[dict(url=x['url'],sha256=x['sha256'],path=x['path'],locator=x['locator']) for x in available]))
            if not checks:
                base='https://www.sec.gov/Archives/edgar/data/'+str(annual.period.cik)+'/'+acc.replace('-','')+'/'
                refs=primary.get(acc,[]);names=sorted({r['filename'] for r in refs})
                exact=base+names[0] if len(names)==1 else None
                already=any(x['url']==exact for x in available)
                backlog.append(dict(ticker=ticker,accession=acc,field=field.value,annual_start=str(annual.period.annual_start),annual_end=str(annual.period.annual_end),
                    accession_directory_url=base,required_artifact_url=exact,primary_metadata_references=refs,
                    action='RETAIN_UNPROVED_SCOPE_OR_MISSING_PASSAGE' if already else 'EXACT_PRIMARY_BODY_MISSING' if exact else 'EXACT_PRIMARY_FILENAME_BINDING_REQUIRED',
                    filename_status='EXACT_METADATA_BOUND' if exact else 'NOT_ESTABLISHED_NO_GUESSED_REPORT_NUMBER',reason=reason,
                    stopping_condition='No retrieval/research authorized; retain NOT_VERIFIED. Existing-body scope gaps are not missing disclosures or automatic acquisition requests.'))
    grouped={}
    for item in backlog:
        key=(item['ticker'],item['accession'],item['required_artifact_url'],item['action'])
        group=grouped.setdefault(key,{k:v for k,v in item.items() if k!='field'})
        group.setdefault('fields',[]).append(item['field'])
    return dict(schema='independent-preparation-spot-check-v1',rows=results,counts=dict(Counter(r['status'] for r in results)),
                field_counts={f.value:dict(Counter(r['status'] for r in results if r['field']==f.value)) for f in SPOT_FIELDS},
                backlog=backlog,artifact_backlog=list(grouped.values()))
