"""Assemble only reviewed portfolio files and a /valuation/ Vite build.

No cloud calls. Output must be new and outside both source repositories.
The manifest/config are siblings of public/, never published website files.
"""

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_FILES = (
    'index.html', 'featured.html', 'project-pipeline.html', 'work.html',
    'contact.html', 'style.css', 'profile.jpg', 'resume.pdf', 'robots.txt', 'sitemap.xml',
)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def verify_source(root, commit):
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Supply a full source commit SHA.')
    if git(root, 'rev-parse', 'HEAD').decode().strip() != commit:
        raise ValueError('Source HEAD differs from the requested checkpoint.')
    if git(root, 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Source has unexpected tracked or untracked changes; review first.')


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('src', 'href'):
            if key in attrs:
                self.links.append(attrs[key])


def check_public(public):
    """Exact publication boundary, byte hashes and every local HTML reference."""
    if public.is_symlink():
        raise ValueError('Public root cannot be a symlink.')
    files = {}
    for file in public.rglob('*'):
        if file.is_symlink():
            raise ValueError('Public symlinks are forbidden.')
        if file.is_file():
            name = file.relative_to(public).as_posix()
            if name not in PORTFOLIO_FILES and name not in (
                'valuation/index.html', 'valuation/favicon.svg'
            ) and not re.fullmatch(r'valuation/assets/index-[\w-]+\.(js|css)', name):
                raise ValueError('Unexpected public file; inspect without publishing.')
            files[name] = file
    if (len(files) != 14 or not set(PORTFOLIO_FILES) <= files.keys()
            or sum(n.endswith('.js') for n in files) != 1
            or sum(n.startswith('valuation/assets/') and n.endswith('.css') for n in files) != 1
            or not {'valuation/index.html', 'valuation/favicon.svg'} <= files.keys()):
        raise ValueError('Expected ten portfolio files and four compiled calculator files.')
    if sum(p.stat().st_size for p in files.values()) > 10 * 1024 * 1024:
        raise ValueError('Combined artifact exceeds the reviewed 10 MiB ceiling.')
    parsed = {}
    for name, file in files.items():
        data = file.read_bytes()
        for marker in (b'-----BEGIN PRIVATE KEY', b'-----BEGIN RSA PRIVATE KEY',
                       b'Bearer ', b'/Users/kc/', b'runtime-manifest.json',
                       b'AIza', b'ghp_', b'-----BEGIN OPENSSH PRIVATE KEY'):
            if marker in data:
                raise ValueError('Potential private marker in artifact; inspect without printing it.')
        if name.endswith('.html'):
            parser = References()
            parser.feed(data.decode())
            parsed[name] = parser
    for name, parser in parsed.items():
        for ref in parser.links:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            target = unquote(url.path)
            if target.startswith('/'):
                target = target.lstrip('/')
            else:
                target = (Path(name).parent / target).as_posix() if target else name
            if target.endswith('/') or not target:
                target += 'index.html'
            if target not in files:
                raise ValueError(f'Broken local reference in {name}: {ref}')
            if url.fragment and (target not in parsed or url.fragment not in parsed[target].ids):
                raise ValueError(f'Broken local fragment in {name}: {ref}')
    index = files['valuation/index.html'].read_text()
    if '/valuation/assets/' not in index or '/valuation/favicon.svg' not in index:
        raise ValueError('Calculator must be explicitly built for /valuation/.')
    script = next(p for n, p in files.items() if n.endswith('.js')).read_bytes()
    if b'/api/v1/catalog' not in script or b'/api/v1/cases/' not in script:
        raise ValueError('Same-origin root API paths must be retained.')
    return {name: hashlib.sha256(file.read_bytes()).hexdigest() for name, file in sorted(files.items())}


def assemble(valuation, portfolio, valuation_commit, portfolio_commit, output):
    valuation, portfolio, output = (Path(p).resolve() for p in (valuation, portfolio, output))
    for source, commit in ((valuation, valuation_commit), (portfolio, portfolio_commit)):
        verify_source(source, commit)
        if output == source or source in output.parents:
            raise ValueError('Output must be outside both repositories.')
    if output.exists():
        raise ValueError('Output already exists; use a new destination.')
    # Build from the clean checkout with its existing lockfile-installed tooling.
    with tempfile.TemporaryDirectory(prefix='combined-calculator-build-') as temp:
        build = Path(temp) / 'dist'
        subprocess.run(['npm', '--prefix', str(valuation / 'frontend'), 'run', 'build', '--',
                        '--base=/valuation/', '--outDir', str(build)], check=True)
        verify_source(valuation, valuation_commit)
        verify_source(portfolio, portfolio_commit)
        output.mkdir()
        public = output / 'public'
        public.mkdir()
        for name in PORTFOLIO_FILES:
            mode = git(portfolio, 'ls-tree', portfolio_commit, '--', name).split()[0]
            if mode != b'100644':
                raise ValueError('Portfolio publication accepts regular committed files only.')
            (public / name).write_bytes(git(portfolio, 'show', f'{portfolio_commit}:{name}'))
        for file in build.rglob('*'):
            if file.is_symlink():
                raise ValueError('Build contains a symlink.')
            if file.is_file():
                dest = public / 'valuation' / file.relative_to(build)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(file.read_bytes())
        hashes = check_public(public)
        config = json.loads((valuation / 'firebase.combined-preview.json').read_text())
        config['hosting']['public'] = str(public)
        (output / 'firebase.json').write_text(json.dumps(config, indent=2) + '\n')
        manifest = dict(valuation_commit=valuation_commit, portfolio_commit=portfolio_commit,
                        calculator_base='/valuation/', files=hashes)
        (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--valuation', type=Path, required=True)
    parser.add_argument('--portfolio', type=Path, required=True)
    parser.add_argument('--valuation-commit', required=True)
    parser.add_argument('--portfolio-commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = assemble(args.valuation, args.portfolio, args.valuation_commit,
                            args.portfolio_commit, args.output)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc)) from None
    print(f"Combined artifact: {len(manifest['files'])} reviewed files; manifest outside public/.")


if __name__ == '__main__':
    main()
