"""Independent nonzero-debt valuation expectations through the actual API worker."""
from decimal import Decimal, localcontext
from fractions import Fraction
import json
from pathlib import Path
import tempfile

from fastapi.testclient import TestClient
from valuation_platform.api.app import create_app
from valuation_platform.api.bundle import build_bundle, remove_bundle

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def ds(x):
    with localcontext() as ctx:
        ctx.prec = 50
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def financing(debt):
    # Cash principal includes lease principal. New financed assets are part of
    # the declared operating investment, with explicit funding counted once.
    return dict(interest_expense_usd=ds(debt * Fraction(6, 100)),
                cash_debt_issued_usd=ds(debt * Fraction(3, 100) + Fraction(3) - Fraction(1, 2)),
                new_finance_asset_funding_usd='0.5', principal_repaid_usd='3')


def document():
    base = json.loads((ROOT / 'examples/valuation/synthetic-base.json').read_text())
    equity, debt = Fraction(394, 3), Fraction(30)
    # Independently derived FCFF growing perpetuity: FCFF1=12.36; debt30;
    # FCFE1=12.36-1.8*(1-.2)+.9=11.82; E=11.82/(.12-.03)=394/3.
    wacc = (Fraction(12, 100) * equity + Fraction(6, 100) * Fraction(8, 10) * debt) / (equity + debt)
    base['wacc'], base['terminal_growth'] = ds(wacc), '0.03'
    for row in base['forecast_years']:
        row.update(revenue_growth='0.03', operating_margin='0.25', forecast_tax_rate='0.20',
                   d_and_a_percent_revenue='0.04', capex_percent_revenue='0.09',
                   change_in_operating_nwc_percent_revenue='0.03')
    base['terminal'] = dict(operating_margin='0.25', operating_tax_rate='0.20', d_and_a_percent_revenue='0.04',
                            investment_percent_revenue='0.09', working_capital_cash_requirement_percent_revenue='0.03')
    years, expectations = [], []
    revenue = Fraction(100)
    for i in range(1, 6):
        years.append(dict(period_index=i, **financing(debt)))
        revenue *= Fraction(103, 100)
        expected_fcff = revenue * Fraction(12, 100)
        expected_fcfe = expected_fcff - debt * Fraction(6, 100) * Fraction(8, 10) + debt * Fraction(3, 100)
        debt *= Fraction(103, 100)
        expectations.append(dict(fcff=expected_fcff, fcfe=expected_fcfe, closing_debt=debt))
    return dict(schema_version='fcfe-forecast-request-v1', base_case=base, scope='DECLARED_PARENT_COMMON',
                cost_of_equity='0.12', opening_debt_usd='30', financing_years=years,
                terminal_growth='0.03', terminal_financing=financing(debt)), expectations


def near(value, expected):
    assert abs(Fraction(value) - expected) < Fraction(1, 10 ** 40), (value, ds(expected))


def main():
    request, expected = document()
    with tempfile.TemporaryDirectory(prefix='valuation-independent-fcfe-') as directory:
        bundle = Path(directory) / 'bundle'
        build_bundle(ROOT, bundle)
        try:
            with TestClient(create_app(bundle)) as client:
                validated = client.post('/api/v1/fcfe/validate', json=request)
                assert validated.status_code == 200, validated.text
                assert validated.json()['calculation_performed'] is False
                response = client.post('/api/v1/fcfe/run', json=request)
                assert response.status_code == 200, response.text
                result = response.json()
                for row, want in zip(result['years'], expected, strict=True):
                    near(row['fcff_usd'], want['fcff'])
                    near(row['fcfe_usd'], want['fcfe'])
                    near(row['closing_debt_usd'], want['closing_debt'])
                near(result['equity_value_usd'], Fraction(394, 3))
                assert result['value_per_share'] is None
                assert result['debt_subtracted_after_fcfe_discounting'] is False
                ff = client.post('/api/v1/cases/run', json=request['base_case'])
                assert ff.status_code == 200, ff.text
                near(ff.json()['stage_b']['enterprise_value'], Fraction(484, 3))
                near(Fraction(ff.json()['stage_b']['enterprise_value']) - Fraction(30), Fraction(394, 3))

                # Runtime economic validations, not merely JSON shape checks.
                bad = json.loads(json.dumps(request))
                bad['terminal_financing']['cash_debt_issued_usd'] = '100'
                rejected = client.post('/api/v1/fcfe/run', json=bad)
                assert rejected.status_code == 422 and 'terminal_financing' in rejected.text
                assert '/Users/' not in rejected.text
                bad = json.loads(json.dumps(request))
                bad['financing_years'][0]['principal_repaid_usd'] = '100'
                principal_error = client.post('/api/v1/fcfe/run', json=bad)
                assert principal_error.status_code == 422 and 'principal_repaid_usd' in principal_error.text
                bad = json.loads(json.dumps(request))
                del bad['financing_years'][0]['interest_expense_usd']
                missing = client.post('/api/v1/fcfe/validate', json=bad)
                assert missing.status_code == 422
                bad = json.loads(json.dumps(request))
                bad['financing_years'][0]['new_finance_asset_funding_usd'] = '20'
                unmatched = client.post('/api/v1/fcfe/run', json=bad)
                assert unmatched.status_code == 422 and 'new_finance_asset_funding_usd' in unmatched.text
                taxed_loss = json.loads(json.dumps(request))
                taxed_loss['base_case']['forecast_years'][0]['operating_margin'] = '0.02'
                taxed_loss['financing_years'][0]['interest_expense_usd'] = '4'
                capped = client.post('/api/v1/fcfe/run', json=taxed_loss)
                assert capped.status_code == 200, capped.text
                near(capped.json()['years'][0]['interest_tax_shield_usd'], Fraction(412, 1000))
                near(capped.json()['years'][0]['fcfe_usd'], Fraction(-928, 100))
                taxed_loss['base_case']['forecast_years'][0]['operating_margin'] = '-0.01'
                no_shield = client.post('/api/v1/fcfe/run', json=taxed_loss)
                assert no_shield.status_code == 200, no_shield.text
                near(no_shield.json()['years'][0]['interest_tax_shield_usd'], Fraction(0))
                near(no_shield.json()['years'][0]['fcfe_usd'], Fraction(-1237, 100))
                consolidated = json.loads(json.dumps(request))
                consolidated['scope'] = 'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION'
                no_common = client.post('/api/v1/fcfe/run', json=consolidated)
                assert no_common.status_code == 200, no_common.text
                assert no_common.json()['scope'] == 'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION'
                assert no_common.json()['value_per_share'] is None
                payload = dict(software_engine_verdict='PASS', independent_expected_equity_usd=ds(Fraction(394, 3)),
                               independent_expected_ev_usd=ds(Fraction(484, 3)), actual_fcfe_result=result,
                               actual_fcff_result=ff.json(), request=request,
                               capped_tax_shield_first_year=capped.json()['years'][0],
                               negative_ebit_tax_shield_first_year=no_shield.json()['years'][0],
                               economic_input_certification='NOT_ESTABLISHED_BY_SYNTHETIC_TEST',
                               unresolved_scope='Historical 17-cell coverage gaps, issuer ownership/valuation basis, dated market-input provenance and S1-S3 remain OPEN.')
                (OUT / 'fcfe-engine-audit.json').write_text(json.dumps(payload, indent=2) + '\n')
                print('PASS: independent 3% growth / nonzero debt / finance-asset funding / principal / WACC reconciliation and actual bounded API worker. Full issuer coverage remains FAIL.')
        finally:
            remove_bundle(bundle)


if __name__ == '__main__':
    main()
