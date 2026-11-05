# Browser migration reference assets

These additive Node.js tools preserve the existing Python source and financial
policies. They do not invoke Python, start servers, deploy, change credentials,
or refresh SEC data.

From the repository root, with the already-running loopback API available:

```sh
node scripts/browser-migration/export-baseline.mjs
node scripts/browser-migration/verify-assets.mjs
```

For a separate deterministic perturbation suite, run
`node scripts/browser-migration/export-extra-parity.mjs`. This reads the immutable
baseline requests and writes `extra-parity.json` and `extra-parity-manifest.json`
beside them. It does not replace the baseline or modify the runtime data manifest.
Its seeded analyst/forecast perturbations include signed cash-flow cases,
reverse-solver branches, and rejected malformed/financially inconsistent requests.
The index retains API error-code counts and flags unexpected oracle acceptance;
HTTP 422 `invalid_case` and `calculation_failed` remain distinct recorded outcomes.

The exporter uses `http://127.0.0.1:8135` by default. An explicit loopback-only
`VALUATION_REFERENCE_API` may select another existing reference server. HTTP POSTs
perform calculations only; data acquisition and cloud services are not invoked.
The market-review reference uses the synthetic issuer and therefore has no live
price lookup. Export requests run sequentially to respect worker limits.

`frontend/public/browser-data/manifest.json` maps exact API GET paths to relative
static filenames and pins each asset's SHA-256. Assets preserve decimal strings,
reported facts, approved derived estimates, assumptions, source URLs, dates and
unresolved qualifications. `anchors.json` maps anchor kinds to full source-rich
anchor objects; `policies.json` maps the three scoped tickers to unchanged approved
policy data. `metadata.json` contains result qualifications and static descriptions
used by the browser implementation. Assets are a manually refreshed snapshot,
not live SEC or market access. No other companies are added.

`frontend/src/browser-engine/fixtures/parity.json` is an array of
`{name,path,body,expected,status}` reference records. It includes synthetic legacy
and terminal-method cases, 5/10-year horizons, enterprise/equity scopes, generic
FCFE, scenarios, growth/exit sensitivity, reverse DCF, review-unavailable behavior,
invalid input cases, and AAPL/META/GOOGL Bear/Base/Bull operating and analyst cases.
Numeric results in fixtures are test oracles, not runtime calculations.

`python-source-baseline.json` pins all Git-tracked Python files at migration start.
Existing snapshots are never silently overwritten; an exporter rerun fails if a
Python source differs. The verifier also checks this snapshot, every static asset,
all route bindings, and the fixture integrity. No source files are copied into the
public asset directory. Personal paths and recognizable secret material are
rejected before public assets are written. This exclusion check complements an
explicit allowlist of three issuers and known API routes; it is not a general
secret scanner for arbitrary data.

Limits: these baseline fixtures are broad but not exhaustive. They do not certify
the JavaScript engine; engine parity and malformed-input tests must independently
compare runtime calculations to these oracles. A successful export does not imply
financial readiness beyond each existing named consumer's acceptance contract.
