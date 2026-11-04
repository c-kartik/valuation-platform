from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from valuation_platform.review import apple_resolution as resolution
from valuation_platform.review.pilot_cashflows import read_cashflows,RESOURCE as PRIOR
ROOT=Path(__file__).resolve().parents[2]

class AppleResolutionTests(unittest.TestCase):
    def test_progress_cannot_clear_financing_claims_or_company(self):
        d=resolution.read_resolution(ROOT)
        self.assertFalse(d['company_complete'])
        self.assertEqual(d['stages'][2]['outcome'],'POLICY_ADOPTED')
        for key in d['readiness']:
            bad=deepcopy(d);bad['readiness'][key]=True
            with self.assertRaises(ValueError):resolution.validate(bad)
        bad=deepcopy(d);bad['company_complete']=True
        with self.assertRaises(ValueError):resolution.validate(bad)

    def test_dated_share_population_cannot_be_eps_cover_or_automatic_rsu(self):
        d=resolution.read_resolution(ROOT)
        self.assertEqual(d['anchor_support']['dated_common_shares'],'14773260000')
        for change in ({'concept':'WeightedAverageNumberOfDilutedSharesOutstanding'}, {'as_of':'2025-10-17'}, {'award_adjusted_shares':'14924834000'}):
            bad=deepcopy(d);bad['share_population'].update(change)
            with self.assertRaises(ValueError):resolution.validate(bad)
        bad=deepcopy(d);bad['anchor_support']['fair_value_per_share_usd']='175'
        with self.assertRaises(ValueError):resolution.validate(bad)

    def test_runtime_keeps_metrics_and_legacy_original_review(self):
        current=read_cashflows(ROOT,'AAPL');old=json.loads((ROOT/PRIOR).read_text())['companies']['AAPL']
        self.assertEqual(current['legacy_review_scope_items'],old['unresolved_scope_items'])
        self.assertNotIn('A1',current['unresolved_scope_items']);self.assertNotIn('A7',current['unresolved_scope_items'])
        self.assertEqual(current['readiness']['counts']['missing_required_input'],0)
        self.assertFalse(current['review_passed'])
        for p,q in zip(current['periods'],old['periods'],strict=True):
            self.assertEqual(p['fcfe'],q['fcfe']);self.assertEqual(p['legacy_cfo_fcff'],q['fcff'])
        self.assertEqual(read_cashflows(ROOT,'META')['periods'],json.loads((ROOT/PRIOR).read_text())['companies']['META']['periods'])

    def test_pin_and_re_pinned_invalid_clearance_fail_closed(self):
        original=(ROOT/resolution.RESOURCE).read_bytes()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);p=root/resolution.RESOURCE;p.parent.mkdir(parents=True);p.write_bytes(original+b' ')
            with self.assertRaises(ValueError):resolution.read_resolution(root)
            d=json.loads(original);d['readiness']['fair_value_per_share']=True;b=json.dumps(d).encode();p.write_bytes(b)
            with patch.object(resolution,'PIN',hashlib.sha256(b).hexdigest()):
                with self.assertRaises(ValueError):resolution.read_resolution(root)

if __name__=='__main__':unittest.main()
