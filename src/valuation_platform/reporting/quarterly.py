"""Versioned quarterly reporting over the existing typed SEC Company Facts layer.

Never mutates normalization, analyst packages, or valuation inputs. USD-only pilot
policy; unsupported/ambiguous observations fail closed rather than becoming zeros.
"""
from datetime import date, timedelta
from decimal import Decimal
from valuation_platform.sec.company_facts import SECCompanyFacts

POLICY = 'quarterly-reported-usd-v1'
METRICS = {
    'revenue': ('RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues', 'SalesRevenueNet'),
    'operating_income': ('OperatingIncomeLoss',),
    'net_income': ('NetIncomeLoss',),
    'cfo': ('NetCashProvidedByUsedInOperatingActivities',),
    'cash_capex': ('PaymentsToAcquirePropertyPlantAndEquipment',),
    'sbc': ('ShareBasedCompensation',),
}

class ReportingError(ValueError):
    """Required reporting evidence is missing, ambiguous or inconsistent."""


def prepare_quarters(facts: SECCompanyFacts, as_of: date, count: int = 20) -> dict:
    if count < 1 or count > 40:
        raise ReportingError('Quarter count must be between 1 and 40')
    index = {c.name: c for c in facts.concepts if c.taxonomy == 'us-gaap'}

    def observations(metric):
        return [(tag, o) for tag in METRICS[metric] if tag in index
                for o in index[tag].observations
                if o.unit == 'USD' and o.start and o.filed <= as_of
                and o.end <= as_of and o.form in ('10-K', '10-Q')
                and isinstance(o.value, (int, float)) and not isinstance(o.value, bool)]

    def pick(metric, start, end, cutoff, accession=None):
        candidates = [(tag, o) for tag, o in observations(metric)
                      if o.start == start and o.end == end and o.filed <= cutoff
                      and (accession is None or o.accession_number == accession)]
        if not candidates:
            raise ReportingError(f'{metric}: missing {start} through {end}')
        # Earliest eligible disclosure of this period; explicit standard-tag priority.
        earliest = min(o.filed for _, o in candidates)
        candidates = [(t, o) for t, o in candidates if o.filed == earliest]
        priority = min(METRICS[metric].index(t) for t, _ in candidates)
        candidates = [(t, o) for t, o in candidates if METRICS[metric].index(t) == priority]
        if len({Decimal(str(o.value)) for _, o in candidates}) != 1:
            raise ReportingError(f'{metric}: conflicting observations for {start}/{end}')
        tag, o = min(candidates, key=lambda item: item[1].accession_number)
        value = Decimal(str(o.value))
        if not value.is_finite() or value != value.to_integral_value():
            raise ReportingError(f'{metric}: noninteger USD observation')
        return {'value': int(value), 'concept': 'us-gaap:' + tag,
                'start': str(start), 'end': str(end), 'filed': str(o.filed),
                'accession': o.accession_number,
                'source_url': f'https://www.sec.gov/Archives/edgar/data/{facts.company.cik}/{o.accession_number.replace("-", "")}/'}

    annual_periods = sorted({(o.start, o.end) for _, o in observations('revenue')
                             if o.form == '10-K' and 330 <= (o.end-o.start).days <= 380})
    if not annual_periods:
        raise ReportingError('No supported annual reporting calendar')
    # Retain sufficient completed fiscal periods and the current interim year.
    annual_periods = annual_periods[-7:]
    latest_end = max(end for _, end in annual_periods)
    periods = [(start, end, True) for start, end in annual_periods]
    interim_start = latest_end + timedelta(days=1)
    interim_ends = [o.end for _, o in observations('revenue')
                    if o.start == interim_start and o.form == '10-Q'
                    and 60 <= (o.end-interim_start).days <= 310]
    if interim_ends:
        periods.append((interim_start, max(interim_ends), False))
    rows, validations, exclusions = [], [], []
    discrete_checks = []
    for start, end, closed in periods:
        # Anchor an annual period to its earliest 10-K, not a later comparison.
        anchor = pick('revenue', start, end, as_of) if closed else None
        cutoff = date.fromisoformat(anchor['filed']) if anchor else as_of
        ends = sorted({o.end for _, o in observations('revenue')
                       if o.start == start and o.form == '10-Q' and o.filed <= cutoff
                       and start < o.end < end and 60 <= (o.end-start).days <= 310})
        ends.append(end)
        expected = 4 if closed else round((end-start).days/91)
        if len(ends) != expected or any(not 70 <= (b-a).days <= 110
                for a, b in zip([start-timedelta(days=1)] + ends[:-1], ends)):
            exclusions.append({'start': str(start), 'end': str(end), 'reason': 'Incomplete or unsupported quarterly calendar'})
            continue
        fiscal_year = end.year if closed else latest_end.year+1
        previous = {}
        year_rows = []
        try:
            for q, qend in enumerate(ends, 1):
                evidence, values = {}, {}
                for metric in METRICS:
                    operand = pick(metric, start, qend, cutoff,
                                   anchor['accession'] if closed and qend == end else None)
                    prior = previous.get(metric)
                    values[metric] = operand['value'] - (prior['value'] if prior else 0)
                    evidence[metric] = {'classification': 'SEC_REPORTED' if q == 1 else 'SEC_SUPPORTED_DERIVATION',
                        'method': 'reported first quarter' if q == 1 else 'full year minus nine months' if q == 4 else 'successive YTD difference',
                        'operands': [operand] + ([prior] if prior else [])}
                    previous[metric] = operand
                if values['cash_capex'] < 0:
                    raise ReportingError('Cash capex purchases must be a nonnegative outflow magnitude')
                qstart = start if q == 1 else ends[q-2]+timedelta(days=1)
                # Compare derived income-statement quarters to a standalone
                # disclosure in the SAME current operand filing where available.
                for metric in ('revenue', 'operating_income', 'net_income'):
                    try:
                        direct = pick(metric, qstart, qend, cutoff,
                                      evidence[metric]['operands'][0]['accession'])
                    except ReportingError as error:
                        if 'missing' in str(error):
                            continue
                        raise
                    discrete_checks.append({'quarter_id': f'FY{fiscal_year}-Q{q}',
                        'metric': metric, 'derived': values[metric], 'reported': direct,
                        'difference': values[metric]-direct['value']})
                row = {'id': f'FY{fiscal_year}-Q{q}', 'fiscal_year': fiscal_year, 'quarter': q,
                       'start': str(start if q == 1 else ends[q-2]+timedelta(days=1)),
                       'end': str(qend), 'values': values, 'evidence': evidence}
                values['fcf'] = values['cfo'] - values['cash_capex']
                values['other_operating'] = values['cfo'] - values['net_income'] - values['sbc']
                values['operating_margin'] = values['operating_income']/values['revenue'] if values['revenue'] else None
                values['fcf_margin'] = values['fcf']/values['revenue'] if values['revenue'] else None
                if values['net_income']+values['sbc']+values['other_operating']-values['cash_capex'] != values['fcf']:
                    raise ReportingError('Quarter bridge does not reconcile')
                year_rows.append(row)
            if closed:
                for metric in METRICS:
                    annual = pick(metric, start, end, cutoff, anchor['accession'])
                    total = sum(r['values'][metric] for r in year_rows)
                    if total != annual['value']:
                        raise ReportingError(f'{metric}: annual tie-out failed')
                    validations.append({'fiscal_year': fiscal_year, 'metric': metric,
                                        'sum_quarters': total, 'annual': annual})
            rows.extend(year_rows)
        except ReportingError as error:
            exclusions.append({'start': str(start), 'end': str(end), 'reason': str(error)})
    rows = sorted(rows, key=lambda r: r['end'])[-count:]
    if rows and rows[-1]['end'] != str(max(o.end for _, o in observations('revenue'))):
        raise ReportingError('Latest reporting period is incomplete; refusing a silent stale fallback')
    if len(rows) != count:
        raise ReportingError(f'Need {count} supported quarters, obtained {len(rows)}; exclusions: {exclusions}')
    for a, b in zip(rows, rows[1:]):
        if date.fromisoformat(a['end']) + timedelta(days=1) != date.fromisoformat(b['start']):
            raise ReportingError('Gap in selected quarterly history')
    return {'schema_version': 1, 'policy': POLICY, 'ticker': facts.company.ticker,
            'company': facts.entity_name, 'as_of': str(as_of), 'currency': 'USD',
            'basis': 'First eligible disclosure within each fiscal-period cohort; annual Q4 balances to the selected original annual filing. Descriptive history, not latest-restated or an as-known backtest.',
            'source_url': facts.source_url, 'rows': rows,
            'validation': {'annual_tie_outs': validations, 'bridge_checks': len(rows), 'excluded_periods': exclusions,
                'discrete_quarter_checks': [r for r in discrete_checks if r['quarter_id'] in {q['id'] for q in rows}]},
            'limitations': ['FCF is CFO less cash PP&E purchases, not FCFF or FCFE.',
                'Other operating reconciliation is CFO minus net income minus SBC; it groups remaining noncash and operating asset/liability movements, not an independently reported line.',
                'SBC add-back describes reported CFO, not an assertion that compensation is economically free.',
                'Comparative revisions and unsupported fiscal calendars require separate review; missing required inputs stop publication.']}
