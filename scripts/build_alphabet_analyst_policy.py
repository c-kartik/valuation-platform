"""Reproduce Alphabet's approved analyst-policy projection from retained filings.

No historical fact bank is mutated. Numerical defaults are disclosed analyst
judgments authorized for the named five-output consumer, not issuer facts.
"""
import argparse
import base64
from decimal import Decimal
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/company-resolutions/GOOGL/analyst-ready-2026-11-04'
FILES = {
    'historical': 'docs/company-resolutions/GOOGL/results.json',
    'ownership': 'docs/company-resolutions/GOOGL/implementation-2026-11-03/schedules.json',
    'share_bridge': 'docs/company-resolutions/implementation-2026-11-03/share-bridge/source-schedules.json',
    'ledger': 'docs/evidence/analyst-operating-nwc-response-bodies.json',
    'preload': 'data/preload/googl-v1/policy.json',
    'observations': 'data/preload/googl-v1/observations.json',
    'source_manifest': 'data/preload/googl-v1/sources/manifest.json',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    data = {k: json.loads((ROOT / f).read_text()) for k, f in FILES.items()}
    spec = importlib.util.spec_from_file_location('alphabet_retained_parser', ROOT / 'docs/company-resolutions/GOOGL/implementation-2026-11-03/build_schedules.py')
    parser_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(parser_module)
    parsed = {}; documents = []
    for year, index in zip(range(2021, 2026), [24, 26, 28, 30, 32], strict=True):
        a = data['ledger']['artifacts'][index]
        raw = gzip.decompress(base64.b64decode(a['response_body_gzip_base64']))
        if hashlib.sha256(raw).hexdigest() != a['sha256']: raise ValueError('Retained primary body changed')
        p = parser_module.Filing(); p.feed(raw.decode())
        parsed[year] = (p, raw.decode())
        documents.append({'fiscal_year': year, 'url': a['source_url'], 'sha256': a['sha256'],
                          'retained_reference': FILES['ledger'] + '#/artifacts/' + str(index)})

    def context(body, context_id):
        match = re.search(r'<(?:[\w-]+:)?context\b[^>]*\bid=[\"\']' + re.escape(context_id) + r'[\"\'][^>]*>([\s\S]*?)</(?:[\w-]+:)?context>', body, re.I)
        if not match: raise ValueError('Context absent')
        return match[1]

    def amount(fact):
        value = Decimal(''.join(fact['text']).replace(',', '').replace('(', '-').replace(')', '').strip()) * Decimal(10) ** int(fact['attrs'].get('scale', 0))
        if fact['attrs'].get('sign') == '-': value = -value
        return str(int(value)) if value == value.to_integral_value() else str(value)

    def annual_point(year, concept, expected=None):
        p, body = parsed[year]; candidates = []
        for xml_id, fact in p.facts.items():
            a = fact['attrs']
            if a.get('name', '').split(':')[-1] != concept: continue
            c = context(body, a['contextref'])
            if f'{year}-01-01' not in c or f'{year}-12-31' not in c: continue
            if re.search(r'<(?:[\w-]+:)?(?:explicitMember|typedMember)', c): continue
            if a.get('unitref') != 'usd': raise ValueError('Annual USD required')
            candidates.append({'value': amount(fact), 'concept': concept, 'primary_locator': 'inline#' + xml_id,
                               'context_id': a['contextref'], 'precision': a.get('decimals'), 'unit': 'USD',
                               'start': f'{year}-01-01', 'end': f'{year}-12-31', 'source': documents[year - 2021]})
        if not candidates or len({c['value'] for c in candidates}) != 1: raise ValueError(f'Ambiguous {year} {concept}')
        point = candidates[0]
        if expected is not None and Decimal(point['value']) != Decimal(expected): raise ValueError('Historical source differs')
        return point

    bridge = next(c for c in data['share_bridge']['companies'] if c['ticker'] == 'GOOGL')
    if bridge['as_of'] != '2025-12-31': raise ValueError('Anchor mismatch')

    def checked(point):
        p, body = parsed[2025]
        xml_id = point['primary_locator'].split('#', 1)[1]
        fact = p.facts[xml_id]
        if amount(fact) != point['value'] or fact['attrs']['contextref'] != point['instance_context_id']: raise ValueError('Anchor point mismatch')
        if fact['attrs']['name'].split(':')[-1] != point['concept']: raise ValueError('Anchor concept mismatch')
        expected_unit = 'shares' if point['unit'] == 'shares' else 'usd'
        if fact['attrs'].get('unitref') != expected_unit: raise ValueError('Anchor unit mismatch')
        if point['scope']['end'] != '2025-12-31': raise ValueError('Dated anchor required')
        c = context(body, fact['attrs']['contextref'])
        if '2025-12-31' not in c or not re.search(r'<[^>]*identifier[^>]*>0*1652044</', c): raise ValueError('Source context entity/date mismatch')
        for dimension in point['scope']['dimensions']:
            if dimension['member'].rsplit('#', 1)[1] not in c: raise ValueError('Share/award dimension mismatch')
        if not point['scope']['dimensions'] and re.search(r'<(?:[\w-]+:)?(?:explicitMember|typedMember)', c): raise ValueError('Unexpected anchor dimension')
        if not any(s['sha256'] == documents[-1]['sha256'] for s in point['sources']): raise ValueError('Anchor primary receipt mismatch')
        return point

    def anchor(concept):
        row = bridge['nondimensional_support'][concept]
        if row['value'] is None: raise ValueError(f'Unresolved anchor {concept}')
        return checked(row['observations'][0])

    selected = {concept: anchor(concept) for concept in (
        'CashAndCashEquivalentsAtCarryingValue', 'MarketableSecuritiesCurrent',
        'LongTermDebtCurrent', 'LongTermDebtNoncurrent', 'LongTermDebtFairValue',
        'FinanceLeaseLiability', 'EquityMethodInvestmentsAndOther', 'NoncontrollingInterestInVariableInterestEntity',
        'RedeemableNoncontrollingInterestInVariableInterestEntity', 'OtherLongTermInvestments')}
    nonmarketable_component = parsed[2025][0].facts['f-755']
    if amount(nonmarketable_component) != '64094000000' or nonmarketable_component['attrs']['contextref'] != 'c-20':
        raise ValueError('Non-marketable equity component differs')
    selected['EquitySecuritiesWithoutReadilyDeterminableFairValueAmount'] = {
        'value': '64094000000', 'concept': 'EquitySecuritiesWithoutReadilyDeterminableFairValueAmount',
        'primary_locator': 'inline#f-755', 'context_id': 'c-20', 'end': '2025-12-31',
        'unit': 'USD', 'precision': '-6', 'source': documents[-1]}
    if Decimal(selected['EquitySecuritiesWithoutReadilyDeterminableFairValueAmount']['value']) + Decimal(selected['EquityMethodInvestmentsAndOther']['value']) != Decimal(selected['OtherLongTermInvestments']['value']):
        raise ValueError('Nonmarketable component reconciliation differs')
    class_facts = {name: checked(point) for name, point in bridge['shares']['class_sources'].items()}
    if set(class_facts) != {'Class A', 'Class B', 'Class C'}: raise ValueError('All three classes required')
    rsu = checked(next(p for p in bridge['awards'] if p['concept'].endswith('OtherThanOptionsNonvestedNumber')))
    D = Decimal
    v = lambda concept: D(selected[concept]['value'])
    gross_cash = v('CashAndCashEquivalentsAtCarryingValue') + v('MarketableSecuritiesCurrent')
    leases = v('FinanceLeaseLiability')
    carrying = v('LongTermDebtCurrent') + v('LongTermDebtNoncurrent') + leases
    fair = v('LongTermDebtFairValue') + leases
    shares = sum((D(p['value']) for p in class_facts.values()), D(0))
    # Note 5 explicitly says redeemable NCI is included in total NCI.
    nci = v('NoncontrollingInterestInVariableInterestEntity')
    if nci != D('3400000000'): raise ValueError('Selected total NCI source changed')

    text = parser_module.norm(' '.join(parsed[2025][0].text))
    quotations = {}
    for label, needle in {
        'financial_class_rights': 'In accordance with our certificate of incorporation, the rights, including the liquidation and dividend rights, of the holders of our Class A, Class B, and Class C stock are identical, except with respect to voting.',
        'nci_scope': 'Total noncontrolling interests (NCI) in our consolidated subsidiaries were',
        'debt_fair_value': 'The total estimated fair value of the outstanding notes was approximately',
    }.items():
        offset = text.find(needle)
        if offset < 0: raise ValueError('Required source disclosure absent')
        quotations[label] = {'source': documents[-1], 'normalization': 'collapse whitespace over retained visible parser text',
                             'normalized_character_offset': offset, 'text': text[offset:offset + (len(needle) if label == 'financial_class_rights' else 650)]}

    config = data['preload']['configuration']
    macro = {o['key']: o for o in data['observations'] if o['key'] in ('treasury_10y', 'implied_erp')}
    rf, erp = D(macro['treasury_10y']['value']), D(macro['implied_erp']['value'])
    ke, kd = rf + D(config['beta']) * erp, rf + D(config['credit_spread'])
    wacc = ke * D(config['equity_weight']) + kd * (1 - D(config['debt_tax_shield'])) * D(config['debt_weight'])
    history = []
    for index, (old, own) in enumerate(zip(data['historical']['periods'], data['ownership']['periods'], strict=True)):
        year = old['fiscal_year']
        if year != 2021 + index or own['fiscal_year'] != year: raise ValueError('Five chronological years required')
        cfo = annual_point(year, 'NetCashProvidedByUsedInOperatingActivities', old['inputs']['cfo'])
        ppe = annual_point(year, 'PaymentsToAcquirePropertyPlantAndEquipment', old['inputs']['cash_ppe'])
        sbc = annual_point(year, 'ShareBasedCompensation')
        funding = sum((D(r['signed_cash_usd']) for r in old['financing']['source_rows'] if r['included_in_net_borrowing']), D(0))
        fcfe = D(cfo['value']) - D(ppe['value']) + funding
        if fcfe != D(old['fcfe']['amount_usd']): raise ValueError('Consolidated history arithmetic changed')
        other = [r for r in old['financing']['source_rows'] if r['classification'] == 'UNCLASSIFIED_FINANCING']
        if other: raise ValueError('Unexpected residual financing requires classification')
        history.append({'fiscal_year': year, 'identity': old['identity'], 'cfo_usd': cfo['value'],
                        'cash_ppe_usd': ppe['value'], 'identified_net_borrowing_usd': str(funding),
                        'other_financing_usd': '0', 'other_financing_status': 'NO_SEPARATELY_CAPTIONED_UNCLASSIFIED_FINANCING_ROW',
                        'sbc_usd': sbc['value'], 'fcff_usd': old['fcff']['amount_usd'],
                        'consolidated_fcfe_usd': str(fcfe), 'source_urls': old['source_urls'],
                        'cfo_source': cfo, 'cash_ppe_source': ppe, 'sbc_source': sbc,
                        'financing_source_reference': FILES['historical'] + '#/periods/' + str(index) + '/financing',
                        'ownership_schedule': own['ownership_schedule'], 'lease_schedule': own['lease_schedule']})
    return {
        'schema_version': 'company-analyst-policy-v1', 'name': 'Alphabet', 'version': 'googl-analyst-2026-11-04-v1',
        'ticker': 'GOOGL', 'cik': 1652044, 'anchor_date': '2025-12-31',
        'approval': 'User requested all five outputs analyst-ready for Meta and Alphabet under the approved Apple practical analyst conditions.',
        'defaults': {'operating_cash_reserve_ratio': '0.02', 'cost_of_equity': str(ke),
                     'pre_tax_cost_of_debt': str(kd), 'rsu_vesting_fraction': '1', 'additional_claims_usd': '0',
                     'historical_other_financing_fraction': '0', 'historical_minority_cash_share': '0',
                     'nci_claim_usd': str(nci), 'additional_assets_usd': selected['OtherLongTermInvestments']['value']},
        'financed_fraction_cash_ppe': config['new_financed_fraction_cash_ppe'],
        'anchor_support': {'gross_cash_usd': str(gross_cash), 'financing_debt_carrying_usd': str(carrying),
                           'financing_debt_fair_proxy_usd': str(fair), 'dated_common_shares': str(shares),
                           'unvested_rsus': rsu['value'], 'nci_book_proxy_usd': str(nci),
                           'nonoperating_investments_carrying_usd': selected['OtherLongTermInvestments']['value']},
        'facts': {'selected_anchor_points': selected, 'dated_class_shares': class_facts, 'unvested_rsus': rsu,
                  'rights_and_nci_excerpts': quotations},
        'discount_basis': {'risk_free': str(rf), 'beta': config['beta'], 'equity_risk_premium': str(erp),
                           'target_equity_weight': config['equity_weight'], 'target_debt_weight': config['debt_weight'],
                           'debt_tax_shield': config['debt_tax_shield'], 'saved_base_wacc': str(wacc),
                           'macro_observations': macro,
                           'macro_sources': [s for s in data['source_manifest']['sources'] if s['id'] in {o['source'] for o in macro.values()}],
                           'classification': 'DATED_MACRO_OBSERVATIONS_AND_CONFIGURED_ANALYST_ASSUMPTIONS'},
        'historical': history, 'retained_primary_documents': documents,
        'source_documents': {f: digest(ROOT / f) for f in FILES.values()},
        'assumption_rationales': {
            'historical_minority_cash_share': 'Default 0 is an explicitly unallocated consolidated cash-flow proxy, not a filing assertion of zero NCI cash. Display consolidated series and parent-proxy qualification together; show editable 1%/5% illustrative allocation stresses, not bounds. Immaterial reported NCI loss alone cannot establish immaterial NCI cash.',
            'nci_claim_usd': 'Use reported total NCI carrying amount as editable valuation proxy where exact subsidiary stakes and full dated market values are not disclosed. Redeemable841M is already inside3.4B, never additive. Deduct once from consolidated operating equity; do not also allocate forward annual FCFE and subtract this claim. Show0/3.4/17/34B stress, not proven fair-value bounds. Do not backdate February2026 Waymo126B postmoney.',
            'share_classes': 'Identical liquidation/dividend rights support equal economic per-share estimates for all A/B/C under the stated assumption; voting/control/liquidity premiums are not valued. Sum all dated classes, not only listedGOOGL or EPS weighted averages.',
            'operating_cash_reserve_ratio': '2% of annual revenue is a transparent analyst operating-liquidity proxy, not filing-disclosed required cash; expose0%/5% stresses.',
            'additional_claims_usd': '0 is no additional adjustment beyond modeled recurring expenses/taxes and separately deducted debt/NCI. It is not proof no contingencies or commitments exist. Pending acquisitions, tax/litigation/guarantee exposure and nonmarketable investments need scenario review, not automatic gross liability deduction.',
            'nonmarketable_investments': '68.687B total non-marketable securities (64.094B measurement-alternative equity plus4.593B equity-method investments and other) are added separately at editable carrying-value proxy, not presented as known fair value. They are financial investments, not PP&E; related gains are in OI&E outside modeled operating EBIT. Use0/50%/100% carrying-value stress, not confidence bounds. These are not consolidated subsidiaries, so do not subtract the consolidated3.4BNCI against them again.',
            'lease_investment': 'Historical financelease financing cash stays in reported debt repayments once; noncash additions are not added to historical cashPPE. Forecast2.5% cashPPE financed additions are an analyst overlay, not historical liability movements; financelease2.5B is included in opening financing debt once, operating leases remain service expense.',
            'sbc': 'Historical CFO includes reported SBC addback; economic cash-flow diagnostic subtracts it. Forecast operating margins retain compensation expense; existing282MRSUs are dilutive at selected vesting fraction and future SBC interpreted as future-grant expense proxy, no extra award fair-value/cost deduction.',
        },
        'methodology_sources': [
            'https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation',
            'https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-v-a',
            'https://pages.stern.nyu.edu/~adamodar/pdfiles/eqnotes/valopt.pdf',
            'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/noncashwc.htm',
        ],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + '\n'
    if args.check:
        if (DEST / 'policy.json').read_text() != text: raise ValueError('Alphabet source policy replay differs')
    else:
        DEST.mkdir(parents=True, exist_ok=True); (DEST / 'policy.json').write_text(text)
    print('PASS: Alphabet source facts, chronological cash histories and analyst policy reproduce.')
