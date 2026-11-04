"""Read-only fresh-interpreter verification against an existing private bundle.

Pass an already built bundle. This script creates no bundle and modifies only its
own audit receipt; the child imports exclusively the sealed bundle's sources.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
parser = argparse.ArgumentParser()
parser.add_argument('bundle',type=Path)
args = parser.parse_args()
bundle = args.bundle.resolve()
oracle = [p['fcff_serialized_usd'] for p in json.loads((HERE/'results.json').read_text())['amounts']]
modules = ['review/apple_operating_history.py','review/operating_fcff.py','review/pilot_cashflows.py',
           'review/resolved_history.py','review/cashflow_readiness.py','api/catalog.py']
hashes = {}
for name in modules:
    relative = 'src/valuation_platform/'+name
    source = (ROOT/relative).read_bytes(); copy = (bundle/relative).read_bytes()
    assert source == copy, 'Existing bundle is stale: '+relative
    assert (bundle/relative).stat().st_mode & 0o222 == 0
    hashes[relative] = hashlib.sha256(copy).hexdigest()
code = '''
import json,sys
from pathlib import Path
from fastapi.testclient import TestClient
from valuation_platform.api.app import create_app
from valuation_platform.api.bundle import verify_bundle
from valuation_platform.review import apple_operating_history,operating_fcff,pilot_cashflows,resolved_history
root=Path(sys.argv[1]);expected=json.loads(sys.argv[2]);verify_bundle(root)
for module in (apple_operating_history,operating_fcff,pilot_cashflows,resolved_history):
    assert Path(module.__file__).is_relative_to(root)
with TestClient(create_app(root)) as client:
    assert client.get('/health').json()=={'status':'ready'}
    response=client.get('/api/v1/cashflows/AAPL');assert response.status_code==200
    data=response.json();assert[p['fcff']['amount_usd']for p in data['periods']]==expected
    catalog=client.get('/api/v1/catalog');assert catalog.status_code==200
    entry=next(p for p in catalog.json()['entries']if p['company']=='AAPL')
    assert[p['fcff']for p in entry['historical_window']]==expected
    assert len(catalog.content)<96*1024
    assert[p['legacy_cfo_fcff']['amount_usd']for p in data['periods']][-2:]==[None,None]
    assert all(p['fcfe']['parent_common_amount_usd']is None for p in data['periods'])
    assert data['readiness']['counts']['missing_required_input']==0
    assert '355m'in data['notice'] and '17.782'in data['notice'] and '13.585'in data['notice']
    assert data['status']=='OPEN'and data['review_passed']is False
    result={'verdict':'PASS_FRESH_SEALED_INTERPRETER','health':'ready','five_source_oracle_amounts_match':True,
            'imports_from_sealed_bundle_only':True,'catalog_bytes':len(catalog.content),
            'all_material_qualifications_in_notice':True,'legacy_gaps_preserved':True,
            'parent_common_fcfe_available':False,'company_review_status':'OPEN'}
print(json.dumps(result))
'''
env = dict(os.environ,PYTHONPATH=str(bundle/'src'),PYTHONDONTWRITEBYTECODE='1')
completed = subprocess.run([sys.executable,'-c',code,str(bundle),json.dumps(oracle)],cwd=bundle,
                           env=env,check=True,capture_output=True,text=True,timeout=60)
result = json.loads(completed.stdout)
result['source_module_hashes'] = hashes
result['bundle_path_at_verification'] = str(bundle)
(HERE/'sealed-runtime-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2))
