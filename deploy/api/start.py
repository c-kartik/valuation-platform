"""Container launcher: one API process, existing calculation limits, PORT support."""

import os
import sys


def command(environ):
    port = environ.get('PORT', '8080')
    if not port.isascii() or not port.isdecimal() or not 1 <= int(port) <= 65535:
        raise ValueError('PORT must be an integer from 1 to 65535')
    return [sys.executable, '-m', 'uvicorn',
            'valuation_platform.api.app:create_app', '--factory',
            '--host', '0.0.0.0', '--port', port, '--workers', '1',
            '--limit-concurrency', '16', '--backlog', '32',
            '--timeout-keep-alive', '5', '--timeout-graceful-shutdown', '2',
            '--no-access-log']


if __name__ == '__main__':
    os.execv(sys.executable, command(os.environ))
