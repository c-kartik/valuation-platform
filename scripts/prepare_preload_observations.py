"""Replay reviewed primary-source mappings for registered issuer preload datasets.

No network, forecast selection, anchor promotion or historical-package writes.
The source snapshots and mapping are inputs; observations are derived records.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from valuation_platform.preload.extract import inline_document, inline_fact, prose_range
from valuation_platform.preload.issuers import registration
from valuation_platform.preload.profile import read_json, read_sources


def build(root, ticker):
    directory = root/'data/preload'/registration(ticker)['dataset']
    mapping = read_json(directory/'mapping.json')
    sources = {s['id']: s for s in read_sources(directory/'sources')}
    documents = {}; observations = []
    for record in mapping['observations']:
        source = sources[record['source']]
        body = (directory/'sources'/source['file']).read_bytes()
        selection = record.get('extraction')
        if selection:
            if selection['kind'] == 'inline-xbrl-v1':
                if source['id'] not in documents: documents[source['id']] = inline_document(body)
                point = inline_fact(documents[source['id']], selection)
            elif selection['kind'] == 'prose-range-v1':
                point = prose_range(body, selection)
            else:
                raise ValueError('Unsupported reviewed mapping')
        else:
            # Macro observations are reused verbatim from a hash-bound existing
            # reviewed mapping. They are not extracted from an unreviewed page.
            imported = read_json(root/record['reviewed_reference'])
            matches = [o for o in imported if o['id'] == record['reviewed_id']]
            if len(matches) != 1 or matches[0]['source_sha256'] != source['sha256']:
                raise ValueError('Reviewed macro reference mismatch')
            observations.append(matches[0]); continue
        observations.append({k:v for k,v in record.items() if k not in ('reviewed_reference','reviewed_id')} |
            point | {'source_sha256':source['sha256'], 'published_at':source['published_at'],
                     'available_at':source['published_at'], 'mapping_version':mapping['version'], 'supersedes':None})
    return observations


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ticker',required=True);parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    rows=build(ROOT,args.ticker);path=ROOT/'data/preload'/registration(args.ticker)['dataset']/'observations.json'
    encoded=json.dumps(rows,indent=2)+'\n'
    if args.check:
        if path.read_text()!=encoded:raise SystemExit('Reviewed observations differ')
    else:path.write_text(encoded)
    print(args.ticker.upper()+': '+str(len(rows))+' source-bound observations replayed; no valuation executed')


if __name__=='__main__':main()
