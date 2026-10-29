from copy import deepcopy
from pathlib import Path
import unittest
from valuation_platform.review.prepare import prepare_context
from valuation_platform.sec.company_facts import CompanyFactsDataError
from valuation_platform.review.sources import FinancialContext

class ContextTests(unittest.TestCase):
    def test_reported_quarter_and_ytd_retained_separately_unknowns_not_zero(self):
        acc='0001652044-26-000084';base={'end':'2026-09-30','accn':acc,'fy':2026,'fp':'Q3','form':'10-Q','filed':'2026-10-29'}
        facts={'cik':1652044,'entityName':'Synthetic source parser fixture','facts':{'us-gaap':{'Revenues':{'label':'Revenue','description':'Fixture','units':{'USD':[{**base,'start':'2026-07-01','val':100},{**base,'start':'2026-01-01','val':250}]}}}}}
        submissions={'cik':'1652044','filings':{'files':[],'recent':{'accessionNumber':[acc],'form':['10-Q'],'filingDate':['2026-10-29'],'reportDate':['2026-09-30'],'primaryDocument':['goog-20260930.htm'],'acceptanceDateTime':['2026-10-29T00:29:06Z']}}}
        sources=[{'url':'https://data.sec.gov/submissions/CIK0001652044.json','checked_at':'2026-10-29T15:24:00+00:00','sha256':'a'*64,'bytes':1},{'url':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001652044.json','checked_at':'2026-10-29T15:25:00+00:00','sha256':'b'*64,'bytes':1}]
        out=prepare_context('GOOGL',submissions,facts,sources)
        self.assertEqual([x['amount']for x in out['observations']],['100','250']);self.assertEqual([x['start']for x in out['observations']],['2026-07-01','2026-01-01']);self.assertEqual(out['checked_at'],'2026-10-29T15:25:00+00:00');self.assertEqual(out['filed'],'2026-10-29');self.assertEqual(out['financials_through'],'2026-09-30');self.assertIsNone(out['information_cutoff']);self.assertFalse(out['valuation_anchor_approved']);self.assertIn('cash_and_cash_equivalents',out['unknown_fields']);self.assertNotIn('ttm',out)
        bad=deepcopy(facts);bad['cik']=123
        with self.assertRaises(CompanyFactsDataError):prepare_context('GOOGL',submissions,bad,sources)
        bad=deepcopy(submissions);bad['cik']='123'
        with self.assertRaisesRegex(ValueError,'company mismatch'):prepare_context('GOOGL',bad,facts,sources)

    def test_retained_current_snapshots_are_context_only_and_distinct_from_approved_anchors(self):
        root=Path(__file__).resolve().parents[2]
        for ticker in ('meta','googl','aapl'):
            snap=FinancialContext.read(root/f'data/investor-context/2026-10-29/{ticker}.json').to_dict()
            self.assertEqual(snap['status'],'NEWER_FILING_AVAILABLE_PREPARATION_INCOMPLETE');self.assertFalse(snap['valuation_anchor_approved']);self.assertIsNone(snap['information_cutoff']);self.assertTrue(snap['sources']);self.assertTrue(snap['unknown_fields']);self.assertTrue(all(x['precision']is None for x in snap['observations']))
