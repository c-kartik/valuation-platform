"""Explicit one-source acquisition only; never executes from API/profile loading."""
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import os
from .profile import exclusive_json

ALLOWED={'www.sec.gov','data.sec.gov','abc.xyz','investor.atmeta.com','www.apple.com','investor.apple.com','home.treasury.gov','aswathdamodaran.blogspot.com','pages.stern.nyu.edu'}


def acquire(url,destination,*,published_at=None,observation_date=None):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname not in ALLOWED or parsed.username or parsed.password or parsed.fragment:
        raise ValueError('Only explicit public primary HTTPS source URLs are supported')
    path=Path(destination).absolute();root=Path(__file__).resolve().parents[3]
    if path.exists() or path.resolve().is_relative_to(root):raise ValueError('Choose a new snapshot directory outside repository')
    user_agent=os.environ.get('SEC_USER_AGENT','').strip()
    if not user_agent:raise ValueError('Set an identifying SEC_USER_AGENT; never put credentials here')
    import requests
    # One request, no retry storm, verified TLS. No credentials/session cookies.
    response=requests.get(url,headers={'User-Agent':user_agent,'Accept-Encoding':'gzip,deflate'},timeout=30,allow_redirects=False,stream=True)
    response.raise_for_status()
    if response.is_redirect:raise ValueError('Redirect needs explicit review; acquire final primary URL')
    body=bytearray()
    for part in response.iter_content(65536):
        body.extend(part)
        if len(body)>12*1024*1024:raise ValueError('Source exceeds 12MiB acquisition limit')
    path.mkdir(parents=True,exist_ok=False)
    with (path/'source.html').open('xb') as stream:stream.write(body)
    manifest={'schema_version':'preload-acquired-source-v1','url':url,'file':'source.html','sha256':hashlib.sha256(body).hexdigest(),
      'bytes':len(body),'retrieved_at':datetime.now(timezone.utc).isoformat(),'published_at':published_at,'observation_date':observation_date,
      'extraction_version':'UNREVIEWED','rights':'Public primary access, not a redistribution-license grant',
      'next_required_action':'Review period/definition and prepare new explicit extraction mapping and source manifest; acquisition never promotes an anchor or becomes a financial fact automatically.'}
    exclusive_json(path/'snapshot.json',manifest)
    return manifest
