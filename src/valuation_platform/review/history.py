"""Display-only ratios from the already pinned, accepted annual populations.

Called after catalog anchor validation. No retrieval, approval, forecast operand,
or claim that these few observations establish historical input sufficiency.
"""
from datetime import date, timedelta
from decimal import Decimal, Context, ROUND_HALF_EVEN, localcontext
import json
from urllib.parse import urlsplit
from valuation_platform.valuation.consumer import ANCHORS


def _annual_operands(root, kind):
    spec = ANCHORS[kind]
    package = json.loads((root / spec['package']).read_text())
    prefix = spec['ticker'].lower()
    rows = package['periods'] if prefix == 'meta' else package[prefix + '_history_review']['periods']
    view = package['current_history' if prefix == 'meta' else prefix + '_current_history']['periods']

    def operand(index, field):
        row, accepted = rows[index], view[index]
        identity = row['identity']; fact = row['facts'][field]; value = accepted['inputs'][field]
        start, end = (date.fromisoformat(identity[k]) for k in ('annual_start', 'annual_end'))
        if (identity != accepted['identity'] or identity['cik'] != spec['identity']['cik']
                or identity['form'] != '10-K' or not 330 <= (end-start).days <= 380
                or value['origin'] != 'reported' or value['value'] != fact['value']
                or value['raw_value'] != fact['value'] or value['unit'] != 'USD'
                or fact['unit'] != 'USD' or value['precision'] != fact['precision']
                or value.get('sign_multiplier', value.get('multiplier')) != 1):
            raise ValueError('Incompatible retained annual population')
        occurrences = fact['occurrences']
        if not any(o['start'] == str(start) and o['end'] == str(end)
                   and not o['dimensions'] and o['raw_value'] == value['value'] for o in occurrences):
            raise ValueError('Exact undimensioned annual occurrence unavailable')
        urls = [s.get('url', s.get('source_url', '')) for s in row['sources']]
        urls = [u for u in urls if urlsplit(u).scheme == 'https' and urlsplit(u).hostname == 'www.sec.gov']
        if not urls: raise ValueError('SEC source unavailable')
        amount = Decimal(value['value'])
        if not amount.is_finite(): raise ValueError('Finite amount required')
        return {'field': field, 'amount': str(amount), 'unit': 'USD', 'precision': value['precision'],
                'period_start': str(start), 'period_end': str(end), 'accession': identity['accession'],
                'concept': fact['concept'], 'sources': urls, 'classification': 'REPORTED'}

    return rows, operand


def historical_window(root, kind):
    """At most three consecutive compatible reported years ending at the anchor.

    Display projection only. FCFF is deliberately unavailable: accepted revenue
    does not establish a compatible historical adjusted cash-flow population.
    """
    rows, operand = _annual_operands(root, kind)
    end = ANCHORS[kind]["identity"]["annual_end"]
    ordered = sorted(range(len(rows)), key=lambda i: rows[i]["identity"]["annual_end"], reverse=True)
    observations = []
    for i in ordered:
        identity = rows[i]["identity"]
        if identity["annual_end"] > end:
            continue
        try:
            revenue = operand(i, "revenue")
            if revenue["period_end"] != end or Decimal(revenue["amount"]) <= 0:
                break
        except (ValueError, KeyError, IndexError, TypeError, ArithmeticError):
            break
        # Keep the catalog's existing byte ceiling. Repeated classification/gap
        # prose is represented by the window contract, not repeated per amount.
        projection = {k: v for k, v in revenue.items() if k not in ("field", "classification")}
        projection["sources"] = [next((u for u in revenue["sources"] if urlsplit(u).path.endswith((".htm", ".html"))), revenue["sources"][0])]
        observations.append({"fiscal_year_label": "FY" + revenue["period_end"][:4],
                             "revenue": projection, "fcff": None})
        end = str(date.fromisoformat(revenue["period_start"]) - timedelta(days=1))
        if len(observations) == 3:
            break
    return list(reversed(observations))


def historical_references(root, kind):
    _, operand = _annual_operands(root, kind)
    references = []
    for metric in ('revenue_growth', 'operating_margin'):
        try:
            revenue = operand(4, 'revenue')
            if Decimal(revenue['amount']) <= 0: raise ValueError('Positive revenue required')
            if metric == 'revenue_growth':
                prior = operand(3, 'revenue')
                if (date.fromisoformat(prior['period_end']) + timedelta(days=1) !=
                        date.fromisoformat(revenue['period_start']) or Decimal(prior['amount']) <= 0):
                    raise ValueError('Consecutive comparable fiscal years required')
                operands = [revenue, prior]; label = 'FY2024 → FY2025 annual revenue growth'
                formula = 'FY2025 revenue / FY2024 revenue − 1'
            else:
                ebit = operand(4, 'ebit'); operands = [ebit, revenue]
                label = 'FY2025 operating margin'; formula = 'FY2025 EBIT / FY2025 revenue'
            with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
                value = Decimal(operands[0]['amount']) / Decimal(operands[1]['amount'])
                if metric == 'revenue_growth': value -= 1
            references.append({'metric': metric, 'label': label, 'value': str(value),
                               'classification': 'DERIVED_HISTORICAL_REFERENCE', 'formula': formula,
                               'operands': operands, 'limitation': 'Reported annual populations only; not a forecast or new valuation approval. Fiscal-year lengths may differ; no day-count adjustment. Source rounding limits precision.'})
        except (ValueError, KeyError, IndexError, TypeError, ArithmeticError):
            references.append({'metric': metric, 'value': None, 'label': 'Historical reference unavailable',
                               'operands': [], 'limitation': 'A compatible accepted annual population is unavailable; no substitution.'})
    return references
