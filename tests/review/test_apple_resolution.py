"""Apple decisions, original-source cash signs, scope and no silent adoption."""
from copy import deepcopy
from decimal import Inexact, ROUND_DOWN, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import resolve_apple_cashflows as resolution


class AppleResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=resolution.build()
        cls.mapping=json.loads((ROOT/resolution.SOURCE_MAP).read_text())
        package=json.loads((ROOT/resolution.ANCHORS['aapl-fy2025']['package']).read_text())
        cls.source=package['aapl_history_review']['periods'][0]
        cls.filing=resolution.RetainedFiling(ROOT,cls.source,{})

    def test_five_known_debt_schedules_and_fcfe_values_independently(self):
        # Independently reviewed statement amounts; no expected value is read
        # from the generated result or inferred by subtraction from its FCFE.
        cfo=[104038,122151,110543,118254,111482]
        ppe=[11085,10708,10959,9447,12715]
        funding=[12665,-123,-9901,-5998,-8483]
        expected=[105618,111320,89683,102809,90284]
        other=[-129,-160,-581,-361,-111]
        self.assertEqual(len(self.data['periods']),5)
        for i,p in enumerate(self.data['periods']):
            self.assertEqual(Fraction(p['fcfe']['amount_usd']),expected[i]*1000000)
            self.assertEqual((cfo[i]-ppe[i]+funding[i])*1000000,expected[i]*1000000)
            self.assertEqual(Fraction(p['financing']['net_borrowing']['amount_usd']),funding[i]*1000000)
            self.assertEqual(Fraction(p['financing']['unknown_components'][0]['amount_usd']),other[i]*1000000)
            self.assertFalse(p['fcfe']['publishable_as_verified'])
            self.assertFalse(p['fcfe']['omitted_other_is_assumed_zero'])
            self.assertEqual(p['financing']['statement_difference_usd'],'0')

    def test_equity_presentation_bridge_has_no_fcfe_effect(self):
        b=self.data['presentation_bridge']
        source_values=sorted(Fraction(p['signed_cash_usd']) for rows in b['source_terms'].values() for p in rows)
        self.assertEqual(source_values,[-129000000,976000000,1105000000])
        self.assertEqual(b['difference_usd'],'0')
        self.assertEqual(b['fcfe_change_usd'],'0')
        self.assertEqual(b['status'],'RESOLVED_NO_NUMERIC_CHANGE')

    def test_method_approval_does_not_certify_alignment_or_mutate_chart(self):
        expected=['95.25','113.90','102.94',None,None]
        for p,old in zip(self.data['periods'],expected,strict=True):
            self.assertEqual(p['platform_before'],p['platform_after'])
            self.assertIsNone(p['verified_operating_fcff'])
            candidate=p['operating_fcff_candidate']
            self.assertIsNone(candidate['verified_operating_fcff'])
            self.assertEqual(candidate['cash_fcf_bridge']['difference_usd'],'0')
            self.assertFalse(candidate['operating_method_test']['sbc_addback'])
            self.assertFalse(candidate['operating_method_test']['interest_addback'])
            actual=p['platform_after']['fcff_usd']
            self.assertEqual(None if actual is None else f'{Fraction(actual)/1000000000:.2f}',old)
        self.assertTrue(all(v is False for k,v in self.data['publication'].items() if k!='reason'))

    def test_no_implicit_zero_for_unknown_financing_or_duplicate_parent(self):
        rows=deepcopy(self.mapping['periods'][0]['financing_rows'])
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            resolution.classified_cash(rows+[rows[4]])
        changed=deepcopy(rows)
        changed[0]['classification']='DEBT_FUNDING_OR_PRINCIPAL'
        changed[0]['included_in_net_borrowing']=True
        with self.assertRaisesRegex(ValueError,'caption/role'):
            resolution.classified_cash(changed)
        changed=[r for r in rows if r['classification']!='OTHER_FINANCING_EXCLUDED']
        with self.assertRaises(ValueError):resolution.classified_cash(changed)
        changed=deepcopy(rows);changed[4]['signed_cash_usd']=None
        with self.assertRaises(ValueError):resolution.classified_cash(changed)

    def test_source_change_cash_sign_and_omitted_actual_cell_fail(self):
        maps=self.mapping['periods'][0]['financing_rows']
        for key,value in [('raw_value_usd','999'),('caption','Unreviewed debt label'),('cash_sign',-1)]:
            changed=deepcopy(maps[0]);changed[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                resolution.verify_cell(self.filing,self.source['identity'],changed)
        with self.assertRaises(ValueError):
            resolution.full_financing(self.filing,self.source['identity'],maps[:-2]+maps[-1:])

    def test_financing_arithmetic_is_exact_under_hostile_decimal_context(self):
        rows=self.mapping['periods'][0]['financing_rows']
        normal=resolution.classified_cash(rows)
        with localcontext() as ctx:
            ctx.prec=3;ctx.rounding=ROUND_DOWN;ctx.traps[Inexact]=True
            self.assertEqual(resolution.classified_cash(rows),normal)

    def test_explicit_approval_scope_and_no_estimate_publication(self):
        data=deepcopy(self.data['decisions'])
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/resolution.DECISIONS).parent.mkdir(parents=True)
            for key,value in [('ticker','META'),('automatic_publication',True),('estimates_permitted',True)]:
                changed=deepcopy(data);changed[key]=value
                (root/resolution.DECISIONS).write_text(json.dumps(changed))
                with self.subTest(key=key),self.assertRaises(ValueError):resolution.approved_decisions(root)

    def test_committed_results_csv_and_input_hashes_reproduce(self):
        self.assertEqual(json.loads((ROOT/resolution.OUTPUT).read_text()),self.data)
        self.assertEqual((ROOT/resolution.CSV_OUTPUT).read_text(),resolution.csv_output(self.data))
        for path,digest in self.data['inputs_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)


if __name__=='__main__':unittest.main()
