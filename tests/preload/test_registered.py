"""Independent financial arithmetic and source isolation for peer preloads."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from valuation_platform.preload.generate import generate, engine_request
from valuation_platform.preload.issuers import registration, resolve_listing, routes
from valuation_platform.preload.profile import refresh_diff
from valuation_platform.valuation.case_inputs import read_case, run_case

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from prepare_preload_observations import build as replay_observations


class RegisteredPreloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles={t:generate(ROOT,ticker=t) for t in ('GOOGL','META','AAPL')}

    def test_alphabet_economic_hash_unchanged_and_issuer_registration_explicit(self):
        self.assertEqual(self.profiles['GOOGL']['economic_hash'],'1c652c65ae2cd9cbf5f726f163963434c17514c6f2b1a0afcf229d059a1768fe')
        self.assertEqual(set(routes()),{'googl-fy2025','meta-fy2025','aapl-fy2025'})
        self.assertEqual(resolve_listing('GOOG')['listing_class'],'C')
        for ticker in ('MSFT','JPM','../META',''):
            with self.assertRaises(ValueError):registration(ticker)

    def test_offline_repeatability_and_primary_mapping_replay(self):
        for ticker in ('META','AAPL'):
            directory=ROOT/'data/preload'/registration(ticker)['dataset']
            with patch.object(socket,'socket',side_effect=AssertionError('No network')):
                a=generate(ROOT,ticker=ticker,generated_at='2026-11-02T01:00:00Z')
                b=generate(ROOT,ticker=ticker,generated_at='2026-11-02T02:00:00Z')
                self.assertEqual(a['economic_hash'],b['economic_hash'])
                self.assertEqual(a['economic'],b['economic'])
                self.assertEqual(replay_observations(ROOT,ticker),json.loads((directory/'observations.json').read_text()))

    def test_independent_fraction_every_forward_amount_terminal_and_ev(self):
        # No estimator or engine helper produces expected values.
        settings={
            'META':{'anchor':F(200966000000),'first':F(181712000000)+F(73000000000+76000000000,2),
                'margin':None,'endg':F('.08'),'endm':F('.35'),'tax0':F('.16'),'tax1':F('.20'),
                'cash':F(140000000000)-F(2769000000)*F(4,3),'cash_growth':[F('.2'),F('.1'),F(0),F('-.05')],
                'finance':F('.03'),'da':F(19509000000)*F(4,3),'wc':F('.1'),'wacc':F('.092535'),
                'g':F('.03'),'tm':F('.35'),'tt':F('.20'),'tda':F('.14'),'ti':F('.20')},
            'AAPL':{'anchor':F(416161000000),'first':F(364357000000)+(F(416161000000)-F(313695000000))*F(109417,94036),
                'margin':F(35695,109417),'endg':F('.05'),'endm':F('.315'),'tax0':F('.18'),'tax1':F('.20'),
                'cash':F(6799000000)*F(4,3),'cash_growth':[F('.1'),F('.08'),F('.06'),F('.05')],
                'finance':F('.01'),'da':F(9973000000)*F(4,3),'wc':F('.05'),'wacc':F('.0827275'),
                'g':F('.025'),'tm':F('.315'),'tt':F('.20'),'tda':F('.025'),'ti':F('.035')},
        }
        tolerance=F(1,10**30)
        for ticker,s in settings.items():
            profile=self.profiles[ticker];doc=engine_request(profile);result=run_case(read_case(json.dumps(doc)),ROOT)['stage_b']
            g0=s['first']/s['anchor']-1;m0=s['margin'] if s['margin'] is not None else (s['first']-F(177000000000))/s['first']
            previous=s['anchor'];cash=s['cash'];da=s['da'];prior_invest=None;pv=F(0)
            for i,year in enumerate(result['stage_a']['years']):
                g=g0+(s['endg']-g0)*F(i,4);margin=m0+(s['endm']-m0)*F(i,4);taxrate=s['tax0']+(s['tax1']-s['tax0'])*F(i,4)
                revenue=previous*(1+g);ebit=revenue*margin;tax=ebit*taxrate;nopat=ebit-tax
                if i:cash*=1+s['cash_growth'][i-1];da+=prior_invest*F('.1')
                investment=cash*(1+s['finance']);wc=s['wc']*(revenue-previous);fcff=nopat+da-investment-wc
                for key,value in {'revenue':revenue,'ebit':ebit,'tax':tax,'nopat':nopat,'d_and_a':da,'investment':investment,'working_capital_cash_requirement':wc,'fcff':fcff}.items():
                    self.assertLess(abs(F(year[key])-value),tolerance,(ticker,i,key))
                pv+=fcff/(1+s['wacc'])**(i+1);previous=revenue;prior_invest=investment
            tr=previous*(1+s['g']);tf=tr*(s['tm']*(1-s['tt'])+s['tda']-s['ti']-s['wc']*s['g']/(1+s['g']))
            ev=pv+tf/(s['wacc']-s['g'])/(1+s['wacc'])**5
            self.assertLess(abs(F(result['enterprise_value'])-ev),tolerance,ticker)
            self.assertEqual(F(doc['wacc']),s['wacc'])

    def test_fiscal_dates_guidance_classification_and_no_gross_capex_substitution(self):
        apple=self.profiles['AAPL']['economic'];meta=self.profiles['META']['economic']
        self.assertEqual(apple['dates']['model_origin'],'2025-09-27')
        a={o['key']:o for o in apple['observations']}
        self.assertEqual((a['ytd2026_revenue']['start'],a['ytd2026_revenue']['end']),('2025-09-28','2026-06-27'))
        self.assertEqual(a['ytd2025_revenue']['end'],'2025-06-28')
        self.assertEqual(meta['fields']['forecast_years[0].operating_margin']['rule'],'full-year-expense-guidance-margin-fade-v1')
        self.assertEqual(F(meta['fields']['forecast_years[0].capex_percent_revenue']['operands']['cash_ppe_usd']),F(136308000000))
        self.assertEqual(F(meta['fields']['forecast_years[0].capex_percent_revenue']['operands']['new_financed_assets_usd']),F(4089240000))
        for o in meta['observations']:
            if 'guidance' in o['key']:self.assertEqual((o['classification'],o['definition']),('MANAGEMENT_GUIDANCE','consolidated-guidance'))
        for economic in (apple,meta):
            self.assertTrue(all(f['value'] is not None for p,f in economic['fields'].items() if p!='exit_ev_ebit_multiple'))
            self.assertIsNone(economic['fields']['exit_ev_ebit_multiple']['value'])
            self.assertEqual(economic['optional_bridge']['status'],'UNSUPPORTED_PREPARATION')
            self.assertTrue(all('FORECAST_ESTIMATE' in f['classification'] for f in economic['fields'].values()))

    def test_wrong_issuer_snapshot_and_same_hash_numeric_tampering_fail(self):
        with self.assertRaisesRegex(ValueError,'issuer/anchor'):
            generate(ROOT,ticker='AAPL',dataset=ROOT/'data/preload/meta-v1')
        with tempfile.TemporaryDirectory() as folder:
            directory=Path(folder)/'aapl';shutil.copytree(ROOT/'data/preload/aapl-v1',directory)
            path=directory/'observations.json';original=json.loads(path.read_text())
            for change in ({'value':'1'},{'start':'2026-01-01'},{'precision':'0'}):
                rows=deepcopy(original);rows[0].update(change);path.write_text(json.dumps(rows))
                with self.assertRaises(ValueError):generate(ROOT,ticker='AAPL',dataset=directory)
            path.write_text(json.dumps(original))
            source=directory/'sources/q3-2026-10q.html';source.write_bytes(source.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'immutable manifest'):generate(ROOT,ticker='AAPL',dataset=directory)

    def test_partial_missing_profile_has_typed_gaps_and_no_issuer_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            directory=Path(folder)/'meta';shutil.copytree(ROOT/'data/preload/meta-v1',directory)
            path=directory/'observations.json';rows=json.loads(path.read_text());path.write_text(json.dumps([o for o in rows if o['key']!='q42026_revenue_guidance_low']))
            p=generate(ROOT,ticker='META',dataset=directory)
            self.assertEqual(p['economic']['fields']['forecast_years[0].revenue_growth']['status'],'MISSING_EVIDENCE')
            self.assertIsNone(p['economic']['fields']['forecast_years[0].revenue_growth']['value'])
            self.assertIsNotNone(p['economic']['fields']['wacc']['value'])
            with self.assertRaisesRegex(ValueError,'Unavailable required inputs'):engine_request(p)
            self.assertIn('forecast_years[0].revenue_growth',refresh_diff(self.profiles['META'],p)['gap_changes'])

    def test_cli_generates_and_exports_each_peer_through_existing_engine(self):
        with tempfile.TemporaryDirectory() as folder:
            for ticker in ('META','AAPL'):
                profile_path=Path(folder)/(ticker+'.json');destination=Path(folder)/ticker
                subprocess.check_output([sys.executable,str(ROOT/'scripts/prepare_preload.py'),'generate',str(profile_path),'--ticker',ticker],cwd=ROOT)
                p=json.loads(profile_path.read_text());self.assertEqual(p['economic_hash'],self.profiles[ticker]['economic_hash'])
                subprocess.check_output([sys.executable,str(ROOT/'scripts/prepare_preload.py'),'export',str(profile_path),str(destination),'--run'],cwd=ROOT)
                request=json.loads((destination/'request.json').read_text())
                result=json.loads((destination/'result.json').read_text())
                self.assertEqual(request['anchor'],p['economic']['anchor'])
                self.assertEqual(result,run_case(read_case(json.dumps(request)),ROOT))


if __name__=='__main__':unittest.main()
