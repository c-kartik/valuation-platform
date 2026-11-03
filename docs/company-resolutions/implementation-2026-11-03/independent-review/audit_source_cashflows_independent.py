"""Independent arithmetic/source audit. No production calculator is imported."""
import base64
from decimal import Decimal, localcontext
from fractions import Fraction
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
LEDGER = ROOT / 'docs/company-data-preparation/historical-fcff-filing-calculations.json'


def local(tag):
    return tag.rsplit('}', 1)[-1]


class Inline(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.facts = {}
        self.active = []
        self.table_stack = []
        self.row_stack = []
        self.rows = []
        self.table_counter = 0
        self.namespaces = {}
        self.text = []
        self.feed(body.decode())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.namespaces.update({k.split(':', 1)[1]: v for k, v in attrs.items() if k.startswith('xmlns:')})
        if tag.lower() == 'table':
            self.table_counter += 1
            self.table_stack.append(self.table_counter)
        if tag.lower() == 'tr' and self.table_stack:
            self.row_stack.append(dict(table=self.table_stack[-1], text=[], facts=[]))
        if tag.lower().endswith(':nonfraction'):
            self.active.append([attrs, []])
            if self.row_stack and attrs.get('id'):
                self.row_stack[-1]['facts'].append(attrs['id'])

    def handle_data(self, data):
        self.text.append(data)
        for _, text in self.active:
            text.append(data)
        for row in self.row_stack:
            row['text'].append(data)

    def handle_endtag(self, tag):
        if tag.lower().endswith(':nonfraction') and self.active:
            attrs, text = self.active.pop()
            if 'id' in attrs:
                self.facts[attrs['id']] = (attrs, ''.join(text))
        if tag.lower() == 'tr' and self.row_stack:
            row = self.row_stack.pop()
            row['text'] = re.sub(r'\s+', ' ', ''.join(row['text'])).strip()
            self.rows.append(row)
        if tag.lower() == 'table' and self.table_stack:
            self.table_stack.pop()


class Audit:
    def __init__(self):
        self.jsons = {}
        self.bodies = {}
        self.parsed = {}
        self.source_receipts = {}
        self.bindings = []

    def read(self, path):
        path = str(path)
        if path not in self.jsons:
            self.jsons[path] = json.loads(Path(path).read_text())
        return self.jsons[path]

    def source(self, ref):
        key = ref['source_reference']
        if key not in self.bodies:
            path, ptr = key.split('#')
            obj = self.read(ROOT / path)
            for segment in ptr.strip('/').split('/'):
                obj = obj[int(segment)] if isinstance(obj, list) else obj[segment]
            encoded = obj['response_body_gzip_base64']
            body = gzip.decompress(base64.b64decode(''.join(encoded) if isinstance(encoded, list) else encoded, validate=True))
            digest = hashlib.sha256(body).hexdigest()
            url = obj.get('source_url', obj.get('url'))
            assert digest == ref['sha256'] == obj['sha256']
            assert len(body) == ref['byte_length'] == obj['byte_length']
            assert url == ref['url'] and url.startswith('https://www.sec.gov/Archives/edgar/data/')
            self.bodies[key] = body
            self.source_receipts[key] = dict(url=url, sha256=digest, byte_length=len(body))
        return self.bodies[key]

    def documents(self, refs):
        primary = next(s for s in refs if s['url'].endswith('.htm'))
        instance = next(s for s in refs if s['url'].endswith('_htm.xml'))
        key = (primary['source_reference'], instance['source_reference'])
        # Check every referenced receipt even when documents are cached.
        pb, ib = self.source(primary), self.source(instance)
        if key not in self.parsed:
            tree = ET.fromstring(ib)
            contexts = {x.attrib['id']: x for x in tree if local(x.tag) == 'context'}
            units = {x.attrib['id']: x for x in tree if local(x.tag) == 'unit'}
            self.parsed[key] = (Inline(pb), tree, contexts, units)
        return self.parsed[key]

    def point(self, p, target, label):
        inline, tree, contexts, units = self.documents(p['sources'])
        if 'source_identity' in p:
            identity = p['source_identity']
            assert all(f'/data/{identity["cik"]}/{identity["accession"].replace("-", "")}/' in s['url']
                       for s in p['sources'])
        concept = p['concept']
        namespace = p['namespace']
        points = []
        for f in tree:
            if f.tag != '{' + namespace + '}' + concept or 'contextRef' not in f.attrib:
                continue
            c = contexts[f.attrib['contextRef']]
            elements = list(c.iter())
            if any(local(x.tag) in ('explicitMember', 'typedMember') for x in elements):
                continue
            dates = {local(x.tag): x.text for x in elements if local(x.tag) in ('startDate', 'endDate', 'identifier')}
            if dates.get('startDate') != target['annual_start'] or dates.get('endDate') != target['annual_end']:
                continue
            assert int(dates['identifier']) == target['cik']
            measures = [x.text.rsplit(':', 1)[-1] for x in units[f.attrib['unitRef']].iter() if local(x.tag) == 'measure']
            assert measures == ['USD']
            points.append((f.attrib['contextRef'], Fraction(f.text)))
        assert points and len({v for _, v in points}) == 1, (label, points)
        value = points[0][1]
        assert value == Fraction(p['value']), label
        occurrences = p['occurrences']
        assert occurrences
        for occurrence in occurrences:
            attrs, displayed = inline.facts[occurrence['xml_id']]
            assert attrs['contextref'] == occurrence['context_id']
            assert (attrs['contextref'], value) in points
            assert attrs['name'].rsplit(':', 1)[-1] == concept
            assert inline.namespaces[attrs['name'].split(':', 1)[0]] == namespace
            digits = re.sub(r'[,\s\u00a0()]', '', displayed)
            parsed = Fraction(digits) if digits not in ('', '-', '—', '–') else Fraction(0)
            parsed *= 10 ** int(attrs.get('scale', 0))
            if attrs.get('sign') == '-':
                parsed = -parsed
            assert parsed == value, (label, parsed, value)
        self.bindings.append(dict(label=label, concept=concept, period=target, value_usd=str(value),
                                  source_refs=[s['source_reference'] for s in p['sources']]))
        return value

    def row(self, row, target, label):
        value = self.point(row['source'], target, label)
        assert value == Fraction(row['raw_value_usd'])
        signed = value * row['cash_sign']
        assert signed == Fraction(row['signed_cash_usd'])
        return signed

    def financing_population(self, rows):
        """Check primary statement population independently of mapped row totals."""
        inline, _, _, _ = self.documents(rows[0]['source']['sources'])
        selected = {r['primary_xml_id'] for r in rows}
        source_rows = [r for r in inline.rows if selected.intersection(r['facts'])]
        tables = {r['table'] for r in source_rows}
        assert len(tables) == 1
        table_rows = [r for r in inline.rows if r['table'] in tables]
        first = next(i for i, row in enumerate(table_rows) if selected.intersection(row['facts']))
        end = max(i for i, row in enumerate(table_rows) if selected.intersection(row['facts']))
        headings = [i for i, row in enumerate(table_rows[:first])
                    if re.fullmatch(r'(cash (?:flows? (?:from|used in) )?)?financing activities:?', row['text'], re.I)]
        assert headings, [r['text'] for r in table_rows[:first]]
        contexts = {r['context_id'] for r in rows}
        population = {fid for row in table_rows[headings[-1] + 1:end + 1] for fid in row['facts']
                      if inline.facts[fid][0].get('contextref') in contexts}
        assert population == selected, (population - selected, selected - population)


def decimal(f):
    if f is None:
        return None
    with localcontext() as ctx:
        ctx.prec = 75
        return str(Decimal(f.numerator) / Decimal(f.denominator))


def close_to_published(actual, published):
    if actual is None:
        assert published is None
    else:
        assert abs(actual - Fraction(published)) < Fraction(1, 10 ** 30), (decimal(actual), published)


def main():
    audit = Audit()
    ledger = audit.read(LEDGER)
    companies = {c['ticker']: c for c in ledger['companies']}
    results = []
    for ticker in ('AAPL', 'META', 'GOOGL'):
        recorded = audit.read(ROOT / f'docs/company-resolutions/{ticker}/results.json')
        for base, published in zip(companies[ticker]['periods'], recorded['periods'], strict=True):
            target = base['identity']
            assert target == published['identity']
            year = int(target['annual_end'][:4])
            operands = {k: audit.point(p, target, f'{ticker} {year} {k}') if p is not None else None
                        for k, p in base['inputs'].items()}
            # Exact selected source rows, not the stored financing net or result total.
            rows = published['financing_source_rows'] if ticker == 'AAPL' else published['financing']['source_rows']
            audit.financing_population(rows)
            cash, net, total, unknown = Fraction(), Fraction(), None, []
            for row in rows:
                signed = audit.row(row, target, f'{ticker} {year} financing: {row["caption"]}')
                role = row['classification']
                if role == 'FINANCING_TOTAL':
                    assert total is None
                    total = signed
                    continue
                cash += signed
                debt = role in ('DEBT_FUNDING_OR_PRINCIPAL', 'LEASE_PRINCIPAL')
                assert row['included_in_net_borrowing'] == debt
                if debt:
                    net += signed
                if role == 'OTHER_FINANCING_EXCLUDED':
                    unknown.append(dict(caption=row['caption'], signed_cash_usd=decimal(signed)))
            assert cash == total
            close_to_published(net, published['financing']['net_borrowing']['amount_usd'])
            receipts = sum((audit.row(r, target, f'{ticker} {year} investment receipt')
                            for r in published.get('investment_receipt_sources', [])), Fraction())
            investment = operands['cash_ppe'] - receipts
            fcff = (operands['cfo'] - investment + operands['interest_expense'] *
                    (1 - operands['tax_provision'] / operands['pretax_income'])) if operands['interest_expense'] is not None else None
            old_fcff = published['platform_after']['fcff_usd'] if ticker == 'AAPL' else published['fcff']['amount_usd']
            close_to_published(fcff, old_fcff)
            fcfe = operands['cfo'] - investment + net
            close_to_published(fcfe, published['fcfe']['amount_usd'])
            results.append(dict(ticker=ticker, fiscal_year=year, metric='FCFF', requested_ownership='CONSOLIDATED',
                                independently_recomputed_usd=decimal(fcff), arithmetic_and_source_verdict='PASS' if fcff is not None else 'UNAVAILABLE',
                                coverage_verdict='CANDIDATE_AVAILABLE_PENDING_RUNTIME' if fcff is not None else 'FAIL',
                                hard_blockers=[] if fcff is not None else ['A1: missing separate gross expensed interest; EBIT alternative is not established'],
                                inputs_usd={k: decimal(v) for k, v in operands.items()}, receipts_usd=decimal(receipts)))
            blockers = (['A2: unclassified Other financing', 'A3: unestablished lease principal containment'] if ticker == 'AAPL' else
                        ['M1: unclassified Other financing'] if ticker == 'META' else ['G1: no parent-common/minority cash attribution'])
            results.append(dict(ticker=ticker, fiscal_year=year, metric='FCFE', requested_ownership='PARENT_COMMON',
                                independently_recomputed_partial_or_consolidated_usd=decimal(fcfe), parent_common_fcfe_usd=None,
                                arithmetic_and_source_verdict='PASS', coverage_verdict='FAIL', hard_blockers=blockers,
                                published_status=published['fcfe']['status'], unallocated_other=unknown, net_borrowing_usd=decimal(net)))
    narrative_checks = []
    maps = audit.read(ROOT / 'docs/company-resolutions/GOOGL/source-map.json')
    for category in ('nci_narrative', 'lease_narrative'):
        for narrative in maps[category]:
            original = next(p for p in companies['GOOGL']['periods'] if p['identity'] == narrative['source_identity'])
            inline, _, _, _ = audit.documents(original['inputs']['cfo']['sources'])
            text = re.sub(r'\s+', ' ', ' '.join(inline.text))
            assert narrative['excerpt'] in text
            narrative_checks.append(dict(category=category, source_identity=narrative['source_identity'], excerpt=narrative['excerpt']))
    schedule_checks = []
    schedule_path = ROOT / 'docs/company-resolutions/GOOGL/implementation-2026-11-03/schedules.json'
    if schedule_path.exists():
        schedule = audit.read(schedule_path)
        for period in schedule['periods']:
            year = period['fiscal_year']
            original = next(p for p in companies['GOOGL']['periods'] if int(p['identity']['annual_end'][:4]) == year)
            lease = period['lease_schedule']
            assert lease['commenced_lease_principal_usd'] is None
            assert lease['additional_cash_deduction_usd'] == '0'
            assert lease['noncash_assets_added_to_cash_capex_usd'] == '0'
            assert period['parent_common_fcfe']['amount_usd'] is None
            assert period['ownership_schedule']['nci_cash_allocation_usd'] is None
            assert period['ownership_schedule']['nci_fair_value_usd'] is None
            for key in ('financing_cash', 'noncash_assets_obtained'):
                point = lease[key]
                if point is None:
                    continue
                ref = point['source']['retained_reference']
                source_period = next(p for p in companies['GOOGL']['periods']
                                     if any(s['source_reference'] == ref for s in p['inputs']['cfo']['sources']))
                refs = source_period['inputs']['cfo']['sources']
                _, tree, _, _ = audit.documents(refs)
                tags = {f.tag for f in tree if local(f.tag) == point['concept'].rsplit(':', 1)[-1]
                        and f.attrib.get('contextRef') == point['context_id']}
                assert len(tags) == 1
                tag = tags.pop()
                mapped = dict(sources=refs, concept=local(tag), namespace=tag[1:].split('}')[0], value=point['amount_usd'],
                              occurrences=[dict(xml_id=point['inline_id'], context_id=point['context_id'])])
                checked = audit.point(mapped, original['identity'], f'GOOGL {year} schedule {key}')
                schedule_checks.append(dict(ticker='GOOGL', fiscal_year=year, operand=key, independently_verified_usd=decimal(checked)))
    payload = dict(schema_version='independent-cashflows-audit-v1', overall_verdict='FAIL', runtime_verdict='PENDING',
                   independent_implementation=True, production_calculator_imported=False, cells=results,
                   source_binding_count=len(audit.bindings), checked_receipts=audit.source_receipts, bindings=audit.bindings,
                   new_schedule_numeric_checks=schedule_checks,
                   narrative_checks=narrative_checks,
                   coverage=dict(candidate_available_fcff=13, unavailable_fcff=2, provisional_fcfe=10,
                                 consolidated_fcfe_without_parent_common=5, parent_common_fcfe_pass=0))
    (OUT / 'source-audit.json').write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps({k: payload[k] for k in ('overall_verdict', 'runtime_verdict', 'source_binding_count', 'coverage')}))


if __name__ == '__main__':
    main()
