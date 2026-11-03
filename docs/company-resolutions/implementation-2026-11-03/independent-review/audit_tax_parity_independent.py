"""Verify retained tax policy bytes and both scenario requests through the live API."""
from fractions import Fraction
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api', default='http://127.0.0.1:5182')
    args = parser.parse_args()
    source = json.loads((OUT.parent / 'basis-bridge/valuation-parity.json').read_text())
    checks = []
    for company in source['companies']:
        policy = company['policy_path']
        original = subprocess.check_output(['git', 'show', company['baseline_git_commit'] + ':' + policy], cwd=ROOT)
        assert original == (ROOT / policy).read_bytes()
        assert hashlib.sha256(original).hexdigest() == company['baseline_policy_sha256'] == company['current_policy_sha256']
        for scenario in company['scenarios']:
            assert scenario['before_request'] == scenario['after_request']
            values = []
            for side in ('before', 'after'):
                body = scenario[side + '_request']
                with urlopen(Request(args.api.rstrip('/') + '/api/v1/cases/run', data=json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json'}), timeout=30) as response:
                    result = json.loads(response.read())
                assert result == scenario[side + '_result']
                actual = result['stage_b']['enterprise_value']
                assert Fraction(actual) == Fraction(scenario[side + '_enterprise_value_usd'])
                values.append(Fraction(actual))
            assert values[0] == values[1]
            checks.append(dict(policy=policy, scenario=scenario['scenario'], ev_difference_usd='0'))
    result = dict(parity_verdict='PASS', api=args.api, independent_live_api_executions=2 * len(checks), scenario_pairs=checks,
                  policy_validity_verdict='NOT_ESTABLISHED_BY_PARITY',
                  meaning='The retained tax policies and their numerical valuations did not change; parity does not establish unique recurring tax economics.')
    (OUT / 'tax-parity-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: retained baseline tax policy bytes and 12 live API executions; all six scenario EV changes zero.')


if __name__ == '__main__':
    main()
