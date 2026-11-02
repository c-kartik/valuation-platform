# Registered starting profiles — Alphabet, Meta and Apple

November 2, 2026. Scoped to these three companies. Wider Top50 preparation remains
paused. All forward values are editable proposed estimates, not reported FCFF,
approved forecasts or current-date fair values. Historical packages and the existing
valuation engine remain unchanged.

## Shared pipeline

Registration → retained source snapshots → reviewed extraction mapping → source-bound
observations → versioned issuer policy → proposed inputs → existing Python DCF engine.

`preload/issuers.py` registers listing identity, approved anchor kind and dataset.
GOOG remains Alphabet's distinct Class C listing; no equity-class equivalence follows.
`preload/extract.py` replays new primary inline-XBRL facts with exact CIK, start/end,
undimensioned consolidated scope, USD units, transformations, precision and locator.
Guidance uses explicit unique prose-range mappings. Body hashes, reviewed observations
and policy configuration remain separate. Unsupported or missing inputs never become
zero or another company's defaults. Alphabet's legacy reviewed observations and
original economic hash are preserved; no retrospective automatic extraction claim.

The API prepares fixed registered profiles offline at startup. Catalog `preload_route`
metadata drives company loading; the client checks exact anchor and company-specific
revenue. Refresh/adoption preserves overrides, notes, additional manual years and
scenario inheritance. Late responses cannot overwrite another company's case.
Acquisition is explicit; API/profile loading performs no network or DCF calculation.

## Peer policy choices

| Component | Meta | Apple |
|---|---|---|
| Retained origin | 2025-12-31 | 2025-09-27 |
| Source period | Nine months to 2026-09-30 | Fiscal nine months 2025-09-28→2026-06-27 |
| First-year revenue | YTD 181.712B + Q4 guidance midpoint 74.5B | YTD 364.357B + prior fiscal Q4 extended by June-quarter revenue growth |
| Prior fiscal Q4 | Not needed | Annual 416.161B − prior YTD 313.695B = 102.466B |
| Starting margin | Estimated full-year revenue less expense-guidance midpoint 177B; legal charge remains included | Reported fiscal Q3 EBIT 35.695B / revenue 109.417B; tariff-refund effects remain included |
| Starting cash PP&E | Inclusive guide midpoint 140B − principal 2.769B×4/3 =136.308B estimate | YTD 6.799B×4/3 =9.065333…B estimate |
| New financed assets | Explicit 3% of cash PP&E estimate | Explicit 1% of cash PP&E estimate |
| Starting expense D&A | YTD cash-flow D&A 19.509B×4/3 | YTD cash-flow D&A 9.973B×4/3 |
| FY2030 growth / margin | 8% / 35% | 5% / 31.5% |
| Annual operating tax | 16%→20% | 18%→20% |
| FY2027–30 cash PP&E changes | +20%,+10%,0%,−5% | +10%,+8%,+6%,+5% |
| Commissioning / incremental WC | 10% prior investment /10% incremental sales | 10% prior investment /5% incremental sales |
| Beta / spread / equity-debt weights | 1.20 / 90bp / 95–5% | 1.05 / 60bp / 85–15% |
| Debt tax shield | 20% | 20% |
| Terminal growth / margin / tax | 3% / 35% /20% | 2.5% / 31.5% /20% |
| Terminal D&A / investment | 14% /20% of revenue | 2.5% /3.5% of revenue |

Management guidance is not an actual result; its midpoint and all extensions are
estimates. Meta's inclusive guide is not substituted directly for operating investment:
remove estimated finance principal once, then add separately estimated financed assets.
Principal is not deducted again from FCFF. Apple uses its actual fiscal periods, not
calendar Q4. SEC submissions checked November 2 still listed the July 31 filing as its
latest 10-Q/10-K; no September result is fabricated.

Annualizing cash-flow D&A is only a labelled forecast starting estimate, not certification
of complete expense-aligned historical D&A. The commissioning rule is not a full vintage/
retirement model. Lease additions, seasonality, acquisitions, legal cash timing and
future intangible amortization remain qualified. Fiscal-origin timing still uses later
information, not a contemporaneous backtest. Forecast SBC stays expensed; historical
CFO-based FCFF keeps its separately disclosed accounting basis.

The reused macro observations are a dated 5.05% Treasury proxy and 3.7% Treasury-based ERP.
Company beta/spread/weights/shield are configured assumptions, not a regression or current
market weights. WACC is 9.2535% for Meta, 8.27275% for Apple; Alphabet remains 8.9408%.
Terminal ratios are independent, not copied from year five or solved to hit an EV.
Bear/Bull retain diagnostic growth/margin±2pp and WACC∓1pp; other ratios inherit Base,
not a separately regenerated investment/WC plan or probabilities.

Primary sources: [Meta 10-Q](https://www.sec.gov/Archives/edgar/data/1326801/000162828026066773/meta-20260930.htm),
[Meta guidance](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Third-Quarter-2026-Results/default.aspx),
[Apple 10-Q](https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/aapl-20260627.htm).
Source manifests retain original approved annual bytes and original macro sources/dates.
Full configurations/rationales: [Meta policy](../data/preload/meta-v1/policy.json) and
[Apple policy](../data/preload/aapl-v1/policy.json).

## Generated results and reproduction

All 37 perpetual-growth inputs are available. Exit multiples, equity/share settings and
years 6–10 stay unfilled. No historical FCFF gaps, source approvals or valuation origins
change. Negative early FCFF stays negative; no input is tuned to hide it.

| Company | FY2026 revenue estimate (B) | First-year growth | First-year margin | Conditional Base EV (B) |
|---|---:|---:|---:|---:|
| GOOGL | 499.159 | 23.91% | 31.81% | 1421.564 |
| META | 256.212 | 27.49% | 30.92% | 944.596 |
| AAPL | 483.583 | 16.20% | 32.62% | 2584.235 |

[Verification JSON](company-data-preparation/registered-preload-verification.json) and
[forecast CSV](company-data-preparation/registered-preload-forecasts.csv) preserve exact
inputs, source hashes and generated annual values. Economic hashes exclude volatile
generation timestamps; saved profiles/requests/results remain separate.

```sh
PYTHONPATH=src .venv/bin/python scripts/prepare_preload_observations.py --ticker META --check
PYTHONPATH=src .venv/bin/python scripts/prepare_preload_observations.py --ticker AAPL --check
PYTHONPATH=src .venv/bin/python scripts/verify_registered_preloads.py --check
.venv/bin/python scripts/prepare_preload.py generate /tmp/meta-profile-new.json --ticker META
.venv/bin/python scripts/prepare_preload.py export /tmp/meta-profile-new.json /tmp/meta-run-new --run
```

Use new profile/run output paths; the CLI refuses overwrite. Refresh diffs expose
sources, policies, rationale, gaps and optional explicitly calculated value changes.
Adding a company later requires eligible operating-company methodology, an approved
consumer anchor, reviewed snapshots/mapping, its own policy and independent tests.
Then add its registration and rebuild the pinned bundle; no new client company branch
is needed. Existing Top50 historical coverage does not establish these prerequisites.
Financials, REITs and other specialized structures still need separate methodology.
No other issuer is activated and no wider historical review resumes here.

Independent Fraction calculations check both new companies' five annual revenue,
EBIT, tax, NOPAT, D&A, investment, WC and FCFF values plus terminal/EV to absolute
error below 1e-30 USD versus the existing precision 50 engine. This verifies arithmetic
under the policy, not forecast accuracy. Test/browser outcomes are in project status.

GOOGL economic hash: `1c652c65ae2cd9cbf5f726f163963434c17514c6f2b1a0afcf229d059a1768fe`.

META economic hash: `0c89bd0947842e24b190b00f25381138ee50f93d6100c6b024e1138727ec547f`.

AAPL economic hash: `3d49d43cb82d7ca8228234e45dbd884f531c20c99a170427de7c6f5e09627d7b`.

Validation: 432 affected tests passed (31 preload, 60 historical/review, 67 API,
274 frontend), production UI build and all offline replays passed. A fresh browser
tab verified both new profiles, fiscal anchors, calculated charts and Apple review
identity. [Meta preview](assets/meta-registered-preload.jpg) and
[Apple preview](assets/apple-registered-preload.jpg). The local runtime uses the
131-entry pinned private bundle; no cloud deployment or repository push.
