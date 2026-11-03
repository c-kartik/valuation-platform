"""Retain a bounded complete FY2021–25 10-Q population; source bank is read-only."""
import gzip, hashlib, json, os, re, time
from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
import requests
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.hide=0
 def handle_starttag(self,t,a):
  if t in ('ix:hidden','script','style'):self.hide+=1
  if t in ('p','div','tr','h1','h2','h3','br') and not self.hide:self.parts.append('\n')
 def handle_endtag(self,t):
  if t in ('ix:hidden','script','style') and self.hide:self.hide-=1
  if t in ('p','div','tr','h1','h2','h3') and not self.hide:self.parts.append('\n')
 def handle_data(self,d):
  if not self.hide:self.parts.append(d+' ')
def plaintext(b):
 p=Text();p.feed(b.decode());return re.sub(r'\n+','\n',re.sub(r'[^\S\n]+',' ',''.join(p.parts)))
def fetch(ident,url):
 path=HERE/(ident+'.gz')
 old=next((s for s in sources if s['id']==ident),None)
 if path.exists() and old:
  raw=gzip.decompress(path.read_bytes());assert hashlib.sha256(raw).hexdigest()==old['sha256'];return raw
 r=requests.get(url,headers={'User-Agent':os.environ['SEC_USER_AGENT']},timeout=45)
 rec={'id':ident,'url':url,'http_status':r.status_code,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'file':path.name,'encoding':'gzip','bytes':len(r.content),'sha256':hashlib.sha256(r.content).hexdigest()}
 sources.append(rec);(HERE/'retrieval-manifest.json').write_text(json.dumps({'sources':sources},indent=2)+'\n')
 if r.status_code!=200:raise ValueError(f'{url} returned{r.status_code}')
 path.write_bytes(gzip.compress(r.content,mtime=0));time.sleep(.2);return r.content
sources=json.loads((HERE/'retrieval-manifest.json').read_text())['sources'] if (HERE/'retrieval-manifest.json').exists() else []
current=json.loads(fetch('submissions-current','https://data.sec.gov/submissions/CIK0001326801.json'))
old=json.loads(fetch('submissions-2017-2024','https://data.sec.gov/submissions/CIK0001326801-submissions-001.json'))
rows=[]
for f in (current['filings']['recent'],old):
 for i,form in enumerate(f['form']):
  if form=='10-Q' and '2021'<=f['reportDate'][i][:4]<='2025':rows.append({k:f[k][i] for k in ('form','reportDate','accessionNumber','primaryDocument','filingDate')})
assert len(rows)==15 and len({r['reportDate'] for r in rows})==15
for r in sorted(rows,key=lambda r:r['reportDate']):
 ident='meta-'+r['reportDate']+'-10q';url='https://www.sec.gov/Archives/edgar/data/1326801/'+r['accessionNumber'].replace('-','')+'/'+r['primaryDocument']
 b=fetch(ident,url);(HERE/(ident+'.txt')).write_text(plaintext(b));print(r['reportDate'],len(b),flush=True)
(HERE/'quarterly-population.json').write_text(json.dumps(rows,indent=2)+'\n')
