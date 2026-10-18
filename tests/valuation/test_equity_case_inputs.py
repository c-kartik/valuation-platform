"""Editable Stage C integration; all executable numerical cases are synthetic."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal as D, Inexact, ROUND_DOWN, Rounded, localcontext
import io
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from tests.valuation.test_case_inputs import ROOT, EXAMPLES, cli, document, parse
from valuation_platform.valuation import case_inputs as c


def equity_document():
    return json.loads((EXAMPLES / 'synthetic-equity.json').read_text())


def execute(doc=None):
    return c.run_case(parse(equity_document() if doc is None else doc), ROOT)


class EquityCaseTests(unittest.TestCase):
    def test_independent_integrated_arithmetic_and_complete_trace(self):
        doc = equity_document(); result = execute(doc); b = result['stage_c']
        # Existing independently calculated A/B fixture: 77.577060352 EV.
        # Equity = EV +10+2 -20 -3 =66.577060352; four shares =>16.644265088.
        self.assertEqual(D(result['stage_b']['enterprise_value']), D('77.577060352'))
        self.assertEqual([D(b[k]) for k in ('eligible_assets','financing_claims','other_equity_claims',
                                          'equity_value','valuation_shares','value_per_share')],
                         list(map(D, ['12','20','3','66.577060352','4','16.644265088'])))
        self.assertEqual(result['schema_version'], c.EQUITY_RESULT_SCHEMA)
        self.assertEqual(result['calculation_scope'], 'EQUITY_PER_SHARE')
        self.assertEqual(b['stage_b'], result['stage_b'])
        self.assertEqual(result['submitted_inputs'], doc)
        self.assertEqual(b['inputs']['shares'], doc['bridge']['shares'])
        for collection in ('components','observations','coverage'):
            self.assertCountEqual(b['inputs'][collection], doc['bridge'][collection])
        self.assertEqual(result['semantic_input_review'], 'NOT_ASSESSED_BY_CALCULATOR')
        self.assertIn('not authenticated', ' '.join(result['limitations']))
        with patch.object(c, 'bridge_to_per_share', wraps=c.bridge_to_per_share) as engine:
            execute(doc)
            engine.assert_called_once()

    def test_v1_json_unchanged_and_no_stage_c_call(self):
        doc = document()
        with patch.object(c, 'bridge_to_per_share') as bridge:
            result = c.run_case(parse(doc), ROOT)
            bridge.assert_not_called()
        self.assertEqual(set(result), {'schema_version','case_name','input_basis','submitted_inputs',
                                     'semantic_input_review','limitations','stage_b'})
        self.assertEqual(result['schema_version'], 'analyst-case-enterprise-value-v1')
        self.assertNotIn('stage_c', result)
        self.assertNotIn('Value per share (USD/share):', cli.render_summary(result))

    def test_amount_and_shares_are_independently_editable(self):
        doc = equity_document(); doc['bridge']['components'][0]['amount'] = '14'
        first = execute(doc)
        self.assertEqual(D(first['stage_c']['value_per_share']), D('17.644265088'))
        doc['bridge']['shares']['shares'] = '8'
        second = execute(doc)
        self.assertEqual(D(second['stage_c']['value_per_share']), D('8.822132544'))
        self.assertEqual(first['stage_b'], second['stage_b'])

    def test_missing_scope_bridge_and_unresolved_fail_before_calculation(self):
        variants=[]
        for field in ('bridge','calculation_scope'):
            d=equity_document(); del d[field]; variants.append((d,field))
        d=equity_document(); d['calculation_scope']='ENTERPRISE_VALUE'; variants.append((d,'calculation_scope'))
        d=equity_document(); d['bridge']=None; variants.append((d,'bridge'))
        d=equity_document(); d['bridge']['shares']=None; variants.append((d,'bridge.shares'))
        d=equity_document(); d['bridge']['unresolved_requirements']=['award allocation']; variants.append((d,'award allocation'))
        for doc, message in variants:
            with self.subTest(message=message), patch.object(c,'forecast_five_years') as a, patch.object(c,'bridge_to_per_share') as b:
                with self.assertRaisesRegex(c.CaseInputError,message): parse(doc)
                a.assert_not_called(); b.assert_not_called()

    def test_unset_meta_preserves_all_37_and_pending_bridge_errors(self):
        doc=json.loads((EXAMPLES/'meta-fy2025-equity-unset.json').read_text())
        original=json.loads((EXAMPLES/'meta-fy2025-unset.json').read_text())
        for key in ('forecast_years','wacc','terminal_growth','terminal','analyst','anchor'):
            self.assertEqual(doc[key], original[key])
        with patch.object(c,'load_meta_revenue_anchor') as anchor:
            with self.assertRaises(c.CaseInputError) as failure: parse(doc)
            anchor.assert_not_called()
        self.assertEqual(sum('UNSET; supply a fractional' in x for x in failure.exception.errors),37)
        self.assertIn('bridge.shares.shares', str(failure.exception))
        self.assertIn('bridge.components', str(failure.exception))
        self.assertIn('bridge.unresolved_requirements', str(failure.exception))
        for collection in ('components','coverage','shares'):
            self.assertIn(collection, str(failure.exception))

    def test_fixed_model_validation_mapping(self):
        edits=[('components',0,'company_cik',124,'company/date'),
               ('components',0,'as_of','2026-01-01','company/date'),
               ('components',0,'unit','EUR','base USD'),
               ('components',0,'scale',1000000,'scale 1'),
               ('components',0,'amount','-1','sign domain'),
               ('components',0,'overlaps_forecast',True,'overlap'),
               ('components',0,'overlap_references',['asset-b'],'overlap'),
               ('components',0,'alternative_references',['asset-b'],'overlap'),
               ('components',0,'overlap_references',['missing'],'reference'),
               ('components',0,'source_references',[],'references'),
               ('components',0,'origin','imagined','origin'),
               ('observations',0,'company_cik',124,'company'),
               ('observations',2,'value','0','references'),
               ('coverage',0,'population_ids',[],'Empty populations'),
               ('coverage',2,'omission_references',[],'omission'),
               ('coverage',2,'omission_references',['gross-assets'],'omission')]
        for collection,index,key,value,message in edits:
            with self.subTest(collection=collection,key=key,value=value):
                d=equity_document(); d['bridge'][collection][index][key]=value
                with self.assertRaisesRegex(c.CaseInputError,message):parse(d)
        for key,value,message in [('shares','0','sign domain'),('shares','-1','sign domain'),
                                  ('unit','millions','share units'),('scale',1000000,'scale 1'),
                                  ('company_cik',124,'company/date'),('observation_date','2026-01-01','company/date'),
                                  ('class_id','other','class mismatch'),('equivalence_convention','automatic','class'),
                                  ('award_policy','add_back_sbc','award')]:
            with self.subTest(key=key,value=value):
                d=equity_document(); d['bridge']['shares'][key]=value
                with self.assertRaisesRegex(c.CaseInputError,message):parse(d)

    def test_null_omission_and_empty_role_coverage_require_explicit_declaration(self):
        d=equity_document(); d['bridge']['components'].pop()
        d['bridge']['coverage'][2]['population_ids']=[]
        result=execute(d)['stage_c']
        self.assertEqual(D(result['other_equity_claims']),D(0))
        note=next(x for x in result['inputs']['observations'] if x['disposition']=='OMISSION')
        self.assertIsNone(note['value']); self.assertIsNone(note['precision'])
        numeric=deepcopy(d); numeric['bridge']['observations'][2].update(
            value='0',precision='INF',source_references=['synthetic:source'])
        with self.assertRaisesRegex(c.CaseInputError,'Omission decisions'):parse(numeric)
        d['bridge']['coverage'][2]['omission_references']=[]
        with self.assertRaisesRegex(c.CaseInputError,'Empty populations'):parse(d)

    def test_strict_parsing_unknown_fields_types_and_metadata(self):
        for key,value in [('amount',10),('amount',True),('amount','10%'),('amount','NaN'),
                          ('source_references','source'),('as_of','20251231'),('unexpected','x')]:
            d=equity_document(); d['bridge']['components'][0][key]=value
            with self.subTest(key=key,value=value), self.assertRaises(c.CaseInputError):parse(d)
        raw=json.dumps(equity_document())
        for bad in (raw.replace('"amount": "10"','"amount": 10.5'),
                    raw.replace('"amount": "10"','"amount": NaN'),
                    raw.replace('"amount": "10"','"amount": "10", "amount": "20"')):
            with self.assertRaises(c.CaseInputError):c.read_case(bad)
        d=equity_document(); d['bridge']['coverage'][0]['review']['author']=None
        with self.assertRaisesRegex(c.CaseInputError,'coverage'):parse(d)
        d=equity_document(); d['bridge']['input_basis']='MANUAL_INPUT'
        with self.assertRaisesRegex(c.CaseInputError,'input_basis'):parse(d)
        d=equity_document(); d['bridge']['convention_version']='other'
        with self.assertRaisesRegex(c.CaseInputError,'convention'):parse(d)
        d=document();d['bridge']={}
        with self.assertRaisesRegex(c.CaseInputError,'unknown field'):parse(d)

    def test_immutable_case_cannot_silently_downgrade_to_ev(self):
        case=parse(equity_document())
        with self.assertRaisesRegex(c.CaseInputError,'declarations disagree'):
            c.run_case(replace(case,bridge=None),ROOT)

    def test_context_determinism_and_input_preservation(self):
        doc=equity_document(); before=deepcopy(doc); case=parse(doc)
        expected=execute(doc); summary=cli.render_summary(expected)
        with localcontext() as ctx:
            ctx.prec=3;ctx.rounding=ROUND_DOWN;ctx.Emax=3;ctx.Emin=-3
            ctx.traps[Inexact]=True;ctx.clear_flags();ctx.flags[Rounded]=True
            previous=ctx.copy()
            self.assertEqual(parse(doc),case)
            actual=c.run_case(case,ROOT)
            self.assertEqual(json.dumps(actual,sort_keys=True),json.dumps(expected,sort_keys=True))
            self.assertEqual(cli.render_summary(actual),summary)
            self.assertEqual((ctx.prec,ctx.rounding,ctx.Emax,ctx.Emin,ctx.flags,ctx.traps),
                             (previous.prec,previous.rounding,previous.Emax,previous.Emin,previous.flags,previous.traps))
        self.assertEqual(doc,before)

    def test_summary_units_signs_reconciliation_exclusions_and_rounding(self):
        result=execute(); report=cli.render_summary(result)
        for text in ['Equity bridge (USD millions','+0.00001000','-0.00002000',
                     'Eligible-asset subtotal (+): 0.00001200','Financing subtotal (subtract): 0.00002000',
                     'Other-claim subtotal (subtract): 0.00000300','Equity value: 0.00006658',
                     'Valuation shares (actual shares, scale 1): 4','2025-12-31','single_common_class',
                     'sbc_expensed_no_duplicate_service_charge_v1','Value per share (USD/share): 16.64426509',
                     'EXCLUDED','OMISSION','unknown amount, not zero','not authenticated']:
            self.assertIn(text,report)
        for value,shown in [('1.234567885','1.23456788'),('1.234567895','1.23456790')]:
            display=deepcopy(result);display['stage_c']['value_per_share']=value
            with patch.object(c,'bridge_to_per_share') as engine:
                self.assertIn('USD/share): '+shown,cli.render_summary(display));engine.assert_not_called()
            self.assertEqual(display['stage_c']['value_per_share'],value)
        d=equity_document(); d['bridge']['components'][2]['amount']='100'
        negative=execute(d)
        self.assertEqual(D(negative['stage_c']['equity_value']),D('-13.422939648'))
        self.assertIn('USD/share): -3.35573491',cli.render_summary(negative))

    def test_cli_validation_run_save_protections_and_no_downgrade(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'case.json';source.write_text(json.dumps(equity_document()))
            original=source.read_bytes()
            for fmt in ('json','summary'):
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    cli.main([str(source),'--format',fmt,'--output',str(Path(tmp)/'never-written')])
                with redirect_stdout(io.StringIO()), patch.object(cli,'run_case') as run, patch.object(c,'bridge_to_per_share') as bridge:
                    self.assertEqual(cli.main([str(source),'--format',fmt]),0)
                    run.assert_not_called();bridge.assert_not_called()
                with redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(cli.main([str(source),'--run','--format',fmt]),0)
                expected=json.dumps(execute(),sort_keys=True,indent=2)+'\n' if fmt=='json' else cli.render_summary(execute())
                self.assertEqual(out.getvalue(),expected)
                dest=Path(tmp)/('result.'+fmt)
                with redirect_stdout(io.StringIO()):self.assertEqual(cli.main([str(source),'--run','--format',fmt,'--output',str(dest)]),0)
                self.assertEqual(dest.read_text(),expected)
                for target in (source,dest,ROOT/'docs/forbidden-equity-output'):
                    with redirect_stderr(io.StringIO()),patch.object(cli,'run_case') as run:
                        self.assertEqual(cli.main([str(source),'--run','--format',fmt,'--output',str(target)]),2)
                        run.assert_not_called()
                self.assertEqual(source.read_bytes(),original)
                bad=equity_document();bad['bridge']['unresolved_requirements']=['unknown claims'];source.write_text(json.dumps(bad))
                with redirect_stderr(io.StringIO()) as err,redirect_stdout(io.StringIO()) as out,patch.object(cli,'run_case') as run:
                    self.assertEqual(cli.main([str(source),'--run','--format',fmt]),2)
                    self.assertEqual(out.getvalue(),'');self.assertIn('unknown claims',err.getvalue());run.assert_not_called()
                source.write_bytes(original)
