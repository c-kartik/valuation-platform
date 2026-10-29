"""Offline fixtures only; primary sources are recorded separately, never fetched here."""
from copy import deepcopy
from datetime import datetime,date,timezone
from decimal import Decimal as D,localcontext,Inexact,ROUND_DOWN
from fractions import Fraction as F
from pathlib import Path
import json,unittest
from unittest.mock import patch,Mock
from fastapi.testclient import TestClient
from valuation_platform.review.sources import MarketOpening,FinancialContext
from valuation_platform.review.market import MassiveProvider,MarketUnavailable
from valuation_platform.review.comparison import run_review,revenue_cagr
from valuation_platform.review.prepare import prepare_context
from valuation_platform.valuation import case_inputs as c,scenario_inputs as ss,sensitivity_inputs as s,reverse_inputs as r
from valuation_platform.api.app import create_app
from tests.api.test_cases import BundleFixture,payload
from tests.api.test_sensitivity import document as grid
from tests.api.test_reverse import document as reverse
ROOT=Path(__file__).resolve().parents[2]
UTC=timezone.utc

def observation(price='10',split=True,ticker='GOOGL',day=date(2025,12,31)):
    return MarketOpening(ticker,D(price),day,datetime.combine(day,datetime.min.time(),UTC).replace(hour=14,minute=30),datetime(2026,1,5,tzinfo=UTC),f'https://api.massive.com/v1/open-close/{ticker}/{day}?adjusted=false','fixture:opening','Fixture, not live','Fixture observed session','Class A' if ticker!='AAPL' else 'Common',split_compatible=split)

def case():
    d=payload(True,'googl-fy2025');d['schema_version']='investor-case-v2';d.pop('analyst');d.pop('scope');d['preparation']={'provenance':'ANONYMOUS_INVESTOR','timestamp_utc':'2026-10-29T12:00:00Z','notes':'Synthetic verification only'};d['bridge']['shares']['equivalence_convention']='explicit_common_unit_equivalence';return d

class ComparisonTests(unittest.TestCase):
    def test_supported_reconciliation_cagr_certified_target_and_one_source_load(self):
        d=case();changed=deepcopy(d)
        for year in changed['forecast_years']:year['revenue_growth']='0.073456789123'
        forward=c.run_case(c.read_case(json.dumps(changed)),ROOT)
        with localcontext() as ctx:
            ctx.prec=80
            price=(D(forward['stage_b']['enterprise_value'])-11)/4
        with patch.object(c,'load_revenue_anchor',wraps=c.load_revenue_anchor) as load:
            out=run_review(c.read_case(json.dumps(d)),ROOT,observation(str(price)));self.assertEqual(load.call_count,1)
        review=out['review'];self.assertEqual(review['status'],'SCOPE_QUALIFIED');self.assertEqual(review['reverse']['status'],'SUCCESS')
        cap=F(str(price))*4;target=cap-12+20+3
        self.assertEqual(F(review['market_cap']),cap);self.assertEqual(F(review['market_implied_ev']),target)
        self.assertAlmostEqual(D(review['forecast_cagr']),D('0.1'),places=45)
        sol=review['reverse']['solution'];self.assertLessEqual(D(sol['absolute_residual']),D(sol['residual_tolerance']))
        fresh=c.run_case(c.read_case(json.dumps(sol['forward_result']['submitted_inputs'])),ROOT);self.assertEqual(fresh,sol['forward_result'])
        self.assertEqual(out['result'],c.run_case(c.read_case(json.dumps(d)),ROOT))

    def test_missing_market_timing_split_class_and_bridge_block_without_zero_or_root(self):
        base=case()
        tests=[(base,None,'Opening'),(base,observation(split=False),'split'),(base,observation(ticker='META'),'company')]
        d=deepcopy(base);d['bridge']['shares']['equivalence_convention']='single_common_class';tests.append((d,observation(),'equivalence'))
        d=deepcopy(base);d.pop('bridge');d.pop('calculation_scope');d['schema_version']='investor-case-v1';tests.append((d,observation(),'bridge'))
        for d,market,reason in tests:
            out=run_review(c.read_case(json.dumps(d)),ROOT,market);self.assertEqual(out['review']['status'],'UNAVAILABLE');self.assertIsNone(out['review']['market_cap']);self.assertIsNone(out['review']['reverse']);self.assertIn(reason,' '.join(out['review']['reasons']))
        late=observation();from dataclasses import replace
        late=replace(late,session_date=date(2026,1,2),observed_at=datetime(2026,1,2,14,30,tzinfo=UTC))
        self.assertIn('stub',' '.join(run_review(c.read_case(json.dumps(base)),ROOT,late)['review']['reasons']))

    def test_negative_target_honest_failure_and_decimal_context_isolation(self):
        d=case();market=observation('0.001')
        out=run_review(c.read_case(json.dumps(d)),ROOT,market)
        self.assertIsNone(out['review']['market_implied_growth']);self.assertNotEqual(out['review']['reverse']['status'],'SUCCESS')
        with localcontext() as ctx:
            ctx.prec=3;ctx.rounding=ROUND_DOWN;ctx.traps[Inexact]=True;before=ctx.copy()
            self.assertEqual(run_review(c.read_case(json.dumps(d)),ROOT,market),out)
            self.assertEqual(ctx.prec,before.prec);self.assertEqual(ctx.flags,before.flags)

    def test_nullable_v2_metadata_v1_still_strict_and_no_calculation_in_readers(self):
        docs=[(s,grid(False,'googl-fy2025')),(r,reverse(False,'googl-fy2025'))]
        for module,d in docs:
            d['source']['information_cutoff']=None;reader=module.read_sensitivity if module is s else module.read_reverse
            with self.assertRaises(ValueError):reader(json.dumps(d))
            d['schema_version']=module.REVIEW_SCHEMA
            with patch.object(c,'load_revenue_anchor',side_effect=AssertionError('no history')):parsed=reader(json.dumps(d))
            result=(module.run_sensitivity if module is s else module.run_reverse)(parsed,ROOT)
            self.assertIsNone(result['selection']['information_cutoff']);self.assertTrue(result['schema_version'].endswith('v2'))
        from tests.valuation.test_scenarios import document
        d=document();d['schema_version']=ss.REVIEW_SCHEMA
        for row in d['scenarios']:row['information_cutoff']=None;row['case']=case()
        out=ss.run_scenario_set(ss.read_scenario_set(json.dumps(d)),ROOT)
        self.assertTrue(all(row['information_cutoff']is None for row in out['scenarios']))

class ProviderTests(unittest.TestCase):
    def test_unconfigured_or_no_rights_never_fetches(self):
        fetch=Mock(side_effect=AssertionError('network'))
        for key,rights in [(None,True),('fixture',False)]:
            with self.assertRaises(MarketUnavailable):MassiveProvider(key,rights,'delayed',fetch).opening('META',datetime.now(UTC))
        fetch.assert_not_called()

    def test_preopen_weekend_holiday_and_today_unavailable_use_actual_returned_session(self):
        for now in (datetime(2026,7,6,12,tzinfo=UTC),datetime(2026,7,5,18,tzinfo=UTC),datetime(2026,7,3,18,tzinfo=UTC)):
            calls=[];day=date(2026,7,2);epoch=int(datetime(2026,7,2,tzinfo=__import__('zoneinfo').ZoneInfo('America/New_York')).timestamp()*1000)
            def fetch(path):
                calls.append(path)
                if '/range/'in path:return {'ticker':'AAPL','adjusted':False,'results':[{'t':epoch}]}
                if '2026-07-02'not in path:return {'status':'NOT_FOUND'}
                return {'status':'OK','symbol':'AAPL','from':str(day),'open':'200.125'}
            o=MassiveProvider('fixture',True,'15-minute delayed',fetch).opening('AAPL',now)
            self.assertEqual(o.session_date,day);self.assertEqual(o.price,D('200.125'));self.assertIn('Previous',o.fallback);self.assertLessEqual(len(calls),3);self.assertFalse(o.split_compatible)
        provider=MassiveProvider('fixture',True,'delayed',lambda _: {'status':'OK','symbol':'AAPL','from':'2026-07-06','open':'201'})
        o=provider.opening('AAPL',datetime(2026,7,6,14,tzinfo=UTC));self.assertEqual(o.session_date,date(2026,7,6))
        with self.assertRaises(MarketUnavailable):provider.decode('AAPL',{'status':'OK','symbol':'AAPL','from':'2026-07-06','open':'201','adjusted':True},datetime(2026,7,6,14,tzinfo=UTC),'fixture')
        stale=MassiveProvider('fixture',True,'delayed',lambda _: {'status':'OK','symbol':'AAPL','from':'2026-07-02','open':'201'})
        with self.assertRaises(MarketUnavailable):stale.opening('AAPL',datetime(2026,7,6,14,tzinfo=UTC))

class ApiReviewTests(BundleFixture,unittest.TestCase):
    def test_forward_survives_market_failure_matches_legacy_and_rejects_browser_quote(self):
        provider=Mock();provider.opening.side_effect=MarketUnavailable('Unavailable test provider')
        with TestClient(create_app(self.bundle,market_provider=provider)) as client:
            d=case();out=client.post('/api/v1/review/run',json=d);self.assertEqual(out.status_code,200,out.text)
            self.assertEqual(out.json()['result'],client.post('/api/v1/cases/run',json=d).json());self.assertEqual(out.json()['review']['status'],'UNAVAILABLE');self.assertEqual(provider.opening.call_count,1)
            bad=deepcopy(d);bad['market']={'price':'1'};self.assertEqual(client.post('/api/v1/review/run',json=bad).status_code,422)
            with patch('valuation_platform.api.process.Calculator.run',side_effect=AssertionError('spawn')):
                self.assertEqual(client.post('/api/v1/cases/validate',json=d).status_code,200)
            context=client.get('/api/v1/catalog').json()['entries'][0]['financial_context'];self.assertFalse(context['valuation_anchor_approved']);self.assertIsNone(context['information_cutoff'])

    def test_review_shares_gate_timeout_cleanup_and_strict_intake(self):
        import concurrent.futures,multiprocessing
        from tests.api.test_cases import blocking_worker
        from valuation_platform.api.budget import ServerPolicy
        from valuation_platform.api.worker import calculate
        ctx=multiprocessing.get_context('spawn');started,release=ctx.Event(),ctx.Event()
        provider=Mock();provider.opening.side_effect=MarketUnavailable('Fixture unavailable')
        with TestClient(create_app(self.bundle,policy=ServerPolicy(deadline_seconds=3),worker_target=blocking_worker,worker_args=(started,release),market_provider=provider)) as client:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pending=pool.submit(client.post,'/api/v1/review/run',json=case());self.assertTrue(started.wait(5))
                for route in ('review','cases','scenarios','sensitivity','reverse'):
                    self.assertEqual(client.post('/api/v1/'+route+'/run',json={}).status_code,503)
                self.assertEqual(client.post('/api/v1/cases/validate',json=case()).status_code,200)
                self.assertEqual(pending.result().status_code,504)
            self.assertIsNone(client.app.state.calculator.job);self.assertEqual(provider.opening.call_count,1)
            client.app.state.calculator.target=calculate;client.app.state.calculator.target_args=()
            self.assertEqual(client.post('/api/v1/review/run',json=case()).status_code,200)
            self.assertEqual(client.post('/api/v1/review/run?bounds=wide',json=case()).status_code,422)
            self.assertEqual(client.post('/api/v1/review/run',json=case(),headers={'Sec-Fetch-Site':'cross-site'}).status_code,403)
            self.assertEqual(client.post('/api/v1/review/run',content=b'x'*(256*1024+1),headers={'Content-Type':'application/json'}).status_code,413)

class ReviewPrecisionTests(unittest.TestCase):
    def test_varying_growth_cagr_is_not_arithmetic_average_and_metadata_immutable(self):
        d=case()
        for y,g in zip(d['forecast_years'],('0.2','0','-0.1','0.3','0.05')):y['revenue_growth']=g
        out=run_review(c.read_case(json.dumps(d)),ROOT)
        ratio=F(1)
        for year in d['forecast_years']:ratio*=1+F(year['revenue_growth'])
        cagr=F(out['review']['forecast_cagr']);self.assertLess(abs((1+cagr)**5-ratio),F('1e-47'))
        self.assertGreater(abs(cagr-sum((F(y['revenue_growth'])for y in d['forecast_years']),F(0))/5),F('0.001'))
        self.assertEqual(out['result']['submitted_inputs'],d)
