# Alphabet — approved ownership and lease schedules

Review date: November 3, 2026. **Company and G1–G3 remain OPEN.** This implements
the approved disclosure search, containment and explicit missing-value treatment;
it does not claim the missing ownership or valuation inputs have been obtained.
The earlier immutable source bank and November 2 audit are unchanged.

## Issues, treatment, effect and remaining evidence

| Item | Original problem | Implemented treatment | Exact numerical effect | Remaining roadblock |
| --- | --- | --- | --- | --- |
| G1 | Consolidated FCFE is not necessarily cash available to Alphabet's common shareholders. | Reproduce the five consolidated FCFE figures, exclude outside equity contributions from borrowing, retain null parent-common attribution and explicit ownership labels. | $0 change to consolidated series; parent-common values stay null. | Subsidiary-level cash and exact shareholder/rights perimeter are not disclosed in the reviewed sources. |
| G2 | Parent equity requires a supported NCI value, not book NCI or outside contributions. | Preserve reported book NCI and included redeemable NCI as context; require a separate dated fair-value assumption and keep it null pending support. | No automatic deduction; no invented share-value result. | Official capital announcements do not provide a complete cap table or all consolidated NCI fair values. |
| G3 | Lease financing cash mixes commenced liabilities and prepayments, while newly obtained lease assets are noncash. | Verify the financing cash and noncash asset points separately; contain lease cash in debt repayments once; expose rounded prepayments separately and prohibit exact residual principal inference. | No second lease deduction and no addition of noncash assets to cash capex. | No full exact commencement/prepayment/FX/modification/interest cash and economic-investment roll-forward. |

The existing historical FCFF is available under its explicitly stated
reported-CFO/expensed-interest/reported-ETR/cash-PP&E convention. A complete
valuation-adjusted FCFF/FCFE history has not been established by this schedule.

## Search of supporting commentary

Official Waymo announcements were reviewed and retained in `research/` with URLs
and SHA256 hashes in its manifest:

- [2021 $2.5B round](https://waymo.com/blog/2021/06/transforming-mobility-with-confidence-of-world-class-investors/): names investors, not exact Alphabet ownership or annual attributable cash.
- [2024 $5.6B round](https://waymo.com/blog/2024/10/investing-to-bring-the-waymo-driver-to-more-riders/): Alphabet-led financing, no complete cap table or cash allocation.
- [2026 $16B round](https://waymo.com/blog/2026/02/waymo-raises-usd16-billion-investment-round/): reports a $126B post-money company valuation and describes Alphabet as majority investor. It supplies neither the exact stake/rights nor the value of all NCI. It is also later than FY2021–25 and cannot be backdated to those year ends.

The retained FY2021–25 Note 5 disclosures say NCI-attributable losses were not
material. That does not supply an exact zero for NCI cash. Book NCI totals include
redeemable NCI; the two must not be added together. Current-year subsidiary capital
proceeds are not a substitute for allocating underlying operating cash flows.

FY2025 Note 4 distinguishes **$1.988B financing cash** from **$1.606B noncash lease
assets obtained**. The cash includes **$1.1B rounded prepayments for leases not yet
commenced** and is inside debt repayments. Subtracting those displayed figures
does not produce a separately disclosed exact commenced-lease principal amount.

## Reproduction and integration contract

Run from the repository root:

```sh
.venv/bin/python docs/company-resolutions/GOOGL/implementation-2026-11-03/build_schedules.py
.venv/bin/python -m unittest discover -s docs/company-resolutions/GOOGL/implementation-2026-11-03 -p 'test_schedules.py'
```

`schedules.json` is the root integration contract. Its `periods` array contains
five records, one per fiscal year, with:

- `fcff`: exact prior reported-cash-convention amount/fraction and availability;
- `consolidated_fcfe_before_nci_allocation`: numerical amount, source convention and ownership scope;
- `parent_common_fcfe`: null amount, availability reason and blocker;
- `ownership_schedule`: capital cash, book NCI/RNCI, null attributable cash and fair value, source excerpts;
- `lease_schedule`: source-bound finance-lease cash and noncash additions, rounded prepayment fact, containment controls and unresolved timing status.

A consumer may display consolidated FCFE with its ownership label. It must not
silently use it for a parent-common FCFE DCF or per-share value. Null attribution,
NCI fair value and exact commenced principal must remain null. `fcff` availability
under the cash convention does not certify a common historical/forecast basis.

The builder verifies five retained primary-body hashes, eight visible inline lease
or asset points with annual contexts and USD units, and five exact FCFE and five
exact FCFF calculations. Eight additional tests check numerical preservation,
nulls, NCI containment and no lease double counting. These checks validate the
stated schedule; they do not close G1–G3 or the shared model roadblocks.
