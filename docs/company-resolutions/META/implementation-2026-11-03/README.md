# Meta approved treatment implementation — November 3, 2026

**Company status: OPEN.** See [decision log](decision-log.json),
[review results](review-results.json), [exact source points](numeric-source-points.json),
[retained source manifest](all-primary-source-manifest.json), and [validation](validation.json).

- **M1:** Reviewed all fifteen FY2021–25 quarterlies and annual/current evidence.
  Three exact FY2022 cash-pool comparative bridges show borrowing can be included
  in Other. The pool ended December 2, 2022, but a complete annual cash/FX/noncash
  bridge is not disclosed. Do not turn its unknown annual funding amount into zero.
- **M2:** Separately scheduled total versus notes-only expensed interest,
  incurred capitalized interest, cash paid and finance-lease cash interest.
  Capitalized incurred interest of $283m/$384m/$535m in FY2023/24/25 does not
  establish cash paid. FY2021/22 supplemental interest-paid rows of zero do not
  establish all financing interest was zero: lease cash interest is separately
  $15m/$16m. No mechanical extra interest add-back is adopted.
- **M3:** Retain reported historical tax and CFO. Explicit forward operating-tax
  assumptions remain 16/17/18/19/20%, with terminal 20%; the charge/reversal
  schedule distinguishes reported accounting provision, cash tax and assumptions.
  [Executed before/after valuation parity](../../implementation-2026-11-03/basis-bridge/valuation-parity.json)
  confirms no change to Base/Bear/Bull inputs or EV.

All five current expense-based cash-convention FCFFs are preserved. Five
identified-funding FCFE calculations remain provisional. No original source or
accepted ledger is overwritten and no broader unlevered investment/tax bridge
is represented as reconciled.

Offline reproduction and tests:

```sh
PYTHONPATH=src .venv/bin/python docs/company-resolutions/META/implementation-2026-11-03/build_review.py
PYTHONPATH=src .venv/bin/python -m unittest discover -s docs/company-resolutions/META/implementation-2026-11-03 -p 'test_*.py' -v
```

The source-extension script records retrieval; deterministic replay uses retained
bodies. Review [script options](build_review.py) before deliberately regenerating
versioned workpapers. This method implementation does not certify missing inputs.
