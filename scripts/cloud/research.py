"""Verify and restore the exact original 42-company audit, without executing it."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

ROOT=Path(__file__).resolve().parents[2]
SNAPSHOT=Path('research/historical-cashflows-42-2026-11-02')


def digest(body):return hashlib.sha256(body).hexdigest()


def verify(root=ROOT):
    folder=root/SNAPSHOT;manifest=json.loads((folder/'manifest.json').read_text())
    archive=folder/manifest['archive_file']
    if manifest['schema_version']!='portable-research-snapshot-v1' or digest(archive.read_bytes())!=manifest['archive_sha256']:
        raise ValueError('Research archive differs from retained original')
    expected={r['path']:r for r in manifest['files']}
    if len(expected)!=len(manifest['files']):raise ValueError('Duplicate research member')
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist()
        if len(infos)!=len(expected) or {i.filename for i in infos}!=set(expected):raise ValueError('Archive member inventory changed')
        for info in infos:
            name=PurePosixPath(info.filename);mode=info.external_attr>>16
            if name.is_absolute() or '..' in name.parts or '\\' in info.filename or name.parts[0]!='historical-cashflows-42' or info.is_dir() or stat.S_ISLNK(mode):
                raise ValueError('Unsafe research archive path/type')
            row=expected[info.filename]
            if info.file_size!=row['bytes'] or digest(z.read(info))!=row['sha256']:raise ValueError('Research member size/hash changed')
    return manifest


def restore(root=ROOT):
    manifest=verify(root);destination=root/'.cloud/research'
    # Validate the full archive before writing. Only an ignored extraction copy
    # is created; neither the original bytes nor company decisions are changed.
    if destination.is_symlink() or not destination.resolve().is_relative_to(root.resolve()):
        raise ValueError('Research destination must stay inside this checkout')
    with zipfile.ZipFile(root/SNAPSHOT/manifest['archive_file']) as z:
        for row in manifest['files']:
            path=destination/row['path']
            if not path.resolve().is_relative_to(destination.resolve()):raise ValueError('Research path escapes destination')
            if path.exists():
                if path.is_symlink() or not path.is_file() or digest(path.read_bytes())!=row['sha256']:
                    raise ValueError('Research extraction changed; preserve it and use a fresh checkout')
                continue
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(row['path']))
    return destination/'historical-cashflows-42'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
    if args.check:
        m=verify();print(f"Verified {len(m['files'])} original research artifacts")
    else:print(restore())

if __name__=='__main__':main()
