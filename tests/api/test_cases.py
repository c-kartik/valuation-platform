"""Local API acceptance; synthetic economics only, including retained anchors."""

import asyncio
from copy import deepcopy
from decimal import Inexact, localcontext
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import httpx2 as httpx
from fastapi.testclient import TestClient

from valuation_platform.api.app import create_app
from valuation_platform.api.budget import ServerPolicy, BudgetError, read_http_case, check_depth
from valuation_platform.api.bundle import build_bundle, remove_bundle, verify_bundle
from valuation_platform.valuation import case_inputs as c

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / 'examples/valuation'


def payload(equity=False, kind=None):
    d = json.loads((EXAMPLES / ('synthetic-equity.json' if equity else 'synthetic-base.json')).read_text())
    if kind:
        identity = c.ANCHORS[kind]['identity']
        d.update(anchor=dict(kind=kind, **identity), input_basis='MANUAL_INPUT', case_name='SYNTHETIC API engineering input on retained ' + kind)
        d['analyst']['rationale'] = 'SYNTHETIC forecasts and bridge only; not analyst estimates or company financial approval.'
        d['conventions']['forecast'] = 'manual-fcff-v1'
        if equity:
            b = d['bridge']; b.update(input_basis='MANUAL_INPUT', convention_version='manual-equity-bridge-v1')
            for x in b['components']: x.update(company_cik=identity['cik'], as_of=identity['annual_end'])
            for x in b['observations']: x['company_cik'] = identity['cik']
            b['shares'].update(company_cik=identity['cik'], observation_date=identity['annual_end'])
    return d


def blocking_worker(conn, body, root, policy, started, release, ignore_term=False):
    if ignore_term:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
    started.set()
    release.wait()
    conn.send_bytes(b'500 {"error":{"code":"test_only"}}')
    conn.close()


def broken_worker(conn, body, root, policy):
    conn.close()
    os._exit(7)


def oversized_worker(conn, body, root, policy):
    try:
        conn.send_bytes(b'200 ' + b'x' * (policy.max_response_bytes + 100000))
    except OSError:
        pass
    finally:
        conn.close()


def borderline_worker(conn, body, root, policy):
    conn.send_bytes(b'200 ' + b'x' * (policy.max_response_bytes + 1))
    conn.close()


def cpu_worker(conn, body, root, policy, started):
    from valuation_platform.api.worker import restrict_runtime
    restrict_runtime(root, 1)
    started.set()
    while True:
        pass


class BundleFixture:
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.bundle = Path(cls.temp.name) / 'private'
        cls.manifest = build_bundle(ROOT, cls.bundle)

    @classmethod
    def tearDownClass(cls):
        remove_bundle(cls.bundle)
        cls.temp.cleanup()


class ApiTests(BundleFixture, unittest.TestCase):
    def test_both_scopes_equal_engine_and_cli_with_full_trace(self):
        with TestClient(create_app(self.bundle)) as client:
            for equity in (False, True):
                d = payload(equity); text = json.dumps(d); before = deepcopy(d)
                out = client.post('/api/v1/cases/run', content=text, headers={'Content-Type': 'application/json'})
                self.assertEqual(out.status_code, 200, out.text)
                self.assertEqual(out.json(), c.run_case(c.read_case(text), ROOT))
                name = 'synthetic-equity.json' if equity else 'synthetic-base.json'
                old = subprocess.check_output([sys.executable, str(ROOT/'scripts/run_analyst_case.py'), str(EXAMPLES/name), '--run'], cwd=ROOT)
                self.assertEqual(out.json(), json.loads(old)); self.assertEqual(d, before)
                self.assertEqual(out.headers['cache-control'], 'no-store')
                self.assertNotIn('access-control-allow-origin', out.headers)
                self.assertEqual('stage_c' in out.json(), equity)

    def test_investor_equity_validation_run_and_unresolved_no_downgrade(self):
        from tests.valuation.test_investor_equity import investor_equity
        d=investor_equity();before=deepcopy(d)
        with TestClient(create_app(self.bundle)) as client:
            with patch.object(c,'run_case',side_effect=AssertionError('calculation')):
                checked=client.post('/api/v1/cases/validate',json=d)
                self.assertEqual(checked.status_code,200,checked.text)
                self.assertEqual(checked.json()['calculation_scope'],'EQUITY_PER_SHARE')
                self.assertFalse(checked.json()['calculation_performed'])
            out=client.post('/api/v1/cases/run',json=d)
            self.assertEqual(out.status_code,200,out.text)
            expected=c.run_case(c.read_case(json.dumps(payload(equity=True))),ROOT)
            self.assertEqual(out.json()['stage_b'],expected['stage_b'])
            self.assertEqual(out.json()['stage_c'],expected['stage_c'])
            self.assertEqual(out.json()['submitted_inputs'],before)
            d['bridge']['unresolved_requirements']=['Unassessed claims']
            for route in ('validate','run'):
                out=client.post('/api/v1/cases/'+route,json=d)
                self.assertEqual(out.status_code,422,out.text);self.assertNotIn('stage_b',out.json())
            self.assertEqual(before['preparation']['notes'],None)

    def test_investor_no_notes_same_finances_validation_and_budgets(self):
        with TestClient(create_app(self.bundle)) as client:
            for kind in (None, *c.ANCHORS):
                legacy = payload(kind=kind)
                d = deepcopy(legacy); d.pop('analyst'); d.pop('scope')
                d.update(schema_version=c.INVESTOR_CASE_SCHEMA,
                         preparation={'provenance':'ANONYMOUS_INVESTOR',
                                      'timestamp_utc':'2026-10-21T10:00:00Z', 'notes':None})
                with patch.object(c, 'run_case', side_effect=AssertionError('calculation')):
                    out = client.post('/api/v1/cases/validate', json=d)
                    self.assertEqual(out.status_code, 200, out.text)
                    self.assertFalse(out.json()['calculation_performed'])
                out = client.post('/api/v1/cases/run', json=d)
                self.assertEqual(out.status_code, 200, out.text)
                self.assertEqual(out.json()['stage_b'], c.run_case(c.read_case(json.dumps(legacy)), ROOT)['stage_b'])
                self.assertEqual(out.json()['submitted_inputs']['preparation'], d['preparation'])
                d['preparation']['notes'] = 'x' * 2049
                out = client.post('/api/v1/cases/run', json=d)
                self.assertEqual(out.status_code, 422); self.assertIn('preparation.notes', out.text)
                d['preparation']['notes'] = None; d['anchor']['accession'] = 'wrong'
                out = client.post('/api/v1/cases/run', json=d)
                self.assertEqual(out.status_code, 422); self.assertIn('anchor.accession', out.text)

    def test_validation_calls_no_financial_loaders_or_calculators(self):
        with TestClient(create_app(self.bundle)) as client:
            with patch.object(c, 'run_case', side_effect=AssertionError('calculation')), patch.object(c, 'load_revenue_anchor', side_effect=AssertionError('load')), patch.object(c, 'load_meta_revenue_anchor', side_effect=AssertionError('load')), patch.object(c, 'forecast_five_years', side_effect=AssertionError('forecast')), patch.object(c, 'bridge_to_per_share', side_effect=AssertionError('bridge')):
                for kind in (None, *c.ANCHORS):
                    for equity in (False, True):
                        response = client.post('/api/v1/cases/validate', json=payload(equity, kind))
                        self.assertEqual(response.status_code, 200, response.text)
                        self.assertFalse(response.json()['calculation_performed'])
                self.assertEqual(client.get('/health').json(), {'status': 'ready'})

    def test_strict_parser_field_paths_and_no_scope_downgrade(self):
        examples = []
        d=payload();d['forecast_years'][2]['revenue_growth']='5%';examples.append((json.dumps(d),'forecast_years[2].revenue_growth'))
        d=payload();d['wacc']=.25;examples.append((json.dumps(d),'wacc'))
        d=payload();d['wacc']=float('nan');examples.append((json.dumps(d),'wacc'))
        d=payload();d['surprise']='unrecognized';examples.append((json.dumps(d),'surprise'))
        d=payload(True);d['bridge']['unresolved_requirements']=['Required selection is missing'];examples.append((json.dumps(d),'bridge.unresolved_requirements'))
        d=payload(True);d.pop('bridge');examples.append((json.dumps(d),'bridge'))
        d=payload();d['anchor']['accession']='stale';examples.append((json.dumps(d),'anchor.accession'))
        text=json.dumps(payload()).replace('"wacc": "0.25"','"wacc":"0.25","wacc":"0.30"');examples.append((text,'Duplicate JSON key'))
        with TestClient(create_app(self.bundle)) as client:
            for text, field in examples:
                for endpoint in ('validate','run'):
                    out=client.post('/api/v1/cases/'+endpoint, content=text, headers={'Content-Type':'application/json'})
                    self.assertEqual(out.status_code,422,out.text);self.assertIn(field,out.text);self.assertNotIn('stage_b',out.json())
            for extra in ('?output=/tmp/result','?deadline=1000','?root=/tmp'):
                self.assertEqual(client.post('/api/v1/cases/run'+extra,json=payload()).status_code,422)

    def test_body_representation_size_and_no_assumed_content_length(self):
        with TestClient(create_app(self.bundle)) as client:
            for headers in ({'Content-Type':'text/plain'},{'Content-Type':'appli cation/json'},{'Content-Type':'application/json','Content-Encoding':'gzip'}, {'Content-Type':'application/json;charset=latin-1'}):
                self.assertEqual(client.post('/api/v1/cases/validate',content=b'{}',headers=headers).status_code,415)
            def chunks():
                for _ in range(5): yield b' '*65536
            out=client.post('/api/v1/cases/validate',content=chunks(),headers={'Content-Type':'application/json'})
            self.assertEqual(out.status_code,413,out.text)
            out=client.post('/api/v1/cases/validate',content=chunks(),headers={'Content-Type':'application/json','Content-Length':'1'})
            self.assertEqual(out.status_code,413,out.text)
            for length in ('-1','not-an-integer','99999999999999999999999999999'):
                self.assertEqual(client.post('/api/v1/cases/validate',content=b'{}',headers={'Content-Type':'application/json','Content-Length':length}).status_code,422)
            self.assertEqual(client.post('/api/v1/cases/validate',content=b'{}',headers={'Content-Type':'application/json','Content-Length':'262145'}).status_code,413)
            self.assertEqual(client.post('/api/v1/cases/validate',content=b'{}',headers={'Content-Type':'application/json','Content-Length':'1'}).status_code,422)

    def test_budgets_deep_malformed_text_arrays_numeric_work_and_bounded_errors(self):
        docs=[]
        for field,value in [('wacc','1e9999999999999999999999999999'),('wacc','1e101'),('wacc','1e-101'),('wacc','0.'+'2'*200)]:
            d=payload();d[field]=value;docs.append(json.dumps(d))
        d=payload();d['analyst']['rationale']='x'*4097;docs.append(json.dumps(d))
        d=payload();d['scope']='x'*4097;docs.append(json.dumps(d))
        d=payload(True);d['bridge']['components']*=17;docs.append(json.dumps(d))
        d=payload(True);d['bridge']['observations']*=44;docs.append(json.dumps(d))
        d=payload(True);d['bridge']['components'][0]['source_references']=['x']*65;docs.append(json.dumps(d))
        d=payload();d['anchor']['accession']='x'*129;docs.append(json.dumps(d))
        d=payload();d.update({f'field{i}':None for i in range(65)});docs.append(json.dumps(d))
        d=payload();d['extra']=[None]*129;docs.append(json.dumps(d))
        d=payload();d['extra']=[[None]*127 for _ in range(127)];docs.append(json.dumps(d))
        docs.extend(['['*25+'0'+']'*25,'{','{} trailing','[NaN]', '{"bad":"\\ud800"}'])
        with TestClient(create_app(self.bundle),raise_server_exceptions=False) as client:
            for text in docs:
                out=client.post('/api/v1/cases/run',content=text.encode(),headers={'Content-Type':'application/json'})
                self.assertEqual(out.status_code,422,out.text);self.assertLess(len(out.content),8192)
            out=client.post('/api/v1/cases/validate',content=b'\xff',headers={'Content-Type':'application/json'})
            self.assertEqual(out.status_code,422)
        # Brackets/escaped quotes inside strings are not structural nesting.
        check_depth(json.dumps({'a':'["' * 100}))
        d=payload();d['wacc']='0.'+'2'*64
        self.assertIsNotNone(read_http_case(json.dumps(d).encode()))

    def test_response_budget_and_sanitized_worker_internal_errors(self):
        with TestClient(create_app(self.bundle,policy=ServerPolicy(max_response_bytes=256))) as client:
            out=client.post('/api/v1/cases/run',json=payload(True));self.assertEqual(out.status_code,422,out.text)
            self.assertEqual(out.json()['error']['code'],'response_budget');self.assertNotIn('stage_b',out.text)
        with TestClient(create_app(self.bundle,worker_target=broken_worker)) as client:
            out=client.post('/api/v1/cases/run',json=payload());self.assertEqual(out.status_code,500)
            self.assertNotIn('test-secret',out.text);self.assertNotIn('Traceback',out.text);self.assertNotIn('/private',out.text)
        with TestClient(create_app(self.bundle,policy=ServerPolicy(max_response_bytes=256),worker_target=oversized_worker)) as client:
            out=client.post('/api/v1/cases/run',json=payload());self.assertEqual(out.status_code,500);self.assertLess(len(out.content),8192)
        with TestClient(create_app(self.bundle,policy=ServerPolicy(max_response_bytes=256),worker_target=borderline_worker)) as client:
            out=client.post('/api/v1/cases/run',json=payload());self.assertEqual(out.status_code,422);self.assertEqual(out.json()['error']['code'],'response_budget')
        # Unexpected parent failure also has a fixed JSON contract, no traceback.
        with TestClient(create_app(self.bundle),raise_server_exceptions=False) as client, patch('valuation_platform.api.app.read_http_case',side_effect=RuntimeError('/private/secret request-body')):
            out=client.post('/api/v1/cases/validate',json=payload());self.assertEqual(out.status_code,500);self.assertEqual(out.json()['error']['code'],'internal_error');self.assertNotIn('secret',out.text)

    def test_decimal_context_and_inputs_unchanged(self):
        d=payload(True);before=deepcopy(d)
        with TestClient(create_app(self.bundle)) as client:
            baseline=client.post('/api/v1/cases/run',json=d).json()
            with localcontext() as ctx:
                ctx.prec=3;ctx.rounding='ROUND_DOWN';ctx.traps[Inexact]=True;ctx.clear_flags();snapshot=ctx.copy()
                response=client.post('/api/v1/cases/run',json=d)
                self.assertEqual(response.json(),baseline)
                self.assertEqual((ctx.prec,ctx.rounding,ctx.traps,ctx.flags),(snapshot.prec,snapshot.rounding,snapshot.traps,snapshot.flags))
        self.assertEqual(d,before)

    def test_retained_anchors_in_both_scopes_synthetic_only(self):
        with TestClient(create_app(self.bundle)) as client:
            for kind in c.ANCHORS:
                for equity in (False,True):
                    d=payload(equity,kind);out=client.post('/api/v1/cases/run',json=d)
                    self.assertEqual(out.status_code,200,out.text)
                    expected=c.run_case(c.read_case(json.dumps(d)),ROOT)
                    self.assertEqual(out.json(),expected)
                    self.assertEqual(out.json()['stage_b']['stage_a']['anchor']['approval_reference'],expected['stage_b']['stage_a']['anchor']['approval_reference'])

    def test_packaging_deterministic_pins_missing_and_tampered(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'second';manifest=build_bundle(ROOT,dest)
            try:
                self.assertEqual(manifest,self.manifest);verify_bundle(dest)
                for record in manifest['files']:
                    p=dest/record['path'];self.assertEqual(p.read_bytes(),(ROOT/record['path']).read_bytes());self.assertEqual(p.stat().st_mode & 0o777,0o444)
                path=dest/'docs/company-data-preparation/meta-analyst-input-package.json';path.chmod(0o644);path.write_bytes(path.read_bytes()+b' ')
                with self.assertRaises(ValueError):verify_bundle(dest)
                # Editing both resource and generated manifest cannot bypass reviewed pins.
                mp=dest/'runtime-manifest.json';mp.chmod(0o644);changed=json.loads(mp.read_text())
                for e in changed['files']:
                    if e['path']==str(path.relative_to(dest)):
                        e.update(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                mp.write_text(json.dumps(changed))
                with self.assertRaises(ValueError):verify_bundle(dest)
                with self.assertRaisesRegex(RuntimeError,'readiness'):
                    with TestClient(create_app(dest)):pass
                path.parent.chmod(0o755)
                path.unlink()
                with self.assertRaises(ValueError):verify_bundle(dest)
                with self.assertRaises(ValueError):build_bundle(ROOT,dest)
            finally:remove_bundle(dest)
        with self.assertRaises(ValueError):build_bundle(ROOT,ROOT/'must-not-create-api-bundle')
        self.assertFalse((ROOT/'must-not-create-api-bundle').exists())

    def test_isolated_bundle_without_git_corpus_network_or_resource_writes(self):
        cases=[payload(equity,kind) for kind in c.ANCHORS for equity in (False,True)]
        program='''import sys,json,hashlib,os
from pathlib import Path
from fastapi.testclient import TestClient
from valuation_platform.api.app import create_app
from valuation_platform.api.worker import restrict_runtime
root=Path(os.environ['VALUATION_APP_ROOT'])
assert not (root/'.git').exists() and not (root/'docs/evidence').exists()
with TestClient(create_app()) as client:
 for d in json.loads(sys.stdin.read()):
  r=client.post('/api/v1/cases/run',json=d)
  assert r.status_code==200,r.text
  assert r.json()['stage_b']['stage_a']['anchor']['approval_reference']
restrict_runtime(root,30)
import resource
assert resource.getrlimit(resource.RLIMIT_CPU)==(30,31)
assert resource.getrlimit(resource.RLIMIT_CORE)==(0,0)
p=root/'docs/company-data-preparation/meta-analyst-input-package.json'
before=p.read_bytes()
try:p.open('ab')
except PermissionError:pass
else:raise AssertionError('write accepted')
import socket
try:socket.create_connection(('127.0.0.1',9))
except PermissionError:pass
else:raise AssertionError('network accepted')
assert p.read_bytes()==before
print('isolated six-case execution and write/network denials passed')
'''
        env={**os.environ,'PYTHONPATH':str(self.bundle/'src'),'PYTHONDONTWRITEBYTECODE':'1','VALUATION_APP_ROOT':str(self.bundle)}
        out=subprocess.run([sys.executable,'-c',program],input=json.dumps(cases),capture_output=True,text=True,cwd=self.temp.name,env=env,timeout=30)
        self.assertEqual(out.returncode,0,out.stderr);self.assertIn('denials passed',out.stdout)


class LifecycleTests(BundleFixture, unittest.IsolatedAsyncioTestCase):
    async def setup_blocked(self,deadline=5,ignore_term=False):
        ctx=multiprocessing.get_context('spawn');started=ctx.Event();release=ctx.Event()
        app=create_app(self.bundle,policy=ServerPolicy(deadline_seconds=deadline),worker_target=blocking_worker,worker_args=(started,release,ignore_term))
        return app,started,release

    async def wait_started(self,event):
        self.assertTrue(await asyncio.to_thread(event.wait,3),'child did not reach synchronization point')

    def assert_gone(self,pid):
        with self.assertRaises(ProcessLookupError):os.kill(pid,0)

    async def test_busy_health_validation_and_capacity_recovery(self):
        app,started,release=await self.setup_blocked()
        async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://local') as client:
            running=asyncio.create_task(client.post('/api/v1/cases/run',json=payload()))
            await self.wait_started(started);pid=app.state.calculator.job.process.pid
            health=await client.get('/health');self.assertEqual(health.status_code,200)
            busy=await client.post('/api/v1/cases/run',json=payload());self.assertEqual(busy.status_code,503);self.assertEqual(busy.headers['retry-after'],'1')
            self.assertEqual((await client.post('/api/v1/cases/validate',json=payload())).status_code,200)
            release.set();self.assertEqual((await running).status_code,500);self.assert_gone(pid)
            self.assertIsNone(app.state.calculator.job)
            app.state.calculator.target=__import__('valuation_platform.api.worker',fromlist=['calculate']).calculate;app.state.calculator.target_args=()
            self.assertEqual((await client.post('/api/v1/cases/run',json=payload())).status_code,200)

    async def test_real_deadline_terminate_kill_reap_and_release(self):
        app,started,release=await self.setup_blocked(deadline=1.5,ignore_term=True)
        async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://local') as client:
            running=asyncio.create_task(client.post('/api/v1/cases/run',json=payload()));await self.wait_started(started);pid=app.state.calculator.job.process.pid
            out=await asyncio.wait_for(running,4)
            self.assertEqual(out.status_code,504);self.assertEqual(out.json()['error']['code'],'deadline_exceeded');self.assert_gone(pid);self.assertIsNone(app.state.calculator.job)

    async def test_shutdown_stops_child_and_fails_inflight_with_no_result(self):
        app,started,release=await self.setup_blocked()
        async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://local') as client:
            running=asyncio.create_task(client.post('/api/v1/cases/run',json=payload()));await self.wait_started(started);pid=app.state.calculator.job.process.pid
            await app.state.calculator.close();out=await running
            self.assertEqual(out.status_code,503);self.assertEqual(out.json()['error']['code'],'shutting_down');self.assert_gone(pid)

    @unittest.skipUnless(os.name=='posix','Unix CPU limit')
    async def test_real_cpu_limit_kills_child(self):
        started=multiprocessing.get_context('spawn').Event()
        app=create_app(self.bundle,policy=ServerPolicy(deadline_seconds=5,cpu_seconds=1),worker_target=cpu_worker,worker_args=(started,))
        async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://local') as client:
            running=asyncio.create_task(client.post('/api/v1/cases/run',json=payload()));await self.wait_started(started);pid=app.state.calculator.job.process.pid
            out=await asyncio.wait_for(running,4);self.assertEqual(out.status_code,500);self.assert_gone(pid);self.assertIsNone(app.state.calculator.job)

    async def test_coroutine_cancellation_reaps_real_child(self):
        app,started,release=await self.setup_blocked()
        async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://local') as client:
            running=asyncio.create_task(client.post('/api/v1/cases/run',json=payload()));await self.wait_started(started);pid=app.state.calculator.job.process.pid
            running.cancel()
            with self.assertRaises(asyncio.CancelledError):await running
            self.assert_gone(pid);self.assertIsNone(app.state.calculator.job)

    async def test_asgi_disconnect_reaps_real_child(self):
        app,started,release=await self.setup_blocked();incoming=asyncio.Queue();sent=[]
        await incoming.put({'type':'http.request','body':json.dumps(payload()).encode(),'more_body':False})
        async def receive():return await incoming.get()
        async def send(message):sent.append(message)
        scope={'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':'POST','scheme':'http','path':'/api/v1/cases/run','raw_path':b'/api/v1/cases/run','query_string':b'','root_path':'','headers':[(b'content-type',b'application/json')],'server':('local',80),'client':('local',123)}
        async with app.router.lifespan_context(app):
            running=asyncio.create_task(app(scope,receive,send));await self.wait_started(started);pid=app.state.calculator.job.process.pid
            await incoming.put({'type':'http.disconnect'});await asyncio.wait_for(running,3);self.assert_gone(pid);self.assertIsNone(app.state.calculator.job)
            self.assertEqual(sent[0]['status'],499)

    async def test_body_timeout_without_calculation(self):
        app=create_app(self.bundle,policy=ServerPolicy(body_seconds=.05));incoming=asyncio.Queue();sent=[]
        await incoming.put({'type':'http.request','body':b'{','more_body':True})
        async def receive():return await incoming.get()
        async def send(message):sent.append(message)
        scope={'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':'POST','scheme':'http','path':'/api/v1/cases/run','raw_path':b'/api/v1/cases/run','query_string':b'','root_path':'','headers':[(b'content-type',b'application/json')],'server':('local',80),'client':('local',123)}
        async with app.router.lifespan_context(app):
            await asyncio.wait_for(app(scope,receive,send),1);self.assertEqual(sent[0]['status'],408);self.assertIsNone(app.state.calculator.job)


if __name__=='__main__':unittest.main()
