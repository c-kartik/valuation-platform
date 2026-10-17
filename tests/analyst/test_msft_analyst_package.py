"""Independent retained MSFT statement points and draft-only package boundaries."""
import copy
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare_msft_analyst_package as package


class MSFTAnalystPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filings=[package.Filing(y) for y in (2025,2026)]
        for f in cls.filings:package.populate(f)
        cls.result=package.resolve_decisions(cls.filings,package.finish(cls.filings))

    def test_exact_package_replay_and_registered_identity(self):
        saved=json.loads((ROOT/package.OUTPUT).read_text())
        for key in ('fy2026_completeness_attempt','fy2026_operation_approval','fy2026_operations_view','fy2026_claim_assumption_approval','fy2026_claim_assumptions_view'):saved.pop(key)
        self.assertTrue(package.accepted_view(self.result)==saved,'Exact original accepted package replay differs')
        self.assertEqual([p['identity']['accession'] for p in self.result['periods']],
            ['0000950170-25-100235','0001193125-26-323660'])
        self.assertEqual([p['identity']['annual_start'] for p in self.result['periods']],['2024-07-01','2025-07-01'])
        self.assertEqual([p['identity']['annual_end'] for p in self.result['periods']],['2025-06-30','2026-06-30'])
        self.assertFalse(self.result['valuation_consumption_approved'])
        self.assertEqual(self.result['financial_sufficiency'],'NOT_ASSESSED')
        self.assertEqual(self.result['new_sec_requests'],0)

    def test_independently_inspected_income_tax_and_investment_points(self):
        # Face income statements, Notes 6/9/11 and cash-flow statements; USD m.
        expected=[dict(revenue=281724,ebit=128528,pretax=123627,expense_da=28000,
            **{'reported:PaymentsToAcquirePropertyPlantAndEquipment':-64551,
               'reported:IncomeTaxExpenseBenefit':21795,'reported:IncomeTaxesPaidNet':-28700}),
            dict(revenue=331839,ebit=155237,pretax=165934,expense_da=39000,
            **{'reported:PaymentsToAcquirePropertyPlantAndEquipment':-115948,
               'reported:IncomeTaxExpenseBenefit':32185,'reported:IncomeTaxesPaidNet':-21188})]
        for p,wanted in zip(self.result['periods'],expected):
            entries={e['input_id']:e for e in p['inputs']}
            self.assertEqual(Decimal(p['facts']['pretax']['value'])/1000000,wanted.pop('pretax'))
            for key,value in wanted.items():self.assertEqual(Decimal(entries[key]['value'])/1000000,value)
            self.assertEqual(entries['expense_da']['precision']['operand_decimals'],['-8','-8'])
            self.assertEqual(entries['reported_etr']['policy'],'annual_reported_effective_tax_rate_v1')
            self.assertEqual(Decimal(entries['reported_etr']['value']),Decimal('0.1762964400980368366133611589701279')
                if p['fiscal_year']==2025 else Decimal('0.1939626598527125242566321549531742'))

    def test_source_supported_partial_nwc_and_book_movement_not_cash(self):
        for p,nwc,ap,whole in zip(self.result['periods'],(-28245,-21353),(20824,15716),(-35145,-48053)):
            e={v['input_id']:v for v in p['inputs']}
            self.assertEqual(Decimal(e['partial_nwc']['value'])/1000000,nwc)
            self.assertEqual(Decimal(e['adjusted_ap']['value'])/1000000,ap)
            self.assertEqual(Decimal(e['whole_ap_comparator']['value'])/1000000,whole)
            self.assertEqual(e['partial_nwc']['completeness'],'partial')
            self.assertNotIn('component_receivables',e['partial_nwc']['operands'])
            self.assertEqual(len(e['partial_nwc']['operands']),len(set(e['partial_nwc']['operands'])))
        movement=self.result['adjacent_book_movement']
        self.assertEqual(Decimal(movement['value_usd'])/1000000,6892)
        self.assertEqual(Decimal(movement['capital_creditor_exclusion_effect_usd'])/1000000,19800)
        self.assertIn('Not cash delta NWC',movement['limitations'][0])

    def test_actual_parent_populations_and_not_inferred_cp_zero(self):
        expected=[(94565,43151,22861,46172),(76843,40294,21925,66594)]
        for p,values in zip(self.result['periods'],expected):
            e={v['input_id']:v for v in p['inputs']}
            for key,value in zip(('current_liquidity','term_debt','operating_liability','finance_liability'),values):
                self.assertEqual(Decimal(e[key]['value'])/1000000,value)
            self.assertEqual(len(p['checks']),7)
            self.assertTrue(all(c['result']=='PASS' and c['difference']=='0' for c in p['checks']))
        first,second=self.result['periods']
        self.assertEqual(first['facts']['commercial_paper']['value'],'0')
        self.assertEqual(first['facts']['commercial_paper']['precision_variants'],['-6','-9'])
        self.assertNotIn('commercial_paper',second['facts'])
        self.assertTrue(any(u['input_id']=='commercial_paper' and u['value'] is None for u in second['unresolved_requirements']))

    def test_shares_dates_award_class_and_non_overlap(self):
        for p,end_common,cover,obs,awards in zip(self.result['periods'],(7434000000,7427000000),
                (7433166379,7425545491),('2025-07-24','2026-07-23'),(82000000,78000000)):
            facts=p['facts'];entries={v['input_id']:v for v in p['inputs']}
            self.assertEqual(Decimal(facts['year_end_common']['value']),end_common)
            self.assertEqual(Decimal(facts['cover_common']['value']),cover)
            self.assertEqual(facts['cover_common']['as_of'],obs)
            self.assertEqual(facts['year_end_common']['precision'],'-6')
            self.assertEqual(facts['cover_common']['precision'],'0')
            self.assertEqual(Decimal(facts['nonvested_awards']['value']),awards)
            self.assertEqual(facts['nonvested_awards']['occurrences'][0]['dimensions'],
                [['us-gaap:AwardTypeAxis','us-gaap:RestrictedStockMember']])
            self.assertEqual(entries['year_end_common']['operands'],['year_end_common'])
            self.assertEqual(entries['cover_common']['operands'],['cover_common'])
            self.assertFalse(any('diluted' in e['input_id'] for e in p['inputs']))

    def test_cfo_signs_roles_and_recast_not_an_adjustment(self):
        for p,cfo,dep,expense,sbc in zip(self.result['periods'],(136162,182935),(34153,38534),(28000,39000),(11974,12405)):
            e={v['input_id']:v for v in p['inputs']}
            self.assertEqual(Decimal(e['reported:NetCashProvidedByUsedInOperatingActivities']['value'])/1000000,cfo)
            self.assertEqual(Decimal(e['reported:DepreciationAmortizationAndOther']['value'])/1000000,dep)
            self.assertEqual(Decimal(e['expense_da']['value'])/1000000,expense)
            self.assertEqual(Decimal(e['sbc_cost_proxy']['value'])/1000000,sbc)
            self.assertEqual(e['sbc_cost_proxy']['origin'],'proxy')
            self.assertEqual(e['sbc_cost_proxy']['status'],package.ACCEPTED)
            self.assertEqual(e['reported:ShareBasedCompensation']['role'],'reported_reconciliation_item')
            self.assertEqual(e['reported:AllocatedShareBasedCompensationExpense']['role'],'noncash_expense')
            self.assertEqual(len(p['cfo_reconciliation']['terms']),14)
            self.assertFalse(any('residual' in i for i in e))
            self.assertEqual(Decimal(e['nonoperating_income']['value'])/1000000,-4901 if p['fiscal_year']==2025 else 10697)
            self.assertTrue(all(e[t]['role'] in ('reported_reconciliation_item','accrued_income') for t in p['cfo_reconciliation']['terms']))
            self.assertTrue(all(e[t]['role']=='cash_payment' for t in ('reported:OperatingLeasePayments',
                'reported:FinanceLeaseInterestPaymentOnLiability','reported:FinanceLeasePrincipalPayments')))
        comparative=self.result['comparative_support']
        self.assertEqual([(c['raw_value'],c['ordinal']) for c in comparative],[('29433000000',692),('-5329000000',698)])
        self.assertTrue(all(c['start']=='2024-07-01' and c['end']=='2025-06-30' for c in comparative))
        self.assertEqual(Decimal(self.result['separately_identified_omitted_asset_growth']['value_usd'])/1000000,19600)

    def test_receipts_and_every_value_has_exact_primary_and_instance_binding(self):
        sources={s['source_id']:s for s in self.result['sources']}
        self.assertEqual(len(sources),4)
        for p,f in zip(self.result['periods'],self.filings):
            for value in p['facts'].values():
                self.assertTrue(value['occurrences'])
                for o in value['occurrences']:
                    raw=f.root[o['ordinal']]
                    self.assertEqual(raw.attrib['id'],o['xml_id'])
                    self.assertEqual(raw.attrib['contextRef'],o['context_id'])
                    self.assertEqual(raw.text,o['raw_value'])
                for kind in ('primary','instance'):
                    source=sources[value[kind+'_source']]
                    receipt=getattr(f,kind)
                    self.assertEqual(source['sha256'],hashlib.sha256(receipt.artifact.body).hexdigest())
                    self.assertEqual(source['http_status'],200)
                    self.assertTrue(source['retrieved_at_utc'])
                    self.assertEqual(source['digest_type'],'sha256_sec_response_body_bytes')
            self.assertEqual(len(p['unresolved_requirements']),len({u['input_id'] for u in p['unresolved_requirements']}))
            self.assertTrue(all(u['value'] is None for u in p['unresolved_requirements']))

    def test_wrong_dates_units_values_nil_and_precision_cannot_populate(self):
        original=self.filings[0]
        for change in ('value','precision','nil','unit','date'):
            f=copy.copy(original);f.facts={};f.entries=[]
            f.root=copy.deepcopy(original.root);f.contexts=copy.deepcopy(original.contexts)
            node=f.root[536]  # independently inspected FY2025 revenue face occurrence
            if change=='value':node.text='1'
            elif change=='precision':node.set('decimals','-9')
            elif change=='nil':node.set('{http://www.w3.org/2001/XMLSchema-instance}nil','true')
            elif change=='unit':node.set('unitRef','U_shares')
            elif change=='date':
                # Exclude every same-date candidate; do not manufacture another period.
                for context in f.contexts.values():
                    end=context.find(package.cash._XI+'period/'+package.cash._XI+'endDate')
                    if end is not None and end.text=='2025-06-30':end.text='2025-06-29'
            with self.subTest(change=change),self.assertRaises((ValueError,KeyError)):
                f.fact('bad','RevenueFromContractWithCustomerExcludingAssessedTax','Synthetic rejection only')

    def test_no_duplicate_selected_id_or_ineligible_etr_denominator(self):
        f=copy.copy(self.filings[0]);f.entries=copy.deepcopy(f.entries);f.facts=copy.deepcopy(f.facts)
        with self.assertRaises(ValueError):f.entry('revenue','duplicate',['revenue'],scope='test',rationale='test')
        for value in ('0','-1'):
            f.facts['pretax']['value']=value
            with self.assertRaises(ValueError):
                f.entry('bad-etr','synthetic',['IncomeTaxExpenseBenefit','pretax'],formula='DIVIDE',unit='pure',scope='test',rationale='test')
        self.assertEqual(package.inline_amount({'format':'ixt-sec:numwordsen'},'no'),0)
        with self.assertRaises((ValueError,InvalidOperation)):package.inline_amount({'format':'ixt:num-dot-decimal'},'no')

    def test_one_pending_sheet_and_no_accepted_new_numeric_assumptions(self):
        self.assertEqual(len(self.result['approval_sheet']),6)
        self.assertTrue(all(d['status']==package.PROPOSED for d in self.result['approval_sheet']))
        self.assertTrue(all(e['origin'] in ('reported','derived','proxy') for p in self.result['periods'] for e in p['inputs']))
        self.assertTrue(all('value' not in d for d in self.result['approval_sheet']))
        self.assertFalse(any(u['input_id']=='sbc_economic_treatment' for p in self.result['periods'] for u in p['unresolved_requirements']))
        self.assertTrue(all(any(u['input_id']=='sbc_economic_treatment' for u in p['original_bundle_unknowns']) for p in self.result['periods']))

    def test_revision_preserves_every_original_fact_selection_and_accepted_output(self):
        prior=json.loads(subprocess.check_output(['git','show',package.REVIEW_BASIS+':'+package.OUTPUT],cwd=ROOT))
        self.assertEqual(self.result['periods'],prior['periods'])
        self.assertEqual(self.result['sources'],prior['sources'])
        self.assertEqual(self.result['adjacent_book_movement'],prior['adjacent_book_movement'])
        self.assertEqual(self.result['previous_approval_sheet'],prior['approval_sheet'])
        self.assertEqual(self.result['schema'],'msft-draft-analyst-historical-package-v2')

    def test_concrete_operating_proxy_and_named_alternatives_have_literal_source_ties(self):
        rows=self.result['decision_resolution']['periods']
        for r,named,assets,current,long,proxy,fac,finance in zip(rows,(-25755,-18600),(24462,40101),
                (14785,16676),(2149,2697),(-23427,-3372),(-15227,24428),(-19127,328)):
            for key,v in [('named_expansion',named),('residual_assets',assets),('residual_current_liabilities',current),
                    ('residual_long_liabilities',long),('proposed_operating_capital',proxy),
                    ('alternative_include_facilitation',fac),('alternative_include_customer_finance',finance)]:
                self.assertEqual(Decimal(r['schedules'][key]['value_usd'])/1000000,v)
            self.assertEqual(r['schedules']['proposed_operating_capital']['origin'],'proxy')
            self.assertEqual(r['schedules']['proposed_operating_capital']['status'],package.PROPOSED)
            terms={v['operand'] for v in r['schedules']['residual_assets']['terms']}
            self.assertFalse(terms & {'restricted_current','restricted_long','long_ar'})
            self.assertEqual(r['additional_facts']['dta_in_other_assets']['location'].split(':')[0],'Note 11 Reported As')
        moves=self.result['decision_resolution']['adjacent_book_movements_usd']
        self.assertEqual({k:Decimal(v)/1000000 for k,v in moves.items()},dict(named_expansion=7155,
            proposed_operating_capital=20055,alternative_include_facilitation=39655,alternative_include_customer_finance=19455))
        self.assertEqual(Decimal(self.result['decision_resolution']['named_only_vs_proxy_movement_difference_usd'])/1000000,12900)

    def test_debt_reconciliation_and_finance_assets_not_duplicate_cash_or_expense(self):
        for r,carrying,funded,net,alternative in zip(self.result['decision_resolution']['periods'],
                (43151,40294),(89323,106888),(160951,245795),(31408,44403)):
            s=r['schedules']
            for key,value in [('face_to_carrying',carrying),('term_and_finance_leases',funded),
                    ('nonfinance_ppe_net',net),('conditional_da_if_rou_excluded',alternative)]:
                self.assertEqual(Decimal(s[key]['value_usd'])/1000000,value)
            self.assertEqual(s['term_and_finance_leases']['status'],package.PROPOSED)
            self.assertEqual([t['operand'] for t in s['term_and_finance_leases']['terms']],['term_debt_parent','finance_liability'])
            self.assertIn('not selected D&A',s['conditional_da_if_rou_excluded']['meaning'])
            self.assertTrue(all(c['result']=='PASS' for c in r['source_checks']))

    def test_restricted_cash_and_short_debt_estimates_never_become_reported_zeros(self):
        first,second=self.result['decision_resolution']['periods']
        self.assertNotIn('restricted_current',first['additional_facts'])
        self.assertEqual(Decimal(second['additional_facts']['restricted_current']['value'])/1000000,3800)
        self.assertEqual(Decimal(second['additional_facts']['restricted_long']['value'])/1000000,7500)
        self.assertEqual(Decimal(second['schedules']['known_restriction_current_pool']['value_usd'])/1000000,73043)
        estimate=next(a for a in second['assumptions'] if a['assumption_id']=='UNREPORTED-SHORT-DEBT')
        self.assertEqual(estimate['value_usd'],'0')
        self.assertIsNone(estimate['source_value_usd'])
        self.assertEqual(estimate['status'],package.PROPOSED)
        for r in (first,second):
            self.assertTrue(all(a['author'] and a['timestamp_utc'] and a['status']==package.PROPOSED for a in r['assumptions']))
            self.assertTrue(all(not s.get('accepted',False) for s in r['schedules'].values()))
        self.assertNotIn('commercial_paper',self.result['periods'][1]['facts'])

    def test_additional_sources_keep_exact_occurrences_and_scope_prose(self):
        for r,f in zip(self.result['decision_resolution']['periods'],self.filings):
            for item in r['additional_facts'].values():
                self.assertEqual(item['evidence_depth'],'exact_primary_inline_and_instance_verified')
                for o in item['occurrences']:
                    n=f.root[o['ordinal']]
                    self.assertEqual(n.attrib['id'],o['xml_id'])
                    self.assertEqual(n.text,o['raw_value'])
                    self.assertEqual(o['end'],str(f.period.annual_end))
            for passage in r['scope_passages']:
                self.assertIn(passage['exact_excerpt'],f.text)
            self.assertIn('Future rates, award valuation and forecast dilution are not historical completion prerequisites',r['historical_tax_and_share_schedule'])
        self.assertEqual(package.inline_amount({'scale':'9'},'4.3'),Decimal('4300000000'))
        with self.assertRaises(ValueError):package.inline_amount({},'4,300')

    def test_original_json_artifacts_and_runtime_source_are_byte_preserved(self):
        # All pre-existing JSONs and runtime source, not only numeric samples.
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',package.BASELINE],cwd=ROOT,text=True).splitlines()
        selected=[p for p in paths if p.startswith('src/') or (p.startswith('docs/') and p.endswith('.json'))]
        for path in selected:
            prior=subprocess.check_output(['git','show',package.BASELINE+':'+path],cwd=ROOT)
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),hashlib.sha256(prior).hexdigest(),path)

    def test_deterministic_json_round_trip(self):
        text=json.dumps(self.result,sort_keys=True,indent=2)+'\n'
        self.assertEqual(json.dumps(json.loads(text),sort_keys=True,indent=2)+'\n',text)

    def test_accepted_defaults_nondefault_estimate_and_original_proposals(self):
        result=package.accepted_view(self.result);view=result.pop('accepted_view')
        self.assertEqual(result,self.result)
        prior=json.loads(subprocess.check_output(['git','show',package.ACCEPTANCE_BASIS+':'+package.OUTPUT],cwd=ROOT))
        self.assertTrue(result==prior,'Complete prior proposal/source payload changed')
        self.assertEqual(view['selected_adjacent_book_movement_usd'],'7155000000')
        self.assertFalse(view['movement_is_cash_delta_nwc'])
        for row,capital,cash,debt in zip(view['periods'],(-25755,-18600),(94565,73043),(89323,106888)):
            for key,value in [('operating_capital',capital),('cash',cash),('borrowings',debt)]:
                self.assertEqual(Decimal(row[key]['selected'].get('value_usd',row[key]['selected'].get('value')))/1000000,value)
                self.assertEqual(row[key]['selected']['status'],package.APPROVED_SCOPE)
                cursor=self.result
                for part in row[key]['source_reference'].strip('/').split('/'):
                    cursor=cursor[int(part)] if isinstance(cursor,list) else cursor[part]
                restored=copy.deepcopy(row[key]['selected']);restored['status']=row[key]['source_status']
                if 'accepted' in cursor:restored['accepted']=cursor['accepted']
                else:restored.pop('accepted')
                self.assertEqual(restored,cursor)
            self.assertIn('operating capital',row['operating_capital']['label'])
            self.assertFalse(row['estimated_nondefault_alternative']['default'])
            self.assertTrue(row['estimated_nondefault_alternative']['estimated'])
            self.assertFalse(row['operating_capital']['complete_current_nwc'])
            self.assertFalse(row['borrowings']['complete_debt'])
            self.assertFalse(row['cash']['unrestricted_or_excess_cash'])
            self.assertIsNone(row['cash']['unknown_restrictions'])
        self.assertIsNone(view['periods'][1]['additional_short_borrowing']['value_usd'])
        self.assertEqual(view['short_debt_zero_proposal_status'],'REJECTED_NOT_SELECTED')
        view['periods'][0]['taxes'][0]['value']='synthetic mutation'
        self.assertTrue(self.result==prior,'View must not alias or mutate original source/proposal data')

    def test_accepted_precision_dates_assumption_and_separate_investments(self):
        for row,original in zip(package.accepted_view(self.result)['accepted_view']['periods'],self.result['periods']):
            entries={e['input_id']:e for e in original['inputs']}
            self.assertEqual(row['expense_da']['selected']['precision'],entries['expense_da']['precision'])
            self.assertFalse(row['expense_da']['source_confirmed_overlap'])
            self.assertFalse(row['expense_da']['additional_rou_addback'])
            self.assertEqual(row['lease_classification']['finance'],'asset_financing')
            self.assertEqual(row['lease_classification']['operating'],'service_cost')
            self.assertEqual(len(row['investment_columns']),4)
            self.assertFalse(row['complete_reinvestment'])
            self.assertEqual(row['shares_awards'],[entries[k] for k in ('year_end_common','cover_common','nonvested_awards','unrecognized_award_cost')])
            self.assertEqual(row['pretax_fact'],original['facts']['pretax'])
            self.assertFalse(row['future_tax_rate_approved'])
            if row['fiscal_year']==2026:
                self.assertEqual(row['additional_deferred_tax_cfo'],[entries['reported:DeferredIncomeTaxesAndTaxCredits']])

    def test_persisted_audit_restart_roundtrip_and_stale_evidence_rejection(self):
        path=ROOT/package.ACCEPTANCE_PATH;body=path.read_text()
        audit=json.loads(body)
        self.assertEqual(audit['source_commit'],package.ACCEPTANCE_BASIS)
        self.assertEqual(audit['source_revision'],package.digest(package.relevant(self.result)))
        with tempfile.TemporaryDirectory() as folder:
            saved=Path(folder)/'acceptance.json';saved.write_text(body)
            self.assertEqual(package.accepted_view(self.result,saved),package.accepted_view(self.result,path))
            self.assertEqual(json.loads(json.dumps(package.accepted_view(self.result,saved))),package.accepted_view(self.result,saved))
            for location,key in [('facts','ar'),('facts','commercial_paper')]:
                changed=copy.deepcopy(self.result)
                changed['periods'][0][location][key]['value']='123'
                with self.assertRaisesRegex(ValueError,'Stale MSFT acceptance'):package.accepted_view(changed,saved)
            for mutation in ('precision','scope','evidence','alternative'):
                changed=copy.deepcopy(self.result)
                changed['decision_resolution']['periods'][0][mutation]='changed'
                with self.assertRaisesRegex(ValueError,'Stale MSFT acceptance'):package.accepted_view(changed,saved)
            audit['decisions']['borrowings']='Select zero'
            saved.write_text(json.dumps(audit))
            with self.assertRaisesRegex(ValueError,'Changed or malformed'):package.accepted_view(self.result,saved)
            audit['sha256']=package.digest({k:v for k,v in audit.items() if k!='sha256'})
            saved.write_text(json.dumps(audit))
            with self.assertRaisesRegex(ValueError,'Unregistered'):package.accepted_view(self.result,saved)
        self.assertEqual(path.read_text(),body)

    def test_missing_audit_cannot_automatically_accept_or_fill_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):package.accepted_view(self.result,Path(folder)/'missing.json')
        result=package.accepted_view(self.result)
        self.assertFalse(result['accepted_view']['valuation_consumption_approved'])
        self.assertFalse(result['accepted_view']['phase1_closed'])
        self.assertEqual(result['accepted_view']['financial_sufficiency'],'NOT_ASSESSED')
        self.assertEqual(result['accepted_view']['decision_statuses'],{k:package.APPROVED_SCOPE for k in package.USER_DECISIONS})
        self.assertIsNone(result['accepted_view']['periods'][1]['additional_short_borrowing']['value_usd'])


if __name__=='__main__':unittest.main()
