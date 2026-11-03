"""Verify the retained primary research bodies, searchable text and excerpts offline."""
import gzip
import hashlib
import json
from pathlib import Path


def verify(root=Path(__file__).resolve().parent):
    sources=json.loads((root/'source-manifest.json').read_text())['sources']
    by_id={s['id']:s for s in sources}
    if len(by_id)!=15:raise ValueError('Expected fifteen reviewed primary sources')
    for s in sources:
        body=(root/s['local_file']).read_bytes()
        if s.get('storage_encoding')=='gzip':body=gzip.decompress(body)
        if hashlib.sha256(body).hexdigest()!=s['sha256']:raise ValueError('Primary research body hash changed')
        if hashlib.sha256((root/s['text_file']).read_bytes()).hexdigest()!=s['text_sha256']:raise ValueError('Search text changed')
    excerpts=json.loads((root/'disclosure-excerpts.json').read_text())
    for e in excerpts:
        s=by_id[e['source_id']]
        lines=(root/e['text_file']).read_text().splitlines()
        if e['source_url']!=s['url'] or e['source_sha256']!=s['sha256'] or '\n'.join(lines[e['line_start']-1:e['line_end']])!=e['excerpt']:
            raise ValueError('Research excerpt binding changed')
    return dict(source_hashes_verified=len(sources),exact_excerpts_verified=len(excerpts))

if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
