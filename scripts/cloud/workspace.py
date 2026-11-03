"""Portable cloud/local startup using the same sealed API bundle and Vite proxy.

Loopback by default. A provider may privately forward the frontend port. There
is no deployment, credential capture, public tunnel or financial-engine change.
"""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from valuation_platform.api.bundle import build_bundle,remove_bundle


def smoke(root=ROOT):
    from fastapi.testclient import TestClient
    from valuation_platform.api.app import create_app
    with tempfile.TemporaryDirectory(prefix='valuation-cloud-smoke-') as directory:
        bundle=Path(directory)/'runtime';build_bundle(root,bundle)
        try:
            with TestClient(create_app(bundle)) as client:
                health=client.get('/health');catalog=client.get('/api/v1/catalog')
                if health.status_code!=200 or catalog.status_code!=200:raise ValueError('API startup smoke failed')
                entries=catalog.json()['entries']
                if [e['company'] for e in entries]!=['META','GOOGL','AAPL']:raise ValueError('Three-company catalog unavailable')
                fixture=json.loads((root/'examples/valuation/synthetic-base.json').read_text())
                result=client.post('/api/v1/cases/run',json=fixture)
                if result.status_code!=200:raise ValueError('Synthetic end-to-end case failed')
                return dict(health='PASS',catalog_bytes=len(catalog.content),companies=[e['company'] for e in entries],synthetic_case='PASS')
        finally:remove_bundle(bundle)


def port_free(port):
    with socket.socket() as s:
        try:s.bind(('127.0.0.1',port))
        except OSError as exc:raise ValueError(f'Port{port} is in use; choose a different port') from exc


def wait_ready(url,process,timeout=30):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if process.poll() is not None:raise ValueError('Development service stopped before readiness')
        try:
            with urlopen(url,timeout=1) as response:
                if response.status==200:return
        except (OSError,TimeoutError):pass
        time.sleep(.2)
    raise ValueError(f'Development service did not become ready at {url}')


def serve(root=ROOT,api_port=8000,frontend_port=5173):
    if api_port==frontend_port:raise ValueError('API and frontend need different ports')
    port_free(api_port);port_free(frontend_port)
    processes=[]
    with tempfile.TemporaryDirectory(prefix='valuation-cloud-dev-') as directory:
        bundle=Path(directory)/'runtime';build_bundle(root,bundle)
        env=dict(os.environ,PYTHONPATH=str(bundle/'src'),VALUATION_APP_ROOT=str(bundle),PYTHONDONTWRITEBYTECODE='1')
        try:
            api=subprocess.Popen([sys.executable,'-m','uvicorn','valuation_platform.api.app:create_app','--factory','--host','127.0.0.1','--port',str(api_port),'--workers','1','--limit-concurrency','16','--backlog','32','--timeout-keep-alive','5','--timeout-graceful-shutdown','2','--no-access-log'],cwd=root,env=env)
            processes.append(api);wait_ready(f'http://127.0.0.1:{api_port}/health',api)
            vite=subprocess.Popen(['node',str(root/'frontend/node_modules/vite/bin/vite.js'),'--host','127.0.0.1','--port',str(frontend_port),'--strictPort'],cwd=root/'frontend',env=dict(os.environ,VALUATION_LOCAL_API=f'http://127.0.0.1:{api_port}'))
            processes.append(vite);wait_ready(f'http://127.0.0.1:{frontend_port}/workspace/',vite)
            print(f'Workspace ready: http://127.0.0.1:{frontend_port}/workspace/',flush=True)
            print('Use only a provider-authenticated private preview to access it remotely; this command does not create a public URL.',flush=True)
            while all(p.poll() is None for p in processes):time.sleep(.3)
            raise ValueError('A development service exited; both owned services are stopping')
        except KeyboardInterrupt:pass
        finally:
            for p in reversed(processes):
                if p.poll() is None:
                    p.terminate()
                    try:p.wait(timeout=6)
                    except subprocess.TimeoutExpired:p.kill();p.wait()
            remove_bundle(bundle)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['smoke','serve']);parser.add_argument('--api-port',type=int,default=8000);parser.add_argument('--frontend-port',type=int,default=5173);args=parser.parse_args()
    if any(not 1<=p<=65535 for p in (args.api_port,args.frontend_port)):parser.error('Ports must be1–65535')
    if args.action=='smoke':print(json.dumps(smoke(),sort_keys=True))
    else:serve(api_port=args.api_port,frontend_port=args.frontend_port)

if __name__=='__main__':main()
