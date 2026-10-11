"""Disjoint CVX v2 publication and inherited semantic-selection adversaries."""
from dataclasses import replace, FrozenInstanceError
from decimal import Decimal
import base64
import gzip
import hashlib
import json
from pathlib import Path
import unittest

from tests.normalization import test_capex_scope as v1_tests
from tests.normalization.test_capex_scope import fixture, INVENTORY, NOW
from valuation_platform.normalization import *
from valuation_platform.sec import SelectedFactObservations
from valuation_platform.normalization.capex_scope import (
    CAPEX_SCOPE_EQUIVALENCE_POLICY as V1, CAPEX_SCOPE_V2_POLICY as V2,
    CAPEX_SCOPE_POLICY_CATALOG, CapexScopePolicyError, VerifiedCapexArtifacts,
    apply_curated_capex_scope_policy, published_capex_scope_entry_for,
    verify_capex_artifacts, validate_capex_scope_provenance,
)


class CVXSelectionTests(unittest.TestCase):
    # These are coherent parsed selection fixtures with synthetic attestations;
    # raw-body verification is exercised separately and in targeted validation.
    def setUp(self):
        self.entry = V2.entries[0]
        row = next(r for r in INVENTORY if r['filing']['accession_number'] == self.entry.accession_number)
        self.bucket, self.instance, self.period, _ = fixture(row)
        self.artifacts = VerifiedCapexArtifacts(self.entry.accession_number, self.entry.artifact_digests)
        self.missing = MissingHistoricalMetric(FinancialMetric.CAPEX,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION, CAPEX_POLICY.candidates)
        self.fact = next(f for f in self.instance.facts if f.concept == self.entry.concept)

    only = v1_tests.CapexScopeTests.only
    direct = v1_tests.CapexScopeTests.direct

    def resolve(self, instance=None, direct=None, **kwargs):
        return apply_curated_capex_scope_policy(kwargs.get('bucket', self.bucket),
            direct or self.missing, self.entry.company_cik, kwargs.get('period', self.period),
            instance or self.instance, kwargs.get('artifacts', self.artifacts), policy=V2)

    test_three_same_context_occurrences = v1_tests.CapexScopeTests.test_three_same_context_occurrences
    test_equivalent_context_unit_and_decimal_representations = v1_tests.CapexScopeTests.test_equivalent_context_unit_and_decimal_representations
    test_conflict_and_changed_negative_values = v1_tests.CapexScopeTests.test_conflict_and_changed_negative_values
    test_precedence_equal_conflict_ambiguity = v1_tests.CapexScopeTests.test_precedence_equal_conflict_ambiguity
    test_wrong_concept_namespace_and_no_facts = v1_tests.CapexScopeTests.test_wrong_concept_namespace_and_no_facts
    test_wrong_entity_period_dimension_excluded = v1_tests.CapexScopeTests.test_wrong_entity_period_dimension_excluded
    test_non_usd_and_nil = v1_tests.CapexScopeTests.test_non_usd_and_nil
    test_structural_errors = v1_tests.CapexScopeTests.test_structural_errors
    test_future_amended_incomplete = v1_tests.CapexScopeTests.test_future_amended_incomplete

    def test_catalog_immutable_exact_publication(self):
        self.assertEqual((len(V1.entries), len(V2.entries)), (10, 5))
        with self.assertRaises(FrozenInstanceError): V2.version = '3'
        for kw in ({'version':'1'}, {'version':'3'}, {'entries':V1.entries}, {'entries':V2.entries[::-1]}):
            with self.assertRaises(CapexScopePolicyError): replace(V2, **kw)
        for kw in ({'unit':'EUR'}, {'company_cik':True}, {'reviewed_evidence':()},
                   {'expected_value':Decimal(1)}, {'reviewed_entry_json':'{}'}, {'support':(1,)}):
            with self.assertRaises(CapexScopePolicyError): replace(self.entry, **kw)
        with self.assertRaises(CapexScopePolicyError):
            replace(CAPEX_SCOPE_POLICY_CATALOG, policies=(V2,V2))
        matrix = json.loads(Path('docs/capex-cvx-scope-evidence-matrix.json').read_text())
        for e, r in zip(V1.entries, matrix['existing_v1_regression_manifest']):
            self.assertEqual(hashlib.sha256(e.reviewed_entry_json.encode()).hexdigest(), r['canonical_reviewed_entry_sha256'])

    def test_57_identity_five_ten_42_regression(self):
        counts = {'1':0,'2':0,'missing':0}
        for row in INVENTORY:
            b,x,p,a = fixture(row)
            entry = published_capex_scope_entry_for(x.company.cik,b.filing,p)
            bundle = VerifiedCapexArtifacts(entry.accession_number, entry.artifact_digests) if entry else None
            selected = SelectedFactObservations(x.company,'company-facts',NOW,(b,),())
            h = normalize_annual_financials(selected,policies=(CAPEX_POLICY,),
                filing_xbrl=(x,),annual_periods=(p,),capex_artifacts=(bundle,) if bundle else ())
            result = h.annual[0].metrics[0]
            if entry:
                self.assertIsInstance(result,NormalizedHistoricalValue)
                self.assertEqual(result.value,entry.expected_value)
                counts[result.policy_provenance.policy_version] += 1
                validate_capex_scope_provenance(result.policy_provenance)
            else:
                self.assertIsInstance(result,MissingHistoricalMetric)
                counts['missing'] += 1
        self.assertEqual(counts, {'1':10,'2':5,'missing':42})

    def test_serialization_and_unknown_version_rejection(self):
        selected = SelectedFactObservations(self.instance.company,'company-facts',NOW,(self.bucket,),())
        h = normalize_annual_financials(selected,filing_xbrl=(self.instance,),
            annual_periods=(self.period,),capex_artifacts=(self.artifacts,))
        out = assemble_standardized_annual_history(h,normalize_annual_balance_sheets(selected))
        payload = json.loads(json.dumps(standardized_history_to_dict(out)))
        m = next(m for m in payload['annual'][0]['measures'] if m['measure']=='capex')
        self.assertEqual(m['policy']['version'],'2')
        self.assertEqual(len(m['policy']['reviewed_evidence']),7)
        p = self.resolve().policy_provenance
        for bad in (replace(p,policy_version='1'),replace(p,policy_version='3'),
                    replace(p,capex_scope=replace(p.capex_scope,confirming_original_ordinals=(999,)))):
            with self.assertRaises(CapexScopePolicyError): validate_capex_scope_provenance(bad)

    def test_raw_evidence_manifest_and_tamper(self):
        records = json.loads(Path('docs/evidence/cvx-capex-perimeter-response-bodies.json').read_text())['artifacts']
        bodies = {a['source_url']:gzip.decompress(base64.b64decode(a['response_body_gzip_base64'])) for a in records}
        for entry in V2.entries:
            r = json.loads(entry.reviewed_entry_json)
            self.assertTrue(all(a['digest_type']=='sha256_sec_response_body_bytes' for a in r['mandatory_artifacts']))
            self.assertFalse(any(u.endswith('/index.json') for u,_ in entry.artifact_digests))
            for a in r['reviewed_evidence']:
                self.assertEqual(hashlib.sha256(bodies[a['source_url']]).hexdigest(),a['sha256'])
            with self.assertRaises(CapexScopePolicyError): verify_capex_artifacts(entry,{},self.instance)
            with self.assertRaises(CapexScopePolicyError): verify_capex_artifacts(entry,
                {u:body+b' ' for u,body in bodies.items()},self.instance)

    def test_nil_contradiction_and_dimensioned_collision(self):
        from valuation_platform.sec import FilingXBRLDimension, FilingXBRLQName
        with self.assertRaises(CapexScopePolicyError): self.resolve(self.only(is_nil=True))
        with self.assertRaises(CapexScopePolicyError): self.resolve(self.only(raw_value='9'))
        c = next(c for c in self.instance.contexts if c.context_id == self.fact.context_id)
        c = replace(c, context_id='dim', dimensions=(FilingXBRLDimension(
            FilingXBRLQName('issuer','Axis'),FilingXBRLQName('issuer','Member'),None),))
        f = replace(self.fact,context_id='dim',dimensions=c.dimensions)
        nil = replace(f,is_nil=True,raw_value=None,numeric_value=None)
        result = self.resolve(replace(self.instance, contexts=(*self.instance.contexts,c),
            facts=(self.fact,f,nil)))
        self.assertEqual(result.value,self.entry.expected_value)
        self.assertEqual(len(result.policy_provenance.filing_xbrl_evidence),1)
