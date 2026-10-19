"""Fixed public projection of verified retained anchors; never a file server."""

import json
from pathlib import Path
from urllib.parse import urlsplit

from .budget import encode_bounded

CATALOG_MAX_BYTES = 64 * 1024
TEMPLATE_NAMES = ('meta-fy2025', 'googl-fy2025', 'aapl-fy2025')


def build_catalog(root: Path) -> bytes:
    # Called once after bundle verification at startup, never on validation.
    from valuation_platform.valuation.consumer import ANCHORS, load_revenue_anchor

    entries = []
    for kind in TEMPLATE_NAMES:
        anchor = load_revenue_anchor(kind, root)
        template = json.loads((root / f'examples/valuation/{kind}-unset.json').read_text())
        details = json.loads(anchor.source_details_json)
        links = []
        for source in details['sources']:
            url = source.get('url', source.get('source_url', ''))
            parsed = urlsplit(url)
            if parsed.scheme == 'https' and parsed.hostname == 'www.sec.gov':
                links.append(url)
        entries.append({
            'kind': kind, 'company': ANCHORS[kind]['ticker'],
            'identity': dict(template['anchor']),
            'revenue': str(anchor.revenue), 'unit': anchor.unit,
            'precision': anchor.precision, 'source_links': links,
            'limitations': template['limitations'], 'template': template,
        })
    demo = json.loads((root / 'examples/valuation/synthetic-base.json').read_text())
    return encode_bounded({
        'schema_version': 'local-ev-catalog-v1', 'entries': entries,
        'synthetic_demo': demo,
        'timing_notice': 'Retained FY2025 data, not automatically refreshed. Fiscal-end analytical date uses later-filed information; not a contemporaneous backtest. No structured information cutoff is enforced by the single-case reader; disclose it in scope/limitations.',
        'input_definitions': {
            'revenue_growth': 'Manual annual revenue growth.',
            'operating_margin': 'EBIT margin including SBC, operating-lease service costs and expense-aligned D&A.',
            'forecast_tax_rate': 'Operating tax rate; no immediate tax benefit on losses.',
            'd_and_a_percent_revenue': 'Expense-aligned D&A / full forecast revenue; add back once.',
            'capex_percent_revenue': 'Investment / full forecast revenue: cash PP&E plus non-overlapping new finance-leased operating assets, excluding principal.',
            'change_in_operating_nwc_percent_revenue': 'Working-capital cash requirement / full forecast revenue: positive uses cash; negative releases cash.',
        },
    }, CATALOG_MAX_BYTES)
