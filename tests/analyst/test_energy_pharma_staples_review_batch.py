"""Retained source fixtures, scope exceptions, inactive review and preservation."""
from copy import deepcopy
from datetime import date
from decimal import Decimal as D
from io import BytesIO
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import types
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare_energy_pharma_staples_review_batch as p
from prepare_msft_analyst_package import InlineFacts
import tests.analyst.test_standard_review_batch as sources


class EnergyPharmaStaplesReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=p.outputs()
        cls.packages={t:cls.outputs[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'] for t in p.TICKERS}
        cls.artifact_files={}
    _artifact=sources.StandardReviewBatchTests._artifact

    def test_fifteen_exact_identities_and210_unique_family_slots(self):
        manifest=json.loads((ROOT/p.shared.MANIFEST).read_text())
        ids=[]
        for t,pack in self.packages.items():
            expected=sorted([r['identity'] for r in manifest['rows'] if r['identity']['cik']==pack['periods'][0]['identity']['cik']],key=lambda x:x['annual_end'])
            self.assertEqual([r['identity'] for r in pack['periods']],expected)
            self.assertEqual([r['fiscal_year'] for r in pack['periods']],list(range(2022,2027)) if t=='PG' else list(range(2021,2026)))
            for r in pack['periods']:
                ids.append(r['identity']['accession'])
                self.assertEqual(len(r['family_checklist']),14)
                self.assertEqual({x['field'] for x in r['family_checklist']},{x.value for x in p.shared.h.Field})
                self.assertFalse(any(x['financial_complete'] for x in r['family_checklist']))
        self.assertEqual(len(set(ids)),15)
        self.assertEqual(self.outputs[p.SUMMARY]['family_slots'],210)
        self.assertEqual(self.packages['CVX']['outcomes'],dict(PROPOSED_PENDING_APPROVAL=65,ESSENTIAL_EXCEPTION=5))
        for t in ('MRK','PG'):self.assertEqual(self.packages[t]['outcomes'],dict(SOURCE_SUPPORTED=10,PROPOSED_PENDING_APPROVAL=60))

    def test_all_fact_occurrences_primary_receipts_and_prose(self):
        count=0
        for pack in self.packages.values():
            for r in pack['periods']:
                sources={s['role']:s for s in r['sources']}
                _,html=self._artifact(sources['primary']);_,xml=self._artifact(sources['instance'])
                for key,raw in [('primary',html),('instance',xml)]:
                    s=sources[key];self.assertEqual(hashlib.sha256(raw).hexdigest(),s['sha256'])
                    self.assertEqual(len(raw),s['byte_length']);self.assertEqual(s['http_status'],200)
                    self.assertEqual(s['digest_type'],'sha256_sec_response_body_bytes');self.assertTrue(s['retrieved_at_utc'])
                inline=InlineFacts();inline.feed(html.decode());root=ET.fromstring(xml)
                text=re.sub(r'\s+',' ',' '.join(inline.text));tables=None
                for excerpt in r['passages']:self.assertIn(excerpt['exact_excerpt'],text)
                facts=list(r['facts'].values())
                if r['independent_displayed_cfo']:
                    proof=r['independent_displayed_cfo'];facts += [x['fact'] for x in proof['rows']]+[proof['cfo']['fact']]
                for fact in facts:
                    if fact.get('representation')=='primary_note_prose_not_XBRL':
                        note=fact['note_evidence'];self.assertIn(note['exact_excerpt'],text)
                        self.assertEqual(note['source_sha256'],sources['primary']['sha256'])
                        self.assertEqual(D(note['raw_display'])*D(10)**note['display_scale'],D(fact['value']))
                        self.assertEqual(fact['precision'],'-6');continue
                    for o in fact['occurrences']:
                        node=root[o['ordinal']]
                        self.assertEqual(node.tag,'{'+fact['namespace']+'}'+fact['concept'])
                        self.assertEqual(node.text,o['raw_value']);self.assertEqual(D(node.text),D(fact['value']))
                        self.assertEqual(node.get('contextRef'),o['context_id']);self.assertEqual(node.get('unitRef'),o['unit_id']);self.assertEqual(node.get('decimals'),o['precision'])
                        loc=o['primary_locator']
                        if loc.startswith('inline#'):attrs,display=inline.facts[loc.split('#',1)[1]]
                        elif loc.startswith('unaddressed-inline#'):attrs,display=inline.unaddressed_facts[int(loc.split('#')[1])]
                        else:
                            if tables is None:tables=p.shared.documents.parse(dict(url=sources['primary']['url'],sha256=sources['primary']['sha256'],body=html),improved=True)
                            pos=fact['primary_table'];cell=tables[pos['table']][pos['row']][pos['column']]
                            match=[x for x in cell['facts'] if x['attrs']['contextref']==o['context_id'] and x['attrs']['name'].split(':')[-1]==fact['concept']]
                            self.assertEqual(len(match),1);attrs,display=match[0]['attrs'],match[0]['text']
                        self.assertEqual(attrs['contextref'],o['context_id']);self.assertEqual(attrs['unitref'],o['unit_id']);self.assertEqual(attrs['decimals'],o['precision'])
                        value=p.shared.cfo.displayed(display,D(0)) if attrs.get('format') in ('ixt:fixed-zero','ixt:zerodash') else p.shared.inline_amount(attrs,display)
                        self.assertEqual(value,D(node.text));count+=1
        self.assertGreater(count,800)

    def test_literal_independently_inspected_values_and_proposed_arithmetic(self):
        expected={
          'CVX':{'face_revenue':[155606,235717,196913,193414,184432],'selected_cfo':[29187,49602,35609,31492,33939],'da':[17925,16319,17326,17282,20132],'named_sbc_expense':[701,1013,-100,510,399],'asset_retirement':[12808,12701,13833,12667,14988]},
          'MRK':{'revenue':[48704,59283,60115,64168,65011],'selected_cfo':[13122,19095,13006,21468,16472],'depreciation_cfo':[1578,1824,1828,2104,3045],'amortization_cfo':[1636,2085,2044,2395,2793],'continuing_sbc_expense':[479,541,645,761,820]},
          'PG':{'revenue':[80187,82006,84039,84284,87032],'ebit':[17813,18134,18545,20451,19748],'selected_cfo':[16723,16848,19846,17817,19556],'da':[2807,2714,2896,2847,3160],'cash_capex':[3156,3062,3322,3773,4409],'named_sbc_expense':[528,545,562,476,524],'face_cash':[7214,8246,9482,9556,9942]}}
        for t,fields in expected.items():
            for k,values in fields.items():self.assertEqual([D(r['facts'][k]['value'])/1000000 for r in self.packages[t]['periods']],list(map(D,values)),(t,k))
        totals={'CVX':([5675,17901,8223,6781,6293],[31369,23339,20836,24541,40758]),'MRK':([8096,13192,7093,13689,14565],[33102,30691,35055,37111,49339]),'PG':([7214,8246,9482,9556,9942],[31493,34607,32460,34508,34138])}
        for t,(cash,fin) in totals.items():
            for key,values in [('current_financial_captions',cash),('named_financing',fin)]:self.assertEqual([D(next(x['value'] for x in r['calculations'] if x['input_id']==key))/1000000 for r in self.packages[t]['periods']],list(map(D,values)))
            for r in self.packages[t]['periods']:
                for calc in r['calculations']:
                    self.assertEqual(calc['status'],p.PROPOSED);self.assertEqual(calc['completeness'],'partial_named_population_only')
                    self.assertEqual(sum((D(r['facts'][o]['value'])*co for o,co in zip(calc['operands'],calc['coefficients'])),D(0)),D(calc['value']))
                    self.assertNotIn('residual',calc['input_id'])

    def test_cvx_essential_perimeter_and_unchanged_capex_approval(self):
        ledger=json.loads((ROOT/'docs/refreshed-capex-ledger.json').read_text())
        for r,amount in zip(self.packages['CVX']['periods'],[7515,10349,14788,15544,16830]):
            self.assertIsNone(r['proposed_selections']['ebit']);self.assertNotIn('ebit',r['facts']);self.assertIsNone(r['derived_ebit'])
            self.assertEqual(next(c for c in r['family_checklist'] if c['field']=='ebit')['status'],'ESSENTIAL_EXCEPTION')
            self.assertIsNone(r['original_supporting_unknowns']['industrial_ebit'])
            result=r['existing_capex_policy_replay'];self.assertEqual(D(result['value'])/1000000,amount);self.assertEqual(result['gaps'],[])
            self.assertEqual(result['policy'],p.prior.ledger_row(ledger,r['identity'])[1]['policy'])
            calc=next(x for x in r['calculations'] if x['input_id']=='named_financing')
            self.assertEqual(calc['operands'],['short_borrowing','debt_finance_long'])
            self.assertNotIn('cp',calc['operands']);self.assertNotIn('finance_lease',calc['operands'])

    def test_mrk_scope_manual_cfo_original_partials_and_registered_ebit(self):
        rows=self.packages['MRK']['periods']
        self.assertEqual([r['cfo_reconciliation']['status'] for r in rows],['PARTIAL']*5)
        self.assertEqual([len(r['independent_displayed_cfo']['rows']) for r in rows],[18,17,18,16,16])
        self.assertEqual([D(r['derived_ebit']['value'])/1000000 for r in rows],[12538,17945,2355,19912,21218])
        for r in rows:
            proof=r['independent_displayed_cfo'];self.assertEqual(proof['status'],'SUPPORTED');self.assertEqual(proof['difference'],'0');self.assertEqual(proof['tolerance'],'0')
            self.assertEqual(sum((D(x['value']) for x in proof['rows']),D(0)),D(proof['cfo']['value']))
            self.assertEqual(len(r['movement_rows']),7)
            other=next(x for x in r['movement_rows'] if x['caption']=='Other');self.assertEqual(other['fact']['concept'],'IncreaseDecreaseInOtherOperatingCapitalNet')
            self.assertEqual(r['facts']['sbc_addback']['role'],'cfo_reconciliation_observation');self.assertEqual(r['facts']['continuing_sbc_expense']['role'],'recognized_expense_observation')
            self.assertTrue(r['derived_ebit']['policy_proof']['operands'])
        self.assertEqual(rows[0]['facts']['discontinued_cfo']['value'],'987000000')
        self.assertEqual(rows[0]['facts']['sbc_expense']['value'],'498000000')
        self.assertEqual([D(next(x['value'] for x in r['calculations'] if x['input_id']=='limited_da_proxy'))/1000000 for r in rows],[3214,3909,3872,4499,5838])
        for r in rows[:2]:self.assertNotIn('cash_capex',r['facts']);self.assertIsNone(r['original_supporting_unknowns']['pure_cash_ppe'])

    def test_pg_extensions_restrictions_preferred_and_nonoverlap(self):
        rows=self.packages['PG']['periods']
        for r,n in zip(rows[:2],[17995,18353]):
            fact=r['facts']['pretax_extension'];self.assertEqual(D(fact['value'])/1000000,n)
            self.assertIn('pg.com',fact['namespace']);self.assertEqual(fact['concept'],'IncomeLossFromContinuingOperationsBeforeIncomeTaxes')
            self.assertEqual(r['reported_tax_policy_replay']['fields']['pretax']['status'],'UNAVAILABLE')
            self.assertIsNone(r['reported_tax_policy_replay']['etr']['value'])
        for r,n in zip(rows,[843,819,798,777,756]):
            self.assertEqual(r['facts']['face_cash']['concept'],'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents')
            pref=[v for k,v in r['facts'].items() if k.startswith('claim:PreferredStockValue:')]
            self.assertEqual(len(pref),1);self.assertEqual(D(pref[0]['value'])/1000000,n)
            self.assertTrue(pref[0]['occurrences'][0]['dimensions'])
            self.assertTrue(any('ESOP debt' in x['exact_excerpt'] for x in r['passages']))
            calc=next(x for x in r['calculations'] if x['input_id']=='named_financing')
            self.assertEqual(calc['operands'],['face_current_borrowing','debt_long'])
            da=next(x for x in r['calculations'] if x['input_id']=='limited_da_proxy');self.assertEqual(da['operands'],['da'])
        self.assertEqual([len(r['movement_rows']) for r in rows],[4,4,4,3,3])
        self.assertEqual([(sum((D(r['facts'][k]['value']) for k in ('cp','debt_current','other_short_borrowing')),D(0))-D(r['facts']['face_current_borrowing']['value']))/1000000 for r in rows],[0,0,0,-1,1])
        fin=next(d for d in self.outputs[p.SUMMARY]['decisions'] if d['decision_id']=='PG-FIN')
        self.assertIn('no plug or inferred rounding explanation',fin['uncertainty_and_alternative'])

    def test_mrk_iprd_expense_and_distinct_deal_cash_are_source_bound(self):
        # Literal independently inspected statement amounts, not acquisition
        # allocations generated from the selected CFO/Capex package.
        expected={2021:{'Acquisition of Acceleron Pharma Inc., net of cash acquired':-11174,
                        'Acquisition of Pandion Therapeutics, Inc., net of cash acquired':-1554},
                  2023:{'Acquisition of Prometheus Biosciences, Inc., net of cash acquired':-10705,
                        'Acquisition of Imago BioSciences Inc., net of cash acquired':-1327},
                  2024:{'Acquisition of Eyebiotech Limited, net of cash acquired':-1344,
                        'Acquisition of MK-1045 from Curon Pharmaceutical':-700},
                  2025:{'Acquisition of Verona Pharma plc, net of cash acquired':-10042}}
        for r in self.packages['MRK']['periods']:
            if r['fiscal_year'] not in expected:continue
            source={s['role']:s for s in r['sources']};_,xml=self._artifact(source['instance'])
            root=ET.fromstring(xml);xi=p.shared.cash._XI
            contexts={n.get('id'):n for n in root.findall(xi+'context')}
            for caption,amount in expected[r['fiscal_year']].items():
                rows=[x for x in r['supporting_note_rows'] if x['table']==r['independent_displayed_cfo']['primary_table'] and x['caption']==caption]
                self.assertEqual(len(rows),1);observations=[]
                for cell in rows[0]['cells']:
                    for item in cell['facts']:
                        a=item['attrs'];ctx=contexts[a['contextref']]
                        if (ctx.findtext(xi+'period/'+xi+'startDate'),ctx.findtext(xi+'period/'+xi+'endDate'))!=(r['identity']['annual_start'],r['identity']['annual_end']):continue
                        raw=p.shared.inline_amount(a,item['text'])
                        self.assertTrue(any(n.get('contextRef')==a['contextref'] and n.tag.split('}')[-1]==a['name'].split(':')[-1] and n.get('unitRef')==a['unitref'] and n.get('decimals')==a['decimals'] and n.text and D(n.text)==raw for n in root))
                        observations.append(p.shared.cfo.displayed(cell['text'],D(0))*D(10)**int(a.get('scale','0')))
                self.assertEqual(observations,[D(amount)*1000000])
                self.assertEqual(rows[0]['source_sha256'],source['primary']['sha256'])

    def test_inactive_decisions_roundtrip_revision_and_offline_replay(self):
        summary=self.outputs[p.SUMMARY]
        self.assertEqual(len({x['decision_id'] for x in summary['decisions']}),30)
        self.assertEqual(sum(x['status']=='OPEN_ESSENTIAL_EXCEPTION' for x in summary['decisions']),1)
        self.assertFalse(any(x['accepted'] for x in summary['decisions']));self.assertFalse(summary['new_assumptions_active'])
        self.assertEqual(summary['evidence_acquisition_requirements'],[])
        self.assertEqual(sum(summary[k] for k in ('completed_company_packages','approved_partial_company_packages','pending_review_company_packages','broad_assessment_only')),42)
        for pack in self.packages.values():
            self.assertFalse(pack['analyst_complete']);self.assertNotIn('history_approval',pack);self.assertNotIn('current_history',pack)
            parent=deepcopy(pack);rev=parent.pop('review_revision');self.assertEqual(p.digest(p.relevant(parent)),rev)
            parent['periods'][0]['facts']['selected_cfo']['value']='1';self.assertNotEqual(p.digest(p.relevant(parent)),rev)
        for path,payload in self.outputs.items():
            self.assertEqual(json.loads(json.dumps(payload)),payload)
            self.assertTrue((ROOT/path).read_text()==json.dumps(payload,sort_keys=True,indent=2)+'\n','Exact replay differs '+path)

    def test_display_binding_rejects_wrong_dates_units_and_precision(self):
        r=self.packages['MRK']['periods'][0];fact=r['independent_displayed_cfo']['rows'][0]['fact']
        source={s['role']:s for s in r['sources']};_,xml=self._artifact(source['instance']);_,html=self._artifact(source['primary'])
        root=ET.fromstring(xml);ns={v[0]:v[1] for _,v in ET.iterparse(BytesIO(xml),events=['start-ns'])};xi=p.shared.cash._XI
        contexts={n.get('id'):n for n in root.findall(xi+'context')};units={n.get('id'):n for n in root.findall(xi+'unit')}
        tables=p.shared.documents.parse(dict(url=source['primary']['url'],sha256=source['primary']['sha256'],body=html),improved=True)
        pos=fact['primary_table'];cell=tables[pos['table']][pos['row']][pos['column']]
        item=next(x for x in cell['facts'] if x['attrs']['contextref']==fact['occurrences'][0]['context_id'])
        i=r['identity'];period=p.shared.cash.Period(i['cik'],i['accession'],date.fromisoformat(i['annual_start']),date.fromisoformat(i['annual_end']))
        f=types.SimpleNamespace(root=root,namespaces=ns,contexts=contexts,units=units,period=period);case={'filing':f}
        self.assertEqual(p.peer.primary_fact(case,item,0,0,0,'Net income')['value'],fact['value'])
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong instant',instant=True)
        changed=deepcopy(item);changed['attrs']['decimals']='0'
        with self.assertRaises(ValueError):p.peer.primary_fact(case,changed,0,0,0,'Wrong precision')
        f.period=p.shared.cash.Period(period.cik,period.accession,period.annual_start,date(2021,12,30))
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong date')
        f.period=period;units[item['attrs']['unitref']]=ET.fromstring('<unit xmlns="http://www.xbrl.org/2003/instance"><measure>xbrli:shares</measure></unit>')
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong unit')

    def test_prior24_packages_and_frozen_ledger_pilot_preservation(self):
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',p.BASELINE],cwd=ROOT,text=True).splitlines()
        packages=[x for x in paths if x.startswith('docs/company-data-preparation/') and x.endswith('-analyst-input-package.json')]
        self.assertEqual(len(packages),24)
        pins=packages+[x for x in paths if x.startswith(('src/valuation_platform/normalization/','docs/evidence/','tests/fixtures/','docs/universe/')) or x.endswith('-ledger.json') or 'pilot' in x and x.endswith('.json') or x in ('docs/operating-income-cvx-ge-perimeter.md','docs/capex-mrk-scope.md')]
        for path in pins:self.assertTrue((ROOT/path).read_bytes()==subprocess.check_output(['git','show',p.BASELINE+':'+path],cwd=ROOT),'Preservation '+path)


if __name__=='__main__':unittest.main()
