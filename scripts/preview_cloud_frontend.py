"""Loopback compiled-frontend preview; Google credentials stay in gcloud's proxy.

Start the authenticated Cloud Run proxy on the selected loopback port first.
This is an engineering preview, not a public hosting/authentication boundary.
"""

import argparse
import re

from http.client import HTTPConnection, HTTPException
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1] / 'frontend' / 'dist'
BODY_LIMIT = 256 * 1024
RESULT_LIMIT = 2 * 1024 * 1024
UPSTREAM_TIMEOUT = 48
ROUTES = {
    ('GET', '/api/v1/catalog'),
    ('POST', '/api/v1/cases/validate'),
    ('POST', '/api/v1/cases/run'),
    *{('POST', f'/api/v1/{tool}/{action}')
      for tool in ('scenarios', 'sensitivity', 'reverse')
      for action in ('validate', 'run')},
}


class PreviewHandler(BaseHTTPRequestHandler):
    # Close every connection: framing failures cannot become a second request.
    protocol_version = 'HTTP/1.0'
    server_version = 'LoopbackPreview'
    sys_version = ''

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, *args):
        pass  # Never log bodies, URLs, tokens or forwarded response contents.

    def reply(self, status, body, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy',
                         "default-src 'self'; connect-src 'self'; img-src 'self' data:; "
                         "style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def error(self, status, message):
        self.reply(status, json.dumps({'error': {'code': 'preview_error',
                                               'message': message}}).encode())

    def handle_request(self):
        host = self.headers.get_all('Host', [])
        expected = f'127.0.0.1:{self.server.server_port}'
        if host != [expected]:
            return self.error(403, 'Use the documented 127.0.0.1 preview URL.')
        origin = self.headers.get('Origin')
        if origin and origin != f'http://{expected}':
            return self.error(403, 'Cross-origin preview requests are not allowed.')
        if self.headers.get('Sec-Fetch-Site') == 'cross-site':
            return self.error(403, 'Cross-site preview requests are not allowed.')
        path = urlsplit(self.path)
        if path.scheme or path.netloc or path.query or path.fragment:
            return self.error(404, 'Unknown preview route.')
        if self.headers.get_all('Transfer-Encoding'):
            return self.error(400, 'Transfer-Encoding is not supported.')
        lengths = self.headers.get_all('Content-Length', [])
        if len(lengths) > 1 or (lengths and (not lengths[0].isascii() or not lengths[0].isdigit())):
            return self.error(400, 'A single decimal Content-Length is required.')
        if lengths and len(lengths[0]) > 8:
            return self.error(413, 'Request exceeds the 256 KiB preview limit.')
        length = int(lengths[0]) if lengths else 0
        if length > BODY_LIMIT:
            return self.error(413, 'Request exceeds the 256 KiB preview limit.')
        if self.command == 'POST' and not lengths:
            return self.error(411, 'Content-Length is required.')
        if self.command != 'POST' and length:
            return self.error(400, 'This method does not accept a request body.')
        if path.path.startswith('/api'):
            if (self.command, path.path) not in ROUTES:
                return self.error(404, 'Unknown API preview route.')
            if self.command == 'POST' and self.headers.get_content_type() != 'application/json':
                return self.error(415, 'Use application/json.')
            try:
                body = self.rfile.read(length)
            except (socket.timeout, OSError):
                return self.error(408, 'Request body read timed out.')
            if len(body) != length:
                return self.error(400, 'Incomplete request body.')
            return self.forward(path.path, body)
        if self.command != 'GET':
            return self.error(405, 'Static preview supports GET only.')
        # Exact build-file map: no fallback into source, directories or symlinks.
        static = {'/' + f.relative_to(ROOT).as_posix(): f for f in ROOT.rglob('*')
                  if f.is_file() and not f.is_symlink() and ROOT.resolve() in f.resolve().parents
                  and public_file(f.relative_to(ROOT).as_posix())}
        aliases = {'/': '/index.html', '/workspace/': '/workspace/index.html'}
        file = static.get(aliases.get(path.path, path.path))
        if file is None:
            return self.error(404, 'Unknown static preview file.')
        types = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript',
                 '.css': 'text/css', '.svg': 'image/svg+xml'}
        self.reply(200, file.read_bytes(), types.get(file.suffix, 'application/octet-stream'))

    def forward(self, path, body):
        upstream = HTTPConnection('127.0.0.1', getattr(self.server, 'upstream_port', 8000), timeout=UPSTREAM_TIMEOUT)
        try:
            # Only the content type is forwarded; never browser cookies/auth/target headers.
            headers = {'Content-Type': self.headers.get('Content-Type', 'application/json')}
            upstream.request(self.command, path, body=body or None, headers=headers)
            response = upstream.getresponse()
            data = response.read(RESULT_LIMIT + 1)
            if len(data) > RESULT_LIMIT:
                return self.error(502, 'Upstream response exceeded the preview limit.')
            self.reply(response.status, data, response.getheader('Content-Type', 'application/json'))
        except (socket.timeout, TimeoutError):
            self.error(504, 'Authenticated local proxy timed out; inputs remain in the browser.')
        except (OSError, ValueError, HTTPException):
            self.error(502, 'Cannot reach the authenticated loopback proxy; inputs remain in the browser.')
        finally:
            upstream.close()

    do_GET = handle_request
    do_POST = handle_request


def public_file(name):
    return name in ('index.html', 'workspace/index.html', 'favicon.svg') or bool(
        re.fullmatch(r'assets/[A-Za-z0-9_-]+\.(?:js|css)', name))


def local_port(value):
    if not value.isascii() or not value.isdecimal() or not 1 <= int(value) <= 65535:
        raise argparse.ArgumentTypeError('Use a port from 1 to 65535.')
    return int(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=local_port, default=4173)
    parser.add_argument('--proxy-port', type=local_port, default=8000)
    args = parser.parse_args()
    if not (ROOT / 'index.html').is_file():
        raise SystemExit('Build first: npm --prefix frontend run build')
    server = ThreadingHTTPServer(('127.0.0.1', args.port), PreviewHandler)
    server.upstream_port = args.proxy_port
    print(f'Compiled preview: http://127.0.0.1:{args.port}/workspace/ '
          f'(authenticated proxy: 127.0.0.1:{args.proxy_port})', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
