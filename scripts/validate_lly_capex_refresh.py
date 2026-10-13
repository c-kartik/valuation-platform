"""Offline, fixed-scope LLY refresh review; never a financial-policy bypass.

The record accepts refreshed report content for the stated review only. Existing
v1 attestations cannot represent it, so no historical input is populated here.
"""
from datetime import datetime
from decimal import Decimal
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from valuation_platform.analyst import capex_evidence_repair as repair
from valuation_platform.analyst import historical_inputs as h
from valuation_platform.normalization import capex_scope as policy
from valuation_platform.sec.filing_xbrl import parse_filing_xbrl_instance
from valuation_platform.sec.annual_period import resolve_annual_period, ResolvedAnnualPeriod
from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.tickers import SECCompanyIdentity

BASELINE = '6e9634c3b3c5c11228c3e1e3c207a848367e66d8'
RECORD = 'docs/evidence/lly-capex-refresh-review-v1.json'
REGISTRY = 'src/valuation_platform/normalization/capex_scope_registry.json'
VERSION = 'lly-capex-report-refresh-review-v1'
BLOCKER = ('V1 verification and output provenance require the immutable original '
           'artifact_digests, reviewed_evidence and reviewed_entry_json exactly. '
           'A different digest needs a separately designed provenance/schema '
           'treatment; no operational refresh or attestation substitution here.')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Report(HTMLParser):
    """Read submitted report cells separately from scripts/taxonomy popups."""
    def __init__(self):
        super().__init__(); self.depth = 0; self.active = False
        self.rows = []; self.row = None; self.cell = None; self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table':
            if not self.active and attrs.get('class') == 'report':
                self.active = True; self.depth = 1
            elif self.active: self.depth += 1
        if not self.active: return
        if tag == 'tr' and self.depth == 1: self.row = []
        if tag in ('td', 'th') and self.depth == 1:
            self.cell = dict(text=[], links=[])
        if tag == 'a' and self.cell is not None and attrs.get('onclick'):
            self.cell['links'].append(attrs['onclick'])

    def handle_data(self, data):
        if self.active:
            self.text.append(data)
            if self.cell is not None: self.cell['text'].append(data)

    def handle_endtag(self, tag):
        if not self.active: return
        if tag in ('td', 'th') and self.depth == 1 and self.cell is not None:
            if self.row is not None:
                self.row.append(dict(text=' '.join(''.join(self.cell['text']).split()),
                                     links=self.cell['links']))
            self.cell = None
        if tag == 'tr' and self.depth == 1 and self.row is not None:
            self.rows.append(self.row); self.row = None
        if tag == 'table':
            self.depth -= 1
            if not self.depth: self.active = False

    @property
    def normalized_text(self):
        return ' '.join(' '.join(self.text).split())


def parse_report(raw):
    p = Report(); p.feed(raw.decode('utf-8')); p.close()
    if not p.rows: raise h.InputError('Selected rendered report table absent')
    return p


def row(p, caption):
    rows = [r for r in p.rows if r and r[0]['text'] == caption]
    if len(rows) != 1: raise h.InputError('Unique exact report caption required: ' + caption)
    return rows[0]


def require(text, passage):
    if passage not in text: raise h.InputError('Reviewed passage not in exact refreshed report: ' + passage)
    return passage


def inspect_entry(entry, payload, accepted):
    """Independent table, note, instance and immutable-approval checks."""
    canonical = json.loads(entry.reviewed_entry_json)
    reports = []
    parsed = []
    for old in canonical['reviewed_evidence']:
        aa = [(i,a) for i,a in enumerate(payload['artifacts']) if a['source_url']==old['source_url']]
        if len(aa)!=1: raise h.InputError('One exact retained receipt required')
        i,a=aa[0]; raw=repair.body(a)
        if (a['accession']!=entry.accession_number or a['http_status']!=200
                or a['prior_expected_sha256']!=old['sha256'] or a['sha256']==old['sha256']):
            raise h.InputError('Exact old/new refresh binding differs')
        p=parse_report(raw); parsed.append(p)
        if 'Dec. 31, '+str(entry.annual_end.year) not in p.normalized_text:
            raise h.InputError('Refreshed report annual header differs')
        reports.append(dict(source_url=old['source_url'], artifact_type=old['report']['MenuCategory'],
            report=old['report'], historical_sha256=old['sha256'],
            historical_digest_type=old['digest_type'], historical_status='ORIGINAL_BODY_UNAVAILABLE_BYTE_EQUIVALENCE_UNESTABLISHED',
            refreshed_sha256=a['sha256'], representation=a['representation'],digest_type=a['digest_type'],
            byte_length=len(raw), receipt_path=repair.OUTPUT,receipt_locator='/artifacts/'+str(i),
            receipt_document_sha256=sha((ROOT/repair.OUTPUT).read_bytes()),
            retrieved_at_utc=a['retrieved_at_utc'],http_status=a['http_status'],refresh_history=a['refresh_history']))
    cash,account,ppe=parsed
    header=cash.rows[0][0]['text']; dates=[c['text'] for c in cash.rows[1]]
    if header!='Consolidated Statements of Cash Flows - USD ($) $ in Millions' or dates[0]!='Dec. 31, '+str(entry.annual_end.year):
        raise h.InputError('Selected consolidated USD-million current column differs')
    purchase=row(cash,'Purchases of property and equipment')
    if len(purchase)!=4 or 'defref_us-gaap_'+entry.concept not in ' '.join(purchase[0]['links']):
        raise h.InputError('Exact cash caption/concept binding differs')
    displayed=purchase[1]['text']
    if not (displayed.startswith('(') and displayed.endswith(')')):
        raise h.InputError('Reported investing cash outflow sign differs')
    magnitude=Decimal(displayed[1:-1].replace(',',''))*1000000
    if magnitude!=entry.expected_value: raise h.InputError('Refreshed current cash amount contradicts approval')
    section=row(cash,'Cash Flows from Investing Activities')
    if cash.rows.index(section)>=cash.rows.index(purchase):raise h.InputError('Purchase not in investing section')
    acquisition_caption=next(c['text'] for r in cash.rows for c in r[:1] if c['text'].startswith('Cash paid for acquisitions, net of cash acquired'))
    acquisitions=row(cash,acquisition_caption); iprd=row(cash,'Purchases of in-process research and development')
    policy_passage=require(account.normalized_text,'The accompanying consolidated financial statements include Eli Lilly and Company and all subsidiaries')
    elimination=require(account.normalized_text,'All intercompany balances and transactions have been eliminated.')
    iprd_passage=next(s for s in ('Acquired IPR&D expense includes the initial costs','Acquired IPR&D and development milestones include the initial costs','Acquired IPR&D includes the initial costs') if s in account.normalized_text)
    nonalternative=require(account.normalized_text,'that do not have an alternative future use')
    cost=require(ppe.normalized_text,'Property and equipment is stated on the basis of cost.')
    physical=[require(ppe.normalized_text,s) for s in ('Land','Buildings','Equipment','Construction in progress')]
    long_lived=next(s for s in (
        'Long-lived assets consist of property and equipment, net, operating lease assets, and certain other noncurrent assets.',
        'Long-lived assets consist of property and equipment, net, operating lease assets, and unamortized computer software costs.') if s in ppe.normalized_text)
    interest=(next((s for s in [f'Capitalized interest costs were not material for the years ended December 31, {entry.annual_end.year}, {entry.annual_end.year-1}, and {entry.annual_end.year-2}.'] if s in ppe.normalized_text),None))
    if entry.annual_end.year<2025 and interest is None:raise h.InputError('Expected capitalized-interest passage missing')
    if entry.annual_end.year==2025 and interest is not None:raise h.InputError('2025 reviewed interest limitation differs')
    # Instance and all non-report requirements retain their original verified bytes.
    raw=accepted[entry.instance_url,entry.instance_digest][0]
    stamp=datetime.fromisoformat(accepted[entry.instance_url,entry.instance_digest][1]['retrieved_at_utc'])
    company=SECCompanyIdentity('LLY',entry.company_cik,f'{entry.company_cik:010d}','Eli Lilly',entry.instance_url,stamp)
    filing=SECFiling(entry.accession_number,entry.form,entry.filed,entry.report_date,entry.primary_document)
    x=parse_filing_xbrl_instance(raw,company=company,filing=filing,source_url=entry.instance_url,retrieved_at=stamp)
    annual=resolve_annual_period(x)
    if not isinstance(annual,ResolvedAnnualPeriod) or (annual.start,annual.end)!=(entry.annual_start,entry.annual_end):
        raise h.InputError('Authoritative annual DEI differs')
    ctx={c.context_id:c for c in x.contexts}
    facts=[]
    for ordinal,f in enumerate(x.facts):
        if (f.namespace,f.concept,f.start,f.end,f.dimensions)==(entry.namespace,entry.concept,entry.annual_start,entry.annual_end,()):
            c=ctx[f.context_id]
            if (c.entity_identifier_scheme!='http://www.sec.gov/CIK' or int(c.entity_identifier)!=entry.company_cik
                    or not policy._usd(f) or f.is_nil or f.numeric_value!=entry.expected_value):
                raise h.InputError('Refreshed review operand differs from immutable approval')
            facts.append(dict(ordinal=ordinal,context_id=f.context_id,unit_ref=f.unit_ref,raw_value=f.raw_value,
                              numeric_value=str(f.numeric_value),decimals=f.decimals,dimensions=[]))
    expected=[dict(ordinal=o['ordinal'],context_id=o['context_id'],unit_ref=o['unit_ref'],raw_value=o['raw_value'],
                  numeric_value=o['numeric_value'],decimals=o['decimals'],dimensions=[]) for o in canonical['operand_occurrences']]
    if facts!=expected:raise h.InputError('Exact approved operand/occurrence/precision differs')
    remaining=[dict(source_url=u,sha256=d,source=accepted[u,d][1]) for u,d in entry.artifact_digests
               if u not in {r['source_url'] for r in reports}]
    if len(remaining)!=7:raise h.InputError('Seven unchanged non-report requirements expected')
    reports[0]['supports']=['CURRENT_CASH_AMOUNT','CONSOLIDATED_INVESTING_SCOPE','ACQUISITION_IPRD_SEPARATION','REPORTED_NOT_RESIDUAL']
    reports[1]['supports']=['CONSOLIDATED_SCOPE','ACQUIRED_IPRD_SEPARATION']
    reports[2]['supports']=['PPE_PHYSICAL_ASSET_SCOPE','BROADER_LEASE_SOFTWARE_NOT_SUBSTITUTED','NO_INTEREST_ADJUSTMENT']
    return dict(identity=dict(cik=entry.company_cik,accession=entry.accession_number,form=entry.form,
        annual_start=str(entry.annual_start),annual_end=str(entry.annual_end),filed=str(entry.filed),primary_document=entry.primary_document),
        financial_policy=dict(policy_id=policy.CAPEX_SCOPE_POLICY_ID,version='1',entry_sha256=sha(entry.reviewed_entry_json.encode())),
        reports=reports, unchanged_requirements=remaining,
        checks=dict(supported=['CURRENT_CASH_AMOUNT','AUTHORITATIVE_ANNUAL_PERIOD','EXACT_OPERAND_OCCURRENCES',
            'CONSOLIDATED_INVESTING_SCOPE','PPE_PHYSICAL_ASSET_SCOPE','ACQUISITION_IPRD_SEPARATION',
            'NO_NONCASH_LEASE_PROCEEDS_INCENTIVE_OR_INTEREST_ADJUSTMENT'],contradicted=[],
            unverified=['HISTORICAL_REPORT_BYTE_EQUIVALENCE','COMPLETE_INCENTIVE_OR_NONCASH_ALLOCATIONS',
                        'COMPLETE_CAPITALIZED_INTEREST_AMOUNT'],
            operationally_unsatisfied=['IMMUTABLE_V1_REPORT_DIGEST_ATTESTATION']),
        observations=dict(header=header,current_column=dates[0],cash_caption=purchase[0]['text'],displayed_outflow=displayed,
            display_unit='USD millions',display_decimals=0 if entry.annual_end.year==2025 else 1,
            approved_magnitude_usd=str(magnitude),operand_occurrences=facts,acquisition_row=acquisitions,iprd_row=iprd,
            consolidation_passage=policy_passage,elimination_passage=elimination,iprd_passage=iprd_passage,
            nonalternative_passage=nonalternative,cost_passage=cost,physical_components=physical,
            broader_long_lived_passage=long_lived,capitalized_interest_passage=interest),
        content_review='SUPPORTED_EXISTING_FINANCIAL_SCOPE',operational_acceptance='BLOCKED_SCHEMA_TREATMENT_REQUIRED',
        blocker=BLOCKER)


def replay_review():
    payload=json.loads((ROOT/repair.OUTPUT).read_text())
    accepted=repair.capex.artifacts()
    accepted.update(repair.verify(payload))
    entries=[e for e in policy.CAPEX_SCOPE_EQUIVALENCE_POLICY.entries if e.company_cik==59478]
    if len(entries)!=5:raise h.InputError('Fixed five LLY entries differ')
    return [inspect_entry(e,payload,accepted) for e in entries]


def validate(record):
    if record['version']!=VERSION or record['baseline_revision']!=BASELINE:
        raise h.InputError('Unsupported immutable refresh-review identity')
    if record['registry_sha256']!=sha((ROOT/REGISTRY).read_bytes()):raise h.InputError('Frozen registry differs')
    if record['receipt_document_sha256']!=sha((ROOT/repair.OUTPUT).read_bytes()):raise h.InputError('Receipt history differs')
    if (record['requests']!=0 or record['activated_entries']!=0 or record['content_supported_entries']!=5
            or record['historical_search']['matches'] or record['coverage']!=dict(DIRECT=145,CURATED=15,EVIDENCE_GAP=5,UNAPPROVED_SCOPE=34)):
        raise h.InputError('Review cannot imply operational acceptance/coverage or recovered originals')
    if record['historical_byte_equivalence']!='UNESTABLISHED_ORIGINAL_BODIES_UNAVAILABLE' or record['renderer_only_change']!='NOT_ESTABLISHED':
        raise h.InputError('Unavailable originals cannot imply byte or renderer equivalence')
    if record['entries']!=replay_review():raise h.InputError('Review is not independently reproducible from exact reports/operands')
    files=[p for p in subprocess.check_output(['git','ls-tree','-r','--name-only',BASELINE],cwd=ROOT,text=True).splitlines() if p.endswith('.json')]
    sources=[dict(path=p,sha256=sha(subprocess.check_output(['git','show',BASELINE+':'+p],cwd=ROOT))) for p in files]
    if record['historical_search_sources']!=sources or record['historical_search']['searched_json_files']!=len(files):
        raise h.InputError('Historical search must bind the exact committed source snapshot')
    ledger=(ROOT/'docs/repaired-capex-ledger.json').read_bytes()
    if sha(ledger)!=record['unchanged_coverage_ledger_sha256']:raise h.InputError('Prior preparation output changed')
    return record


if __name__=='__main__':
    x=validate(json.loads((ROOT/RECORD).read_text()))
    print(json.dumps(dict(reviewed_artifacts=15,content_supported_entries=5,activated_entries=0,
                         blocked_entries=5,requests=0,coverage=x['coverage']),sort_keys=True))
