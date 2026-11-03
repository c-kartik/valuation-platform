"""Cloud preparation preserves evidence and starts the existing calculation API."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/cloud'))
import research
import workspace


class CloudWorkspaceTests(unittest.TestCase):
    def test_original_research_inventory_and_archive_bytes(self):
        m=research.verify(ROOT)
        self.assertEqual(len(m['files']),52)
        self.assertEqual(m['uncompressed_bytes'],138733053)
        self.assertTrue({'historical-cashflows-42/calculations.json','historical-cashflows-42/evidence-final.json','historical-cashflows-42/report.html'}<={r['path'] for r in m['files']})

    def fixture(self,root,members):
        folder=root/research.SNAPSHOT;folder.mkdir(parents=True);archive=folder/'example.zip'
        with zipfile.ZipFile(archive,'w') as z:
            for name,body in members.items():z.writestr(name,body)
        data={'schema_version':'portable-research-snapshot-v1','archive_file':archive.name,'archive_sha256':research.digest(archive.read_bytes()),'files':[{'path':n,'bytes':len(b),'sha256':research.digest(b)} for n,b in members.items()]}
        (folder/'manifest.json').write_text(json.dumps(data));return folder,data

    def test_restore_is_idempotent_and_rejects_overwriting_changed_research(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root,{'historical-cashflows-42/report.html':b'<p>original</p>'})
            destination=research.restore(root);self.assertEqual(research.restore(root),destination)
            (destination/'report.html').write_text('edited')
            with self.assertRaises(ValueError):research.restore(root)

    def test_path_traversal_or_archive_tampering_cannot_write_any_research(self):
        for name in ('../escape','/escape','historical-cashflows-42/../escape','historical-cashflows-42\\escape'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as d:
                root=Path(d);self.fixture(root,{name:b'bad'})
                with self.assertRaises(ValueError):research.restore(root)
                self.assertFalse((root/'.cloud').exists())
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);folder,m=self.fixture(root,{'historical-cashflows-42/report.html':b'ok'})
            (folder/'example.zip').write_bytes(b'changed')
            with self.assertRaises(ValueError):research.restore(root)
            self.assertFalse((root/'.cloud').exists())

    def test_smoke_runs_isolated_catalog_and_synthetic_case(self):
        self.assertEqual(workspace.smoke(ROOT),{'health':'PASS','catalog_bytes':81564,'companies':['META','GOOGL','AAPL'],'synthetic_case':'PASS'})

    def test_service_exit_and_busy_ports_fail_without_taking_over_processes(self):
        import socket
        with socket.socket() as s:
            s.bind(('127.0.0.1',0));port=s.getsockname()[1]
            with self.assertRaisesRegex(ValueError,'in use'):workspace.port_free(port)
        class Stopped:
            def poll(self):return 1
        with self.assertRaisesRegex(ValueError,'stopped'):workspace.wait_ready('http://127.0.0.1:1',Stopped())

if __name__=='__main__':unittest.main()
