"""Loopback combined artifact review using the existing local API on port 8000.

Models the explicit redirects, files, page aliases and calculator-only fallback;
not an emulator of Firebase infrastructure. Never serves either source repository.
"""

import argparse
import json
import mimetypes
from pathlib import Path
from urllib.parse import urlsplit, unquote
from http.server import ThreadingHTTPServer

from assemble_combined_preview import check_public
from preview_cloud_frontend import PreviewHandler


class CombinedHandler(PreviewHandler):
    public = None
    hosting = None

    def reply(self, status, body, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        path = urlsplit(self.path).path
        for rule in self.hosting['headers']:
            if rule['source'] == '**' or (rule['source'] == '/valuation/assets/**'
                    and path.startswith('/valuation/assets/')):
                for header in rule['headers']:
                    # Set cache policy once, reflecting Hosting's last match.
                    if header['key'] != 'Cache-Control':
                        self.send_header(header['key'], header['value'])
        cache = ('public, max-age=31536000, immutable' if path.startswith('/valuation/assets/')
                 and status == 200 else 'no-store')
        self.send_header('Cache-Control', cache)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def handle_request(self):
        url = urlsplit(self.path)
        expected = f'127.0.0.1:{self.server.server_port}'
        if (self.headers.get_all('Host', []) != [expected]
                or self.headers.get('Origin', f'http://{expected}') != f'http://{expected}'
                or self.headers.get('Sec-Fetch-Site') == 'cross-site'):
            return self.error(403, 'Use the documented loopback preview origin.')
        if url.scheme or url.netloc or url.fragment:
            return self.error(404, 'Unknown preview route.')
        path = unquote(url.path)
        if path == '/api' or path.startswith('/api/'):
            # Reuse the bounded framing/proxy implementation; it never forwards credentials.
            return super().handle_request()
        if self.command != 'GET':
            return self.error(405, 'Static preview supports GET only.')
        if self.headers.get('Transfer-Encoding') or self.headers.get('Content-Length', '0') != '0':
            return self.error(400, 'Static requests do not accept bodies.')
        if '..' in path.split('/') or '\\' in path or '\x00' in path:
            return self.error(404, 'Unknown preview route.')
        if path == '/valuation':
            self.send_response(301)
            self.send_header('Location', '/valuation/' + ('?' + url.query if url.query else ''))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        name = 'index.html' if path == '/' else path.lstrip('/')
        if path == '/valuation/':
            name = 'valuation/index.html'
        file = self.public / name
        if not file.is_file():
            for rewrite in self.hosting['rewrites']:
                if rewrite['source'] == path and 'destination' in rewrite:
                    file = self.public / rewrite['destination'].lstrip('/')
                    break
            else:
                if path.startswith('/valuation/'):
                    file = self.public / 'valuation/index.html'
        if not file.is_file() or file.is_symlink() or self.public.resolve() not in file.resolve().parents:
            return self.reply(404, b'<!doctype html><title>Not found</title><h1>Page not found</h1>', 'text/html; charset=utf-8')
        self.reply(200, file.read_bytes(), mimetypes.guess_type(file.name)[0] or 'application/octet-stream')

    do_GET = handle_request
    do_POST = handle_request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifact', type=Path)
    parser.add_argument('--port', type=int, default=8088)
    args = parser.parse_args()
    artifact = args.artifact.resolve()
    public = artifact / 'public'
    if check_public(public) != json.loads((artifact / 'manifest.json').read_text())['files']:
        raise SystemExit('Artifact differs from the reviewed manifest.')
    CombinedHandler.public = public
    CombinedHandler.hosting = json.loads((artifact / 'firebase.json').read_text())['hosting']
    server = ThreadingHTTPServer(('127.0.0.1', args.port), CombinedHandler)
    print(f'Combined review: http://127.0.0.1:{args.port}/ (local API 127.0.0.1:8000)', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
