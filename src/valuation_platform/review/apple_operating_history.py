"""Apple's explicitly standardized EBIT/current-NWC history, display only.

Current tax accruals remain inside NWC in every year; this is a declared model
convention, not exact unlevered cash taxes or a pure operating cash reconstruction.
"""
from fractions import Fraction
import hashlib
import json
from .operating_fcff import amount, serialized

RESOURCE = 'docs/company-resolutions/AAPL/operating-fcff-2026-11-04/adopted-history.json'
PIN = 'ccdc7beda9546d0e160e22eb2e42acb68101c544aa2400edc82a68ab3d479cb8'
BASIS = 'STANDARDIZED_EBIT_CURRENT_NWC_CASH_PPE'
METHOD = 'aapl-ebit-reported-etr-current-nwc-cash-ppe-v1'
BALANCE_SIGNS = {'current_assets': 1, 'cash': -1, 'current_securities': -1,
                 'current_liabilities': -1, 'commercial_paper': 1,
                 'current_term_debt': 1, 'current_finance_lease': 1, 'current_operating_lease': 1}
NOTICE = ('Apple historical FCFF uses operating income, reported provision/pretax tax allocation, '
          'reported combined cash-statement D&A, cash PP&E and change in standardized noncash/nondebt '
          'current working capital. Both current lease liabilities are excluded; current tax accruals '
          'and mixed Other current balances remain included consistently. SBC stays expensed. '
          'Current tax payable rose $17.782B in FY2024 and fell $13.585B in FY2025, affecting this series. '
          'This qualified balance-sheet convention is not exact unlevered cash flow. '
          'FY2024 later note depreciation plus amortization exceeds cash-statement D&A by $355m; no plug is made. '
          'Forecast tax, investment and working-capital bases differ; no cross-basis FCFF CAGR or automatic calibration.')


def working_capital(inputs):
    if set(inputs) != set(BALANCE_SIGNS):
        raise ValueError('Exact current-working-capital populations required')
    values = {k: amount(v) for k, v in inputs.items()}
    if any(v < 0 for v in values.values()):
        raise ValueError('Source balance magnitudes must be nonnegative')
    if values['cash'] + values['current_securities'] > values['current_assets']:
        raise ValueError('Cash and securities exceed current assets')
    if sum((values[k] for k in ('commercial_paper','current_term_debt','current_finance_lease','current_operating_lease')), Fraction()) > values['current_liabilities']:
        raise ValueError('Excluded financing/lease liabilities exceed current liabilities')
    return sum((values[k] * sign for k, sign in BALANCE_SIGNS.items()), Fraction())


def calculate(inputs):
    keys = {'ebit','tax_provision','pretax_income','da','cash_ppe','opening_nwc','closing_nwc'}
    if set(inputs) != keys:
        raise ValueError('Exact operating FCFF operands required; no zero fill')
    v = {k: amount(s) for k, s in inputs.items()}
    if v['pretax_income'] <= 0 or v['da'] < 0 or v['cash_ppe'] < 0:
        raise ValueError('Unsupported historical operand signs')
    nopat = v['ebit'] * (1 - v['tax_provision'] / v['pretax_income'])
    return serialized(nopat + v['da'] - v['cash_ppe'] - (v['closing_nwc'] - v['opening_nwc']))


def read_overlay(root):
    body = (root / RESOURCE).read_bytes()
    if hashlib.sha256(body).hexdigest() != PIN:
        raise ValueError('Apple operating history differs from adopted pin')
    data = json.loads(body)
    if data['methodology'] != METHOD or data['basis'] != BASIS or data['ticker'] != 'AAPL' or data['forecast_calibration'] is not False:
        raise ValueError('Incompatible Apple operating history')
    if len(data['periods']) != 5 or [p['fiscal_year'] for p in data['periods']] != list(range(2021,2026)):
        raise ValueError('Five consecutive approved Apple annuals required')
    for p in data['periods']:
        if p['identity']['cik'] != 320193 or p['identity']['form'] != '10-K':
            raise ValueError('Apple annual identity mismatch')
        for side in ('opening','closing'):
            if str(working_capital(p[side+'_balances'])) != p['inputs'][side+'_nwc']:
                raise ValueError('Working capital does not reproduce')
        if calculate(p['inputs']) != p['fcff']:
            raise ValueError('Apple operating FCFF does not reproduce')
        if not p['source_urls'] or any(not u.startswith('https://www.sec.gov/Archives/edgar/data/320193/') for u in p['source_urls']):
            raise ValueError('Official Apple annual sources required')
    for previous, current in zip(data['periods'],data['periods'][1:]):
        if previous['closing_balances'] != current['opening_balances']:
            raise ValueError('Opening and prior closing balances must agree')
    return data


def apply_window(root, rows):
    overlay = read_overlay(root)
    for row, p in zip(rows, overlay['periods'], strict=True):
        r = row['revenue']; i = p['identity']
        if (r['period_start'],r['period_end'],r['accession']) != (i['annual_start'],i['annual_end'],i['accession']):
            raise ValueError('Apple historical display identity mismatch')
        row['legacy_cfo_fcff'] = {'amount_usd': row['fcff'], 'basis': row['fcff_basis']}
        row['fcff'] = p['fcff']['amount_usd']; row['fcff_basis'] = BASIS
        row['fcff_calculation'] = {'status': 'CALCULATED_STANDARDIZED_CONVENTION',
            'inputs': p['inputs'], 'sources': p['source_urls'],
            'reported_etr': serialized(amount(p['inputs']['tax_provision'])/amount(p['inputs']['pretax_income']))['amount_usd']}
    return rows


def policy():
    return {'methodology': METHOD, 'basis': BASIS, 'classification': 'STANDARDIZED_DERIVED_WITH_DECLARED_CONVENTIONS',
            'notice': NOTICE, 'forecast_calibration': False, 'cross_basis_cagr': False,
            'missing_input_policy': 'Missing operands remain unavailable; no inferred interest, tax split or cash movement.'}
