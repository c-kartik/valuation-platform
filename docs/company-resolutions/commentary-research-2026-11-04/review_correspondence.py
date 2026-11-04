"""Offline, content-aware extraction of the retained SEC correspondence packet."""
from pathlib import Path
from html.parser import HTMLParser
from io import BytesIO
import gzip
import hashlib
import json
import re

from pypdf import PdfReader

HERE = Path(__file__).resolve().parent


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def main():
    manifest = json.loads((HERE / 'retrieval-manifest.json').read_text())
    inventory = json.loads((HERE / 'correspondence-inventory.json').read_text())
    results = []
    patterns = [r'interest expense', r'other financing', r'\bleases?\b',
                r'cash flows?', r'non[ -]?controlling', r'working capital',
                r'depreciation', r'amortization', r'cash pool']
    for item in inventory:
        r = next(r for r in manifest if r['url'] == item['url'] and r['status'] == 200)
        b = gzip.decompress((HERE / r['body']).read_bytes())
        assert hashlib.sha256(b).hexdigest() == r['sha256']
        if b.startswith(b'%PDF'):
            reader = PdfReader(BytesIO(b))
            chunks = [(i + 1, page.extract_text() or '') for i, page in enumerate(reader.pages)]
            method = 'pypdf; all pages extracted'
            assert all(len(text.strip()) > 30 for _, text in chunks)
        else:
            parser = Text()
            parser.feed(b.decode('utf-8'))
            chunks = [(None, ' '.join(parser.parts))]
            method = 'HTMLParser; scripts/styles excluded'
        combined = '\n'.join((f'[Page {page}] ' if page else '') + ' '.join(text.split())
                             for page, text in chunks) + '\n'
        target = (HERE / r['body']).with_suffix('.txt')
        target.write_text(combined)
        hits = []
        for page, text in chunks:
            text = ' '.join(text.split())
            for pattern in patterns:
                for hit in re.finditer(pattern, text, re.I):
                    hits.append(dict(pattern=pattern, page=page, start=hit.start(),
                                     excerpt=text[max(0, hit.start()-140):hit.end()+600]))
        results.append(dict(**item, source_sha256=r['sha256'], extraction=method + '; derived text whitespace collapsed',
                            text_sha256=hashlib.sha256(combined.encode()).hexdigest(),
                            pages=len(chunks) if b.startswith(b'%PDF') else None,
                            text_file=str(target.relative_to(HERE)), hits=hits))
    (HERE / 'correspondence-screen.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(dict(documents=len(results), pdf_documents=sum(r['pages'] is not None for r in results),
                         source_hash_checks='PASS', hits=sum(len(r['hits']) for r in results))))
    for r in results:
        if r['hits']:
            print(json.dumps(dict(ticker=r['ticker'], date=r['date'], url=r['url'], hits=r['hits'])))


if __name__ == '__main__':
    main()
