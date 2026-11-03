"""Rebuild the current readable report without changing any source or value."""
from pathlib import Path
from decimal import Decimal,localcontext
import html
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/company-resolutions/implementation-2026-11-03'

def amount(v):
    if v is None:return 'Unavailable'
    with localcontext() as c:
        c.prec=80
        return format(Decimal(v)/Decimal(10**9),',.3f')+'B'

def report():
    d=json.loads((OUT/'platform-cashflows.json').read_text())
    audit=json.loads((OUT/'independent-review/integrated-verdict.json').read_text())
    if audit['overall_verdict']!='FAIL' or audit['financial_coverage']['total_failed_requested_cells']!=17:
        raise ValueError('This report template requires a new reviewed version when financial clearance changes')
    parts=[]
    for ticker in ('AAPL','META','GOOGL'):
        c=d['companies'][ticker];rows=[]
        for p in c['periods']:
            ff,fe=p['fcff'],p['fcfe']
            status='Consolidated · before minority allocation' if ticker=='GOOGL' else 'Provisional · financing scope unresolved'
            rows.append('<tr>'+''.join('<td>'+html.escape(s)+'</td>' for s in (str(p['fiscal_year']),amount(ff['amount_usd']),amount(fe['amount_usd']),status,'Unavailable',', '.join(ff['open_items']+fe['open_items'])))+'</tr>')
        parts.append(f'<section><h2>{ticker}</h2><p>USD billions · reported-cash convention · annual dates and exact operands in <a href="platform-cashflows.json">source-aware export</a>.</p><div class="scroll"><table><thead><tr><th>FY</th><th>FCFF</th><th>FCFE review amount</th><th>FCFE scope/status</th><th>Parent-common FCFE</th><th>Direct blockers</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div><p>Broader open scope: '+html.escape(', '.join(c['unresolved_scope_items']))+'.</p></section>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><title>Current three-company FCFF / FCFE review</title><style>body{font:16px/1.5 system-ui;color:#193b4b;background:#f1f4f6;margin:0;padding:32px}main{max-width:1280px;margin:auto}h1{font:44px Georgia;margin:0 0 12px}h2{font:32px Georgia}section,.status{background:white;border:1px solid #dae2e8;border-radius:12px;padding:24px;margin:24px 0}th,td{padding:12px;text-align:left;border-bottom:1px solid #e0e6eb;vertical-align:top}th{background:#f4f6f8}table{border-collapse:collapse;width:100%}.scroll{overflow:auto}.status{border-left:5px solid #af892e}a{color:#315c70}small{color:#627486}</style><main><h1>FCFF and FCFE · current pilot review</h1><small>Apple · Meta · Alphabet / FY2021–FY2025 / November 3, 2026</small><div class="status"><strong>OPEN — full financial availability review has not passed.</strong><p>13 of 30 strict FCFF/parent-common FCFE cells pass the named historical convention; 17 remain blocked. All 30 records reach the platform with explicit status and scope. Alphabet has five calculated consolidated FCFEs; those are not parent-common cash allocations.</p></div>'''+''.join(parts)+'''<section><h2>What remains</h2><p><strong>Apple:</strong> gross expensed interest FY2024/25; financing residual and actual finance-lease principal/containment in all five years. The investigated EBIT alternative still needs complete D&A, operating cash-movement and investment alignment.</p><p><strong>Meta:</strong> full annual classification of Other financing. Broader replacement FCFF also needs capitalized-interest cash and matching investment/tax alignment.</p><p><strong>Alphabet:</strong> annual subsidiary cash/ownership allocation for parent-common FCFE, dated NCI fair value for valuation, and lease prepayment/noncash investment alignment.</p><p><strong>Shared:</strong> full historical/forecast basis bridge, issuer-reviewed FCFE financing/discount inputs, and eligible cash/claims/class/awards policies for per-share value. Manual FCFE software exists; it does not supply those facts.</p><p>No unknown is zeroed, no missing input is inferred from a balance change, no consolidated value is relabeled as parent common, and no book NCI is substituted for fair value.</p></section><section><h2>Evidence and review</h2><p><a href="implementation-log.json">18-treatment execution log</a> · <a href="independent-review/findings.md">Independent findings</a> · <a href="independent-review/integrated-verdict.json">Full independent verdict</a> · <a href="basis-bridge/decision-log.json">Partial basis bridge</a> · <a href="share-bridge/README.md">Share and claims schedules</a> · <a href="README.md">Reproduction and limitations</a></p><p>The November2 42-company snapshot is preserved. This report reads the newer versioned three-company projection. Historical inputs are rounded filing figures; FCFF/FCFE are derived under stated conventions, not separately reported audited line items.</p></section></main></html>'''

if __name__=='__main__':
    (OUT/'report.html').write_text(report())
    print('Current report generated; overall financial clearance remains OPEN/FAIL.')
