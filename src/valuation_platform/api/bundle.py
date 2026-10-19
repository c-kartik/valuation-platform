"""Allowlisted, byte-preserving private bundle; no runtime generation."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil

CONFIG = Path(__file__).with_name('bundle-files.json')
MANIFEST = 'runtime-manifest.json'


def configuration():
    return json.loads(CONFIG.read_text(encoding='utf-8'))


def _file(root, name):
    path = root / name
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Invalid private bundle file')
    return path


def _entry(root, name):
    content = _file(root, name).read_bytes()
    return {'path': name, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}


def verify_bundle(root):
    """Check exact allowlist/hash manifest and pinned resource bytes, no activation."""
    root = Path(root).resolve()
    config = configuration()
    try:
        manifest = json.loads(_file(root, MANIFEST).read_text(encoding='utf-8'))
        names = sorted(config['python_files'] + list(config['resources']) + ['src/valuation_platform/api/bundle-files.json'])
        expected = {'schema_version': 'local-case-runtime-v1', 'files': [_entry(root, n) for n in names]}
        if manifest != expected:
            raise ValueError('Manifest mismatch')
        for name, digest in config['resources'].items():
            if _entry(root, name)['sha256'] != digest:
                raise ValueError('Pinned resource mismatch')
        return manifest
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError('Private runtime bundle is missing or failed integrity verification') from exc


def build_bundle(source_root, destination):
    """Offline build, outside source tree, exclusive destination; copied bytes only."""
    root, destination = Path(source_root).resolve(), Path(destination).resolve()
    if destination.is_relative_to(root) or destination.exists():
        raise ValueError('Choose a new bundle directory outside the source repository')
    config = configuration()
    names = sorted(config['python_files'] + list(config['resources']) + ['src/valuation_platform/api/bundle-files.json'])
    for name, digest in config['resources'].items():
        if _entry(root, name)['sha256'] != digest:
            raise ValueError('Source resource differs from reviewed pin')
    destination.mkdir(parents=True, exist_ok=False)
    try:
        for name in names:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(_file(root, name), target)
        manifest = {'schema_version': 'local-case-runtime-v1', 'files': [_entry(destination, n) for n in names]}
        (destination / MANIFEST).write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        verify_bundle(destination)
        # Only the newly created bundle is chmod'd; never working originals.
        for path in destination.rglob('*'):
            if path.is_file():
                path.chmod(0o444)
        for path in sorted(destination.rglob('*'), key=lambda p: len(p.parts), reverse=True):
            if path.is_dir():
                path.chmod(0o555)
        destination.chmod(0o555)
        return manifest
    except BaseException:
        remove_bundle(destination)
        raise


def remove_bundle(root):
    """Cleanup helper for build failures/tests of our own read-only temporary copy."""
    root = Path(root)
    for p in [root, *root.rglob('*')]:
        if p.is_dir():
            p.chmod(0o755)
    shutil.rmtree(root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    result = build_bundle(root, args.destination)
    print(f"Built verified read-only private bundle: {len(result['files'])} files")


if __name__ == '__main__':
    main()
