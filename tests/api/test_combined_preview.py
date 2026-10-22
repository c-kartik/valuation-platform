"""Combined publication/routing checks; no cloud calls or financial reruns."""

from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from assemble_combined_preview import PORTFOLIO_FILES, check_public, verify_source, assemble
from preview_combined_site import CombinedHandler


def fixture(public):
    public.mkdir()
    for name in PORTFOLIO_FILES:
        (public / name).write_text('<html><div id="work">Portfolio</div><a href="/valuation/">DCF Calculator</a></html>'
                                   if name.endswith('.html') else 'public asset')
    (public / 'valuation/assets').mkdir(parents=True)
    (public / 'valuation/index.html').write_text('<html><script src="/valuation/assets/index-test.js"></script>'
        '<link href="/valuation/assets/index-test.css"><link href="/valuation/favicon.svg"></html>')
    (public / 'valuation/favicon.svg').write_text('<svg/>')
    (public / 'valuation/assets/index-test.js').write_text('/api/v1/catalog /api/v1/cases/run')
    (public / 'valuation/assets/index-test.css').write_text('body{}')


class PublicationTests(unittest.TestCase):
    def test_exact_files_references_and_deterministic_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            public = Path(temp) / 'public'; fixture(public)
            self.assertEqual(len(check_public(public)), 14)
            self.assertEqual(check_public(public), check_public(public))
            (public / 'index.html').write_text('<a href="resume.pdf">CV</a><a href="work.html#work">Work</a>')
            check_public(public)
            (public / 'index.html').write_text('<a href="work.html#missing">broken</a>')
            with self.assertRaisesRegex(ValueError, 'fragment'): check_public(public)

    def test_unexpected_files_secrets_symlinks_and_wrong_base_reject(self):
        for name, body in (('.git/config', 'private'), ('case.json', '{}'),
                           ('valuation/assets/index-test.js.map', '{}'),
                           ('index.html', '-----BEGIN PRIVATE KEY'),
                           ('valuation/index.html', '<script src="/assets/index-test.js"></script>')):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                public = Path(temp) / 'public'; fixture(public)
                file = public / name; file.parent.mkdir(parents=True, exist_ok=True); file.write_text(body)
                with self.assertRaises(ValueError): check_public(public)
        with tempfile.TemporaryDirectory() as temp:
            public = Path(temp) / 'public'; fixture(public)
            (public / 'escape').symlink_to('/etc/hosts')
            with self.assertRaisesRegex(ValueError, 'symlink'): check_public(public)

    def test_clean_explicit_checkpoint_and_external_exclusive_output(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'source'; source.mkdir()
            def git(*args):
                return subprocess.check_output(['git', '-C', str(source), *args], stderr=subprocess.DEVNULL)
            git('init'); git('config', 'user.email', 'test@example.invalid'); git('config', 'user.name', 'Synthetic test')
            (source / 'file').write_text('fixture'); git('add', '.'); git('commit', '-m', 'fixture')
            sha = git('rev-parse', 'HEAD').decode().strip(); verify_source(source, sha)
            for wrong in ('main', '0' * 40):
                with self.assertRaises(ValueError): verify_source(source, wrong)
            with self.assertRaisesRegex(ValueError, 'outside'):
                assemble(source, source, sha, sha, source / 'output')
            with self.assertRaisesRegex(ValueError, 'exists'):
                assemble(source, source, sha, sha, Path(temp))
            (source / 'untracked').write_text('unexpected')
            with self.assertRaisesRegex(ValueError, 'changes'): verify_source(source, sha)
            (source / 'untracked').unlink(); (source / 'file').write_text('dirty')
            with self.assertRaisesRegex(ValueError, 'changes'): verify_source(source, sha)

    def test_assembly_copies_committed_bytes_and_records_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); valuation = root / 'valuation'; portfolio = root / 'portfolio'
            valuation.mkdir(); portfolio.mkdir()
            source_public = root / 'source-public'; fixture(source_public)
            for name in PORTFOLIO_FILES: (portfolio / name).write_bytes((source_public / name).read_bytes())
            (valuation / 'firebase.combined-preview.json').write_bytes((ROOT / 'firebase.combined-preview.json').read_bytes())
            def fake_git(repo, *args):
                if args[0] == 'ls-tree': return b'100644 blob hash file'
                if args[0] == 'show': return (portfolio / args[1].split(':')[1]).read_bytes()
                raise AssertionError(args)
            def build(command, **kwargs):
                self.assertIn('--base=/valuation/', command)
                dest = Path(command[-1]); dest.mkdir()
                import shutil
                shutil.copytree(source_public / 'valuation', dest, dirs_exist_ok=True)
            with patch('assemble_combined_preview.verify_source'), patch('assemble_combined_preview.git', fake_git), patch('assemble_combined_preview.subprocess.run', build):
                out = root / 'assembled'; manifest = assemble(valuation, portfolio, 'a'*40, 'b'*40, out)
            self.assertEqual(manifest['valuation_commit'], 'a'*40)
            self.assertEqual(manifest['files'], check_public(out / 'public'))
            self.assertFalse((out / 'public/manifest.json').exists())
            for name in PORTFOLIO_FILES:
                self.assertEqual((out / 'public' / name).read_bytes(), (portfolio / name).read_bytes())


class RoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(); cls.public = Path(cls.temp.name) / 'public'; fixture(cls.public)
        CombinedHandler.public = cls.public
        CombinedHandler.hosting = json.loads((ROOT / 'firebase.combined-preview.json').read_text())['hosting']
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), CombinedHandler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join(); cls.temp.cleanup()

    def request(self, path, headers=None):
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        try:
            connection.request('GET', path, headers=headers or {}); response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally: connection.close()

    def test_portfolio_exact_files_aliases_and_real_404(self):
        for name in PORTFOLIO_FILES:
            self.assertEqual(self.request('/' + name)[2], (self.public / name).read_bytes())
        self.assertEqual(self.request('/')[2], (self.public / 'index.html').read_bytes())
        for stem in ('featured', 'project-pipeline', 'work', 'contact'):
            self.assertEqual(self.request('/' + stem)[2], (self.public / (stem + '.html')).read_bytes())
        for path in ('/unknown', '/src/', '/.git/config', '/apix', '/%2e%2e/private', '/api-extra'):
            self.assertEqual(self.request(path)[0], 404)

    def test_subpath_redirect_assets_and_scoped_refresh(self):
        status, headers, _ = self.request('/valuation?review=1')
        self.assertEqual(status, 301); self.assertEqual(headers['Location'], '/valuation/?review=1')
        for path in ('/valuation/', '/valuation/review', '/valuation/review?x=1'):
            self.assertEqual(self.request(path)[2], (self.public / 'valuation/index.html').read_bytes())
        status, headers, body = self.request('/valuation/assets/index-test.js')
        self.assertEqual(status, 200); self.assertIn('immutable', headers['Cache-Control'])
        self.assertIn(b'/api/v1/catalog', body)

    def test_api_errors_json_no_fallback_and_loopback_guard(self):
        for path in ('/api', '/api/missing', '/api/v1/cases/run'):
            status, headers, body = self.request(path)
            self.assertEqual(status, 404); self.assertIn('application/json', headers['Content-Type'])
            self.assertEqual(headers['Cache-Control'], 'no-store'); self.assertIn('error', json.loads(body))
        self.assertEqual(self.request('/', {'Host': 'evil.invalid'})[0], 403)

    def test_configuration_has_no_global_fallback_and_retains_api_first(self):
        config = CombinedHandler.hosting
        self.assertEqual(config['site'], 'kartikchaturvedi-website')
        self.assertEqual(config['rewrites'][0]['source'], '/api{,/**}')
        self.assertEqual(config['rewrites'][0]['run'], dict(serviceId='valuation-api-preview', region='us-central1', pinTag=True))
        self.assertEqual(config['rewrites'][-1], dict(source='/valuation/**', destination='/valuation/index.html'))
        self.assertNotIn('**', [r['source'] for r in config['rewrites']])


if __name__ == '__main__':
    unittest.main()
