"""Bounded source screening, not automatic financial classification or clearance."""
from pathlib import Path
from html.parser import HTMLParser
import gzip
import hashlib
import json
import re

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

    def handle_data(self, text):
        if not self.skip:
            self.parts.append(text)


def main():
    manifest = json.loads((HERE / 'retrieval-manifest.json').read_text())
    records = []
    for r in manifest:
        if r['status'] != 200 or not any(word in r['role'] for word in ('quarterly notes', 'Related-party Waymo')):
            continue
        raw = gzip.decompress((HERE / r['body']).read_bytes())
        assert hashlib.sha256(raw).hexdigest() == r['sha256']
        html = raw.decode('utf-8')
        parser = Text()
        parser.feed(html)
        text = ' '.join(' '.join(parser.parts).split())
        textfile = (HERE / r['body']).with_suffix('.txt')
        textfile.write_text(text)
        findings = []
        for pattern in (r'interest expense', r'interest paid', r'cash paid for interest',
                        r'finance leases?', r'principal payments', r'other financing activities',
                        r'cash pool', r'non[ -]?controlling', r'Waymo LLC'):
            matches = list(re.finditer(pattern, text, re.I))
            findings.append(dict(pattern=pattern, occurrences=len(matches),
                                 excerpts=[dict(start=m.start(), end=m.end(),
                                                text=text[max(0, m.start()-140):m.end()+550])
                                           for m in matches[:10]]))
        # Presence alone supplies neither period, amount, nor an economic allocation.
        names = re.findall(r'name=["\']([^"\']+)["\']', html)
        wanted = ['us-gaap:InterestExpense', 'us-gaap:InterestPaidNet',
                  'us-gaap:FinanceLeasePrincipalPayments']
        records.append(dict(url=r['url'], role=r['role'], source_sha256=r['sha256'],
                            text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                            text_file=str(textfile.relative_to(HERE)), findings=findings,
                            exact_inline_tag_presence={n: names.count(n) for n in wanted}))
    (HERE / 'later-and-quarterly-screen.json').write_text(json.dumps(records, indent=2) + '\n')
    print(json.dumps(dict(source_documents=len(records), source_hash_checks='PASS')))
    for r in records:
        if 'Apple FY2021-25' in r['role']:
            print(json.dumps(dict(source=r['url'].rsplit('/', 1)[-1],
                                  tag_occurrences=r['exact_inline_tag_presence'],
                                  interest_excerpts=next(f['excerpts'] for f in r['findings'] if f['pattern']=='interest expense')[:2])))


if __name__ == '__main__':
    main()
