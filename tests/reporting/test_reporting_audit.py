"""Checks for the independent audit reader; does not use preparation selection."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('audit_reporting',ROOT/'scripts/audit_reporting.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
XML=b'''<xbrl xmlns="http://www.xbrl.org/2003/instance" xmlns:us-gaap="http://fasb.org/us-gaap/2026" xmlns:iso4217="http://www.xbrl.org/2003/iso4217" xmlns:xbrldi="http://xbrl.org/2006/xbrldi" xmlns:goog="http://www.google.com/20260930"><context id="whole"><entity><identifier scheme="SEC">0001652044</identifier></entity><period><startDate>2026-01-01</startDate><endDate>2026-03-31</endDate></period></context><context id="segment"><entity><identifier scheme="SEC">0001652044</identifier><segment><xbrldi:explicitMember dimension="us-gaap:StatementBusinessSegmentsAxis">goog:GoogleCloudMember</xbrldi:explicitMember></segment></entity><period><startDate>2026-01-01</startDate><endDate>2026-03-31</endDate></period></context><unit id="USD"><measure>iso4217:USD</measure></unit><us-gaap:Revenues contextRef="whole" unitRef="USD" decimals="-6">100000000</us-gaap:Revenues><us-gaap:Revenues contextRef="segment" unitRef="USD" decimals="-6">20000000</us-gaap:Revenues></xbrl>'''

class AuditReaderTests(unittest.TestCase):
    def test_exact_context_currency_entity_and_amount(self):
        facts=audit.raw_instance(XML)
        op={'concept':'us-gaap:Revenues','value':100000000,'start':'2026-01-01','end':'2026-03-31','accession':'test'}
        self.assertEqual(audit.check_fact(facts,op,1652044)['context_ids'],['whole'])
        for wrong in [dict(op,value=20000000),dict(op,end='2026-06-30')]:
            with self.assertRaises(audit.AuditError):audit.check_fact(facts,wrong,1652044)
        with self.assertRaises(audit.AuditError):audit.check_fact(facts,op,320193)
        with self.assertRaises(audit.AuditError):audit.check_fact(audit.raw_instance(XML.replace(b'iso4217:USD',b'iso4217:EUR')),op,1652044)

    def test_dimensions_never_substitute_for_consolidated(self):
        op={'concept':'Revenues','value':20000000,'start':'2026-01-01','end':'2026-03-31','accession':'test'}
        facts=audit.raw_instance(XML)
        with self.assertRaises(audit.AuditError):audit.check_fact(facts,op,1652044)
        dims=[('{http://fasb.org/us-gaap/2026}StatementBusinessSegmentsAxis','{http://www.google.com/20260930}GoogleCloudMember')]
        self.assertEqual(audit.check_fact(facts,op,1652044,'http://fasb.org/us-gaap/2026',dims)['context_ids'],['segment'])

    def test_unsafe_xml_rejected(self):
        with self.assertRaises(audit.AuditError):audit.raw_instance(b'<!DOCTYPE xbrl>'+XML)
