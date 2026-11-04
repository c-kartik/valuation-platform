"""Recalculate and publish the bounded Apple analyst implementation record."""
import argparse
from decimal import Decimal
import hashlib
from html import escape
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from valuation_platform.preload.generate import generate, engine_request
from valuation_platform.review.apple_analyst import DEFAULTS, RESOURCE, run_apple_analyst

DEST = ROOT / 'docs/company-resolutions/AAPL/analyst-ready-2026-11-04'


def build():
    profile = generate(ROOT, ticker='AAPL', generated_at='2026-11-04T00:00:00+00:00')
    cases = {}
    for label in ('Bear', 'Base', 'Bull'):
        doc = {'schema_version': 'apple-analyst-request-v1', 'base_case': engine_request(profile, label), 'assumptions': dict(DEFAULTS)}
        cases[label] = run_apple_analyst(doc, ROOT)
    return {'schema_version': 'apple-analyst-acceptance-results-v1', 'date': '2026-11-04',
            'scope': 'AAPL FY2021–25 histories, selected FY2025-origin forecast and both equity/share routes under disclosed analyst conventions',
            'analyst_scope_status': 'ANALYST_READY_WITH_QUALIFICATIONS',
            'exact_reconstruction_claim': False,
            'source_policy_sha256': hashlib.sha256((ROOT / RESOURCE).read_bytes()).hexdigest(), 'cases': cases}


def render(data):
    b = data['cases']['Base']; money = lambda s: f'{Decimal(s):,.2f}'
    billion = lambda s: f'{Decimal(s)/Decimal(10**9):,.2f}B'
    ready = ''.join(f'<tr><td>{escape(r["label"])}</td><td><span class="ready">Analyst-ready with qualifications</span></td><td>{escape(r["detail"])}</td></tr>' for r in b['readiness'])
    history = ''.join('<tr><td>FY'+str(r['fiscal_year'])+'</td>'+''.join('<td>'+billion(r[k])+'</td>' for k in ('fcff_usd','fcfe_usd','economic_fcfe_usd','other_financing_usd'))+'</tr>' for r in b['historical'])
    scenarios = ''.join('<tr><td>'+label+'</td>'+''.join('<td>$'+money(r[m]['value_per_share_usd'])+'</td>' for m in ('fcff','fcfe'))+'</tr>' for label,r in data['cases'].items())
    stresses = ''.join('<tr><td>'+escape(r['label'])+'</td><td>$'+money(r['fcff_value_per_share_usd'])+'</td><td>$'+money(r['fcfe_value_per_share_usd'])+'</td></tr>' for r in b['sensitivities'])
    quals = ''.join('<li>'+escape(q)+'</li>' for q in b['qualifications'])
    sources = ''.join('<li><a href="'+escape(url,quote=True)+'">'+escape(url.split('/')[-1] or url)+'</a></li>' for url in b['source_urls'])
    cards = ''.join(f'<div class="card"><span>{m.upper()} fair value per share</span><strong>${money(b[m]["value_per_share_usd"])}</strong><small>Base · analyst estimate</small></div>' for m in ('fcff','fcfe'))
    delta = Decimal(b['fcfe']['value_per_share_usd']) - Decimal(b['fcff']['value_per_share_usd'])
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apple — analyst readiness</title>
<style>body{{margin:0;background:#f1f4f7;color:#193c4b;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1120px;margin:32px auto;padding:36px;background:white;border:1px solid #dce5eb;border-radius:16px}}h1{{font:52px/1.1 Georgia,serif;margin:12px 0}}h2{{font:29px Georgia,serif;margin-top:40px}}.eyebrow{{letter-spacing:.12em;font-size:12px;text-transform:uppercase}}.cards{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.card{{border:1px solid #dce5eb;padding:24px;border-radius:12px}}strong{{display:block;font:44px Georgia,serif;margin:10px 0}}small{{color:#617385}}table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{text-align:left;padding:13px 10px;border-bottom:1px solid #dce5eb;vertical-align:top}}th{{background:#f4f6f8}}.scroll{{overflow:auto}}.ready{{color:#38634b;font-weight:600}}.note{{border-left:3px solid #ad8734;background:#faf7ef;padding:14px 18px}}a{{color:#235870}}li{{margin:10px 0}}@media(max-width:650px){{main{{margin:10px;padding:20px}}h1{{font-size:38px}}.cards{{grid-template-columns:1fr}}table{{min-width:650px}}}}</style>
<main><div class="eyebrow">Apple · implementation and acceptance · 4 November 2026</div><h1>Five outputs, analyst-ready</h1><p><b>Ready with qualifications</b> for the defined Apple analytical model. Reported facts remain traceable; modeling assumptions are explicit and editable. This does not certify exact historical FCFE.</p>
<div class="cards">{cards}</div><p class="note">FCFE is ${money(abs(delta))} per share lower. FCFF uses target-weight WACC; FCFE assumes flat explicit debt with CAPM cost of equity. These are different financing scenarios, not a failed arithmetic reconciliation.</p>
<p>Analytical origin <b>27 September 2025</b>, using later-filed information. These figures are not current-date target prices or a historical backtest. Current market price/consensus comparison is outside this implementation; no trading recommendation is made.</p>
<h2>Acceptance by output</h2><div class="scroll"><table><thead><tr><th>Output</th><th>Assessment</th><th>Implemented treatment</th></tr></thead><tbody>{ready}</tbody></table></div>
<h2>Historical cash flows</h2><p>USD billions. FCFF uses the adopted EBIT/current-NWC convention. CFO-based FCFE keeps the cash-statement SBC addback; the economic companion subtracts that reported SBC. Tax and investment populations still differ, so automatic calibration and cross-basis CAGR remain disabled.</p><div class="scroll"><table><thead><tr><th>Year</th><th>FCFF</th><th>FCFE · CFO basis</th><th>Economic FCFE</th><th>Net Other</th></tr></thead><tbody>{history}</tbody></table></div><p>Source: <a href="../remaining-issues-2026-11-04/financing/results.json">filing-bound financing workpaper</a> and <a href="../operating-fcff-2026-11-04/adopted-history.json">adopted FCFF history</a>. Net Other is excluded from borrowing by the base assumption; it is not proven non-debt.</p>
<h2>Equity bridge and assumptions</h2><p>Gross liquidity {billion(b['bridge']['gross_cash_usd'])} − operating reserve {billion(b['bridge']['operating_reserve_usd'])} = eligible liquidity <b>{billion(b['bridge']['eligible_cash_usd'])}</b>. The reserve is an analyst-selected 2% of anchor revenue. FCFF deducts {billion(b['bridge']['debt_claims_usd'])} of financing claims once; FCFE deducts no debt after discounting.</p><p>Valuation denominator: 14.773260B dated common shares + 0.151574B existing RSUs = <b>14.924834B shares</b>, assuming all RSUs vest. Future SBC remains in margins as a future-grant expense proxy. Base additional non-operating claims: zero, explicitly assumed. <a href="../remaining-issues-2026-11-04/equity/results.json">Dated source observations</a>.</p><p>Default cost of equity: 5.05% risk-free + 1.05 beta × 3.70% equity premium = <b>8.935%</b>. Debt cost <b>5.65%</b>; Base WACC <b>8.27275%</b> with 85/15 target equity/debt and 20% tax shield. Macro dates and original source hashes are retained in <a href="policy.json">the policy/source record</a>; beta, spread and weights are configured assumptions.</p>
<h2>Scenario estimates</h2><div class="scroll"><table><thead><tr><th>Operating case</th><th>FCFF / share</th><th>FCFE / share</th></tr></thead><tbody>{scenarios}</tbody></table></div><p>Bear and Bull are existing diagnostic operating/WACC offsets, not researched probabilities. Lower margins, slower growth and higher discount rates reduce value; changing these drivers calls for recalculation rather than an automatic trade action.</p>
<h2>Sensitivity and materiality</h2><p>Illustrative one-at-a-time changes. These are not confidence intervals or proven exposure bounds.</p><div class="scroll"><table><thead><tr><th>Change</th><th>FCFF / share</th><th>FCFE / share</th></tr></thead><tbody>{stresses}</tbody></table></div>
<h2>Qualifications retained</h2><ul>{quals}</ul><h2>Verification and reproducibility</h2><p>Financial identity, source projection, isolated API worker and browser tests are recorded in <a href="validation.json">the validation record</a>. Independent review: <a href="independent-review.md">acceptance findings</a>. Implementation decisions and future update steps: <a href="README.md">company resolution log</a>.</p><p>Frozen sources, original exact-reconstruction results and other issuer outputs are preserved. All five current outputs are available in the platform under <b>Apple → DCF → Apple analyst valuation</b>, with editable assumptions, financing tables, sensitivities and export.</p><details><summary>Primary methodological and filing sources</summary><ul>{sources}</ul></details></main></html>'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    data = build(); outputs = {'results.json': json.dumps(data, indent=2, sort_keys=True)+'\n', 'report.html': render(data)}
    for name, text in outputs.items():
        if args.check:
            if (DEST/name).read_text() != text: raise ValueError('Apple analyst report replay differs: '+name)
        else: (DEST/name).write_text(text)
    print('PASS: three Apple scenarios, five analyst outputs and report reproduce.')
