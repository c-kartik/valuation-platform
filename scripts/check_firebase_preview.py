"""Read-only check of the deliberately small Firebase public artifact.

No Firebase/cloud call or provisioning; site identity must be reviewed separately.
"""

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT, *, for_deploy=False):
    config = json.loads((root / 'firebase.preview.json').read_text())['hosting']
    if config['public'] != 'frontend/dist':
        raise ValueError('Only frontend/dist is approved as the public root.')
    if for_deploy and not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,62}', config['site']):
        raise ValueError('Existing Hosting site identity is unresolved; do not deploy.')
    public = root / 'frontend/dist'
    if public.is_symlink():
        raise ValueError('Public root must not be a symlink.')
    files = []
    for file in public.rglob('*'):
        if file.is_symlink():
            raise ValueError('Symlinks are not approved in the public artifact.')
        if file.is_file():
            name = file.relative_to(public).as_posix()
            if name not in ('index.html', 'favicon.svg') and not re.fullmatch(r'assets/index-[A-Za-z0-9_-]+\.(js|css)', name):
                raise ValueError('Unexpected file in the public artifact; inspect before publishing.')
            files.append(file)
    names = {file.relative_to(public).as_posix() for file in files}
    if (len(files) != 4 or not {'index.html', 'favicon.svg'} <= names
            or sum(name.endswith('.js') for name in names) != 1
            or sum(name.endswith('.css') for name in names) != 1):
        raise ValueError('Build must contain index, favicon, one hashed JS and one hashed CSS file.')
    if sum(file.stat().st_size for file in files) > 2 * 1024 * 1024:
        raise ValueError('Public artifact exceeds the reviewed 2 MiB size ceiling.')
    data = b'\n'.join(file.read_bytes() for file in files)
    for marker in (b'-----BEGIN PRIVATE KEY', b'-----BEGIN RSA PRIVATE KEY',
                   b'Bearer ', b'print-identity-token', b'/Users/kc/',
                   b'runtime-manifest.json', b'run.app'):
        if marker in data:
            raise ValueError('Unexpected credential/private/target marker; inspect without printing it.')
    index = (public / 'index.html').read_text()
    references = re.findall(r'(?:src|href)="([^"]+)"', index)
    if not references or any(ref.lstrip('/') not in names for ref in references):
        raise ValueError('Index references must resolve only to the reviewed public files.')
    if b'/api/v1/catalog' not in data or b'/api/v1/cases/' not in data:
        raise ValueError('Expected relative API contract is absent.')
    return sorted(names)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--for-deploy', action='store_true')
    args = parser.parse_args()
    try:
        names = check(for_deploy=args.for_deploy)
    except (ValueError, OSError, KeyError) as exc:
        raise SystemExit(str(exc)) from None
    print('Public artifact scope passed: ' + ', '.join(names))
