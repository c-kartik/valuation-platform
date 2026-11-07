# Excel model snapshots

The workspace's **Download Excel** action saves the selected company's current
state as a genuine `.xlsx` file. It also appears inside the model and manual
equity editors, where it includes the open draft without submitting, validating
or recalculating that draft. Empty and invalid draft entries can be saved.

Each file contains the active scenario and all other saved scenarios for that
company; it does not silently include other companies. The workbook captures
the input state synchronously at the click before lazy loading the Excel writer.
Later edits/calculation completions cannot change the captured copy.

## Workbook contract

- **Overview:** company, selected scenario, UTC export timestamp, fiscal anchor,
  horizon, terminal method, input/editor scope and calculation status.
- **Assumptions:** all saved scenarios, annual drivers, terminal/alternative-method
  operands, case names and notes. An open model-editor draft replaces the selected
  case in this readable view; the previously saved case remains in exact state.
- **Bridge & Analyst:** manual bridge declarations, open bridge-editor values,
  current analyst form inputs and last calculated analyst bridge. The manual
  bridge is distinct from the issuer-specific analyst bridge.
- **Last Results:** existing operating/manual equity and analyst per-share
  outputs, with stale/incomplete/calculating status retained. An open editor is
  explicitly identified as not yet applied. No new results are inferred.
- **Sources:** existing anchor/source URLs and financial qualifications.
- **Model State:** `valuation-workbook-state-v1` JSON in ordered, Unicode-safe
  chunks of at most 12,000 UTF-16 code units, with a SHA-256 checksum. It includes
  the complete company session, exact decimal strings, parked horizon/method
  inputs, source profile, analysis settings/results, analyst form and result-form
  bindings, and pending editor/touched/reset/replacement state when applicable.

Excel cells display percentages as fractions with percentage formatting. Manual
bridge and analyst money inputs are explicitly USD millions; calculated bridge
and result amounts are USD. Blank is not zero. Ordinary numeric Excel cells
have finite precision; the exact state preserves the original strings. Formula-
like user text is written literally, never as formulas or external links.

This is a **snapshot**, not a recalculating Excel financial model. Editing visible
cells does not update calculated values or the separate exact state. **Loading
workbooks is not implemented.** A future loader must specify which edited values
it consumes, validate the schema/financial contracts and source bindings, and
invalidate/recalculate results; the checksum is integrity, not authentication.

## Implementation and validation

`modelSnapshot.ts` freezes serializable state; `modelWorkbook.ts` writes the XLSX;
`ModelExportButton.tsx` lazily imports that writer, creates a Blob download and
reports retryable failures without editing the model. ExcelJS 4.4.0 is pinned.
Its approximately 261KB compressed writer chunk loads only when downloading;
ordinary calculations do not load it or call a backend. Files stay on-device.

The feature does not touch Python, static financial data or valuation math.
Tests reopen generated files and verify precision-preserving state/checksum,
five/ten-year and pending editor state, blanks versus zeros, inactive/parked inputs,
analyst stale/form bindings, literal text, filenames, click-time capture and
download failure/retry. Browser checks exercise real Apple downloads, including
an unfinished ten-year model, an unsaved manual bridge, changed analyst inputs
and phone-size editor controls. Exported workbooks are imported independently
and visually checked for readable assumptions and bridge formatting.

Dependency audit currently flags ExcelJS's transitive UUID advisory for UUID
v3/v5/v6 custom-buffer APIs. This write-only export does not expose those APIs or
accept an input workbook. Reassess dependencies before adding file import.
