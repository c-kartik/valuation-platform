"""Loopback harness checks; these do not authenticate or invoke Cloud Run."""

from http.client import HTTPConnection, BadStatusLine
from http.server import ThreadingHTTPServer
from pathlib import Path
import runpy
import socket
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch, MagicMock


module = runpy.run_path(str(Path(__file__).resolve().parents[2] / 'scripts/preview_cloud_frontend.py'))
Handler = module['PreviewHandler']
GLOBALS = Handler.handle_request.__globals__


class FrontendPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name) / 'dist'
        cls.root.mkdir()
        (cls.root / 'index.html').write_bytes(b'<html>compiled</html>')
        (cls.root / 'app.js').write_bytes(b'compiled javascript')
        private = Path(cls.temp.name) / 'private.json'
        private.write_text('not public')
        (cls.root / 'escape.json').symlink_to(private)
        cls.root_patch = patch.dict(GLOBALS, ROOT=cls.root)
        cls.root_patch.start()
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.root_patch.stop()
        cls.temp.cleanup()

    def request(self, path='/', method='GET', body=None, headers=None):
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        try:
            connection.request(method, path, body, headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_only_built_assets_no_traversal_directory_or_symlink(self):
        status, headers, body = self.request()
        self.assertEqual((status, body), (200, b'<html>compiled</html>'))
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertIn("connect-src 'self'", headers['Content-Security-Policy'])
        self.assertEqual(self.request('/app.js')[0], 200)
        for path in ('/../private.json', '/%2e%2e/private.json', '/private.json',
                     '/escape.json', '/src/', '/app.js?url=http://example.com'):
            with self.subTest(path=path):
                self.assertEqual(self.request(path)[0], 404)
        self.assertEqual(self.request('http://example.com/api/v1/catalog')[0], 403)

    def test_host_and_origin_are_loopback_only(self):
        for headers in ({'Host': 'evil.example'}, {'Origin': 'https://evil.example'},
                        {'Sec-Fetch-Site': 'cross-site'}):
            with self.subTest(headers=headers):
                self.assertEqual(self.request(headers=headers)[0], 403)

    def test_known_routes_only(self):
        for path, method in (('/api/private', 'GET'), ('/api/v1/cases/run', 'GET'),
                             ('/api/v1/catalog', 'POST')):
            self.assertEqual(self.request(path, method, b'{}' if method == 'POST' else None)[0], 404)
        self.assertEqual(self.request('/index.html', 'POST', b'{}')[0], 405)

    def test_body_budget_type_and_framing(self):
        path = '/api/v1/cases/run'
        for headers, status in (({'Content-Length': '262145'}, 413),
                                ({'Content-Length': '9' * 5000}, 413),
                                ({'Content-Length': 'x'}, 400),
                                ({'Transfer-Encoding': 'chunked'}, 400)):
            self.assertEqual(self.request(path, 'POST', b'', headers)[0], status)
        self.assertEqual(self.request(path, 'POST', b'{}', {'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.request('/', headers={'Content-Length': '1'})[0], 400)

    def test_forward_preserves_status_body_content_type_without_credentials(self):
        remote = MagicMock()
        remote.getresponse.return_value.status = 422
        remote.getresponse.return_value.read.return_value = b'{"error":"synthetic"}'
        remote.getresponse.return_value.getheader.return_value = 'application/json; charset=utf-8'
        with patch.dict(GLOBALS, HTTPConnection=MagicMock(return_value=remote)):
            status, headers, body = self.request('/api/v1/cases/run', 'POST', b'{"x":"1"}',
                {'Content-Type': 'application/json', 'Authorization': 'never-forward', 'Cookie': 'never-forward'})
            self.assertEqual((status, body), (422, b'{"error":"synthetic"}'))
            self.assertEqual(headers['Content-Type'], 'application/json; charset=utf-8')
            self.assertEqual(headers['Cache-Control'], 'no-store')
            GLOBALS['HTTPConnection'].assert_called_once_with('127.0.0.1', 8000, timeout=48)
            remote.request.assert_called_once_with('POST', '/api/v1/cases/run', body=b'{"x":"1"}',
                                                   headers={'Content-Type': 'application/json'})
            remote.close.assert_called_once()

    def test_bounded_upstream_failure_and_large_response(self):
        for exception, expected in ((socket.timeout(), 504), (ConnectionRefusedError(), 502),
                                    (BadStatusLine('malformed'), 502)):
            remote = MagicMock()
            remote.request.side_effect = exception
            with patch.dict(GLOBALS, HTTPConnection=MagicMock(return_value=remote)):
                self.assertEqual(self.request('/api/v1/catalog')[0], expected)
                remote.close.assert_called_once()
        remote = MagicMock()
        remote.getresponse.return_value.read.return_value = b'x' * (2 * 1024 * 1024 + 1)
        with patch.dict(GLOBALS, HTTPConnection=MagicMock(return_value=remote)):
            self.assertEqual(self.request('/api/v1/catalog')[0], 502)
            remote.getresponse.return_value.read.assert_called_once_with(2 * 1024 * 1024 + 1)


if __name__ == '__main__':
    unittest.main()
