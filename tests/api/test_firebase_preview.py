"""Local publication/configuration guards, not Firebase emulator/cloud proof."""

import json
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
check = runpy.run_path(str(ROOT / 'scripts/check_firebase_preview.py'))['check']


class FirebasePreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = json.loads((ROOT / 'firebase.preview.json').read_text())
        (self.root / 'firebase.preview.json').write_text(json.dumps(self.config))
        self.public = self.root / 'frontend/dist'
        (self.public / 'assets').mkdir(parents=True)
        (self.public / 'index.html').write_text('<script src="/assets/index-test.js"></script><link href="/assets/index-test.css"><link href="/favicon.svg">')
        (self.public / 'favicon.svg').write_text('<svg/>')
        (self.public / 'assets/index-test.js').write_text('"/api/v1/catalog";"/api/v1/cases/";')
        (self.public / 'assets/index-test.css').write_text('body{}')

    def test_api_rewrite_precedes_spa_and_pins_only_future_service(self):
        hosting = self.config['hosting']
        self.assertEqual(hosting['public'], 'frontend/dist')
        self.assertEqual(hosting['site'], 'kartikchaturvedi-website')
        self.assertEqual(hosting['rewrites'], [
            {'source': '/api{,/**}', 'run': {'serviceId': 'valuation-api-public-preview', 'region': 'us-central1', 'pinTag': True}},
            {'source': '**', 'destination': '/index.html'}])
        self.assertNotIn('functions', self.config)
        self.assertNotIn('valuation-api-staging', json.dumps(self.config))
        self.assertEqual(hosting['headers'][-1], {'source': '/api{,/**}', 'headers': [{'key': 'Cache-Control', 'value': 'no-store'}]})

    def test_artifact_and_resolved_site_pass_but_unresolved_site_fails_closed(self):
        self.assertEqual(len(check(self.root)), 4)
        self.assertEqual(len(check(self.root, for_deploy=True)), 4)
        self.config['hosting']['site'] = 'UNRESOLVED_EXISTING_HOSTING_SITE'
        (self.root / 'firebase.preview.json').write_text(json.dumps(self.config))
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            check(self.root, for_deploy=True)

    def test_private_files_symlinks_markers_and_wrong_root_reject(self):
        for name in ('case.json', '.env', 'assets/index-test.js.map', 'docs/evidence.txt'):
            file = self.public / name
            file.parent.mkdir(exist_ok=True)
            file.write_text('not public')
            with self.subTest(name=name), self.assertRaises(ValueError): check(self.root)
            file.unlink()
        file = self.public / 'outside.svg'
        file.symlink_to(self.root / 'firebase.preview.json')
        with self.assertRaisesRegex(ValueError, 'Symlinks'): check(self.root)
        file.unlink()
        (self.public / 'assets/index-test.js').write_text('Bearer TEST_SENTINEL')
        with self.assertRaisesRegex(ValueError, 'marker'): check(self.root)
        self.config['hosting']['public'] = '.'
        (self.root / 'firebase.preview.json').write_text(json.dumps(self.config))
        with self.assertRaisesRegex(ValueError, 'public root'): check(self.root)

    def test_external_or_missing_static_reference_rejects(self):
        for target in ('https://untrusted.example/code.js', '/private.json'):
            (self.public / 'index.html').write_text(f'<script src="{target}"></script>')
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, 'references'): check(self.root)


if __name__ == '__main__':
    unittest.main()
