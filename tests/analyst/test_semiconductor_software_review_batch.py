"""Independent retained facts, inactive decisions and prior-byte preservation."""
from copy import deepcopy
from datetime import date
from decimal import Decimal as D
from io import BytesIO
from pathlib import Path
import hashlib,json,re,subprocess,sys,types,unittest
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import prepare_semiconductor_software_review_batch as p
from prepare_msft_analyst_package import InlineFacts
import tests.analyst.test_standard_review_batch as sources


class SemiconductorSoftwareReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=p.outputs();cls.packages={t:cls.outputs[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'] for t in p.TICKERS};cls.artifact_files={}
    _artifact=sources.StandardReviewBatchTests._artifact

    def test_fifteen_exact_selections_and210_families(self):
        manifest=json.loads((ROOT/p.shared.MANIFEST).read_text());ids=[]
        for t,pack in self.packages.items():
            expected=sorted([r['identity'] for r in manifest['rows'] if r['identity']['cik']==pack['periods'][0]['identity']['cik']],key=lambda x:x['annual_end'])
            self.assertEqual([r['identity'] for r in pack['periods']],expected)
            self.assertEqual([r['fiscal_year'] for r in pack['periods']],list(range(2022,2027)) if t=='LRCX' else list(range(2021,2026)))
            for r in pack['periods']:
                ids.append(r['identity']['accession']);self.assertEqual({c['field'] for c in r['family_checklist']},{f.value for f in p.shared.h.Field})
                self.assertEqual(len(r['family_checklist']),14);self.assertFalse(any(c['financial_complete'] for c in r['family_checklist']))
                self.assertEqual(sum(c['status']=='SOURCE_SUPPORTED' for c in r['family_checklist']),2)
                self.assertFalse(any(c['status']=='ESSENTIAL_EXCEPTION' for c in r['family_checklist']))
        self.assertEqual(len(set(ids)),15);self.assertEqual(self.outputs[p.SUMMARY]['family_slots'],210)

    def test_all_actual_occurrences_primary_receipts_and_prose(self):
        count=0;unaddressed=0;structural=0
        for pack in self.packages.values():
            for r in pack['periods']:
                source={s['role']:s for s in r['sources']};_,html=self._artifact(source['primary']);_,xml=self._artifact(source['instance'])
                for s,body in [(source['primary'],html),(source['instance'],xml)]:
                    self.assertEqual(hashlib.sha256(body).hexdigest(),s['sha256']);self.assertEqual(len(body),s['byte_length']);self.assertEqual(s['http_status'],200)
                    self.assertEqual(s['digest_type'],'sha256_sec_response_body_bytes');self.assertTrue(s['retrieved_at_utc'])
                inline=InlineFacts();inline.feed(html.decode());root=ET.fromstring(xml);text=re.sub(r'\s+',' ',' '.join(inline.text))
                tables=None
                facts=list(r['facts'].values())
                if r['independent_displayed_cfo']:facts += [x['fact'] for x in r['independent_displayed_cfo']['rows']]+[r['independent_displayed_cfo']['cfo']['fact']]
                for excerpt in r['passages']:self.assertTrue(excerpt['exact_excerpt'] in text,f"Exact primary excerpt absent {pack['ticker']} {r['fiscal_year']} {excerpt['marker']}")
                for fact in facts:
                    if fact.get('representation')=='primary_note_prose_not_XBRL':
                        note=fact['note_evidence'];self.assertTrue(note['exact_excerpt'] in text,'Exact prose confirmation absent');self.assertEqual(note['source_sha256'],source['primary']['sha256'])
                        if 'raw_display' in note:self.assertEqual(D(note['raw_display'])*D(10)**note['display_scale'],D(fact['value']));self.assertEqual(fact['precision'],'-5')
                        else:self.assertEqual(fact['precision'],'verbal_explicit_none')
                        continue
                    for o in fact['occurrences']:
                        n=root[o['ordinal']];self.assertEqual(n.text,o['raw_value']);self.assertEqual(n.get('contextRef'),o['context_id']);self.assertEqual(n.get('unitRef'),o['unit_id']);self.assertEqual(n.get('decimals'),o['precision']);self.assertEqual(n.tag,'{'+fact['namespace']+'}'+fact['concept']);self.assertEqual(D(n.text),D(fact['value']))
                        loc=o['primary_locator']
                        if loc.startswith('inline#'):a,display=inline.facts[loc.removeprefix('inline#')]
                        elif loc.startswith('unaddressed-inline#'):
                            a,display=inline.unaddressed_facts[int(loc.split('#')[1])];self.assertNotIn('id',a);unaddressed+=1
                        else:
                            if tables is None:tables=p.shared.documents.parse(dict(url=source['primary']['url'],sha256=source['primary']['sha256'],body=html),improved=True)
                            pos=fact['primary_table'];cell=tables[pos['table']][pos['row']][pos['column']]
                            matches=[x for x in cell['facts'] if x['attrs'].get('contextref')==o['context_id'] and x['attrs']['name'].split(':')[-1]==fact['concept']]
                            self.assertEqual(len(matches),1);a,display=matches[0]['attrs'],matches[0]['text'];self.assertNotIn('id',a);structural+=1
                        self.assertEqual(a['contextref'],o['context_id']);self.assertEqual(a['unitref'],o['unit_id']);self.assertEqual(a['decimals'],o['precision'])
                        self.assertEqual(p.shared.cfo.displayed(display,D(0)) if a.get('format') in ('ixt:fixed-zero','ixt:zerodash') else p.shared.inline_amount(a,display),D(n.text))
                        count+=1
        self.assertGreater(count,600);self.assertGreater(unaddressed,0);self.assertGreater(structural,0)

    def test_independently_inspected_literal_schedules(self):
        expected={'LRCX':{'combined_da':['333.739','342.432','359.699','386.277','441.533'],'productive_cash':['546.034','501.568','396.670','759.186','966.405'],'cfo':['3099.674','5178.938','4652.269','6173.264','5857.657'],'sbc_note_expense':['259.064','286.600','293.058','343.371','386.381']},
          'PLTR':{'da':['14.897','22.522','33.354','31.587','26.145'],'cfo':['333.851','223.737','712.183','1153.865','2134.473'],'face_tax':['31.885','10.067','19.716','21.255','22.724'],'sbc_expense':['778.215','564.798','475.903','691.638','684.033']},
          'AMAT':{'depreciation':[345,404,471,346,389],'cash_capex':[668,787,1106,1190,2260],'cfo':[5442,5399,8700,8677,7958],'sbc_expense':[346,413,490,577,660]}}
        for t,fields in expected.items():
            for k,values in fields.items():self.assertEqual([D(r['facts'][k]['value'])/1000000 for r in self.packages[t]['periods']],[D(x) for x in values],(t,k))
        calcs={'LRCX':(['3657.732','5374.697','5847.856','6390.659','5579.171'],['5005.830','5011.541','4983.334','4484.505','3734.563']),
          'PLTR':(['2524.827','2633.675','3674.179','5229.987','7177.043'],[0]*5),'AMAT':([5459,2581,6869,9471,8573],[5452,5457,5663,6259,6555])}
        for t,(cash,fin) in calcs.items():
            for key,values in [('current_financial_captions',cash),('named_financing',fin)]:self.assertEqual([D(next(c['value'] for c in r['calculations'] if c['input_id']==key))/1000000 for r in self.packages[t]['periods']],[D(x) for x in values],(t,key))

    def test_proxy_negative_scope_and_overlap_preserved(self):
        lrcx=self.packages['LRCX']
        for r in lrcx['periods']:
            self.assertNotIn('cash_capex',r['facts']);self.assertIsNone(r['original_supporting_unknowns']['pure_cash_ppe'])
            fin=next(c for c in r['calculations'] if c['input_id']=='named_financing');self.assertEqual(fin['operands'],['debt_finance_current','debt_finance_long']);self.assertNotIn('finance_lease',fin['operands'])
        self.assertEqual([D(r['facts']['deferred_plan_obligation']['value'])/1000000 for r in lrcx['periods']],[D(v) for v in ('280.0','318.0','385.5','423.9','498.5')])
        self.assertEqual([D(r['facts']['deferred_plan_investments']['value'])/1000000 for r in lrcx['periods']],[D(v) for v in ('291.3','318.1','393.5','438.8','511.8')])
        self.assertEqual([D(r['facts']['inventory_transfers']['value'])/1000000 for r in lrcx['periods']],[D(v) for v in ('75.068','76.856','71.267','90.873','125.691')])
        for r in self.packages['AMAT']['periods']:
            cs={c['input_id']:c for c in r['calculations']};self.assertNotIn('finance_amortization',cs['limited_da_proxy']['operands'])
            if r['fiscal_year']==2024:self.assertEqual(cs['named_financing']['operands'],['debt_long','face_short_debt'])
        r=self.packages['AMAT']['periods'][-1];self.assertEqual(r['facts']['sbc_addback']['value'],'668000000');self.assertEqual(r['facts']['sbc_expense']['value'],'660000000')
        self.assertTrue(any('781' in x['exact_excerpt'] and '548' in x['exact_excerpt'] for x in r['passages']))
        for t,pack in self.packages.items():
            for r in pack['periods']:
                for c in r['calculations']:
                    self.assertEqual(c['status'],p.PROPOSED);self.assertEqual(c['completeness'],'partial_named_population_only');self.assertEqual(sum((D(r['facts'][o]['value'])*co for o,co in zip(c['operands'],c['coefficients'])),D(0)),D(c['value']))
                    self.assertNotIn('residual',c['input_id'])
                self.assertEqual(r['cash_sign_multipliers']['productive_cash' if t=='LRCX' else 'cash_capex'],-1)

    def test_cfo_proofs_original_partial_tax_conflicts_and_movement_roles(self):
        self.assertEqual([r['cfo_reconciliation']['status'] for r in self.packages['PLTR']['periods']],['PARTIAL']*4+['SUPPORTED'])
        for t,pack in self.packages.items():
            for r in pack['periods']:
                manual=r['independent_displayed_cfo']
                if manual:self.assertEqual(manual['difference'],'0');self.assertEqual(sum((D(x['value']) for x in manual['rows']),D(0)),D(manual['cfo']['value']))
                else:
                    pop=r['cfo_reconciliation']['populations'][0];self.assertEqual(sum((D(x['value']) for x in pop['rows']),D(0)),D(pop['cfo']['value']))
                self.assertGreater(len(r['movement_rows']),0)
                self.assertEqual(r['facts']['sbc_addback']['role'],'cfo_reconciliation_observation')
                self.assertEqual(r['facts']['sbc_note_expense' if t=='LRCX' else 'sbc_expense']['role'],'recognized_expense_observation')
        for r in self.packages['PLTR']['periods'][1:]:
            self.assertEqual(r['reported_tax_policy_replay']['fields']['provision']['status'],'CONFLICTING');self.assertGreater(len(r['alternatives']['tax']['competing_values']),1)
        self.assertIn('under the 2014 Credit Facility',self.packages['PLTR']['periods'][-1]['facts']['facility_balance_explicit_none']['note_evidence']['exact_excerpt'])

    def test_share_dates_classes_and_split_not_aggregated(self):
        lrcx=self.packages['LRCX']['periods']
        self.assertEqual([r['facts']['shares:CommonStockSharesOutstanding:'+r['identity']['annual_end']+':4f53cda1']['value'] for r in lrcx],['136975000','133297000','130377000','1268740000','1251278000'])
        for r in self.packages['PLTR']['periods']:
            classes=[v for k,v in r['facts'].items() if k.startswith('shares:CommonStockSharesOutstanding')]
            self.assertGreaterEqual(len(classes),4);self.assertEqual({v['as_of'] for v in classes},{r['identity']['annual_end']})
            self.assertFalse(any('shares' in c['input_id'] for c in r['calculations']))
        self.assertTrue(any('49.999999' in x['exact_excerpt'] for x in self.packages['PLTR']['periods'][0]['passages']))

    def test_no_id_parser_actual_position_and_duplicate_rejection(self):
        parser=InlineFacts();parser.feed('<ix:nonfraction name="u:X">1</ix:nonfraction><ix:nonfraction id="x">2</ix:nonfraction>')
        self.assertEqual(len(parser.unaddressed_facts),1);self.assertEqual(set(parser.facts),{'x'});self.assertEqual(parser.unaddressed_facts[0][1],'1')
        with self.assertRaises(ValueError):parser.feed('<ix:nonfraction id="x">3</ix:nonfraction>')

    def test_bound_primary_rejects_dates_units_precision_and_conflicts(self):
        r=self.packages['PLTR']['periods'][0];manual=r['independent_displayed_cfo'];fact=manual['rows'][0]['fact'];_,xml=self._artifact(next(s for s in r['sources'] if s['role']=='instance'));_,html=self._artifact(next(s for s in r['sources'] if s['role']=='primary'))
        root=ET.fromstring(xml);ns={v[0]:v[1] for _,v in ET.iterparse(BytesIO(xml),events=['start-ns'])};xi=p.shared.cash._XI
        contexts={n.get('id'):n for n in root.findall(xi+'context')};units={n.get('id'):n for n in root.findall(xi+'unit')};tables=p.shared.documents.parse(dict(body=html,url=r['sources'][0]['url'],sha256=r['sources'][0]['sha256']),improved=True);pos=fact['primary_table'];item=tables[pos['table']][pos['row']][pos['column']]['facts'][0]
        i=r['identity'];period=p.shared.cash.Period(i['cik'],i['accession'],date.fromisoformat(i['annual_start']),date.fromisoformat(i['annual_end']));f=types.SimpleNamespace(root=root,contexts=contexts,units=units,namespaces=ns,period=period);case={'filing':f}
        self.assertEqual(p.peer.primary_fact(case,item,0,0,0,'Net loss')['value'],fact['value'])
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong instant',instant=True)
        changed=deepcopy(item);changed['attrs']['decimals']='0'
        with self.assertRaises(ValueError):p.peer.primary_fact(case,changed,0,0,0,'Wrong precision')
        f.period=p.shared.cash.Period(period.cik,period.accession,period.annual_start,date(2021,12,30))
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong date')
        f.period=period;units[item['attrs']['unitref']]=ET.fromstring('<unit xmlns="http://www.xbrl.org/2003/instance"><measure>xbrli:shares</measure></unit>')
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong unit')

    def test_inactive_revision_serialization_and_committed_replay(self):
        summary=self.outputs[p.SUMMARY];self.assertEqual(len({d['decision_id'] for d in summary['decisions']}),27)
        self.assertFalse(summary['new_assumptions_active']);self.assertEqual(summary['evidence_acquisition_requirements'],[])
        self.assertEqual(summary['completed_company_packages']+summary['approved_partial_company_packages']+summary['pending_review_company_packages']+summary['broad_assessment_only'],42)
        for d in summary['decisions']:self.assertFalse(d['accepted']);self.assertEqual(d['status'],p.PROPOSED)
        for t,v in self.packages.items():
            self.assertNotIn('history_approval',v);self.assertNotIn('current_history',v);self.assertFalse(v['analyst_complete'])
            parent=deepcopy(v);revision=parent.pop('review_revision');self.assertEqual(p.digest(p.relevant(parent)),revision)
            changed=deepcopy(parent);changed['periods'][0]['facts']['revenue']['value']='1';self.assertNotEqual(p.digest(p.relevant(changed)),revision)
        for path,payload in self.outputs.items():
            self.assertTrue(json.loads(json.dumps(payload))==payload,'Roundtrip '+path)
            self.assertTrue((ROOT/path).read_text()==json.dumps(payload,sort_keys=True,indent=2)+'\n','Bounded exact replay '+path)

    def test_all21_prior_packages_frozen_pilots_ledgers_and_negative_findings_unchanged(self):
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',p.BASELINE],cwd=ROOT,text=True).splitlines();prior_packages=[x for x in paths if x.startswith('docs/company-data-preparation/') and x.endswith('-analyst-input-package.json')]
        self.assertEqual(len(prior_packages),21)
        pins=prior_packages+[x for x in paths if x.startswith(('src/valuation_platform/normalization/','docs/evidence/','tests/fixtures/','docs/universe/')) or x.endswith('-ledger.json') or 'pilot' in x and x.endswith('.json') or x in ('docs/capex-lrcx-component-completeness.md',)]
        for path in pins:
            baseline=subprocess.check_output(['git','show',p.BASELINE+':'+path],cwd=ROOT)
            self.assertTrue((ROOT/path).read_bytes()==baseline,'Original artifact changed '+path)


if __name__=='__main__':unittest.main()
