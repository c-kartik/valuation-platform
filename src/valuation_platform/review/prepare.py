"""Bounded current-context preparation using existing SEC parsers/concept policies.

This is observation preparation, not a new valuation-anchor adapter or approval.
No TTM derivation, quarterly annualization or economic bridge classification.
"""
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from valuation_platform.sec.company_facts import _parse_company_facts
from valuation_platform.sec.submissions import _parse_main_submissions
from valuation_platform.sec.tickers import SECCompanyIdentity
from valuation_platform.normalization import concepts as policies
from valuation_platform.normalization.balance_sheet import ANNUAL_BALANCE_SHEET_POLICIES

COMPANIES = {'META': 1326801, 'GOOGL': 1652044, 'AAPL': 320193}
FIELDS = ('revenue','operating_income','cash_and_cash_equivalents','short_term_investments',
          'long_term_marketable_securities','commercial_paper','short_term_borrowings',
          'current_portion_of_long_term_debt','long_term_debt_noncurrent')


def prepare_context(ticker, submissions, facts, sources):
    if ticker not in COMPANIES:
        raise ValueError('Only META, GOOGL and AAPL are supported')
    cik = COMPANIES[ticker]
    if int(submissions.get("cik",-1)) != cik:raise ValueError("Submissions company mismatch")
    identity = SECCompanyIdentity(ticker,cik,f'{cik:010d}',ticker,sources[0]['url'],datetime.fromisoformat(sources[0]['checked_at']))
    filings,_ = _parse_main_submissions(submissions)
    relevant = [f for f in filings if f.form in ('10-K','10-Q','10-K/A','10-Q/A') and f.report_date]
    if not relevant:raise ValueError('No supported annual/interim filing')
    latest = max(relevant,key=lambda f:(f.report_date,f.filing_date,f.accession_number))
    _, concepts = _parse_company_facts(facts,identity)
    available = {(c.taxonomy,c.name):c for c in concepts}
    observations = []
    for field in FIELDS:
        policy = next((v for v in vars(policies).values() if isinstance(v,policies.MetricConceptPolicy) and v.metric.value == field),None)
        candidates = policy.candidates if policy else tuple(c.concept for p in ANNUAL_BALANCE_SHEET_POLICIES if p.metric.value==field for c in p.candidates if c.applicable_ciks is None or cik in c.applicable_ciks)
        matches = []
        for key in candidates:
            concept = available.get((key.taxonomy,key.name))
            if not concept:continue
            for o in concept.observations:
                if o.accession_number != latest.accession_number or o.end != latest.report_date or o.unit!='USD':continue
                if isinstance(o.value,bool) or not isinstance(o.value,(int,str,Decimal)):continue
                if o.start and not 60 <= (o.end-o.start).days <= 370:continue
                matches.append((key,o))
        # Keep quarter and YTD separately; concept alternatives never summed.
        seen=set()
        for key,o in matches:
            signature=(key.taxonomy,key.name,o.start,o.end,str(o.value))
            if signature in seen:continue
            seen.add(signature)
            observations.append({'field':field,'concept':key.taxonomy+':'+key.name,'amount':str(o.value),
                'unit':o.unit,'scale':1,'start':o.start.isoformat() if o.start else None,'end':o.end.isoformat(),
                'period_basis':'reported duration; not annualized' if o.start else 'reported instant',
                'accession':o.accession_number,'filed':o.filed.isoformat(),'classification':'REPORTED','precision':None,
                'source_reference':sources[1]['url']+'#'+key.taxonomy+':'+key.name,
                'limitation':'Context observation only. Alternatives/overlap and eligibility require review.'})
    # Companyfacts omits dimensional class detail; cover aggregate is explicitly scoped.
    common=available.get(('dei','EntityCommonStockSharesOutstanding'))
    if common:
        candidates=[o for o in common.observations if o.accession_number==latest.accession_number and o.unit=='shares']
        for o in candidates:
            if type(o.value) is not int:continue
            observations.append({'field':'reported_common_shares','concept':'dei:EntityCommonStockSharesOutstanding',
                'amount':str(o.value),'unit':'shares','scale':1,'start':None,'end':o.end.isoformat(),
                'period_basis':'cover observation; may postdate report end','accession':o.accession_number,
                'filed':o.filed.isoformat(),'classification':'REPORTED','precision':None,'source_reference':sources[1]['url']+'#dei:EntityCommonStockSharesOutstanding',
                'limitation':'Class/award scope not established by aggregate companyfacts; not valuation shares.'})
    recent=submissions['filings']['recent'];index=recent['accessionNumber'].index(latest.accession_number)
    accepted=recent.get('acceptanceDateTime',[None]*len(recent['form']))[index]
    if accepted:datetime.fromisoformat(accepted.replace('Z','+00:00'))
    url=f'https://www.sec.gov/Archives/edgar/data/{cik}/{latest.accession_number.replace("-","")}/{latest.primary_document}'
    unknown=[field for field in (*FIELDS,'reported_common_shares') if not any(x['field']==field for x in observations)]
    unknown += ['eligible_nonoperating_assets','finance_lease_liabilities','other_equity_claims','award_adjusted_shares','class_share_breakdown','strategic_holdings_eligibility','venture_claim_present_values','unpaid_acquisition_obligations']
    return {'schema_version':'investor-financial-context-v1','company':ticker,'cik':cik,
        'financials_through':latest.report_date.isoformat(),'form':latest.form,'filed':latest.filing_date.isoformat(),
        'accepted_at':accepted,'checked_at':max(s['checked_at']for s in sources),'filing_url':url,
        'accession':latest.accession_number,'sources':sources,'observations':observations,'unknown_fields':unknown,
        'status':'NEWER_FILING_AVAILABLE_PREPARATION_INCOMPLETE','valuation_anchor_approved':False,
        'information_cutoff':None,'limitations':[
            'Newer filing checked; selected reported context prepared, valuation consumer preparation incomplete.',
            'Retained FY2025 revenue remains the approved calculation anchor. Current context is not silently consumed.',
            'No TTM/annualization; duration observations retain their actual start/end.',
            'Companyfacts projection has no filing-cell decimal precision; precision remains unknown. Unprepared fields may exist in filing notes.',
            'Gross financial assets are not excess cash. Debt alternatives, leases, other claims, awards and settlement overlap remain unresolved.',
            'No class-equivalence, share denominator or source-approval change.']}
