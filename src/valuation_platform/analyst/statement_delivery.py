"""Exact retained primary evidence for preparation, never financial acceptance.

This catalog preserves historical bodies and receipts. Discovery binds a primary
filename to retained metadata, not a plausible instance stem or a later filing.
"""
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
import base64
import gzip
import hashlib
import json
import re

from . import historical_inputs as h, preparation_validation as validation
from .cash_flow_inputs import Receipt

ROOT = validation.a.ROOT
ACQUISITION = 'docs/evidence/preparation-statement-acquisition.json'


def canonical(v): return json.dumps(v, sort_keys=True, separators=(',', ':'))


def records(root=ROOT):
    """Raw bodies only. Invalid/missing receipts remain diagnostics, not sources."""
    out = []; errors = []
    for path in sorted((root/'docs/evidence').glob('*.json')) + sorted((root/'tests/fixtures').glob('capex*json')):
        doc = json.loads(path.read_bytes())
        entries = doc if isinstance(doc, list) else doc.get('artifacts', [])
        if not isinstance(entries, list): continue
        for index, entry in enumerate(entries):
            url = entry.get('source_url', '')
            encoded = entry.get('response_body_gzip_base64') or entry.get('body_gzip_base64')
            if not encoded: continue
            if entry.get('representation') != 'sec_response_body_bytes' or entry.get('digest_type') != 'sha256_sec_response_body_bytes':
                continue  # Other explicitly typed historical representations are not relabeled.
            body = gzip.decompress(base64.b64decode(''.join(encoded) if isinstance(encoded,list) else encoded, validate=True))
            if hashlib.sha256(body).hexdigest() != entry.get('sha256'):
                errors.append(dict(path=str(path.relative_to(root)), index=index, url=url, reason='BODY_DIGEST_MISMATCH')); continue
            if entry.get('byte_length') is not None and entry['byte_length']!=len(body):
                errors.append(dict(path=str(path.relative_to(root)),index=index,url=url,reason='BODY_LENGTH_MISMATCH'));continue
            stamp = entry.get('retrieved_at_utc') or entry.get('original_retrieval_at_utc') or entry.get('retrieved_at')
            status = entry.get('http_status') or entry.get('original_http_status')
            if not stamp or status != 200:
                errors.append(dict(path=str(path.relative_to(root)), index=index, url=url, reason='RECEIPT_INCOMPLETE')); continue
            try:
                if datetime.fromisoformat(stamp).utcoffset().total_seconds() != 0: raise ValueError('UTC required')
            except (ValueError, AttributeError):
                errors.append(dict(path=str(path.relative_to(root)), index=index, url=url, reason='RECEIPT_UTC_INVALID')); continue
            out.append(dict(path=str(path.relative_to(root)), locator='/artifacts/'+str(index),
                url=url, sha256=entry['sha256'], body=body, retrieved_at_utc=stamp, http_status=status,
                retrieval_mode=entry.get('retrieval_mode') or 'retained_actual_receipt'))
    return out, errors


def primary_metadata(catalog):
    refs = validation.primary_references()
    # Submission response fields provide additional authoritative joins; no name inference.
    for record in catalog:
        if not record['url'].startswith('https://data.sec.gov/submissions/'): continue
        doc = json.loads(record['body'])
        match=re.search(r'CIK(\d+)',record['url'])
        cik=int(doc['cik']) if doc.get('cik') is not None else int(match[1]) if match else None
        data = doc.get('filings', {}).get('recent', doc)
        accs = data.get('accessionNumber', [])
        names = data.get('primaryDocument', [])
        forms = data.get('form', [])
        for index, (acc, name, form) in enumerate(zip(accs, names, forms)):
            if form == '10-K' and name:
                refs.setdefault(acc, []).append(dict(filename=name, path=record['path'],
                    locator=record['locator']+'/response/filings/row/'+str(index),
                    metadata_body_sha256=record['sha256'], authority='OFFICIAL_SUBMISSION_RESPONSE',cik=cik))
    return refs


def scope(root=ROOT):
    catalog, errors = records(root)
    refs = primary_metadata(catalog)
    rows = json.loads((root/'docs/repaired-income-ledger.json').read_text())['rows']
    result = []
    for row in rows:
        p = row['identity']; candidates = [x for x in refs.get(p['accession'], []) if x.get('cik',p['cik'])==p['cik']]
        official = [x for x in candidates if x.get('authority')=='OFFICIAL_SUBMISSION_RESPONSE']
        eligible = official or candidates
        names = {x['filename'] for x in eligible}
        valid = len(names)==1 and not any('/' in n or '\\' in n for n in names)
        url = ('https://www.sec.gov/Archives/edgar/data/'+str(p['cik'])+'/'+p['accession'].replace('-','')+'/'+next(iter(names))) if valid else None
        bodies = [r for r in catalog if r['url']==url]
        distinct = {r['sha256'] for r in bodies}
        status = 'RETAINED' if len(distinct)==1 else 'BODY_CONFLICT' if len(distinct)>1 else 'MISSING_PRIMARY' if url else 'METADATA_UNRESOLVED'
        result.append(dict(ticker=row['issuer'], identity=p, url=url, metadata=candidates,
            metadata_selection='Exact official submission join' if official else 'Unique retained reviewed filing metadata',
            status=status))
    if len(result)!=199 or len({r['identity']['accession'] for r in result})!=199:
        raise h.InputError('Exact 199 selected identity scope required')
    return result, catalog, errors


def receipt(record, period):
    return Receipt(h.Artifact(record['url'], period.accession, 'sec_response_body_bytes',
        'sha256_sec_response_body_bytes', record['sha256'], record['body']), len(record['body']),
        record['retrieved_at_utc'], record['http_status'], record['retrieval_mode'])


def verify_primary(record, identity):
    """Independent primary DEI annual context; no calendar-date reconstruction."""
    text = record['body'].decode('utf-8')
    if record.get('url') and not re.fullmatch(r'https://www\.sec\.gov/Archives/edgar/data/'+str(identity['cik'])+'/'+re.escape(identity['accession'].replace('-',''))+r'/[^/?#]+',record['url']):
        raise h.InputError('Primary URL exact accession/CIK differs')
    if record.get('sha256') and hashlib.sha256(record['body']).hexdigest()!=record['sha256']:raise h.InputError('Primary original-body digest differs')
    namespaces=dict(re.findall(r'xmlns:([^\s=]+)=["\']([^"\']+)',text))
    class DEI(HTMLParser):
        def __init__(self):super().__init__();self.stack=[];self.values=[]
        def handle_starttag(self,tag,attrs):
            if tag=='ix:nonnumeric':self.stack.append((dict(attrs),[]))
        def handle_data(self,data):
            for _, parts in self.stack:parts.append(data)
        def handle_endtag(self,tag):
            if tag=='ix:nonnumeric' and self.stack:
                attrs,parts=self.stack.pop();self.values.append((attrs,' '.join(''.join(parts).split())))
    parser=DEI();parser.feed(text);parser.close()
    def dei(name):return [(a,v) for a,v in parser.values if a.get('name')=='dei:'+name]
    if {int(v) for _,v in dei('EntityCentralIndexKey')}!={identity['cik']} or {v for _,v in dei('DocumentType')}!={'10-K'}:
        raise h.InputError('Primary CIK/form not independently established')
    ends = dei('DocumentPeriodEndDate')
    def date_value(attrs,value):
        if not attrs.get('format'):return value
        prefix=attrs['format'].split(':')[0]
        if not namespaces.get(prefix,'').startswith(('http://www.xbrl.org/inlineXBRL/transformation/','http://www.sec.gov/inlineXBRL/transformation/')):
            raise h.InputError('DEI transformation namespace unverified')
        fmt=attrs['format'].split(':')[-1]
        if fmt in ('date-monthname-day-year-en','datemonthdayyearen'):
            for pattern in ('%B %d, %Y','%B %d %Y','%b %d, %Y','%b %d %Y'):
                try:return datetime.strptime(value,pattern).date().isoformat()
                except ValueError:continue
        if fmt=='date-month-day-year':
            for pattern in ('%m/%d/%Y','%m-%d-%Y'):
                try:return datetime.strptime(value,pattern).date().isoformat()
                except ValueError:continue
        raise h.InputError('Unsupported explicit DEI date transformation')
    if not ends or {date_value(a,v) for a,v in ends}!={identity['annual_end']}: raise h.InputError('Primary annual end differs')
    verified = False
    for attrs, _ in ends:
        ref=attrs.get('contextref')
        if not ref: continue
        context = re.search(r'<xbrli:context\b[^>]*\bid=["\']'+re.escape(ref)+r'["\'].*?</xbrli:context>', text,re.I|re.S)
        if not context or 'explicitMember' in context[0] or 'typedMember' in context[0]: continue
        start = re.search(r'<xbrli:startDate>([^<]+)',context[0],re.I)
        end = re.search(r'<xbrli:endDate>([^<]+)',context[0],re.I)
        if start and end and (start[1],end[1])==(identity['annual_start'],identity['annual_end']): verified=True
    if not verified: raise h.InputError('Exact nondimensional primary annual DEI context unavailable')
    return True


class Tables(HTMLParser):
    """Preserve displayed rows and inline bindings; never read expected assembly values."""
    def __init__(self):
        super().__init__(); self.tables=[]; self.depth=0; self.table=None; self.row=None; self.cell=None; self.fact=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='table':
            if self.depth==0: self.table=[]
            self.depth+=1
        if self.depth!=1:return
        if tag=='tr':self.row=[]
        if tag in ('td','th'):self.cell=dict(text=[],facts=[],attrs=attrs)
        if tag=='ix:nonfraction' and self.cell is not None:
            self.fact=dict(attrs=attrs,text=[]);self.cell['facts'].append(self.fact)
    def handle_data(self,data):
        if self.cell is not None:
            self.cell['text'].append(data)
            if self.fact is not None:self.fact['text'].append(data)
    def handle_endtag(self,tag):
        if tag=='ix:nonfraction':self.fact=None
        if self.depth==1 and tag in ('td','th') and self.cell is not None:
            self.cell['text']=' '.join(''.join(self.cell['text']).split())
            for fact in self.cell['facts']:fact['text']=''.join(fact['text']).strip()
            if self.row is not None:self.row.append(self.cell)
            self.cell=None
        if self.depth==1 and tag=='tr' and self.row is not None:
            self.table.append(self.row);self.row=None
        if tag=='table':
            self.depth-=1
            if self.depth==0:self.tables.append(self.table);self.table=None


def parse(record):
    parser=Tables();parser.feed(record['body'].decode('utf-8'));parser.close();return parser.tables


def primary_bindings(record):
    """Primary's own namespaces, contexts and units, independently of instance IDs."""
    text=record['body'].decode('utf-8')
    namespaces=dict(re.findall(r'xmlns:([^\s=]+)=["\']([^"\']+)',text))
    contexts={m[0]:m[1] for m in re.findall(r'<xbrli:context\b[^>]*\bid=["\']([^"\']+)["\']([^>]*>.*?</xbrli:context>)',text,re.I|re.S)}
    units={m[0]:m[1] for m in re.findall(r'<xbrli:unit\b[^>]*\bid=["\']([^"\']+)["\']([^>]*>.*?</xbrli:unit>)',text,re.I|re.S)}
    return namespaces,contexts,units


def check_primary_binding(bindings, attrs, namespace, context, unit):
    namespaces,contexts,units=bindings
    name=attrs.get('name','');prefix=name.split(':')[0]
    if namespaces.get(prefix)!=namespace:raise h.InputError('Primary namespace differs')
    raw=contexts.get(attrs.get('contextref'))
    if raw is None or 'explicitMember' in raw or 'typedMember' in raw:raise h.InputError('Primary context absent/dimensioned')
    identifier=re.search(r'<xbrli:identifier\b[^>]*scheme=["\']http://www.sec.gov/CIK["\'][^>]*>([^<]+)',raw,re.I)
    if not identifier or int(identifier[1])!=int(context.entity_identifier):raise h.InputError('Primary entity differs')
    def date(tag):
        m=re.search(r'<xbrli:'+tag+r'>([^<]+)',raw,re.I);return None if not m else m[1]
    if (date('startDate'),date('endDate') or date('instant'))!=(None if context.start is None else str(context.start),str(context.end)):
        raise h.InputError('Primary annual/instant context dates differ')
    raw=units.get(attrs.get('unitref'))
    if raw is None or '<xbrli:divide' in raw:raise h.InputError('Primary unit absent/divided')
    measures=re.findall(r'<xbrli:measure>([^<]+)',raw,re.I)
    expected=[(q.namespace,q.local_name) for q in unit.numerator_measures]
    actual=[(namespaces.get(q.split(':')[0]),q.split(':')[-1]) for q in measures]
    if actual!=expected or unit.denominator_measures:raise h.InputError('Primary unit/currency differs')
