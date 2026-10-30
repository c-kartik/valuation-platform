"""Versioned profile integrity, immutable sources and reviewable refresh differences."""
import hashlib
import json
from datetime import date
from pathlib import Path
from .rules import number

STATES = {'AVAILABLE_ESTIMATE','CONFIGURED_CONVENTION','MISSING_EVIDENCE','INCOMPATIBLE_DEFINITION',
          'UNSUPPORTED_PREPARATION','STALE','USER_OVERRIDE'}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read_json(path):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result: raise ValueError('Duplicate JSON key: '+key)
            result[key]=value
        return result
    return json.loads(Path(path).read_text(),object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def exclusive_json(path, value):
    """CLI outputs are outside the repository, with exclusive creation."""
    path=Path(path).absolute()
    root=Path(__file__).resolve().parents[3]
    if path.resolve().is_relative_to(root): raise ValueError('Choose a NEW output outside the repository')
    with path.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')


def read_sources(directory):
    directory=Path(directory)
    sources=read_json(directory/'manifest.json')['sources']
    for source in sources:
        name=source['file']
        path=directory/name
        if Path(name).name!=name or path.is_symlink(): raise ValueError('Invalid snapshot path')
        body=path.read_bytes()
        if hashlib.sha256(body).hexdigest()!=source['sha256'] or len(body)!=source['bytes']:
            raise ValueError('Source body differs from immutable manifest: '+source['id'])
        if not source['url'].startswith('https://'): raise ValueError('HTTPS source required')
        for key in ('retrieved_at','rights','extraction_version'):
            if not source.get(key): raise ValueError('Source metadata missing: '+key)
    if len({s['id'] for s in sources})!=len(sources): raise ValueError('Duplicate source ID')
    return sources


def select_observation(observations, key, *, definition, unit, cutoff):
    """Explicit supersession, not an implicit latest-fact overwrite."""
    rows=[o for o in observations if o['key']==key and (o.get('available_at') or o.get('published_at') or '9999-12-31')[:10]<=cutoff]
    replaced={o['supersedes'] for o in rows if o.get('supersedes')}
    if any(o.get('supersedes') and o['supersedes'] not in {r['id'] for r in rows} for o in rows):
        raise ValueError('Restatement supersedes an absent observation')
    rows=[o for o in rows if o['id'] not in replaced]
    if not rows: raise LookupError('MISSING_EVIDENCE: '+key)
    if len(rows)!=1: raise ValueError('Duplicate/incompatible periods: '+key)
    row=rows[0]
    if row['definition']!=definition or row['unit']!=unit: raise TypeError('INCOMPATIBLE_DEFINITION: '+key)
    number(row['value']);date.fromisoformat(row['end']);date.fromisoformat((row.get('available_at') or row['published_at'])[:10])
    if row.get('start') and row['start']>row['end']:raise ValueError('Reversed period')
    return row


def validate_profile(profile):
    if profile.get('schema_version')!='preload-profile-v1': raise ValueError('Unsupported profile version')
    economic=profile['economic']
    if digest(economic)!=profile['economic_hash']:raise ValueError('Economic-content hash mismatch')
    fields=economic['fields']
    if len(fields)!=38:raise ValueError('Expected 37 Gordon fields plus separate exit field')
    from valuation_platform.valuation.case_inputs import ANNUAL_RATES
    expected={f'forecast_years[{i}].{key}' for i in range(5) for key in ANNUAL_RATES}
    expected|={'wacc','terminal_growth','exit_ev_ebit_multiple'}
    expected|={'terminal.'+key for key in economic['case_template']['terminal']}
    if set(fields)!=expected:raise ValueError('Profile field paths mismatch')
    source_ids={s['id'] for s in economic['sources']}
    for path,field in fields.items():
        if field['status'] not in STATES or field['unit'] not in ('fraction','multiple'):
            raise ValueError('Invalid field state/unit: '+path)
        if field['value'] is not None:number(field['value'])
        elif field['status'] in {'AVAILABLE_ESTIMATE','CONFIGURED_CONVENTION','USER_OVERRIDE'}:
            raise ValueError('Available field has no value: '+path)
        if field['status'] in {'MISSING_EVIDENCE','INCOMPATIBLE_DEFINITION','UNSUPPORTED_PREPARATION'} and field['value'] is not None:
            raise ValueError('Unavailable field has a numerical value: '+path)
        if economic['scenarios']['Base'].get(path)!=field['value']:raise ValueError('Base scenario differs from generated field: '+path)
        if not field['rule'] or not field['limitation'] or not field['classification'] or not field['basis']:
            raise ValueError('Incomplete provenance: '+path)
        if any(s not in source_ids for s in [*field['sources'],*field.get('context_sources',[])]):raise ValueError('Unknown source reference')
    return profile


def refresh_diff(previous, candidate, previous_result=None, candidate_result=None):
    validate_profile(previous);validate_profile(candidate)
    a,b=previous['economic'],candidate['economic']
    def changes(old,new):return {k:{'previous':old.get(k),'candidate':new.get(k)} for k in sorted(set(old)|set(new)) if old.get(k)!=new.get(k)}
    return {'schema_version':'preload-refresh-diff-v1','previous_hash':previous['economic_hash'],'candidate_hash':candidate['economic_hash'],
            'source_changes':changes({s['id']:s for s in a['sources']},{s['id']:s for s in b['sources']}),
            'filing_restatement_changes':changes({o['id']:o for o in a['observations']},{o['id']:o for o in b['observations']}),
            'policy_changes':changes(a['policy'],b['policy']), 'configuration_changes':changes(a['configuration'],b['configuration']),
            'configuration_rationale_changes':changes(a['configuration_provenance'],b['configuration_provenance']),
            'field_preparation_changes':changes({k:{m:n for m,n in v.items() if m not in ('value','status')} for k,v in a['fields'].items()}, {k:{m:n for m,n in v.items() if m not in ('value','status')} for k,v in b['fields'].items()}),
            'forecast_changes':changes({k:v['value'] for k,v in a['fields'].items()},{k:v['value'] for k,v in b['fields'].items()}),
            'gap_changes':changes({k:v['status'] for k,v in a['fields'].items()},{k:v['status'] for k,v in b['fields'].items()}),
            'valuation_changes':None if previous_result is None or candidate_result is None else {'previous_ev':previous_result['stage_b']['enterprise_value'],'candidate_ev':candidate_result['stage_b']['enterprise_value']},
            'anchor_promotion':'NOT_PERFORMED; newer evidence is not a new approved anchor'}
