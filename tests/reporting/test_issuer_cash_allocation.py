"""Apple/Meta extension, tested against retained XBRL and primary statements."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
import gzip
import hashlib
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare_issuer_cash_allocation as cash
X='{http://www.xbrl.org/2003/instance}'
D='{http://xbrl.org/2006/xbrldi}'

class IssuerCashAllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages={t:cash.prepare(t) for t in ['AAPL','META']}

    def test_offline_reproduction_matches_committed_packages(self):
        for t,p in self.packages.items():
            self.assertEqual(p,json.loads((ROOT/f'frontend/public/cash-allocation/{t}.json').read_text()))
            self.assertEqual(p,cash.prepare(t))
        self.assertEqual([len(self.packages['AAPL'][k]) for k in ['annual','quarterly','ttm']],[6,24,21])
        self.assertEqual([len(self.packages['META'][k]) for k in ['annual','quarterly','ttm']],[5,23,20])

    def test_all_cash_components_tie_and_apple_fiscal_calendar_is_preserved(self):
        for t,p in self.packages.items():
            for mode in ['annual','quarterly','ttm']:
                for r in p[mode]:cash.reconcile(r)
            for a in p['annual']:
                quarters=[q for q in p['quarterly'] if q['id'].startswith(a['id']+'-')]
                self.assertEqual(len(quarters),4)
                for k in cash.mapping(t):self.assertEqual(sum(cash.amount(q,k) for q in quarters),cash.amount(a,k))
        first=self.packages['AAPL']['quarterly'][0]
        self.assertEqual((first['id'],first['start'],first['end']),('FY2021-Q1','2020-09-27','2020-12-26'))
        self.assertEqual(self.packages['AAPL']['annual'][2]['end'],'2023-09-30')
        self.assertEqual(self.packages['META']['annual'][-1]['values']['financeLeasePayments'],-2524000000)
        self.assertEqual(self.packages['META']['annual'][-1]['values']['heldForSalePurchases'],-2432000000)
        self.assertEqual(self.packages['META']['annual'][-1]['values']['ventureDistributions'],2554000000)

    def test_note_only_meta_investment_is_not_double_counted(self):
        p=self.packages['META'];row=next(r for r in p['reported_periods'].values() if r['id'].startswith('0001326801-21-000049:'))
        self.assertIsNone(row['values']['otherPurchases']);self.assertIsNone(row['evidence']['otherPurchases'])
        self.assertEqual(row['excluded_note_facts']['otherPurchases']['fact']['reported_value'],20000000)
        statement=p['statement_evidence']['0001326801-21-000049']
        self.assertFalse(any(c.endswith(':PaymentsForEquitySecuritiesWithoutReadilyDeterminableFairValue') for c in statement['concepts']))
        self.assertEqual(row['values']['otherInvesting'],-62000000)
        self.assertEqual(row['values']['investing'],-13069000000)

    def test_ppe_categories_exact_balances_and_no_invented_alphabet_split(self):
        for t,p in self.packages.items():
            for b in p['ppe']:
                v=b['values'];self.assertEqual(sum(v[c['id']] for c in p['ppe_categories']),v['gross']);self.assertEqual(v['gross']-v['depreciation'],v['net']);self.assertIsNone(b['servers_network_share_approx'])
        self.assertEqual(self.packages['AAPL']['ppe'][1]['values']['net'],52084000000)
        self.assertEqual(self.packages['AAPL']['ppe'][1]['date'],'2026-09-26')
        self.assertNotIn('pending',self.packages['AAPL']['ppe'][1]['values'])
        self.assertEqual(self.packages['META']['ppe'][1]['values']['net'],176400000000)
        self.assertEqual(self.packages['META']['ppe'][1]['values']['financeLeases'],8187000000)

    def test_independent_raw_source_replay_and_statement_role_checks(self):
        checked=0
        for t,p in self.packages.items():
            source=cash.Sources(t,ROOT,False);instances={}
            for row in p['reported_periods'].values():
                acc=row['id'].split(':')[0]
                if acc not in instances:
                    url=p['sources'][acc]['source_url'];raw=source.read(url)
                    self.assertEqual(hashlib.sha256(raw).hexdigest(),p['sources'][acc]['sha256'])
                    xml=ET.fromstring(raw);contexts={c.attrib['id']:c for c in xml.findall(X+'context')};instances[acc]=(xml,contexts)
                xml,contexts=instances[acc]
                for key,e in row['evidence'].items():
                    if e is None:continue
                    hits=[f for f in xml if f.tag==e['concept'] and f.attrib.get('contextRef') in e['context_ids']]
                    self.assertTrue(hits)
                    for f in hits:
                        c=contexts[f.attrib['contextRef']]
                        self.assertEqual(int(c.findtext(X+'entity/'+X+'identifier')),cash.CIKS[t]);self.assertEqual(int(f.text),e['reported_value']);self.assertEqual(e['reported_value']*e['sign'],e['value']);self.assertIsNone(c.find('.//'+D+'explicitMember'));self.assertIsNone(c.find('.//'+D+'typedMember'))
                        if e['instant']:self.assertEqual(c.findtext(X+'period/'+X+'instant'),e['instant'])
                        else:self.assertEqual((c.findtext(X+'period/'+X+'startDate'),c.findtext(X+'period/'+X+'endDate')),(row['start'],row['end']))
                    if key not in ['opening','closing']:
                        self.assertTrue(any(c.split(':')[-1]==e['concept'].split('}')[-1] for c in p['statement_evidence'][acc]['concepts']))
                    checked+=1
            for b in p['ppe']:
                for e in b['evidence'].values():
                    xml,contexts=instances[p['annual'][-1]['operand_ids'][0].split(':')[0]]
                    hits=[f for f in xml if f.tag==e['concept'] and f.attrib.get('contextRef') in e['context_ids']]
                    self.assertTrue(hits);self.assertTrue(all(int(f.text)==e['reported_value'] for f in hits));self.assertTrue(all(contexts[f.attrib['contextRef']].findtext(X+'period/'+X+'instant')==b['date'] for f in hits));checked+=1
        self.assertEqual(checked,897)

    def test_parser_rejects_ambiguous_cash_statement_role(self):
        parser=cash.CashStatementTables();parser.feed('<table><tr><td>not a statement</td></tr></table>')
        with self.assertRaises(ValueError):parser.selected()

if __name__=='__main__':unittest.main()
