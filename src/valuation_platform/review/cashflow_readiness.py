"""Separate historical measurement from ownership and valuation readiness.

The November 4 instruction adopts separation of consumers, not new cash values,
an Other-financing waiver, or a retroactive pass of the parent-common review.
"""


def readiness(company):
    """Called only after the pinned pilot reader validates issuer/metric states."""
    periods = []
    for period in company['periods']:
        ff, fe = period['fcff'], period['fcfe']
        consolidated = fe['status'] == 'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION'
        periods.append({'fiscal_year': period['fiscal_year'],
            'fcff_historical_calculation': 'AVAILABLE_STATED_CONVENTION' if ff['amount_usd'] is not None else 'UNAVAILABLE_REQUIRED_INPUT',
            'fcfe_historical_calculation': 'AVAILABLE_CONSOLIDATED_STATED_CONVENTION' if consolidated else 'PROVISIONAL_INCOMPLETE_FINANCING',
            'fcff_forecast_calibration': 'NOT_CLEARED_BASIS_BRIDGE_REQUIRED',
            'parent_common_fcfe': 'UNAVAILABLE_OWNERSHIP_ATTRIBUTION' if consolidated else 'UNAVAILABLE_FINANCING_SCOPE'})
    ff_available = sum(p['fcff_historical_calculation'] == 'AVAILABLE_STATED_CONVENTION' for p in periods)
    fe_available = sum(p['fcfe_historical_calculation'] == 'AVAILABLE_CONSOLIDATED_STATED_CONVENTION' for p in periods)
    provisional = 5 - fe_available
    return {'schema_version': 'cashflow-consumer-readiness-v1',
        'contract': 'Consolidated historical availability is separate from exact parent cash attribution, forecast alignment, equity-value and per-share review.',
        'adoption_record': 'docs/company-resolutions/execution-2026-11-04/accepted-policy.json',
        'prior_parent_common_review_passed': False,
        'counts': {'available_stated_convention': ff_available + fe_available,
                   'provisional_financing': provisional, 'missing_required_input': 5 - ff_available,
                   'parent_common_fcfe_available': 0},
        'periods': periods,
        'gates': [
            {'id': 'history', 'label': 'Historical calculations', 'status': 'SCOPED_AVAILABILITY',
             'detail': f'{ff_available + fe_available} available under stated conventions; {provisional} provisional; {5 - ff_available} missing required inputs.'},
            {'id': 'parent_cash', 'label': 'Parent-common cash attribution', 'status': 'UNAVAILABLE',
             'detail': 'Consolidated FCFE needs minority cash attribution.' if company['ticker'] == 'GOOGL' else 'Complete financing classification is unresolved.'},
            {'id': 'comparison', 'label': 'History-to-forecast comparison', 'status': 'NOT_CLEARED',
             'detail': 'A reviewed SBC, tax and investment bridge is required. No cross-basis FCFF CAGR or automatic calibration.'},
            {'id': 'forecast', 'label': 'Forward valuation assumptions', 'status': 'REVIEW_SEPARATELY',
             'detail': 'Manual forecasting remains available. Financing, discount rate, taxes and terminal inputs require their own validation.'},
            {'id': 'parent_value', 'label': 'Parent equity-value bridge', 'status': 'REVIEW_SEPARATELY',
             'detail': 'Use matching cash, claims and outside-interest values; never deduct debt twice in the FCFE route.'},
            {'id': 'per_share', 'label': 'Fair value per share', 'status': 'REVIEW_SEPARATELY',
             'detail': 'Requires a supported parent equity numerator and dated shares, classes and award treatment.'}],
        'financial_review_status': 'OPEN', 'history_gap_disables_manual_forecast': False,
        'amounts_changed': company.get('active_fcff_method_adoption') == 'AAPL_OPERATING_2026_11_04', 'prior_clearance_flags_changed': False}
