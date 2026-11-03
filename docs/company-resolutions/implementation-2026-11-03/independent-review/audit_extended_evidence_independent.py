"""Check newly collected issuer operands independently, without replay builders."""
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from audit_source_cashflows_independent import Audit, Inline, local

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def walk(obj, path=''):
    if isinstance(obj, dict):
        yield path, obj
        for key, value in obj.items():
            yield from walk(value, path + '/' + key)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from walk(value, path + '/' + str(i))


def main():
    audit = Audit()
    apple_dir = ROOT / 'docs/company-resolutions/AAPL/implementation-2026-11-03'
    apple = json.loads((apple_dir / 'evidence-ledger.json').read_text())
    seen = set()
    for path, p in walk(apple):
        if not all(k in p for k in ('value', 'concept', 'namespace', 'sources', 'occurrences', 'target_annual_start', 'target_annual_end')):
            continue
        if p.get('unit') != 'USD' or p.get('as_of') is not None:
            continue
        key = (p['concept'], p['namespace'], p['value'], p['target_annual_start'], p['target_annual_end'], tuple(s['source_reference'] for s in p['sources']))
        if key in seen:
            continue
        seen.add(key)
        target = dict(cik=320193, annual_start=p['target_annual_start'], annual_end=p['target_annual_end'])
        audit.point(p, target, 'AAPL extended evidence ' + path)

    meta_dir = ROOT / 'docs/company-resolutions/META/implementation-2026-11-03'
    meta = json.loads((meta_dir / 'review-results.json').read_text())
    sources = {}
    for manifest in (meta_dir / 'retrieval-manifest.json', meta_dir.parent / 'research/source-manifest.json'):
        for source in json.loads(manifest.read_text())['sources']:
            sources[source['id']] = (manifest.parent, source)
    for source in json.loads((meta_dir / 'all-primary-source-manifest.json').read_text())['sources']:
        sources[source['id']] = (ROOT, dict(source, file=source['path']))
    parsed = {}
    checks = []
    for path, p in walk(meta):
        if not all(k in p for k in ('source_id', 'amount_usd', 'occurrences')):
            continue
        sid = p['source_id']
        if sid not in parsed:
            folder, source = sources[sid]
            name = source.get('file', source.get('local_file'))
            stored = (folder / name).read_bytes()
            body = gzip.decompress(stored) if name.endswith('.gz') else stored
            assert hashlib.sha256(body).hexdigest() == source['sha256'] == p['source_sha256']
            assert source['url'] == p['source_url'] and source['url'].startswith('https://www.sec.gov/Archives/')
            tree = ET.fromstring(body)
            contexts = {x.attrib['id']: x for x in tree.iter() if local(x.tag) == 'context'}
            units = {x.attrib['id']: x for x in tree.iter() if local(x.tag) == 'unit'}
            parsed[sid] = (Inline(body), contexts, units)
        inline, contexts, units = parsed[sid]
        for occurrence in p['occurrences']:
            attrs, display = inline.facts[occurrence['attrs']['id']]
            assert attrs['contextref'] == occurrence['attrs']['contextref']
            assert attrs['name'] == occurrence['attrs']['name']
            context = contexts[attrs['contextref']]
            values = {local(x.tag): x.text for x in context.iter() if local(x.tag) in ('identifier', 'startDate', 'endDate', 'instant')}
            assert int(values['identifier']) == 1326801
            assert values.get('startDate') == p['start'] and values.get('endDate') == p['end'], (path, values, p['start'], p['end'])
            assert values.get('instant') == occurrence['context']['instant']
            dimensions = [x.text for x in context.iter() if local(x.tag) in ('explicitMember', 'typedMember')]
            assert dimensions == occurrence['context']['dimensions']
            measures = [x.text.rsplit(':', 1)[-1] for x in units[attrs['unitref']].iter() if local(x.tag) == 'measure']
            assert measures == ['USD']
            digits = re.sub(r'[,\s\u00a0()]', '', display)
            value = Fraction(digits) if digits not in ('', '-', '—', '–') else Fraction(0)
            value *= 10 ** int(attrs.get('scale', 0))
            if attrs.get('sign') == '-':
                value = -value
            assert value == Fraction(p['amount_usd']), (path, value, p['amount_usd'])
        checks.append(dict(path=path, source_id=sid, amount_usd=p['amount_usd'], start=p['start'], end=p['end']))
    for bridge in meta['comparative_presentations']:
        assert Fraction(bridge['old_other_usd']) + Fraction(bridge['old_overdraft_usd']) == Fraction(bridge['later_other_usd'])
        assert bridge['annual_debt_change_justified_usd'] is None
    assert meta['historical_values_changed'] is False and meta['parent_status'] == 'OPEN'
    assert apple['parent_status'] == 'OPEN'
    result = dict(source_operand_verdict='PASS', apple_unique_monetary_duration_bindings=len(audit.bindings),
                  apple_bindings=audit.bindings, meta_primary_operand_checks=len(checks), meta_checks=checks,
                  coverage_change='NONE: neither later comparatives nor quarterly presentations resolve the 17 required historical cells',
                  financial_scope_verdict='FAIL_OPEN')
    (OUT / 'extended-evidence-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('apple_bindings', 'meta_checks')}))


if __name__ == '__main__':
    main()
