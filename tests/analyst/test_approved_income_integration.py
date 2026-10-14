"""No fabricated metadata; approved operands are replayed, never copied outputs."""
from collections import Counter
from dataclasses import replace
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import unittest
from tests.analyst.preparation_preservation import assert_preserved
from unittest.mock import patch
from valuation_platform.analyst import approved_income_integration as integration
from valuation_platform.analyst import retained_income_sweep as sweep, historical_inputs as h
from valuation_platform.analyst import nvda_income_inputs as shared
from valuation_platform.normalization import operating_income_derivation as policy

BASELINE='14f2d34496f94660111e01d34d77bdd6c6ea4bc8'


class ApprovedIncomeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger,cls.histories=integration.build();cls.data=integration.bindings()
        cls.before=json.loads((shared.ROOT/'docs/retained-income-sweep-ledger.json').read_text())
        cls.config,cls.refs=sweep.sources()
        cls.manifest=shared.pinned(shared.MANIFEST,shared.MANIFEST_SHA256)

    def test_scope_direct_derived_and_precise_remaining_requirements(self):
        self.assertEqual(self.ledger['outcomes'],dict(POPULATED=337,DERIVED=15,CONFLICTING_VALUES=11,
            NO_ELIGIBLE_DIRECT_CONCEPT=15,MISSING_RETAINED_BODY=18,INSUFFICIENT_IDENTITY_BINDING=2))
        self.assertEqual(sum(self.ledger['outcomes'].values()),398)
        self.assertEqual(len(self.ledger['derivation_metadata_exceptions']),10)
        self.assertEqual(len(self.ledger['identity_backlog']),1)
        self.assertEqual(self.ledger,json.loads((shared.ROOT/'docs/approved-income-integration-ledger.json').read_text()))
        self.assertEqual(self.ledger,integration.build()[0])

    def test_nine_seed_identities_exact_reviewed_rows_not_inferred_years(self):
        self.assertEqual(len(self.data['seed_identities']),9)
        text=(shared.ROOT/'docs/annual-period-evidence.md').read_text().splitlines()
        for row in self.data['seed_identities']:
            line=int(row['reference'].split(':')[-1]);identity=row['identity']
            self.assertIn(identity['accession'],text[line-1]);self.assertIn(identity['annual_start'],text[line-1])
            found=next(r for r in self.ledger['rows'] if r['issuer']==row['issuer'] and r['identity']==identity)
            self.assertTrue(all(f['outcome']=='MISSING_RETAINED_BODY' for f in found['fields']))
            self.assertIn('not freshly replayed',found['identity_depth'])
        missing=self.ledger['identity_backlog'][0]
        self.assertEqual((missing['issuer'],missing['identity']['annual_end']),('COST','2026-08-30'))
        self.assertIsNone(missing['identity']['accession']);self.assertIsNone(missing['identity']['annual_start'])

    def test_all_337_populated_bindings_and_eleven_conflicts_unchanged(self):
        count=Counter()
        for old,new in zip(self.before['rows'],self.ledger['rows']):
            for f in old['fields']:
                if f['outcome'] in ('POPULATED','CONFLICTING_VALUES'):
                    self.assertEqual(f,next(x for x in new['fields'] if x['field']==f['field']));count[f['outcome']]+=1
        self.assertEqual(count,dict(POPULATED=337,CONFLICTING_VALUES=11))
        self.assertEqual(self.before['history_exceptions'],self.ledger['history_exceptions'])

    def test_all_thirty_ebit_slots_match_only_immutable_registry(self):
        original=[r for r in self.before['rows'] if any(f['field']=='ebit' and f['outcome']=='NO_ELIGIBLE_DIRECT_CONCEPT' for f in r['fields'])]
        self.assertEqual(len(original),30)
        matched=0
        for row in original:
            p=shared.period(row['identity']);entry=policy.operating_income_derivation_entry_for(p.cik,p.accession,p.annual_end,p.annual_start,p.annual_end)
            if entry:matched+=1
            else:self.assertEqual(row['issuer'],'CVX')
        self.assertEqual(matched,25)
        self.assertEqual({r['identity']['cik'] for r in self.ledger['derivation_metadata_exceptions']},{200406,319201})

    def test_operand_arithmetic_precision_and_validation_provenance(self):
        derived=[r for r in self.ledger['rows'] if any(f['outcome']=='DERIVED' for f in r['fields'])]
        self.assertEqual(len(derived),15)
        for row in derived:
            slot=next(f for f in row['fields'] if f['field']=='ebit');proof=slot['provenance']
            self.assertEqual((proof['policy_id'],proof['policy_version']),('operating_income_component_derivation','1'))
            self.assertEqual(sum((Decimal(o['contribution']) for o in proof['operands'] if o['contribution'] is not None),Decimal(0)),Decimal(slot['value_usd']))
            self.assertTrue(all(v['passed'] for v in proof['validations']))
            for o in proof['operands']:
                for occurrence in o['occurrences']:
                    self.assertEqual(occurrence['accession_number'],row['identity']['accession'])
                    self.assertEqual(occurrence['numeric_value'],o['expected_value'])
                    self.assertTrue(occurrence['decimals']);self.assertFalse(occurrence['dimensions'])
            if row['issuer']=='IBM':
                self.assertTrue(all(o['decimals']=='-6' for p in proof['operands'] for o in p['occurrences']))
        lly=next(r for r in derived if r['issuer']=='LLY' and r['identity']['annual_end']=='2025-12-31')
        a=next(o for o in next(f for f in lly['fields'] if f['field']=='ebit')['provenance']['operands'] if o['operand_id']=='A')
        self.assertTrue(a['reviewed_nonselected_occurrences']);self.assertEqual(a['reviewed_nonselected_occurrences'][0]['decimals'],'-8')

    def test_actual_replay_identity_mismatch_and_ibm_precision_gate(self):
        row=next(r for r in self.manifest['rows'] if r['ticker']=='IBM')
        evidence,_,_,_=sweep.inspect_row(row,self.refs,self.config)
        metadata=next(r['filing'] for r in self.data['filings'] if r['filing']['accession_number']==row['identity']['accession'])
        with self.assertRaises(h.InputError):integration.execute(evidence,dict(metadata,accession_number='0000000000-00-000000'))
        with self.assertRaises(h.InputError):integration.execute(evidence,dict(metadata,filing_date='1900-01-01'))
        parsed=integration.parse_filing_xbrl_instance
        seen=[]
        def changed_parse(*args,**kwargs):
            xbrl=parsed(*args,**kwargs);p=evidence.period
            entry=policy.operating_income_derivation_entry_for(p.cik,p.accession,p.annual_end,p.annual_start,p.annual_end)
            concept=entry.operands[0].concept
            facts=tuple(replace(f,decimals='-3') if f.concept==concept and f.start==p.annual_start and f.end==p.annual_end and not f.dimensions else f for f in xbrl.facts)
            seen.append(True);return replace(xbrl,facts=facts)
        with patch.object(integration,'parse_filing_xbrl_instance',side_effect=changed_parse):
            self.assertNotIsInstance(integration.execute(evidence,metadata),integration.DerivedHistoricalValue)
        self.assertTrue(seen)
        self.assertIn('filing_date',metadata)
        self.assertEqual(integration.execute(evidence,metadata).policy_version,'1')

    def test_serialization_preserves_complete_policy_proof_and_rejects_tampering(self):
        history=self.histories['LLY'];annual=history.annuals[-1]
        one=replace(history,annuals=(annual,));payload=h.serialize(one)
        self.assertEqual(h.serialize(integration.validate_serialized_history(payload)),payload)
        root=next(v for v in annual.inputs if v.formula)
        self.assertEqual(root.origin,h.Origin.DERIVED)
        changed=replace(annual,inputs=tuple(replace(v,value=v.value+1) if v is root else v for v in annual.inputs))
        with self.assertRaises(h.InputError):integration.validate_serialized_history(h.serialize(replace(one,annuals=(changed,))))
        changed=replace(root,flags=tuple(f for f in root.flags if not f.startswith(integration.PROOF_FLAG)))
        with self.assertRaises(h.InputError):integration.validate_serialized_history(h.serialize(replace(one,annuals=(replace(annual,inputs=tuple(changed if v is root else v for v in annual.inputs)),))))

    def test_frozen_sources_registries_original_ledger_and_schemas_unchanged(self):
        paths=['src/valuation_platform/normalization/operating_income_derivation.py',
            'src/valuation_platform/analyst/historical_inputs.py','docs/phase1-selected-filing-identity-manifest.json',
            'docs/retained-income-sweep-ledger.json','docs/evidence/income-sweep-backlog-acquisition.json']
        for path in paths:
            assert_preserved(self, shared.ROOT, path, BASELINE)


if __name__=='__main__':unittest.main()
