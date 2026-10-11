"""Frozen 94-period acceptance regression and adversarial curated D&A checks."""

from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from valuation_platform.normalization import (
    CAPEX_POLICY, FinancialMetric, normalize_annual_financials,
    normalize_annual_balance_sheets, assemble_standardized_annual_history,
    standardized_history_to_dict,
)
from valuation_platform.normalization.capex_scope import (
    CAPEX_SCOPE_EQUIVALENCE_POLICY as POLICY, CapexScopePolicyError,
    VerifiedCapexArtifacts, apply_curated_capex_scope_policy,
    verify_capex_artifacts,
)
from valuation_platform.normalization.models import (
    AmbiguityReason, AmbiguousHistoricalMetric, EvidenceSourceKind, FactEvidence, HistoricalPeriod,
    MissingHistoricalMetric, MissingReason, NormalizedHistoricalValue,
)
from valuation_platform.normalization.output import HistoricalOutputError
from valuation_platform.sec import (
    SECCompanyIdentity, SECFiling, SECFilingXBRL, FilingXBRLContext,
    FilingXBRLFact, FilingXBRLUnit, FilingXBRLQName, FilingFactObservations,
    SelectedFactObservations,
)
from tests.normalization.test_pretax_scope import annual_period

from valuation_platform.normalization.d_and_a_scope import _dimensions

NOW = datetime(2026, 10, 10, tzinfo=timezone.utc)
INVENTORY = json.loads((Path(__file__).resolve().parents[2] /
                       "docs/capex-inventory.json").read_text())["rows"]


def fixture(row):
    f = row["filing"]
    filing = SECFiling(f["accession_number"], f["form"],
                      date.fromisoformat(f["filing_date"]),
                      date.fromisoformat(f["report_date"]), f["primary_document"])
    company = SECCompanyIdentity(row["ticker"], row["cik"], f"{row['cik']:010d}",
                                 row["ticker"], "ticker-source", NOW)
    contexts = tuple(FilingXBRLContext(
        key, c["entity_identifier_scheme"], c["entity_identifier"],
        date.fromisoformat(c["start"]) if c["start"] else None,
        date.fromisoformat(c["end"]), _dimensions(c["dimensions"]),
    ) for key, c in row["contexts"].items())
    cmap = {c.context_id: c for c in contexts}
    units = tuple(FilingXBRLUnit(
        u["unit_id"], tuple(FilingXBRLQName(**q) for q in u["numerator_measures"]),
        tuple(FilingXBRLQName(**q) for q in u["denominator_measures"]),
    ) for u in row["units"].values())
    umap = {u.unit_id: u for u in units}
    facts = tuple(FilingXBRLFact(
        o["concept_key"].split("#")[0], o["concept_key"].split("#")[1],
        o["context_id"], cmap[o["context_id"]].start, cmap[o["context_id"]].end,
        cmap[o["context_id"]].dimensions, o["unit_ref"], umap.get(o["unit_ref"]),
        o["raw_value"], Decimal(o["numeric_value"]) if o["numeric_value"] else None,
        o["decimals"], o["is_nil"], filing.accession_number, row["source_url"],
    ) for o in row["occurrences"])
    instance = SECFilingXBRL(company, filing, contexts, units, facts, row["source_url"], NOW)
    entry = next((e for e in POLICY.entries if e.accession_number == filing.accession_number), None)
    period_entry = SimpleNamespace(company_cik=row["cik"],
                                   annual_start=date.fromisoformat(row["annual_start"]),
                                   annual_end=date.fromisoformat(row["annual_end"]),
                                   report_date=filing.report_date)
    period = annual_period(period_entry, filing)
    period = replace(period, filing=replace(period.filing, source_url=row["source_url"]))
    bucket = FilingFactObservations(filing, ())
    artifacts = VerifiedCapexArtifacts(entry.accession_number, entry.artifact_digests) if entry else None
    return bucket, instance, period, artifacts


class CapexScopeTests(unittest.TestCase):
    def setUp(self):
        self.entry = POLICY.entries[0]
        row = next(r for r in INVENTORY if r['filing']['accession_number'] == self.entry.accession_number)
        self.bucket, self.instance, self.period, self.artifacts = fixture(row)
        self.missing = MissingHistoricalMetric(FinancialMetric.CAPEX,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION, CAPEX_POLICY.candidates)
        self.fact = next(f for f in self.instance.facts if f.concept == self.entry.concept)

    def resolve(self, instance=None, direct=None, **kwargs):
        return apply_curated_capex_scope_policy(
            kwargs.get('bucket', self.bucket), direct or self.missing, self.entry.company_cik,
            kwargs.get('period', self.period), instance or self.instance,
            kwargs.get('artifacts', self.artifacts))

    def only(self, **kwargs):
        return replace(self.instance, facts=(replace(self.fact, **kwargs),))

    def direct(self, value):
        e = FactEvidence(EvidenceSourceKind.COMPANY_FACTS, 'company-facts', 'us-gaap',
            CAPEX_POLICY.candidates[0].name, value, 'USD', self.entry.annual_start,
            self.entry.annual_end, self.entry.accession_number, '10-K', self.entry.filed,
            None, None, None)
        return NormalizedHistoricalValue(FinancialMetric.CAPEX, value, 'USD',
            HistoricalPeriod(self.entry.annual_start, self.entry.annual_end), e, ())

    def test_57_period_regression(self):
        yes = no = 0
        for row in INVENTORY:
            b, x, p, a = fixture(row)
            selected = SelectedFactObservations(x.company, 'company-facts', NOW, (b,), ())
            old = normalize_annual_financials(selected, policies=(CAPEX_POLICY,),
                filing_xbrl=(x,), annual_periods=(p,)).annual[0].metrics[0]
            new = normalize_annual_financials(selected, policies=(CAPEX_POLICY,),
                filing_xbrl=(x,), annual_periods=(p,),
                capex_artifacts=(a,) if a else ()).annual[0].metrics[0]
            self.assertIsInstance(old, MissingHistoricalMetric)
            if a:
                self.assertIsInstance(new, NormalizedHistoricalValue)
                self.assertEqual(new.value, Decimal(row['potential_reported_value_usd']))
                yes += 1
            else:
                self.assertEqual(old, new); no += 1
        self.assertEqual((yes, no), (10, 47))

    def test_immutable_models_and_invalid_identity(self):
        with self.assertRaises(FrozenInstanceError): self.entry.unit = 'EUR'
        for kw in ({'form':'10-K/A'}, {'namespace':'extension'}, {'expected_value':Decimal(-1)},
                   {'company_cik':True}, {'reviewed_evidence':()}, {'instance_digest':'bad'},
                   {'primary_document':'other'}, {'concept':'PaymentsToAcquireBusinesses'},
                   {'economic_scope':'OTHER'}, {'unit':'EUR'}, {'reviewed_entry_json':'{}'}):
            with self.subTest(kw=kw), self.assertRaises(CapexScopePolicyError):replace(self.entry, **kw)
        for kw in ({'entries':(self.entry,)*10}, {'version':'2'}, {'policy_id':'other'}):
            with self.assertRaises(CapexScopePolicyError):replace(POLICY, **kw)

    def test_three_same_context_occurrences(self):
        r = self.resolve(replace(self.instance, facts=(self.fact,)*3))
        self.assertEqual([e.occurrence_ordinal for e in r.policy_provenance.filing_xbrl_evidence], [1,2,3])
        self.assertEqual(r.policy_provenance.capex_scope.confirming_original_ordinals, (0,1,2))

    def test_equivalent_context_unit_and_decimal_representations(self):
        c = next(c for c in self.instance.contexts if c.context_id == self.fact.context_id)
        c = replace(c, context_id='equivalent'); u = replace(self.fact.unit, unit_id='other-usd')
        f = replace(self.fact, context_id=c.context_id, unit_ref=u.unit_id, unit=u,
            raw_value=str(self.entry.expected_value)+'.00', numeric_value=self.entry.expected_value,
            decimals='-4')
        r = self.resolve(replace(self.instance, facts=(self.fact,f),
            contexts=(*self.instance.contexts,c), units=(*self.instance.units,u)))
        self.assertEqual(len(r.policy_provenance.filing_xbrl_evidence), 2)
        self.assertEqual(r.policy_provenance.filing_xbrl_evidence[1].raw_value, f.raw_value)

    def test_conflict_and_changed_negative_values(self):
        self.assertIsInstance(self.resolve(replace(self.instance, facts=(self.fact,
            replace(self.fact,numeric_value=Decimal(9),raw_value='9')))), AmbiguousHistoricalMetric)
        for v in (Decimal(9),Decimal(-1)):
            self.assertIsInstance(self.resolve(self.only(numeric_value=v,raw_value=str(v))), MissingHistoricalMetric)

    def test_precedence_equal_conflict_ambiguity(self):
        d = self.direct(self.entry.expected_value); r = self.resolve(direct=d)
        self.assertEqual(r.chosen_source,d.chosen_source)
        self.assertIsNotNone(r.policy_provenance.capex_scope)
        self.assertIsInstance(self.resolve(direct=self.direct(1)),AmbiguousHistoricalMetric)
        self.assertIsInstance(self.resolve(self.only(numeric_value=Decimal(9),raw_value='9'),
            direct=d),AmbiguousHistoricalMetric)
        a = AmbiguousHistoricalMetric(FinancialMetric.CAPEX,AmbiguityReason.CONFLICTING_CONCEPT_VALUES,(d.chosen_source,))
        self.assertIs(self.resolve(direct=a),a)
        self.assertEqual(self.resolve(direct=d,artifacts=None),d)

    def test_wrong_concept_namespace_and_no_facts(self):
        for kw in ({'concept':'PaymentsToAcquireIntangibleAssets'}, {'namespace':'http://issuer'}):
            self.assertEqual(self.resolve(self.only(**kw)),self.missing)
        self.assertEqual(self.resolve(replace(self.instance,facts=())),self.missing)

    def test_wrong_entity_period_dimension_excluded(self):
        from valuation_platform.sec.filing_xbrl import FilingXBRLDimension
        c = next(c for c in self.instance.contexts if c.context_id==self.fact.context_id)
        variants = [replace(c,context_id='other',entity_identifier='0000000001'),
            replace(c,context_id='other',start=date(2000,1,1)),
            replace(c,context_id='other',dimensions=(FilingXBRLDimension(
                FilingXBRLQName('http://issuer','Axis'), FilingXBRLQName('http://issuer','Member'),None),))]
        for bad in variants:
            f = replace(self.fact,context_id=bad.context_id,start=bad.start,end=bad.end,
                dimensions=bad.dimensions,numeric_value=Decimal(9))
            x = replace(self.instance,contexts=(*self.instance.contexts,bad),facts=(self.fact,f))
            self.assertEqual(self.resolve(x).value,self.entry.expected_value)

    def test_non_usd_and_nil(self):
        u = replace(self.fact.unit,unit_id='eur',numerator_measures=(FilingXBRLQName('http://www.xbrl.org/2003/iso4217','EUR'),))
        x = replace(self.only(unit_ref='eur',unit=u),units=(*self.instance.units,u))
        self.assertEqual(self.resolve(x),self.missing)
        self.assertEqual(self.resolve(self.only(is_nil=True,numeric_value=None,raw_value=None)),self.missing)
        with self.assertRaises(CapexScopePolicyError):
            self.resolve(replace(self.instance,facts=(self.fact,replace(self.fact,is_nil=True,numeric_value=None,raw_value=None))))

    def test_structural_errors(self):
        for kw in ({'context_id':'broken'},{'unit_ref':'broken'}, {'unit_ref':None,'unit':None},
                   {'source_url':'other'},{'accession_number':'other'}, {'numeric_value':None},
                   {'numeric_value':Decimal('NaN')},{'start':date(2000,1,1)}):
            with self.subTest(kw=kw),self.assertRaises(CapexScopePolicyError):self.resolve(self.only(**kw))
        for x in (replace(self.instance,source_url='other'),replace(self.instance,contexts=(*self.instance.contexts,self.instance.contexts[0]))):
            with self.assertRaises(CapexScopePolicyError):self.resolve(x)

    def test_future_amended_incomplete(self):
        for kw in ({'form':'10-K/A'},{'accession_number':'0001018724-27-000001'},
                   {'filing_date':date(2027,1,1)}, {'primary_document':'other'}):
            self.assertEqual(self.resolve(bucket=replace(self.bucket,filing=replace(self.bucket.filing,**kw))),self.missing)
        self.assertEqual(self.resolve(artifacts=None),self.missing)
        with self.assertRaises(CapexScopePolicyError):self.resolve(artifacts=replace(self.artifacts,accession_number='other'))
        with self.assertRaises(CapexScopePolicyError):verify_capex_artifacts(self.entry,{},self.instance)

    def test_output_serialization_and_provenance_tamper(self):
        selected = SelectedFactObservations(self.instance.company,'company-facts',NOW,(self.bucket,),())
        h = normalize_annual_financials(selected,filing_xbrl=(self.instance,),annual_periods=(self.period,),capex_artifacts=(self.artifacts,))
        out = assemble_standardized_annual_history(h,normalize_annual_balance_sheets(selected))
        payload = json.loads(json.dumps(standardized_history_to_dict(out)))
        self.assertEqual(payload['schema_version'],'5')
        m = next(m for m in payload['annual'][0]['measures'] if m['measure']=='capex')
        self.assertEqual(m['policy']['version'],'1')
        self.assertEqual(m['policy']['capex_scope']['reviewed_entry']['expected_value_usd'],str(self.entry.expected_value))
        self.assertEqual(len(m['policy']['reviewed_evidence']),3)
        from valuation_platform.normalization.output import _policy_reference
        p = self.resolve().policy_provenance
        for bad in (replace(p,policy_version='2'),replace(p,capex_scope=replace(p.capex_scope,confirming_original_ordinals=(999,)))):
            with self.assertRaises(HistoricalOutputError):_policy_reference(bad,self.bucket.filing)

    def test_generic_policy_unchanged(self):
        self.assertEqual(tuple(c.name for c in CAPEX_POLICY.candidates),('PaymentsToAcquirePropertyPlantAndEquipment',))

    def test_authorized_refresh_bodies_and_old_audit(self):
        import hashlib, base64, gzip
        from valuation_platform.normalization.capex_scope import _validate_representation_records
        records = json.loads((Path(__file__).resolve().parents[1] /
            'fixtures/capex_amzn_response_bodies.json').read_text())
        self.assertEqual(len(records),15)
        for e in POLICY.entries:
            if e.company_cik != 1018724: continue
            row = json.loads(e.reviewed_entry_json)
            bodies = {}
            for r in records:
                if r['accession_number'] != e.accession_number: continue
                body = gzip.decompress(base64.b64decode(r['body_gzip_base64']))
                self.assertEqual(hashlib.sha256(body).hexdigest(),r['sha256'])
                self.assertEqual(len(body),r['byte_count'])
                self.assertNotEqual(r['sha256'],r['old_sha256'])
                self.assertEqual(r['old_status'],'unverifiable_original_body_unavailable')
                bodies[r['source_url']] = body
            _validate_representation_records(row,bodies)
            url = next(iter(bodies))
            with self.assertRaises(CapexScopePolicyError):
                _validate_representation_records(row,{**bodies,url:bodies[url]+b' '})

    def test_refresh_requires_independent_approved_review(self):
        from valuation_platform.normalization.capex_scope import _validate_representation_records
        for change in ({'review_status':'unreviewed'}, {'old_status':'verified'},
                       {'scope_assertions':[]}, {'sha256':'0'*64},
                       {'accession_number':'0001018724-27-000001'}):
            record = json.loads(self.entry.reviewed_entry_json)
            record['evidence_refresh'][0].update(change)
            with self.assertRaises(CapexScopePolicyError):_validate_representation_records(record)

    def test_representation_audits_preserve_both_hash_types(self):
        import hashlib
        import base64
        from valuation_platform.normalization.capex_scope import _validate_representation_records
        responses = json.loads((Path(__file__).resolve().parents[1] /
            'fixtures/capex_index_responses.json').read_text())
        for e in POLICY.entries:
            if e.company_cik != 59478:
                continue
            record = json.loads(e.reviewed_entry_json)
            c = record['representation_correction']
            response = next(r for r in responses if r['source_url'] == c['source_url'])
            raw = base64.b64decode(response['response_body_base64'])
            # Preserve retrieved bodies, never recreate a response by compaction.
            self.assertEqual(hashlib.sha256(raw).hexdigest(), c['response_digest'])
            self.assertNotEqual(c['response_digest'], c['retained_digest'])
            _validate_representation_records(record, {c['source_url']: raw})
            with self.assertRaises(CapexScopePolicyError):
                _validate_representation_records(record,
                    {c['source_url']: c['retained_utf8_text'].encode('utf-8')})

    def test_wrong_representation_label_or_digest_rejected(self):
        from valuation_platform.normalization.capex_scope import _validate_representation_records
        e = next(e for e in POLICY.entries if e.company_cik == 59478)
        for key, value in (('retained_digest_type', 'sha256_sec_response_body_bytes'),
                           ('response_digest_type', 'parsed_json'),
                           ('retained_digest', '0' * 64), ('retained_utf8_text', '{}')):
            record = json.loads(e.reviewed_entry_json)
            record['representation_correction'][key] = value
            with self.assertRaises(CapexScopePolicyError): _validate_representation_records(record)
        record = json.loads(e.reviewed_entry_json)
        record['mandatory_artifacts'][0]['digest_type'] = 'parsed_json'
        with self.assertRaises(CapexScopePolicyError): _validate_representation_records(record)
