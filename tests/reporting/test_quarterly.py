from datetime import date
from dataclasses import replace
import gzip, json
from pathlib import Path
import unittest
from unittest import TestCase
from valuation_platform.sec.company_facts import fetch_company_facts
from valuation_platform.sec.tickers import SECCompanyIdentity
from valuation_platform.reporting.quarterly import prepare_quarters, ReportingError
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[2]
CIDS = {'GOOGL': 1652044, 'AAPL': 320193, 'META': 1326801}
def fixture(ticker):
    class Client:
        def get_json(self, url):
            return json.loads(gzip.decompress((ROOT/f'data/quarterly-reporting/sources/{ticker}.json.gz').read_bytes()))
    cik=CIDS[ticker]
    return fetch_company_facts(Client(), SECCompanyIdentity(ticker,cik,f'{cik:010d}',ticker,'SEC',datetime.now(timezone.utc)))

def test_pilot_calendar_bridges_and_annuals(ticker):
    result=prepare_quarters(fixture(ticker),date(2026,11,9))
    assert len(result['rows'])==20
    assert result['validation']['excluded_periods']==[]
    assert len(result['validation']['discrete_quarter_checks'])==45
    assert all(abs(c['difference'])<=1000000 for c in result['validation']['discrete_quarter_checks'])
    assert all(t['sum_quarters']==t['annual']['value'] for t in result['validation']['annual_tie_outs'])
    for row in result['rows']:
        v=row['values']
        assert v['net_income']+v['sbc']+v['other_operating']==v['cfo']
        assert v['cfo']-v['cash_capex']==v['fcf']
        assert all(o['filed']<=result['as_of'] for e in row['evidence'].values() for o in e['operands'])
    if ticker=='AAPL':
        assert result['rows'][-1]['end'].endswith(('09-26','09-27','09-28','09-30'))
        assert any(row['start'][-5:] not in ['01-01','04-01','07-01','10-01'] for row in result['rows'])

def test_missing_required_metric_is_not_zero_or_stale_fallback():
    facts=fixture('GOOGL')
    broken=replace(facts,concepts=tuple(c for c in facts.concepts if c.name!='ShareBasedCompensation'))
    with TestCase().assertRaises(ReportingError): prepare_quarters(broken,date(2026,11,9))

def test_same_period_conflicts_are_rejected():
    facts=fixture('GOOGL')
    concepts=[]
    for c in facts.concepts:
        if c.name=='NetCashProvidedByUsedInOperatingActivities':
            originals=[o for o in c.observations if str(o.start)=='2026-01-01' and str(o.end)=='2026-09-30']
            c=replace(c,observations=c.observations+(replace(originals[0],value=originals[0].value+1),))
        concepts.append(c)
    with TestCase().assertRaisesRegex(ReportingError,'Latest reporting period is incomplete'):
        prepare_quarters(replace(facts,concepts=tuple(concepts)),date(2026,11,9))

def test_asof_cutoff_and_negative_free_cash_flow():
    facts=fixture('GOOGL')
    old=prepare_quarters(facts,date(2025,3,1))
    assert old['rows'][-1]['end']=='2024-12-31'
    current=prepare_quarters(facts,date(2026,11,9))
    assert current['rows'][-1]['values']['fcf']<0

class QuarterlyReportingTests(unittest.TestCase):
    def test_alphabet(self): test_pilot_calendar_bridges_and_annuals('GOOGL')
    def test_apple(self): test_pilot_calendar_bridges_and_annuals('AAPL')
    def test_meta(self): test_pilot_calendar_bridges_and_annuals('META')
    def test_missing(self): test_missing_required_metric_is_not_zero_or_stale_fallback()
    def test_conflict(self): test_same_period_conflicts_are_rejected()
    def test_cutoff(self): test_asof_cutoff_and_negative_free_cash_flow()

    def test_offline_reproduction_matches_published_packages(self):
        for ticker in CIDS:
            generated=prepare_quarters(fixture(ticker),date(2026,11,9))
            published=json.loads((ROOT/f'frontend/public/research-data/{ticker}.json').read_text())
            generated['source_snapshot_sha256']=published['source_snapshot_sha256']
            self.assertEqual(generated,published)
            receipt=json.loads((ROOT/f'data/quarterly-reporting/{ticker}-filing-validation.json').read_text())
            self.assertEqual(receipt['source_snapshot_sha256'],published['source_snapshot_sha256'])
            self.assertEqual(receipt['checks'],18)
            self.assertTrue(all(r['status']=='MATCH' for r in receipt['evidence']))
