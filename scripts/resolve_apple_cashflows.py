"""Replay the manually approved Apple cash-flow treatments, offline.

New issuer mappings are reviewed data, never guessed from a ticker or a residual.
This separate resolution record cannot overwrite accepted history or forecasts.
"""
import argparse
from copy import copy
import csv
from datetime import date
from decimal import Decimal
from fractions import Fraction
import hashlib
from io import StringIO
import json
from pathlib import Path

from calculate_historical_fcff_from_filings import RetainedFiling
import test_operating_fcff_from_filings as operating
from valuation_platform.analyst import statement_delivery as statements
from valuation_platform.review.cfo_history import adopted_window
from valuation_platform.review.operating_fcff import amount, serialized
from valuation_platform.valuation.consumer import ANCHORS, load_revenue_anchor

ROOT = Path(__file__).resolve().parents[1]
FOLDER = Path('docs/company-resolutions/AAPL')
SOURCE_MAP = FOLDER / 'source-map.json'
DECISIONS = FOLDER / 'decisions.json'
OUTPUT = FOLDER / 'results.json'
CSV_OUTPUT = FOLDER / 'results.csv'
APPROVED_IDS = ('AAPL-FCFE-001', 'AAPL-FCFE-002', 'AAPL-FCFF-001', 'AAPL-TAX-001')
DEBT_CAPTIONS = {
    'Proceeds from issuance of term debt, net', 'Repayments of term debt',
    'Proceeds from/(Repayments of) commercial paper, net',
}
OWNER_CAPTIONS = {
    'Proceeds from issuance of common stock',
    'Payments for taxes related to net share settlement of equity awards',
    'Repurchases of common stock',
}
CLASSIFICATIONS = {
    'COMMON_EQUITY_OR_OTHER_OWNER_CASH', 'DIVIDENDS_NOT_NET_BORROWING',
    'DEBT_FUNDING_OR_PRINCIPAL', 'OTHER_FINANCING_EXCLUDED', 'FINANCING_TOTAL',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classified_cash(rows):
    """Sum identified financing; exact closure never certifies Other's content."""
    if not rows:
        raise ValueError('Explicit full financing population required')
    keys = [(r['table'], r['row'], r['column'], r['context_id']) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate financing source cell')
    totals, net, cash_sum, unknown = [], Fraction(), Fraction(), []
    for row in rows:
        role, caption = row['classification'], row['caption']
        cash = amount(row['signed_cash_usd'])
        if role not in CLASSIFICATIONS:
            raise ValueError('Unreviewed financing classification')
        included = row['included_in_net_borrowing']
        if type(included) is not bool or included != (role == 'DEBT_FUNDING_OR_PRINCIPAL'):
            raise ValueError('Financing inclusion conflicts with reviewed role')
        if (caption in DEBT_CAPTIONS) != included:
            raise ValueError('Reviewed Apple debt caption/role mismatch')
        if caption in OWNER_CAPTIONS and role != 'COMMON_EQUITY_OR_OTHER_OWNER_CASH':
            raise ValueError('Owner cash must not become borrowing')
        if role == 'FINANCING_TOTAL':
            totals.append(cash)
            continue
        cash_sum += cash
        if included:
            net += cash
        if role == 'OTHER_FINANCING_EXCLUDED':
            unknown.append({'caption': caption, 'amount_usd': str(cash),
                            'classification': 'UNALLOCATED_NOT_ASSUMED_ZERO',
                            'source_cell': {k:row[k] for k in ('table','row','column','context_id')}})
    if len(totals) != 1 or totals[0] != cash_sum:
        raise ValueError('Complete financing statement does not reconcile')
    if len([r for r in rows if r['included_in_net_borrowing']]) != 3:
        raise ValueError('Exactly three separately disclosed debt cash rows required')
    if len(unknown) != 1:
        raise ValueError('Reviewed explicit Other row required, including a disclosed zero')
    return {'net_borrowing': serialized(net), 'financing_cash_total': serialized(cash_sum),
            'statement_difference_usd': '0', 'unknown_components': unknown,
            'complete_financing_classification': False}


def verify_cell(filing, target, mapping):
    """Match selected row, period, USD inline value, instance and displayed sign."""
    selector = copy(filing)
    # The later comparative has the source accession but the target duration.
    selector.period = type(filing.period)(target['cik'], filing.period.accession,
        date.fromisoformat(target['annual_start']), date.fromisoformat(target['annual_end']))
    selector.statement_tables = getattr(filing, 'statement_tables', None) or statements.parse(
        {'body': filing.primary.artifact.body}, improved=True)
    table = selector.statement_tables[mapping['table']]
    row = table[mapping['row']]
    if not row or row[0]['text'].strip() != mapping['caption']:
        raise ValueError('Reviewed financing caption moved or changed; review new source')
    point = operating.table_point(selector, target, mapping, mapping['concept'],
        mapping['namespace'], {mapping['context_id']})
    if point['value'] != mapping['raw_value_usd'] or any(o['dimensions'] for o in point['occurrences']):
        raise ValueError('Financing source amount or dimensions changed')
    if not any(o['xml_id'] == mapping['primary_xml_id'] for o in point['occurrences']):
        raise ValueError('Primary financing cell identity changed')
    sign = mapping['cash_sign']
    if type(sign) is not int or sign not in (-1, 1):
        raise ValueError('Explicit source-to-cash sign required')
    if amount(point['value']) * sign != amount(mapping['signed_cash_usd']):
        raise ValueError('Cash sign/amount disagrees with source')
    cell = row[mapping['column']]
    observations = [f for f in cell['facts'] if f['attrs'].get('id') == mapping['primary_xml_id']]
    if len(observations) != 1:
        raise ValueError('Unique selected inline financing observation required')
    observed = observations[0]
    from prepare_standard_review_batch import cfo
    display = cfo.displayed(cell['text'], Decimal(0)) * Decimal(10) ** int(observed['attrs'].get('scale','0'))
    if amount(str(display)) != amount(mapping['signed_cash_usd']):
        raise ValueError('Displayed financial cash sign differs from mapping')
    return dict(mapping, source=point)


def full_financing(filing, target, mappings):
    bound = [verify_cell(filing, target, m) for m in mappings]
    table_id = {m['table'] for m in mappings}
    if len(table_id) != 1:
        raise ValueError('One complete reviewed financing table required')
    table = statements.parse({'body':filing.primary.artifact.body}, improved=True)[next(iter(table_id))]
    first, last = min(m['row'] for m in mappings), max(m['row'] for m in mappings)
    selected = {(m['row'],m['column'],m['context_id']) for m in mappings}
    contexts = {m['context_id'] for m in mappings}
    actual = {(ri,ci,f['attrs']['contextref']) for ri in range(first,last+1)
              for ci,cell in enumerate(table[ri]) for f in cell['facts']
              if f['attrs'].get('contextref') in contexts}
    if actual != selected:
        raise ValueError('Financing map omits or duplicates a current-period source cell')
    return bound, classified_cash(bound)


def bridge_mapping(term):
    r = term['row']; f = r['primary_fact']; obs = r['instance_observations']
    values = {x['value_usd'] for x in obs}
    if len(values) != 1:
        raise ValueError('Competing comparative financing populations')
    raw = next(iter(values)); sign = amount(r['value_usd']) / amount(raw) if amount(raw) else Fraction(1)
    if sign not in (-1,1):
        raise ValueError('Invalid comparative sign')
    return dict(table=r['table'],row=r['row'],column=f['cell'],caption=r['caption'],
                concept=f['concept'].split(':')[-1],namespace=obs[0]['namespace'],
                context_id=f['context_id'],primary_xml_id=f['xml_id'],raw_value_usd=raw,
                signed_cash_usd=r['value_usd'],cash_sign=int(sign))


def presentation_bridge(filings, source_map):
    bridge = source_map['equity_presentation_bridge']
    bound = []
    for side in ('left_terms','right_terms'):
        points = []
        for term in bridge[side]:
            source_year = int(term['source_filing_identity']['annual_end'][:4])
            filing = filings[source_year]
            if filing.source_identity != term['source_filing_identity']:
                raise ValueError('Comparative source filing identity mismatch')
            point = verify_cell(filing, term['target_identity'], bridge_mapping(term))
            points.append(point)
        bound.append(points)
    totals = [sum((amount(x['signed_cash_usd']) for x in points), Fraction()) for points in bound]
    if totals[0] != totals[1]:
        raise ValueError('FY2021 stock-proceeds presentation bridge does not reconcile')
    return {'issue_id':'AAPL-FCFE-002','status':'RESOLVED_NO_NUMERIC_CHANGE',
            'source_terms':dict(zip(('original','later_comparative'),bound)),
            'original_total':serialized(totals[0]),'later_total':serialized(totals[1]),
            'difference_usd':'0','fcfe_change_usd':'0',
            'rule':'Known common-stock issuance remains equity, not debt; original unallocated Other is still unresolved.'}


def approved_decisions(root):
    data = json.loads((root/DECISIONS).read_text())
    rows = data['decisions']
    if tuple(r['id'] for r in rows) != APPROVED_IDS or any(r['authorization']!='USER_APPROVED_TREATMENT' for r in rows):
        raise ValueError('Explicit bounded Apple manual-treatment authorization required')
    if data['ticker']!='AAPL' or data['fiscal_years']!=[2021,2022,2023,2024,2025]:
        raise ValueError('Approval does not cover this company/period')
    if data['automatic_publication'] is not False or data['estimates_permitted'] is not False:
        raise ValueError('No automatic publication or missing-input estimates approved')
    return data


def build(root=ROOT):
    decisions=approved_decisions(root)
    mapping=json.loads((root/SOURCE_MAP).read_text())
    spec=ANCHORS['aapl-fy2025'];load_revenue_anchor('aapl-fy2025',root)
    package=json.loads((root/spec['package']).read_text())
    rows=package['aapl_history_review']['periods']
    if len(rows)!=5 or [int(r['identity']['annual_end'][:4]) for r in rows]!=decisions['fiscal_years']:
        raise ValueError('Five approved original Apple annuals required')
    if [m['identity'] for m in mapping['periods']] != [r['identity'] for r in rows]:
        raise ValueError('Source mapping/approved historical period mismatch')
    manifests={};filings={int(r['identity']['annual_end'][:4]):RetainedFiling(root,r,manifests) for r in rows}
    # Replay the existing independent statement verifier; no earlier audit file
    # is modified and no test candidate becomes adopted history.
    op=next(c for c in operating.build(root)['companies'] if c['ticker']=='AAPL')
    before=adopted_window(root,'aapl-fy2025')
    result=[]
    for source, mapped, candidate, live in zip(rows,mapping['periods'],op['periods'],before,strict=True):
        identity=source['identity'];year=int(identity['annual_end'][:4]);filing=filings[year]
        if candidate['identity']!=identity:
            raise ValueError('Operating method/financing identity mismatch')
        cells,funding=full_financing(filing,identity,mapped['financing_rows'])
        inputs=candidate['inputs'];cfo=amount(inputs['cfo_control']['value']);capex=amount(inputs['cash_ppe']['value'])
        net=Fraction(int(funding['net_borrowing']['exact_fraction_usd']['numerator']),int(funding['net_borrowing']['exact_fraction_usd']['denominator']))
        fcfe=serialized(cfo-capex+net)
        # The candidate retains the disclosed reported-ETR diagnostic. No
        # normalized rate, mixed-row allocation or lease flow is fabricated.
        result.append({'fiscal_year':year,'identity':identity,
            'fcfe':dict(fcfe,status='PROVISIONAL_FINANCING_SCOPE_UNRESOLVED',publishable_as_verified=False,
                formula='reported CFO - cash PP&E + identified net debt funding',
                omitted_other_is_assumed_zero=False),
            'financing':funding,'financing_source_rows':cells,
            'reported_cash_fcf':serialized(cfo-capex),
            'operating_fcff_candidate':candidate,
            'platform_before':{'fcff_usd':live['fcff'],'basis':live['fcff_basis']},
            'platform_after':{'fcff_usd':live['fcff'],'basis':live['fcff_basis']},
            'platform_numeric_change_usd':'0' if live['fcff'] is not None else None,
            'verified_operating_fcff':None,
            'approval_does_not_supply_missing_inputs':True,
            'remaining_reviews':['Other financing and finance-lease principal classification',
                'Mixed operating cash movements and complete expense-aligned noncash/investment scope',
                'Recurring operating-tax treatment; no normalized forecast rate selected']})
    bridge=presentation_bridge(filings,mapping)
    if adopted_window(root,'aapl-fy2025')!=before:
        raise ValueError('Resolution replay changed adopted chart history')
    inputs=[SOURCE_MAP,DECISIONS,Path(spec['package']),Path(operating.PRIOR_PATH),Path(operating.JSON_PATH),
        Path('scripts/resolve_apple_cashflows.py'),Path('scripts/test_operating_fcff_from_filings.py'),
        Path('scripts/calculate_historical_fcff_from_filings.py'),
        Path('scripts/prepare_trillion_review_batch.py'),
        Path('src/valuation_platform/review/operating_fcff.py'),
        Path('src/valuation_platform/review/cfo_history.py')]
    return {'schema_version':'company-cashflow-resolution-v1','ticker':'AAPL','review_date':'2026-11-03',
        'scope':'User-approved Apple FY2021–25 reconciliation, not other-company adoption',
        'decisions':decisions,'inputs_sha256':{str(p):sha(root/p) for p in inputs},
        'periods':result,'presentation_bridge':bridge,
        'decision_outcomes':{'AAPL-FCFE-001':'RECONCILED_UNRESOLVED_COMPONENTS_REMAIN',
            'AAPL-FCFE-002':'RESOLVED_NO_NUMERIC_CHANGE',
            'AAPL-FCFF-001':'OPERATING_ROUTE_REPLAYED_INPUT_ALIGNMENT_UNRESOLVED',
            'AAPL-TAX-001':'REPORTED_TAX_PRESERVED_NO_RECURRING_RATE_SELECTED'},
        'validation':{'full_financing_statements_reconciled':5,'independent_cfo_checks':5,
            'operating_to_cash_fcf_bridges':5,'presentation_bridges':1,'source_mismatches':0,
            'chart_numeric_changes':0,'verified_new_fcff_periods':0,'verified_new_fcfe_periods':0},
        'publication':{'historical_chart_changed':False,'forecast_inputs_changed':False,
            'enterprise_values_changed':False,'automatic_fcfe_adoption':False,
            'reason':'Method authorization does not resolve missing classifications or supply a tax rate.'}}


def csv_output(data):
    stream=StringIO(newline='')
    fields=['fiscal_year','cash_fcf_usd','identified_net_borrowing_usd','provisional_fcfe_usd',
        'unallocated_other_financing_usd','operating_fcff_candidate_usd','verified_operating_fcff_usd',
        'platform_fcff_before_usd','platform_fcff_after_usd','fcfe_status','operating_status']
    writer=csv.DictWriter(stream,fields,lineterminator='\n');writer.writeheader()
    for p in data['periods']:
        writer.writerow(dict(fiscal_year=p['fiscal_year'],cash_fcf_usd=p['reported_cash_fcf']['amount_usd'],
            identified_net_borrowing_usd=p['financing']['net_borrowing']['amount_usd'],
            provisional_fcfe_usd=p['fcfe']['amount_usd'],unallocated_other_financing_usd=p['financing']['unknown_components'][0]['amount_usd'],
            operating_fcff_candidate_usd=p['operating_fcff_candidate']['operating_method_test']['result']['amount_usd'],
            verified_operating_fcff_usd='',platform_fcff_before_usd=p['platform_before']['fcff_usd'] or '',
            platform_fcff_after_usd=p['platform_after']['fcff_usd'] or '',fcfe_status=p['fcfe']['status'],
            operating_status=p['operating_fcff_candidate']['status']))
    return stream.getvalue()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check',action='store_true');mode.add_argument('--write',action='store_true')
    args=parser.parse_args();data=build()
    outputs={OUTPUT:json.dumps(data,indent=2,sort_keys=True)+'\n',CSV_OUTPUT:csv_output(data)}
    for path,value in outputs.items():
        if args.check:
            if (ROOT/path).read_text()!=value:
                raise SystemExit(f'Resolution record differs: {path}; review evidence and decision before writing')
        else:(ROOT/path).write_text(value)
    print(json.dumps(data['validation'],sort_keys=True))


if __name__=='__main__':main()
