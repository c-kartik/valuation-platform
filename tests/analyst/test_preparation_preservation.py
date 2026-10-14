"""Backward compatibility against old code, not expectations from new assembly."""
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
import subprocess
import sys
import types
import unittest

from valuation_platform.analyst import historical_inputs as h, pilot_historical_inputs as pilot
from tests.analyst.test_historical_inputs import history, reported, unknown
from tests.analyst.preparation_preservation import MODEL, assert_preserved

ROOT = pilot.ROOT
BASELINES = ('14f2d34496f94660111e01d34d77bdd6c6ea4bc8',
             '1220bd2ee2edaa3867de7eb7ba8066f5554a3b96')


class PreparationPreservationTests(unittest.TestCase):
    def test_legacy_v1_bytes_and_guards_against_historical_implementations(self):
        for baseline in BASELINES:
            name = 'valuation_platform.analyst._historical_compat_' + baseline
            module = types.ModuleType(name)
            module.__package__ = 'valuation_platform.analyst'
            sys.modules[name] = module
            try:
                code = subprocess.check_output(['git', 'show', baseline + ':' + MODEL], cwd=ROOT)
                exec(compile(code, name, 'exec'), module.__dict__)
                for value in (unknown(h.Field.REVENUE), reported(),
                              replace(reported(), value=Decimal('-123400'), scale=1000, sign=-1)):
                    payload = h.serialize(history(value))
                    self.assertEqual(module.serialize(module.deserialize(payload)), payload)
                self.assertEqual(module.SCHEMA, h.SCHEMA)
                # Both implementations reject unsupported units and absent null reasons.
                for field in ('unit', 'null_reason'):
                    old = module.deserialize(h.serialize(history())).annuals[0].inputs[0]
                    change = {'unit': 'pure'} if field == 'unit' else {'null_reason': None}
                    with self.assertRaises(module.InputError): replace(old, **change)
                    with self.assertRaises(h.InputError): replace(unknown(h.Field.EBIT), **change)
            finally:
                sys.modules.pop(name, None)

    def test_reviewed_source_and_original_pilot_bytes_are_independent_pins(self):
        assert_preserved(self, ROOT, MODEL, BASELINES[0])
        hashes = {'MSFT': 'e05f85125b6244c321fbdee6469fa89bb809533614bbcc9c5399d2b5c56eb8b5',
                  'AAPL': '2772f34db57beb116f4fdb498f0016dc6502d7642b7bbc18f9e89e3645e66f83',
                  'GOOGL': 'f442e248f1ea2884967680db78c99076ee8beefdaae0bc050b6ee2f0c9b324d5'}
        for ticker, expected in hashes.items():
            self.assertEqual(hashlib.sha256(pilot.serialize(pilot.load_history(ticker)).encode()).hexdigest(), expected)

    def test_exact_bridge_preservation_assertions_without_another_financial_build(self):
        # Replay precisely the changed byte-assertion loop, not the unchanged
        # financial assertions/build already exercised by the full suite.
        baseline = 'a10505f5cac930a97411f4f7019dd5e4637ac32c'
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', baseline,
                                         'src', 'docs/evidence', 'docs/universe'], cwd=ROOT).decode().splitlines()
        paths = [p for p in paths if p not in (
            'src/valuation_platform/analyst/retained_components.py',
            'src/valuation_platform/analyst/retained_bridge_components.py',
            'src/valuation_platform/analyst/preparation_validation.py')]
        paths += ['docs/retained-d-and-a-ledger.json', 'docs/pilot-historical-input-mappings.json',
                  'docs/refreshed-capex-ledger.json', 'docs/retained-tax-sbc-ledger.json',
                  'docs/retained-working-capital-ledger.json']
        for path in paths:
            assert_preserved(self, ROOT, path, baseline)

    def test_only_reviewed_negative_da_and_orcl_observation_transitions(self):
        baseline = 'cbe33aba56133c1b8b03153f883aface272180da'
        for name in ('retained-d-and-a-ledger.json', 'retained-bridge-component-ledger.json'):
            path = 'docs/' + name
            old = json.loads(subprocess.check_output(['git', 'show', baseline + ':' + path], cwd=ROOT))
            new = json.loads((ROOT / path).read_text())
            assert_preserved(self, ROOT, path, baseline)
            self.assertEqual(len(old['rows']), len(new['rows']))
            changes = []
            for before, after in zip(old['rows'], new['rows']):
                self.assertEqual(before['identity'], after['identity'])
                if name.startswith('retained-d-and-a'):
                    if before != after:
                        changes.append(after['issuer'])
                        self.assertEqual((before['status'], after['status'], after['value_usd']),
                                         ('DIRECT', 'SCOPE_DOWNGRADED', None))
                        self.assertEqual({k for k in after if before[k] != after[k]},
                                         {'policy', 'status', 'support_observations', 'value_usd'})
                else:
                    self.assertEqual({k:v for k,v in before.items() if k not in ('fields','diagnostics')},
                                     {k:v for k,v in after.items() if k not in ('fields','diagnostics')})
                    self.assertEqual(before['diagnostics'], [r for r in after['diagnostics']
                                     if r['concept']!='LongTermNotesAndLoans'])
                    for diagnostic in after['diagnostics']:
                        if diagnostic['concept']=='LongTermNotesAndLoans':
                            self.assertEqual(after['issuer'], 'ORCL')
                            self.assertEqual(diagnostic['disposition'], 'STANDARD_NON_DIMENSIONAL_INSTANT_CANDIDATE')
                    for field in before['fields']:
                        a, b = before['fields'][field], after['fields'][field]
                        self.assertEqual(a['observations'], [r for r in b['observations']
                                         if r['concept'] != 'LongTermNotesAndLoans'])
                        added = [r for r in b['observations'] if r['concept']=='LongTermNotesAndLoans']
                        if added:
                            self.assertEqual(after['issuer'], 'ORCL'); self.assertEqual(len(added), 1)
                            changes.append(after['issuer'])
                        self.assertEqual({k:v for k,v in a.items() if k not in ('observations','unobserved_concepts')},
                                         {k:v for k,v in b.items() if k not in ('observations','unobserved_concepts')})
                        self.assertEqual([c for c in b['unobserved_concepts'] if c!='LongTermNotesAndLoans'],
                                         a['unobserved_concepts'])
            self.assertEqual(sorted(changes), sorted(['AMZN']*5+['HD']*2) if name.startswith('retained-d-and-a') else ['ORCL']*5)

    def test_exact_claims_preservation_loop_with_reviewed_ledger_transitions(self):
        baseline = 'cbe33aba56133c1b8b03153f883aface272180da'
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', baseline,
            'src/valuation_platform/normalization', 'docs/evidence', 'docs/universe'], cwd=ROOT).decode().splitlines()
        paths += ['docs/retained-bridge-component-ledger.json', 'docs/retained-d-and-a-ledger.json',
                  'docs/pilot-historical-input-mappings.json', 'docs/retained-cfo-ledger.json',
                  'docs/retained-working-capital-ledger.json', 'docs/retained-tax-sbc-ledger.json',
                  'docs/refreshed-capex-ledger.json']
        for path in paths:
            assert_preserved(self, ROOT, path, baseline)
