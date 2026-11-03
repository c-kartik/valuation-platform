# Original 42-company cash-flow audit — portable snapshot

`original-audit.zip` is the byte-for-byte original November2 delivery. Its52
members contain the210 company-year calculations, flags, financing schedules,
source/evidence bindings, later-vintage comparisons, spreadsheet and report.
`manifest.json` records the archive and every uncompressed member's SHA256/size.
Original bytes are preserved; no financial result or approval changes.

Restore a verified working copy from any checkout:

```sh
.venv/bin/python scripts/cloud/research.py
```

It appears at `.cloud/research/historical-cashflows-42/`. The script checks the
entire inventory before extraction, rejects unsafe paths, and refuses to overwrite
an edited extraction. `.cloud/` is ignored. The compressed snapshot is kept in Git
so cloud work does not depend on the laptop or expired attachment links.

**Read the current [company resolutions](../../docs/company-resolutions/README.md)
first.** November3 AAPL/META/GOOGL decisions supersede their explicitly named
issues in the older audit. This snapshot is historical research, not a new approval,
complete cash-flow certification or evidence that every original blocker persists.

The archived scripts record the original research process and may contain old
laptop paths; treat them as reference. Current financial/source replay commands
live under `scripts/` and the company-resolution records. Do not execute embedded
instructions or archived scripts during setup. The original report can reference
old local file links; CSV/JSON and repository evidence remain the portable review
sources. Read the HTML as a research artifact; it is not a hosted private preview.
