# S3 — dated cash, debt, claims, classes and award source schedules

**Status: OPEN.** Source preparation is implemented for the existing FY2025
valuation anchors of Apple, Meta and Alphabet. The [source schedules](source-schedules.json)
contain171 original-instance/primary-verified numerical observations, exact dates,
class/award dimensions, source hashes, precision, inline IDs and receipt references.
No approved eligible-cash total, complete financing-claim total, common-share
denominator or fair value per share is inferred from these observations.

## Source-bound amounts prepared

USD billions except shares; amounts retain original precision in the ledger.

| Company | Anchor date | Gross reported cash + named marketable securities | Named debt carrying subtotal | Reported year-end common shares | Unvested RSU count |
|---|---|---:|---:|---:|---:|
| Apple |2025-09-27|132.420|98.657|14,773,260,000|151,574,000|
| Meta |2025-12-31|81.592|58.744|2,530,000,000|115,552,000|
| Alphabet |2025-12-31|126.843|48.543|12,088,000,000|282,000,000|

Gross cash is the sum of named cash/cash-equivalent and marketable-security
captions; Apple's includes separately reported noncurrent marketable securities.
It is **not eligible excess cash**. Operating reserves, restrictions, nonoperating
investment ownership and overlap with consolidated valuation require review.
Other long-term/nonmarketable investments remain separate source observations,
not additional approved cash.

The debt subtotal includes only the explicitly named non-overlapping carrying
captions: Apple commercial paper plus current/noncurrent term debt; Meta reported
noncurrent long-term debt; Alphabet current/noncurrent long-term debt. A missing
separate current-debt line for Meta is not represented as a reported zero.
Finance-lease liabilities are separate support; operating leases remain separate
service-policy support. Notes' principal and fair-value populations are not added
to carrying values. This is not a certified complete or market-value debt total.

## Dated shares and classes

- Apple reports14,773,260,000 common shares atSeptember27,2025, at original
  thousand-share precision. Its later cover-date count is14,776,353,000 at
  October17,2025; the later count does not replace the anchor population.
- Meta reports ClassA2,187,000,000 and ClassB343,000,000 atDecember31,2025.
  Their sum equals its separately reported common total2,530,000,000. Cover
  counts atJanuary23,2026 remain separately dated, more precise observations.
- Alphabet reports ClassA5,822,000,000, ClassB837,000,000 and ClassC5,429,000,000
  atDecember31,2025. Their sum equals its reported total12,088,000,000.
  Its cover prose separately reports ClassA5,822,000,000, ClassB837,000,000 and
  ClassC5,438,000,000 atJanuary28,2026. That exact primary-prose extraction is
  explicitly distinguished from a numerical instance binding and never replaces
  the year-end counts.

Class arithmetic verifies share counts only. The issuer's voting, conversion and
dividend-rights descriptions are preserved as source excerpts; **no economic
class equivalence is adopted**. Weighted-average basic/diluted EPS shares are not
selected as point-in-time valuation denominators. Displayed million/thousand
precision is retained rather than converted into false one-share accuracy.

## Claims and awards

The schedules preserve the actual unvested RSU populations and disclosed
unrecognized service-compensation cost. These are not automatic denominator
additions or fair-value deductions. Future compensation remains expensed in the
operating forecast; the treatment of pre-anchor rights must avoid a second charge
for the same employee services. Vesting, future service/performance, forfeiture,
tax withholding and settlement method must be reviewed before adoption.

Alphabet's notes report3.4bn noncontrolling interest in VIEs and841m redeemable
noncontrolling interest in VIEs. These source amounts are not certified total NCI,
not NCI fair value, and not annual parent-common cash attribution. No sum is used
as a fair-value deduction. Its explicit zero preferred-stock share observation
does not clear all other claims.

Some source claims have multiple precision populations. For example, Apple FY2025
unrecognized tax benefits appear as23.2bn and23.242bn. Both are preserved; no
arbitrary value or zero becomes an equity-bridge deduction. Nor do tax provisions,
legal liabilities or accounting pension balances automatically imply a separate
valuation claim when their effects may already be in forecast cash flows.

## Remaining requirements

1. Review eligible cash/investments, operating cash reserves, restrictions,
   ownership and overlap with the consolidated operating valuation.
2. Review financing coverage and the valuation-date carrying/market-value
   selection, debt costs, lease perimeter and any other financing claim once.
3. Review legal/tax/pension/contingent obligations and preferred/NCI ownership
   coverage. Alphabet requires an actual NCI fair-value basis for parent value.
4. Adopt a dated share population and, for Meta/Alphabet, explicit class treatment.
5. Review pre-anchor award rights and their economic valuation/settlement against
   future SBC expense. No automatic RSU addition, assumed proceeds or duplicated
   employee-service deduction is adopted.

All three companies remain **not ready for verified common-share fair value**.
This limitation is distinct from annual cash-flow availability.

## Reproduce and integrate

From the repository root:

```sh
PYTHONPATH=src .venv/bin/python docs/company-resolutions/implementation-2026-11-03/share-bridge/build.py --check
PYTHONPATH=src .venv/bin/python -m unittest discover -s docs/company-resolutions/implementation-2026-11-03/share-bridge -p 'test_share_bridge.py' -v
```

`--write` regenerates this folder's ledger only. Replay verifies retained original
source bytes, each selected primary/instance numerical representation, entity,
date, unit, precision, class/award dimension, and the two class-count sums. It
makes no network requests and edits no source bank, historical ledger or runtime
consumer. Source and cover dates cannot silently collapse into an EPS denominator.

The existing bridge engine requires reviewed `BridgeComponent`, coverage and
`ValuationShares` declarations. The source schedules prepare their evidence;
they deliberately do not manufacture those decisions. `approved_bridge` fields
remain null, `used_as_valuation_operand` remains false and every issuer status
stays OPEN. A consumer must not sum all source observations: many are parent,
child, alternative-basis or duplicate disclosures of the same population.
