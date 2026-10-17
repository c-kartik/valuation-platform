"""Original primary/instance review bindings, not automatic issuer approvals."""
from copy import deepcopy
from datetime import date
from decimal import Decimal as D
from io import BytesIO
import hashlib,json,subprocess,sys,types,unittest
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import prepare_network_retail_review_batch as p
import tests.analyst.test_standard_review_batch as source_tests


class NetworkRetailReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=p.outputs();cls.packages={t:cls.outputs[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'] for t in p.TICKERS}
        cls.summary=cls.outputs[p.SUMMARY];cls.artifact_files={}

    _artifact=source_tests.StandardReviewBatchTests._artifact

    def test_every_source_occurrence_original_receipt_and_independent_primary(self):
        source_tests.StandardReviewBatchTests.test_every_source_occurrence_primary_representation_and_receipt(self)

    def test_fifteen_exact_identities_fiscal_labels_and210_family_slots(self):
        manifest=json.loads((ROOT/p.shared.MANIFEST).read_text())
        for t,package in self.packages.items():
            rows=package['periods'];expected=sorted([r['identity'] for r in manifest['rows'] if r['identity']['cik']==rows[0]['identity']['cik']],key=lambda r:r['annual_end'])
            self.assertEqual([r['identity'] for r in rows],expected);self.assertEqual(len(rows),5)
            self.assertEqual([r['fiscal_year'] for r in rows],list(range(2022,2027)) if t=='WMT' else list(range(2021,2026)))
            for r in rows:self.assertEqual({c['field'] for c in r['family_checklist']},{f.value for f in p.shared.h.Field})
        self.assertEqual(self.summary['family_slots'],210)
        self.assertEqual(sum(p['outcomes'].get('SOURCE_SUPPORTED',0) for p in self.packages.values()),25)
        self.assertEqual(sum(p['outcomes'].get('PROPOSED_PENDING_APPROVAL',0) for p in self.packages.values()),185)

    def test_literal_primary_statement_income_cash_and_selected_alternatives(self):
        expected={'V':{'revenue':[24105,29310,32653,35926,40000],'ebit':[15804,18813,21000,23595,23994],'cfo':[15227,18849,20755,19950,23059],'combined_da':[804,861,943,1034,1220],'productive_cash':[705,970,1059,1257,1482]},
                  'INTC':{'revenue':[79024,63054,54228,53101,52853],'ebit':[19456,2334,93,-11678,-2214],'cfo':[29991,15433,11471,8288,9697],'face_sbc':[2036,3128,3229,3410,2434],'cash_capex':[18733,24844,25750,23944,14646]},
                  'WMT':{'face_revenue':[572754,611289,648125,680985,713163],'net_sales':[567762,605881,642637,674538,706413],'membership_other':[4992,5408,5488,6447,6750],
                         'cfo':[24181,28841,35726,36443,41565],'face_da':[10658,10945,11853,12973,14203],'face_sbc_expense':[1163,1578,2093,2769,3603],'face_cash':[14760,8625,9867,9037,10727]}}
        for t,fields in expected.items():
            for k,values in fields.items():self.assertEqual([D(r['facts'][k]['value'])/1000000 for r in self.packages[t]['periods']],values,(t,k))

    def test_visa_curated_policy_replay_artifact_integrity_and_metadata_limits(self):
        store=p.capex_policy.artifacts()
        for r in self.packages['V']['periods']:
            for kind,proof in r['curated_policy_replays'].items():
                self.assertTrue(proof['existing_approval']);bindings=proof['policy']['artifact_bindings']
                self.assertEqual(len(bindings),13 if kind=='capex' else 9)
                for b in bindings:
                    url=b.get('url',b.get('source_url'));sha=b['sha256']
                    if (url,sha) in store:
                        body,ref=store[url,sha];self.assertEqual(hashlib.sha256(body).hexdigest(),sha)
                        self.assertEqual(ref['digest_type'],'sha256_sec_response_body_bytes')
                        # Null original retrieval fields are preserved, not supplied
                        # by this review or replaced with current availability.
                        if 'path' in b:self.assertEqual(b.get('http_status'),ref.get('http_status'))
                        else:self.assertEqual(url,next(s['url'] for s in r['sources'] if s['role']=='instance'))
                    else:self.assertEqual(sha,next(s['sha256'] for s in r['sources'] if s['role']=='instance'))
            self.assertEqual(r['facts']['productive_cash']['concept'],'PaymentsToAcquireProductiveAssets')
            self.assertEqual(r['cash_sign_multipliers']['productive_cash'],-1)

    def test_independent_cfo_hierarchy_movements_not_parent_child_sum(self):
        expected={'V':8,'INTC':6,'WMT':5}
        for t,package in self.packages.items():
            for r in package['periods']:
                rec=r['cfo_reconciliation'];self.assertEqual(rec['status'],'SUPPORTED');pop=rec['populations'][0]
                self.assertEqual(sum((D(x['value']) for x in pop['rows']),D(0)),D(pop['cfo']['value']))
                self.assertEqual(len(r['movement_rows']),expected[t])
                if t=='INTC':
                    h=pop['hierarchy_proof'];self.assertEqual(h['status'],'SUPPORTED')
                    self.assertEqual(sum((D(x['value']) for x in h['children']),D(0)),D(h['parent']['value']))
                    self.assertNotEqual(sum((D(x['value']) for x in pop['rows']+h['children']),D(0)),D(pop['cfo']['value']))
                self.assertFalse(any('residual' in c['input_id'] for c in r['calculations']))
        self.assertTrue(any(x['concept']=='IncreaseDecreaseInSettlementReceivable' for x in self.packages['V']['periods'][0]['movement_rows']))
        self.assertFalse(any(x['concept'].startswith('AmortizationOf') for x in self.packages['V']['periods'][0]['movement_rows']))

    def test_inactive_proxy_financing_and_walmart_revenue_identity(self):
        expected={'V':([804,861,943,1034,1220],[20977,22450,20463,20836,25171]),
                  'INTC':([11792,13035,9602,11379,11706],[38101,42051,49266,50011,46585]),
                  'WMT':([10658,10945,11853,12973,14203],[42831,44622,46891,45790,51523])}
        ledger=json.loads((ROOT/'docs/repaired-income-ledger.json').read_text())
        for t,package in self.packages.items():
            for r,da,fin in zip(package['periods'],*expected[t]):
                cs={c['input_id']:c for c in r['calculations']}
                self.assertEqual(D(cs['limited_da_proxy']['value'])/1000000,da);self.assertEqual(cs['limited_da_proxy']['origin'],'proxy')
                self.assertEqual(D(cs['named_financing']['value'])/1000000,fin)
                for c in cs.values():self.assertEqual(c['status'],p.PROPOSED);self.assertEqual(c['completeness'],'partial_named_population_only')
                if t=='WMT':
                    self.assertEqual(r['revenue_display_identity']['difference'],'0')
                    original=next(x for x in ledger['rows'] if x['identity']==r['identity'])
                    self.assertIn('CONFLICT',original['fields'][0]['status'])
                    self.assertNotIn('revenue',r['facts']);self.assertNotIn('sbc_addback',r['facts'])
                    self.assertNotIn('finance_current',cs['named_financing']['operands']);self.assertNotIn('finance_long',cs['named_financing']['operands'])

    def test_scope_precision_alternatives_shares_and_unknowns(self):
        for t,package in self.packages.items():
            for r in package['periods']:
                self.assertTrue(all(v is None for v in r['original_supporting_unknowns'].values()))
                self.assertFalse(r['analyst_complete']);self.assertFalse(r['new_assumptions_active'])
                self.assertTrue(any(k.startswith('shares:') for k in r['facts']))
                self.assertFalse(any('shares:' in k for c in r['calculations'] for k in c['operands']))
                if t=='INTC':
                    self.assertTrue(r['alternatives']['sbc']['competing_values'])
                    self.assertEqual(r['facts']['face_sbc']['precision'],'-6')
                if t=='V':
                    if r['fiscal_year']<=2023:self.assertTrue(r['facts']['client_cash_collateral'])
                    else:self.assertTrue(any(e['input_id']=='client_cash_collateral' and e['value'] is None for e in r['source_binding_exceptions']))
                    self.assertTrue(r['facts']['settlement_receivable'])
                    self.assertTrue(any(k.startswith('claim:PreferredStockValueOutstanding') for k in r['facts']))
                    self.assertTrue(all(k not in ('litigation_escrow','client_cash_collateral','settlement_receivable') for c in r['calculations'] if c['input_id']=='current_financial_captions' for k in c['operands']))

    def test_actual_instant_selector_rejects_duration_date_and_unit_mismatches(self):
        r=self.packages['WMT']['periods'][-1];fact=r['facts']['face_cash'];source=next(s for s in r['sources'] if s['role']=='instance');_,body=self._artifact(source)
        _,primary=self._artifact(next(s for s in r['sources'] if s['role']=='primary'))
        root=ET.fromstring(body);namespaces={v[0]:v[1] for event,v in ET.iterparse(BytesIO(body),events=['start-ns'])}
        xi=p.shared.cash._XI;contexts={n.get('id'):n for n in root.findall(xi+'context')};units={n.get('id'):n for n in root.findall(xi+'unit')}
        inline=p.shared.InlineFacts();inline.feed(primary.decode());o=fact['occurrences'][0];attrs,text=inline.facts[o['primary_locator'].removeprefix('inline#')]
        f=types.SimpleNamespace(root=root,contexts=contexts,units=units,namespaces=namespaces,period=p.shared.cash.Period(r['identity']['cik'],r['identity']['accession'],date.fromisoformat(r['identity']['annual_start']),date.fromisoformat(r['identity']['annual_end'])))
        item=dict(attrs=attrs,text=text);loc=fact['primary_table'];case={'filing':f}
        bound=p.peer.primary_fact(case,item,loc['table'],loc['row'],loc['column'],loc['caption'],instant=True);self.assertEqual(bound['value'],fact['value'])
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong duration')
        old=f.period;f.period=p.shared.cash.Period(old.cik,old.accession,old.annual_start,date(2026,1,30))
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong instant',instant=True)
        f.period=old;units[attrs['unitref']]=ET.fromstring('<unit xmlns="http://www.xbrl.org/2003/instance"><measure>xbrli:shares</measure></unit>')
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong unit',instant=True)

    def test_exact_replay_revisions_28_decisions_and_preservation(self):
        for path,payload in self.outputs.items():
            self.assertTrue(json.loads(json.dumps(payload))==payload,'Round trip differs '+path)
            self.assertTrue((ROOT/path).read_text()==json.dumps(payload,sort_keys=True,indent=2)+'\n','Exact replay differs '+path)
        ds=self.summary['decisions'];self.assertEqual(len(ds),28);ids={d['decision_id'] for d in ds};self.assertEqual(len(ids),28)
        for d in ds:self.assertFalse(d['accepted']);self.assertEqual(d['status'],p.PROPOSED)
        for package in self.packages.values():
            parent=deepcopy(package);revision=parent.pop('review_revision');self.assertEqual(revision,p.digest(p.relevant(parent)))
            changed=deepcopy(parent);changed['periods'][0]['facts']['cfo']['value']='1';self.assertNotEqual(revision,p.digest(p.relevant(changed)))
            for r in package['periods']:
                for c in r['family_checklist']:self.assertTrue(set(c['pending_decisions'])<=ids)
        protected=['src','docs/evidence','docs/universe','tests/fixtures','docs/repaired-income-ledger.json']
        for t in ('msft','aapl','googl','cost','cat','ko','nvda','amzn','meta','avgo','tsla','lly','mu','amd','jnj'):protected.append(f'docs/company-data-preparation/{t}-analyst-input-package.json')
        self.assertEqual(subprocess.check_output(['git','diff',p.BASELINE,'--',*protected],cwd=ROOT),b'')
        self.assertEqual(self.summary['evidence_acquisition_requirements'],[])
        self.assertEqual(self.summary['completed_company_packages']+self.summary['approved_partial_company_packages']+self.summary['pending_review_company_packages']+self.summary['broad_assessment_only'],42)


if __name__=='__main__':unittest.main()
