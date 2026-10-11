"""Visa v3 publication, retained-byte integrity and semantic adversaries."""
from dataclasses import replace, FrozenInstanceError
from decimal import Decimal
import base64
import gzip
import hashlib
import json
from pathlib import Path
import unittest

from tests.normalization import test_capex_scope as v1
from tests.normalization import test_capex_scope_v2 as v2
from valuation_platform.normalization import *
from valuation_platform.normalization.capex_scope import (
    CAPEX_SCOPE_V3_POLICY as V3, CAPEX_SCOPE_POLICY_CATALOG,
    CapexScopePolicyError, VerifiedCapexArtifacts, apply_curated_capex_scope_policy,
    verify_capex_artifacts, validate_capex_scope_provenance,
)
from valuation_platform.sec import SelectedFactObservations, parse_filing_xbrl_instance, resolve_annual_period


def retained_bodies():
    return {a['source_url']:gzip.decompress(base64.b64decode(a['response_body_gzip_base64']))
            for a in json.loads(Path('docs/evidence/visa-capex-response-bodies.json').read_text())['artifacts']}


class VisaSelectionTests(unittest.TestCase):
    def setUp(self):
        self.entry=V3.entries[0]
        row=next(r for r in v1.INVENTORY if r['filing']['accession_number']==self.entry.accession_number)
        self.bucket,self.instance,self.period,_=v1.fixture(row)
        self.artifacts=VerifiedCapexArtifacts(self.entry.accession_number,self.entry.artifact_digests)
        self.missing=MissingHistoricalMetric(FinancialMetric.CAPEX,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,CAPEX_POLICY.candidates)
        self.fact=next(f for f in self.instance.facts if f.concept==self.entry.concept)

    only=v1.CapexScopeTests.only
    direct=v1.CapexScopeTests.direct

    def resolve(self,instance=None,direct=None,**kwargs):
        return apply_curated_capex_scope_policy(kwargs.get('bucket',self.bucket),direct or self.missing,
            self.entry.company_cik,kwargs.get('period',self.period),instance or self.instance,
            kwargs.get('artifacts',self.artifacts),policy=V3)

    # Selection fixtures carry synthetic attestations; real byte verification
    # below separately proves no modified instance can satisfy published hashes.
    test_three_same_context_occurrences=v1.CapexScopeTests.test_three_same_context_occurrences
    test_equivalent_context_unit_and_decimal_representations=v1.CapexScopeTests.test_equivalent_context_unit_and_decimal_representations
    test_conflict_and_changed_negative_values=v1.CapexScopeTests.test_conflict_and_changed_negative_values
    test_precedence_equal_conflict_ambiguity=v1.CapexScopeTests.test_precedence_equal_conflict_ambiguity
    test_wrong_concept_namespace_and_no_facts=v1.CapexScopeTests.test_wrong_concept_namespace_and_no_facts
    test_wrong_entity_period_dimension_excluded=v1.CapexScopeTests.test_wrong_entity_period_dimension_excluded
    test_non_usd_and_nil=v1.CapexScopeTests.test_non_usd_and_nil
    test_structural_errors=v1.CapexScopeTests.test_structural_errors
    test_future_amended_incomplete=v1.CapexScopeTests.test_future_amended_incomplete
    test_nil_contradiction_and_dimensioned_collision=v2.CVXSelectionTests.test_nil_contradiction_and_dimensioned_collision
    test_57_identity_five_fifteen_37_regression=v2.CVXSelectionTests.test_57_identity_five_ten_42_regression

    def test_immutable_publication_and_old_fingerprints(self):
        self.assertEqual(tuple((p.version,len(p.entries)) for p in CAPEX_SCOPE_POLICY_CATALOG.policies),
                         (('1',10),('2',5),('3',5)))
        with self.assertRaises(FrozenInstanceError):V3.version='4'
        for kwargs in ({'version':'2'},{'entries':V3.entries[::-1]},{'entries':V3.entries[:4]}):
            with self.assertRaises(CapexScopePolicyError):replace(V3,**kwargs)
        for kwargs in ({'company_cik':True},{'expected_value':Decimal(1)},{'unit':'EUR'},
                       {'reviewed_evidence':()},{'reviewed_entry_json':'{}'},{'support':(1,)}):
            with self.assertRaises(CapexScopePolicyError):replace(self.entry,**kwargs)
        with self.assertRaises(CapexScopePolicyError):replace(CAPEX_SCOPE_POLICY_CATALOG,policies=(V3,V3))
        matrix=json.loads(Path('docs/capex-visa-scope-evidence-matrix.json').read_text())
        for record in matrix['existing_curated_regression_manifest']:
            policy=next(p for p in CAPEX_SCOPE_POLICY_CATALOG.policies if p.version==record['policy_version'])
            entry=next(e for e in policy.entries if e.accession_number==record['filing']['accession_number'])
            self.assertEqual(hashlib.sha256(entry.reviewed_entry_json.encode()).hexdigest(),record['canonical_reviewed_entry_sha256'])

    def test_all_five_real_instances_and_artifacts(self):
        bodies=retained_bodies()
        for entry in V3.entries:
            row=next(r for r in v1.INVENTORY if r['filing']['accession_number']==entry.accession_number)
            bucket,x,_,_=v1.fixture(row)
            x=parse_filing_xbrl_instance(bodies[entry.instance_url],company=x.company,filing=x.filing,
                                       source_url=entry.instance_url,retrieved_at=v1.NOW)
            period=resolve_annual_period(x)
            bundle=verify_capex_artifacts(entry,bodies,x)
            value=apply_curated_capex_scope_policy(bucket,self.missing,entry.company_cik,period,x,bundle,policy=V3)
            self.assertEqual(value.value,entry.expected_value)
            self.assertEqual(value.policy_provenance.policy_version,'3')
            self.assertEqual(len(value.policy_provenance.reviewed_evidence),7)
            self.assertEqual(len(value.policy_provenance.capex_scope.verified_artifact_digests),13)
            validate_capex_scope_provenance(value.policy_provenance)

    def test_missing_tampered_wrong_representation_and_parsed_source(self):
        bodies=retained_bodies();entry=self.entry
        x=parse_filing_xbrl_instance(bodies[entry.instance_url],company=self.instance.company,
            filing=self.instance.filing,source_url=entry.instance_url,retrieved_at=v1.NOW)
        for url,_ in entry.artifact_digests:
            missing={u:b for u,b in bodies.items() if u!=url}
            with self.assertRaises(CapexScopePolicyError):verify_capex_artifacts(entry,missing,x)
            changed=dict(bodies);changed[url]+=b' '
            with self.assertRaises(CapexScopePolicyError):verify_capex_artifacts(entry,changed,x)
        with self.assertRaises(CapexScopePolicyError):verify_capex_artifacts(entry,bodies,self.instance)
        record=json.loads(entry.reviewed_entry_json)
        record['mandatory_artifacts'][0]['digest_type']='sha256_parsed_json'
        with self.assertRaises(CapexScopePolicyError):replace(entry,reviewed_entry_json=json.dumps(record))
        with self.assertRaises(CapexScopePolicyError):self.resolve(artifacts=replace(self.artifacts,accession_number='wrong'))

    def test_serialization_multiplicity_and_supporting_precedence(self):
        x=replace(self.instance,facts=(self.fact,replace(self.fact,raw_value=str(self.entry.expected_value)+'.00',decimals='-2'),self.fact))
        selected=SelectedFactObservations(x.company,'company-facts',v1.NOW,(self.bucket,),())
        h=normalize_annual_financials(selected,filing_xbrl=(x,),annual_periods=(self.period,),capex_artifacts=(self.artifacts,))
        output=assemble_standardized_annual_history(h,normalize_annual_balance_sheets(selected))
        payload=json.loads(json.dumps(standardized_history_to_dict(output)))
        self.assertEqual(payload['schema_version'],'5')
        capex=next(v for v in payload['annual'][0]['measures'] if v['measure']=='capex')
        self.assertEqual(capex['policy']['version'],'3')
        p=self.resolve(x).policy_provenance
        self.assertEqual(p.capex_scope.confirming_original_ordinals,(0,1,2))
        self.assertEqual(tuple(e.occurrence_ordinal for e in p.filing_xbrl_evidence),(1,2,3))
        equal=self.resolve(x,self.direct(self.entry.expected_value))
        self.assertEqual(equal.chosen_source.concept,CAPEX_POLICY.candidates[0].name)
        validate_capex_scope_provenance(equal.policy_provenance)
        for change in ({'policy_version':'4'},{'policy_version':'2'},
                       {'filing_xbrl_evidence':p.filing_xbrl_evidence[::-1]},
                       {'capex_scope':replace(p.capex_scope,confirming_original_ordinals=(0,))}):
            with self.assertRaises((CapexScopePolicyError,ValueError)):
                validate_capex_scope_provenance(replace(p,**change))

    def test_nonfinite_and_broken_links(self):
        for bad in ('NaN','Infinity','not-a-number'):
            with self.assertRaises(CapexScopePolicyError):self.resolve(self.only(raw_value=bad,numeric_value=Decimal('NaN')))
        with self.assertRaises(CapexScopePolicyError):self.resolve(self.only(unit_ref='missing'))
        with self.assertRaises(CapexScopePolicyError):self.resolve(self.only(accession_number='wrong'))
