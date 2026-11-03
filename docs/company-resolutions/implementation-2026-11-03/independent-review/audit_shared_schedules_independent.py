"""Independent S1/S3 source checks; none of these workpapers supplies missing inputs."""
from fractions import Fraction
import json
from pathlib import Path
import re

from audit_source_cashflows_independent import Audit, local

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'docs/company-resolutions/implementation-2026-11-03'


def qname(name, namespaces):
    prefix, value = name.split(':', 1)
    return namespaces[prefix] + '#' + value


def main():
    audit = Audit()
    basis = json.loads((BASE / 'basis-bridge/schedules.json').read_text())
    for p in basis['periods']:
        cfo = audit.point(p['reported_cfo_source'], p['identity'], p['ticker'] + ' S1 CFO')
        sbc = audit.point(p['reported_sbc_addback_source'], p['identity'], p['ticker'] + ' S1 SBC')
        expense = audit.point(p['reported_total_sbc_expense_source'], p['identity'], p['ticker'] + ' S1 total SBC expense')
        assert cfo - sbc == Fraction(p['cfo_after_reversing_reported_sbc_addback']['amount_usd'])
        assert expense - sbc == Fraction(p['reported_expense_minus_addback_arithmetic_comparison_usd']['amount_usd'])
        assert p['valuation_aligned_fcff_usd'] is None and p['valuation_aligned_fcfe_usd'] is None
        assert p['reported_historical_values_replaced'] is False
    shares = json.loads((BASE / 'share-bridge/source-schedules.json').read_text())
    checked = []
    for company in shares['companies']:
        assert all(v is None for v in company['approved_bridge'].values())
        for p in company['source_points']:
            inline, tree, contexts, units = audit.documents(p['sources'])
            fact = list(tree)[p['instance_ordinal']]
            assert fact.tag == '{' + p['namespace'] + '}' + p['concept']
            assert fact.attrib['contextRef'] == p['instance_context_id']
            assert Fraction(fact.text) == Fraction(p['value'])
            assert fact.attrib['decimals'] == p['precision']
            context = contexts[p['instance_context_id']]
            dates = {local(x.tag): x.text for x in context.iter() if local(x.tag) in ('identifier', 'startDate', 'endDate', 'instant')}
            assert int(dates['identifier']) == p['scope']['cik']
            assert dates.get('startDate') == p['scope']['start']
            assert dates.get('endDate', dates.get('instant')) == p['scope']['end']
            dimensions = [dict(axis=qname(x.attrib['dimension'], inline.namespaces), member=qname(x.text, inline.namespaces))
                          for x in context.iter() if local(x.tag) == 'explicitMember']
            assert sorted(dimensions, key=str) == sorted(p['scope']['dimensions'], key=str)
            unit = units[fact.attrib['unitRef']]
            measures = [x.text.rsplit(':', 1)[-1] for x in unit.iter() if local(x.tag) == 'measure']
            assert measures == {'USD': ['USD'], 'shares': ['shares'], 'USD_per_share': ['USD', 'shares']}[p['unit']]
            attrs, display = inline.facts[p['primary_locator'].split('#', 1)[1]]
            assert attrs['contextref'] == p['instance_context_id']
            assert attrs['name'].rsplit(':', 1)[-1] == p['concept']
            assert inline.namespaces[attrs['name'].split(':', 1)[0]] == p['namespace']
            digits = re.sub(r'[,\s\u00a0()]', '', display)
            value = Fraction(0) if attrs.get('format', '').endswith(':fixed-zero') else Fraction(digits) if digits not in ('', '-', '—', '–') else Fraction(0)
            value *= Fraction(10) ** int(attrs.get('scale', 0))
            if attrs.get('sign') == '-':
                value = -value
            assert value == Fraction(p['value'])
            assert p['used_as_valuation_operand'] is False
            checked.append(dict(ticker=company['ticker'], concept=p['concept'], value=p['value'], scope=p['scope'], unit=p['unit']))
    result = dict(source_operand_verdict='PASS', sbc_diagnostic_periods=len(basis['periods']),
                  sbc_exact_source_bindings=len(audit.bindings), share_claim_unique_source_points=len(checked),
                  share_claim_checks=checked, scope_verdict='OPEN',
                  reason='S1 is a named SBC-only diagnostic; S3 has no approved eligible cash, complete claims, share denominator, class or awards value. Neither supplies missing historical cash or clears issuer valuation.')
    (OUT / 'shared-schedules-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'share_claim_checks'}))


if __name__ == '__main__':
    main()
