"""Observed dates/classes/accounting bases, not issuer equity or share totals."""
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
import hashlib,json,subprocess,unittest
from tests.analyst.preparation_preservation import assert_preserved
import xml.etree.ElementTree as ET
from valuation_platform.analyst import retained_claims_shares as c,retained_components as r,historical_inputs as h
from valuation_platform.analyst import pilot_historical_inputs as p
from valuation_platform.sec import filing_xbrl as x
ROOT=c.bridge.parent.capex.shared.ROOT
HEAD='cbe33aba56133c1b8b03153f883aface272180da'


class ClaimsSharesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger,cls.parents,cls.overlays,cls.prior=c.build()
        cls.a=cls.overlays['AAPL'][-1]
        cls.e=r.prepare(cls.a.period,(cls.a.receipt,),(r.ArtifactBinding(cls.a.receipt.artifact.url,cls.a.receipt.artifact.sha256,'instance'),))
        cls.f,cls.i=next((f,i) for f,i in cls.e.facts if f.concept==c.SHARE_CONCEPT)

    def test_all_398_slots_identity_history_and_offline_replay(self):
        self.assertEqual(self.ledger,json.loads((ROOT/c.LEDGER).read_text()))
        self.assertEqual(self.prior,json.loads((ROOT/c.bridge.LEDGER).read_text()))
        self.assertEqual((self.ledger['selected_periods'],self.ledger['issuer_count']),(199,42))
        self.assertEqual({tuple(sorted(v['identity'].items())) for v in self.ledger['rows']},
                         {tuple(sorted(v['identity'].items())) for v in self.prior['rows']})
        self.assertEqual(len(self.ledger['history_exceptions']),11)
        self.assertFalse(self.overlays['XOM'])
        for field in c.FIELDS:self.assertEqual(sum(self.ledger['summary'][field.value]['outcomes'].values()),199)
        for entries in self.overlays.values():
            for a in entries:self.assertFalse(a.period.cik in h.SPECIALIZED_CIKS)

    def test_actual_xml_sources_dates_dimensions_units_and_precision(self):
        for entries in self.overlays.values():
            for a in entries:
                root=ET.fromstring(a.receipt.artifact.body)
                for v in (*a.other_bridge,*a.shares):
                    observations=(v,*v.alternatives) if v.value is not None else v.alternatives
                    for obs in observations:
                        for s in obs.sources:
                            fact=root[s.occurrence_ordinal]
                            self.assertEqual(fact.tag,'{'+s.namespace+'}'+s.concept)
                            self.assertEqual(fact.get('contextRef'),s.context_id)
                            self.assertEqual(fact.get('unitRef'),json.loads(s.locator)['unit_id'])
                            self.assertEqual(Decimal(fact.text.strip()),obs.value)
                            self.assertEqual(fact.get('decimals'),obs.precision)
                            self.assertEqual((s.start,s.end),(None,obs.as_of))
                            self.assertEqual(s.receipt,a.receipt)
                            self.assertEqual(s.unit,'shares' if obs.field is h.Field.SHARES else 'USD')
                            self.assertEqual((obs.sign,obs.scale),(1,1))
                self.assertEqual(hashlib.sha256(a.receipt.artifact.body).hexdigest(),a.receipt.artifact.sha256)

    def test_share_dates_classes_not_fy_end_weighted_average_or_totals(self):
        values,row=c.inspect(self.e,h.Field.SHARES)
        actual=[v for v in values if v.value is not None]
        self.assertTrue(actual);self.assertTrue(any(v.as_of!=self.a.period.annual_end for v in actual))
        self.assertTrue(all(v.sources[0].concept==c.SHARE_CONCEPT for v in actual))
        self.assertIsNone(values[0].value);self.assertIsNone(values[0].as_of)
        googl=self.overlays['GOOGL'][-1]
        classes=[v for v in googl.shares if v.value is not None]
        self.assertGreater(len(classes),1)
        self.assertTrue(any(v.sources[0].dimensions for v in classes))
        self.assertTrue(all(v.formula is None and v.completeness is h.Completeness.PARTIAL for v in classes))
        for name in c.WEIGHTED:
            f=replace(self.f,concept=name,namespace=self.e.namespaces['us-gaap'])
            values,row=c.inspect(replace(self.e,facts=((f,self.i),)),h.Field.SHARES)
            self.assertEqual(row['status'],'NO_ELIGIBLE_OBSERVATIONS')
            self.assertEqual(row['diagnostics'][0]['disposition'],'WEIGHTED_AVERAGE_NOT_POINT_IN_TIME')

    def test_duplicate_precision_conflict_and_distinct_dates_never_merge(self):
        e=replace(self.e,facts=((self.f,self.i),(self.f,self.i+10000)))
        v,row=c.inspect(e,h.Field.SHARES);self.assertEqual(len(v[1].sources),2)
        f=replace(self.f,raw_value='1',numeric_value=Decimal('1'))
        v,row=c.inspect(replace(self.e,facts=((self.f,self.i),(f,self.i+10000))),h.Field.SHARES)
        self.assertEqual(row['status'],'CONFLICTING');self.assertEqual(len(v[1].alternatives),2)
        self.assertIsNone(v[1].value)
        v,row=c.inspect(replace(self.e,facts=((self.f,self.i),(replace(self.f,decimals='INF'),self.i+10000))),h.Field.SHARES)
        self.assertEqual(row['status'],'OBSERVATIONS');self.assertEqual(v[1].alternatives[0].precision,'INF')
        ctx=self.e.contexts[self.f.context_id];other=replace(ctx,context_id='other-date',end=ctx.end+timedelta(days=1))
        f=replace(f,context_id=other.context_id,end=other.end)
        e=replace(self.e,contexts={**self.e.contexts,other.context_id:other},facts=((self.f,self.i),(f,self.i+10000)))
        v,row=c.inspect(e,h.Field.SHARES)
        self.assertEqual(row['status'],'OBSERVATIONS');self.assertEqual(len({a.as_of for a in v[1:]}),2)

    def test_class_populations_and_unit_entity_duration_mismatches(self):
        ctx=self.e.contexts[self.f.context_id]
        ds=(x.FilingXBRLDimension(x.FilingXBRLQName('http://example.com','ClassAxis'),x.FilingXBRLQName('http://example.com','ClassB'),None),)
        other=replace(ctx,context_id='other-class',dimensions=ds)
        f=replace(self.f,context_id=other.context_id,dimensions=ds,raw_value='2',numeric_value=Decimal('2'))
        e=replace(self.e,contexts={**self.e.contexts,other.context_id:other},facts=((self.f,self.i),(f,self.i+10000)))
        vv,row=c.inspect(e,h.Field.SHARES)
        self.assertEqual(row['status'],'OBSERVATIONS');self.assertEqual(len(vv[1:]),2)
        self.assertFalse(any(v.formula for v in vv));self.assertTrue(vv[2].sources[0].dimensions)
        for bad in (replace(self.f,unit=None),replace(self.f,is_nil=True),replace(self.f,decimals='bad')):
            self.assertEqual(c.inspect(replace(self.e,facts=((bad,self.i),)),h.Field.SHARES)[1]['status'],'EVIDENCE_GAP')
        usd=x.FilingXBRLUnit('USD',(x.FilingXBRLQName('http://www.xbrl.org/2003/iso4217','USD'),),())
        self.assertEqual(c.inspect(replace(self.e,facts=((replace(self.f,unit=usd),self.i),)),h.Field.SHARES)[1]['status'],'EVIDENCE_GAP')
        for bad in (replace(ctx,start=self.a.period.annual_start),replace(ctx,entity_identifier='999')):
            e=replace(self.e,contexts={**self.e.contexts,ctx.context_id:bad},facts=((self.f,self.i),))
            self.assertEqual(c.inspect(e,h.Field.SHARES)[1]['status'],'NO_ELIGIBLE_OBSERVATIONS')

    def test_closed_scope_bases_investment_overlap_and_no_netting(self):
        rules={v.concept:v for v in c.RULES}
        self.assertNotEqual(rules['DefinedBenefitPlanAssetsForPlanBenefits'].role,rules['DefinedBenefitPlanFundedStatusOfPlan'].role)
        self.assertNotEqual(rules['DeferredTaxAssetsGross'].role,rules['DeferredTaxAssetsOperatingLossCarryforwards'].role)
        self.assertIn('cash_investment_components:equity_method',rules['EquityMethodInvestments'].overlap)
        # Same verified instant numeric representation, changed bounded element:
        ctx=self.e.contexts[self.f.context_id];ctx=replace(ctx,end=self.a.period.annual_end)
        usd=x.FilingXBRLUnit('USD',(x.FilingXBRLQName('http://www.xbrl.org/2003/iso4217','USD'),),())
        for name in ('PreferredStockValue','DefinedBenefitPlanFundedStatusOfPlan','DeferredTaxAssetsOperatingLossCarryforwards'):
            f=replace(self.f,concept=name,namespace=self.e.namespaces['us-gaap'],unit=usd)
            e=replace(self.e,contexts={**self.e.contexts,ctx.context_id:ctx},facts=((f,self.i),))
            vv,row=c.inspect(e,h.Field.OTHER_BRIDGE)
            self.assertEqual(row['status'],'OBSERVATIONS');self.assertEqual(vv[1].role,rules[name].role)
            self.assertIsNone(vv[0].value)
            e=replace(e,contexts={**e.contexts,ctx.context_id:replace(ctx,end=ctx.end+timedelta(days=1))})
            self.assertEqual(c.inspect(e,h.Field.OTHER_BRIDGE)[1]['status'],'NO_ELIGIBLE_OBSERVATIONS')
        f=replace(self.f,namespace='http://example.com/issuer')
        self.assertEqual(c.inspect(replace(self.e,facts=((f,self.i),)),h.Field.SHARES)[1]['status'],'UNSUPPORTED_SCOPE')

    def test_serialization_independent_replay_dates_dimensions_and_tampering(self):
        for name in ('AAPL','GOOGL','MSFT','IBM'):
            v=self.overlays[name][-1];payload=c.serialize(v)
            self.assertEqual(c.deserialize(payload),v);self.assertEqual(c.serialize(c.deserialize(payload)),payload)
        observed=next(v for v in self.a.shares if v.value is not None)
        bad=replace(self.a,shares=tuple(replace(v,role='issuer_total') if v==observed else v for v in self.a.shares))
        with self.assertRaises(h.InputError):c.serialize(bad)
        doc=json.loads(c.serialize(self.a));doc['schema']='unknown'
        with self.assertRaises(h.InputError):c.deserialize(json.dumps(doc))
        empty=r.Evidence(self.a.period,(),None,{}, {},(),('Missing receipt.',))
        value,rows=c.overlay(empty)
        self.assertTrue(all(v['status']=='EVIDENCE_GAP' for v in rows.values()))
        self.assertEqual(c.deserialize(c.serialize(value)),value)

    def test_prior_fields_pilot_payload_hashes_and_frozen_artifacts_preserved(self):
        hashes={'MSFT':'e05f85125b6244c321fbdee6469fa89bb809533614bbcc9c5399d2b5c56eb8b5',
          'AAPL':'2772f34db57beb116f4fdb498f0016dc6502d7642b7bbc18f9e89e3645e66f83',
          'GOOGL':'f442e248f1ea2884967680db78c99076ee8beefdaae0bc050b6ee2f0c9b324d5'}
        for name,expected in hashes.items():self.assertEqual(hashlib.sha256(p.serialize(p.load_history(name)).encode()).hexdigest(),expected)
        protected=subprocess.check_output(['git','ls-tree','-r','--name-only',HEAD,'src/valuation_platform/normalization','docs/evidence','docs/universe'],cwd=ROOT).decode().splitlines()
        protected+=['docs/retained-bridge-component-ledger.json','docs/retained-d-and-a-ledger.json','docs/pilot-historical-input-mappings.json',
                    'docs/retained-cfo-ledger.json','docs/retained-working-capital-ledger.json','docs/retained-tax-sbc-ledger.json','docs/refreshed-capex-ledger.json']
        for path in protected:assert_preserved(self, ROOT, path, HEAD)
        old=c.bridge.overlay(self.e)[0]
        self.assertEqual(c.bridge.deserialize(c.bridge.serialize(old)),old)
        for name in ('AAPL','MSFT','GOOGL'):
            history=self.parents[name]
            if type(history) is c.bridge.parent.RefreshedHistory:history=history.bundle
            for a in p.load_history(name).annuals:self.assertEqual(next(v for v in history.annuals if v.period==a.period),a)


if __name__=='__main__':unittest.main()
