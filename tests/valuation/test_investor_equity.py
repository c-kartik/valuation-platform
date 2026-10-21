"""Anonymous Stage C extension; synthetic inputs, unchanged bridge/legacy contracts."""
from copy import deepcopy
from decimal import Decimal,localcontext,Inexact,ROUND_UP
import json
import unittest
from unittest.mock import patch
from tests.valuation.test_equity_case_inputs import equity_document
from tests.valuation.test_case_inputs import ROOT, cli, parse, document
from valuation_platform.valuation import case_inputs as c


def investor_equity():
    doc=equity_document()
    doc.pop('analyst');doc.pop('scope')
    doc.update(schema_version=c.INVESTOR_EQUITY_CASE_SCHEMA,
               preparation={'provenance':'ANONYMOUS_INVESTOR','timestamp_utc':'2026-10-21T10:00:00Z','notes':None})
    return doc


class InvestorEquityTests(unittest.TestCase):
    def test_existing_engine_full_components_and_anonymous_metadata(self):
        old=equity_document();doc=investor_equity();before=deepcopy(doc)
        expected=c.run_case(parse(old),ROOT)
        with patch.object(c,'bridge_to_per_share',wraps=c.bridge_to_per_share) as bridge:
            result=c.run_case(parse(doc),ROOT);bridge.assert_called_once()
        self.assertEqual(result['stage_b'],expected['stage_b']);self.assertEqual(result['stage_c'],expected['stage_c'])
        self.assertEqual(result['schema_version'],c.INVESTOR_EQUITY_RESULT_SCHEMA)
        self.assertEqual(result['submitted_inputs'],before);self.assertEqual(doc,before)
        self.assertIsNone(parse(doc).analyst)
        self.assertIn('unverified', ' '.join(result['limitations']).replace('no verified','unverified'))
        self.assertIn('INVESTOR CALCULATION — EQUITY / VALUE PER SHARE',cli.render_summary(result))

    def test_validate_does_no_calculation_and_never_downgrades(self):
        with patch.object(c,'forecast_five_years',side_effect=AssertionError('calculation')),patch.object(c,'bridge_to_per_share',side_effect=AssertionError('bridge')):
            self.assertIsNotNone(parse(investor_equity()).bridge)
            for key in ('bridge','calculation_scope'):
                doc=investor_equity();del doc[key]
                with self.assertRaises(c.CaseInputError):parse(doc)
            doc=investor_equity();doc['bridge']['unresolved_requirements']=['Unassessed awards']
            with self.assertRaisesRegex(c.CaseInputError,'Unassessed awards'):parse(doc)

    def test_v1_ev_and_legacy_json_remain_unchanged(self):
        old=document();inv=deepcopy(old);inv.pop('analyst');inv.pop('scope');inv.update(schema_version=c.INVESTOR_CASE_SCHEMA,preparation=investor_equity()['preparation'])
        result=c.run_case(parse(inv),ROOT);self.assertNotIn('stage_c',result);self.assertEqual(result['schema_version'],c.INVESTOR_RESULT_SCHEMA)
        inv['bridge']=investor_equity()['bridge']
        with self.assertRaisesRegex(c.CaseInputError,'unknown field'):parse(inv)
        self.assertEqual(c.run_case(parse(old),ROOT)['schema_version'],c.RESULT_SCHEMA)

    def test_notes_strict_parsing_and_required_metadata(self):
        doc=investor_equity();doc['preparation']['notes']='  Personal text\nonly  '
        self.assertEqual(c.run_case(parse(doc),ROOT)['submitted_inputs']['preparation']['notes'],'  Personal text\nonly  ')
        for change in ({'analyst':{}},{'scope':'not supported'},{'calculation_scope':'ENTERPRISE_VALUE'}):
            with self.assertRaises(c.CaseInputError):parse(dict(doc,**change))
        for text in (json.dumps(doc).replace('"wacc": "0.25"','"wacc":0.25'),json.dumps(doc).replace('"wacc": "0.25"','"wacc":"0.25","wacc":"0.3"')):
            with self.assertRaises(c.CaseInputError):c.read_case(text)

    def test_missing_zero_and_omissions_are_distinct(self):
        doc=investor_equity();doc['bridge']['components'][0]['amount']=None
        with self.assertRaisesRegex(c.CaseInputError,'amount'):parse(doc)
        doc['bridge']['components'][0]['amount']='0';case=parse(doc)
        self.assertEqual(case.bridge.components[0].amount,Decimal('0'))
        self.assertIsNone(case.bridge.observations[-1].value)
        doc['bridge']['coverage'][2]['omission_references']=[]
        with self.assertRaisesRegex(c.CaseInputError,'omission'):parse(doc)

    def test_inherited_date_unit_class_award_overlap_guards(self):
        edits=[('shares','shares','0'),('shares','shares','-1'),('shares','observation_date','2026-01-01'),('shares','unit','million shares'),('shares','equivalence_convention','assumed'),('shares','award_policy','automatic_dilution'),('shares','class_id','different')]
        for collection,key,value in edits:
            doc=investor_equity();doc['bridge'][collection][key]=value
            with self.subTest(key=key),self.assertRaises(c.CaseInputError):parse(doc)
        for key,value in [('overlap_references',['asset-b']),('alternative_references',['asset-b']),('overlaps_forecast',True)]:
            doc=investor_equity();doc['bridge']['components'][0][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(c.CaseInputError,'overlap'):parse(doc)

    def test_negative_equity_no_clamping_and_context_isolation(self):
        doc=investor_equity();doc['bridge']['components'][3]['amount']='200'
        with localcontext() as context:
            context.prec=2;context.rounding=ROUND_UP;context.traps[Inexact]=True
            result=c.run_case(parse(doc),ROOT)['stage_c']
            self.assertEqual(context.prec,2)
        self.assertEqual(Decimal(result['equity_value']),Decimal('-130.422939648'))
        self.assertEqual(Decimal(result['value_per_share']),Decimal('-32.605734912'))
