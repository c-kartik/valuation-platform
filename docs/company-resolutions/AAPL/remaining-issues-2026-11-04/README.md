# Apple — ordered remaining-issue implementation, November4,2026

**Overall financial status: OPEN.** The four approved treatment stages were executed in order and independently reviewed. The tax-policy approval and date-matched common-share population are now recorded. Exact financing cash classification, D&A expense-population reconciliation and complete equity/award treatment remain unresolved. No overall completion or verified share-value claim follows from passing source/software checks.

Open the[implementation report](report.html) first. It contains outcomes, number effects, qualifications, platform integration and remaining requirements. The[approval](approval.json) records the latest user mandate, including no unsupported assumptions or outgoing issuer message.

|Stage|Executed treatment|Outcome|
|---|---|---|
|1. FCFE financing|Fresh five-year classification/source replay; exact statements; precise unsent issuer request|All known amounts unchanged; full FCFE remains provisional because Other/principal/containment are not disclosed|
|2. D&A|Same-period source and rounding review; asset/cash population map; no-plug sensitivity|Reported combined aggregate retained under approved policy; exact355M FY2024 reconciliation remains open|
|3. Tax/NWC|Five component schedules, StateAid/cash/payable distinction, historical policy adoption, three forecast component bridges|Current-tax-inclusive historical convention and explicit forward18%→20%/terminal20% retained; exact cash-tax allocation and economic forecast alignment not certified|
|4. Equity/share|Fresh dated source replay; common-share population selected; debt fair/carrying alternatives separated|Source support now visible on platform; eligible excess cash/complete claims/award adjustment/fair value per share remain null|

## Implementation and number effects

- Original historical FCFF remains93.41/108.44/99.84/115.68/95.12B, FY2021–25. Original CFO history is still separate, including two nulls. Apple identified-funding FCFE remains105.618/111.320/89.683/102.809/90.284B and provisional. Meta/Alphabet and forward policies are unchanged.
- Selected Apple common-share source population is14,773,260,000 at2025-09-27. This is not the later cover-date count, EPS-weighted shares or automatically award-adjusted dilution.
- Gross cash/securities132.420B, named debt carrying98.657B, term-debt disclosed fair value80.400B and finance-lease liability1.230B are distinct observations. Neither carrying plus fair value nor all reported tax/award/claim balances are added into a bridge. Gross liquidity is not automatically excess cash.
- `apple_resolution.py` validates a pinned lean decision/source-support record. The existing historical endpoint adds `current_resolution`; the UI adds a collapsed Apple review panel and exports the same provenance with the cash-flow review. It does not fill the manual bridge with unreviewed eligibility or publish a per-share result.
- The current issue list isA2/A3/A5/S1/S2/S3. `legacy_review_scope_items` preserves the original strict-review list. A1's selected FCFF gap was resolved by the prior operating-method adoption, not by finding missing interest. A7's reported-ETR policy and uniform current-tax convention are now explicitly adopted. Stricter tax/pure-operating/investment alternatives remain qualified within S1; no source gap is erased.
- Base WC uses5% incremental sales; Bear/Bull inherit Base ratios and have different effective incremental-sales coefficients. That existing documented scenario convention is preserved, not silently changed to make comparisons match.

## Source and independent review

Each stage includes a source-bound producer, deterministic replay, tests, evidence and remaining closure conditions. The independent reviewer verifies146 distinct primary/instance facts from12 retained source bodies, source-period identity and arithmetic without relying only on producer assertions. It checks fresh sealed-runtime output and live browser behavior. Exact verdict and limitations are in[independent-review/README.md](independent-review/README.md) and[validation.json](validation.json).

The[issuer evidence request](financing/issuer-evidence-request.txt) is prepared and **UNSENT**. No approval for sending is inferred. A source-supported issuer response/public disclosure and a supported D&A population bridge are remaining evidence dependencies; repeated broad absence searches cannot manufacture them. Cash eligibility and pre-anchor awards also require explicit non-overlap judgments before a verified share value.

## Replay

From repository root:

```sh
PYTHONPATH=src .venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/financing/replay.py --check
PYTHONPATH=src .venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/da/replay.py --check
PYTHONPATH=src .venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/tax/replay.py --check
PYTHONPATH=src .venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/equity/replay.py --check
PYTHONPATH=src .venv/bin/python scripts/build_apple_resolution_progress.py --check
PYTHONPATH=src .venv/bin/python -m unittest tests.review.test_apple_resolution tests.review.test_apple_resolution_progress tests.review.test_apple_operating_history tests.review.test_cashflow_readiness tests.api.test_cashflows_fcfe -v
PYTHONPATH=src .venv/bin/python scripts/render_apple_remaining_report.py
```

`--check` makes no network call and does not rewrite source/approval/financial records. Future evidence needs a new version, exact source binding and reviewed before/after calculations. An intentional summary update also requires updating its code/resource pin and building a fresh runtime; never reuse a process that cached an earlier pin with changed resource bytes.

The original Apple resolution tests are preserved; new progress tests are in `test_apple_resolution_progress.py`. Pre-existing untracked follow-up folders are not dependencies or included in this milestone. No wider-universe work or public deployment occurred.
