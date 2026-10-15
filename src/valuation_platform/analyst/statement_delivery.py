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
BINDING_REPAIR = 'docs/evidence/preparation-statement-binding-repair.json'


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
    for record in catalog:
        match=re.fullmatch(r'https://www.sec.gov/Archives/edgar/data/(\d+)/(\d+)/([\d-]+)-index.html',record['url'])
        if not match:continue
        for entry in index_documents(record['body'],int(match[1]),match[3]):
            if entry['type']=='10-K' and entry['url'].endswith(('.htm','.html')):
                refs.setdefault(match[3],[]).append(dict(filename=entry['url'].split('/')[-1],path=record['path'],
                    locator=record['locator']+'/index/row/'+str(entry['row']),metadata_body_sha256=record['sha256'],
                    authority='OFFICIAL_ACCESSION_INDEX',cik=int(match[1])))
    return refs


def index_documents(body,cik,accession):
    """Exact official document-type rows, not filename heuristics."""
    class Index(HTMLParser):
        def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
        def handle_starttag(self,tag,attrs):
            if tag=='tr':self.row=[]
            if tag in ('td','th'):self.cell=dict(text=[],links=[])
            if tag=='a' and self.cell is not None:self.cell['links'].append(dict(attrs).get('href',''))
        def handle_data(self,data):
            if self.cell is not None:self.cell['text'].append(data)
        def handle_endtag(self,tag):
            if tag in ('td','th') and self.cell is not None:
                self.cell['text']=' '.join(''.join(self.cell['text']).split())
                if self.row is not None:self.row.append(self.cell)
                self.cell=None
            if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
    parser=Index();parser.feed(body.decode());parser.close();out=[]
    base='https://www.sec.gov/Archives/edgar/data/'+str(cik)+'/'+accession.replace('-','')+'/'
    for n,row in enumerate(parser.rows):
        if len(row)<4 or row[3]['text'] not in ('10-K','EX-13','EX-13.1'):continue
        for href in row[2]['links']:
            if href.startswith('/ix?doc='):href=href[len('/ix?doc='):]
            url='https://www.sec.gov'+href if href.startswith('/') else base+href
            if url.startswith(base) and '/' not in url[len(base):] and '?' not in url and '#' not in url:
                out.append(dict(type=row[3]['text'],url=url,description=row[1]['text'],row=n))
    return out


def repaired_records(scope,catalog):
    """Independent acquisition bindings; no financial acceptance registry."""
    result={r['identity']['accession']:next(x for x in catalog if x['url']==r['url']) for r in scope if r['status']=='RETAINED'}
    path=ROOT/BINDING_REPAIR
    if not path.exists():return result
    payload=json.loads(path.read_bytes())
    targets={r['identity']['accession']:r['identity'] for r in scope}
    for row in payload['rows']:
        if row['status']!='DOCUMENT_BOUND':continue
        identity=row['identity'];acc=identity['accession']
        if identity!=targets.get(acc):raise h.InputError('Statement repair selected identity differs')
        bound={}
        for role in ('index','primary','document'):
            ref=row[role];matches=[r for r in catalog if r['url']==ref['url'] and r['sha256']==ref['sha256']]
            if not matches:raise h.InputError('Required repaired statement body/receipt unavailable')
            if len({r['sha256'] for r in catalog if r['url']==ref['url']})!=1:raise h.InputError('Conflicting repaired statement bodies')
            bound[role]=matches[0]
        index=index_documents(bound['index']['body'],identity['cik'],acc)
        if not any(x['type']=='10-K' and x['url']==bound['primary']['url'] for x in index):raise h.InputError('Primary not bound to authoritative index')
        verify_primary(bound['primary'],identity)
        if row['document_type']!='10-K':
            if not any(x['type']==row['document_type'] and x['url']==bound['document']['url'] for x in index):raise h.InputError('Statement not bound to indexed annual report')
            text=re.sub('<[^>]+>',' ',bound['primary']['body'].decode())
            if not re.search(r'annual report.{0,250}incorporat|incorporat.{0,250}annual report',text,re.I|re.S):raise h.InputError('Explicit primary incorporation reference unavailable')
        record=dict(bound['document'],document_type=row['document_type'],filing_primary=bound['primary'],index_record=bound['index'],selected_identity=identity)
        result[acc]=record
    return result


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
    if record.get('document_type') in ('EX-13','EX-13.1'):
        if any(record.get('selected_identity',{}).get(k)!=v for k,v in identity.items()):raise h.InputError('Incorporated statement identity differs')
        if hashlib.sha256(record['body']).hexdigest()!=record['sha256']:raise h.InputError('Incorporated statement body differs')
        for key in ('filing_primary','index_record'):
            metadata=record.get(key)
            if metadata is None or hashlib.sha256(metadata['body']).hexdigest()!=metadata.get('sha256') or metadata.get('http_status')!=200 or not metadata.get('retrieved_at_utc'):
                raise h.InputError('Incorporated identity metadata body/receipt invalid')
        entries=index_documents(record['index_record']['body'],identity['cik'],identity['accession'])
        if not any(x['url']==record['url'] and x['type']==record['document_type'] for x in entries):raise h.InputError('Incorporated document index binding differs')
        return verify_primary(record['filing_primary'],identity)
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


class BoundTables(Tables):
    """Inline nesting and explicit split-cell punctuation, without column guesses."""
    def __init__(self):super().__init__();self.fact_stack=[]
    def handle_starttag(self,tag,attrs):
        super().handle_starttag(tag,attrs)
        if tag=='ix:nonfraction' and self.depth==1 and self.cell is not None:
            if self.fact_stack:self.fact['nested_parent']=self.fact_stack[-1]['attrs'].get('name')
            self.fact_stack.append(self.fact)
    def handle_data(self,data):
        if self.cell is not None:
            self.cell['text'].append(data)
            for fact in self.fact_stack:fact['text'].append(data)
    def handle_endtag(self,tag):
        if tag=='ix:nonfraction' and self.fact_stack:
            self.fact_stack.pop();self.fact=self.fact_stack[-1] if self.fact_stack else None
            return
        super().handle_endtag(tag)


def parse(record,improved=False):
    parser=BoundTables() if improved else Tables();parser.feed(record['body'].decode('utf-8'));parser.close()
    if improved:
        for table in parser.tables:
            for row in table:
                for index,cell in enumerate(row[:-1]):
                    # Only an explicit adjacent closing parenthesis is joined.
                    # No missing punctuation or inferred cash sign is supplied.
                    if cell['facts'] and cell['text'].strip().startswith('(') and not cell['text'].strip().endswith(')') and row[index+1]['text'].strip()==')' and not row[index+1]['facts']:
                        cell['split_sign_cells']=[index,index+1];cell['text']+=')'
    return parser.tables


def primary_bindings(record):
    """Primary's own namespaces, contexts and units, independently of instance IDs."""
    text=record['body'].decode('utf-8')
    namespaces=dict(re.findall(r'xmlns:([^\s=]+)=["\']([^"\']+)',text))
    contexts={m[0]:m[1] for m in re.findall(r'<xbrli:context\b[^>]*\bid=["\']([^"\']+)["\']([^>]*>.*?</xbrli:context>)',text,re.I|re.S)}
    units={m[0]:m[1] for m in re.findall(r'<xbrli:unit\b[^>]*\bid=["\']([^"\']+)["\']([^>]*>.*?</xbrli:unit>)',text,re.I|re.S)}
    if not contexts and record.get('document_type') in ('EX-13','EX-13.1'):
        own_ns,contexts,units=primary_bindings(record['filing_primary'])
        if any(own_ns.get(k)!=v for k,v in namespaces.items() if k in own_ns):raise h.InputError('Inline document-set namespaces conflict')
        namespaces={**own_ns,**namespaces}
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
