# Ticker onboarding — Scope 1 first, Scope 2 second

Reusable checklist, November 7, 2026. This records a path for future tickers;
it does not resume the paused universe review or authorize an unnamed issuer.
Copy this structure into a named issuer record when the user authorizes work.

## Identity and consumer declaration

- [ ] Name ticker, stable security ID/share class, issuer CIK, currency, dates and
  intended consumer. Check dated aliases and multiple-class mappings.
- [ ] Review the issuer's existing preparation/resolution records and original
  freeze/pause status before gathering or changing facts.
- [ ] Classify generic operating-company suitability. Use a dedicated methodology
  gate for financial/specialized businesses; do not force generic FCFF acceptance.
- [ ] Declare explicit history, forecast horizon and product scope. Identify
  source facts, derived estimates, analyst assumptions and unresolved fields.

## Gate A — evidence-accounted preparation

- [ ] Trace each observation/omission to sources and periods, including incomplete
  history, revised filings and known conflicts.
- [ ] Reconcile retained facts and transformations under the issuer's existing
  approved policies; preserve missing values and original evidence.
- [ ] Update `docs/company-data-preparation/<TICKER>...` and applicable shared
  register/issuer resolution records when preparation/policy changes are in scope.
- [ ] Record evidence-accounted status separately from financial-input sufficiency.

Passing Gate A is not whole-history provenance or valuation readiness.

## Gate B — Scope 1 financial-input sufficiency and DCF acceptance

- [ ] Establish the named historical FCFF/FCFE consumer's required inputs and
  consistent perimeter; trace each material estimate and its limitations.
- [ ] Define supported forward assumptions/terminal policy, financing, ownership,
  awards, cash/investment/debt/claim treatment and share denominator.
- [ ] Keep history versus forecast conventions explicit; no automatic calibration
  across incompatible bases, duplicate debt/lease/SBC charges or forced parity.
- [ ] Reconcile arithmetic/intermediate values and matched sources; test Base,
  Bear/Bull, changed assumptions, invalid inputs and supported horizon/methods.
- [ ] Require explicit inputs for years 6–10 unless a separate extension policy
  is approved; an optional UI is not approval to fabricate defaults.
- [ ] Independently compare browser outputs to the retained reference/approved
  expectations and preserve user input/revision/cancellation safeguards.
- [ ] Verify chart, source/qualification, equity/share and Excel snapshot consumers
  against the named scenario and exact submitted inputs.
- [ ] Record scope acceptance, qualifications, remaining blockers, versions and
  test evidence. Only then register/release the issuer under the named contract.

Do not copy AAPL/META/GOOGL economic assumptions into another issuer merely
because its engine/schema is shared. Scope 1 completion is per issuer and consumer.

## Gate C — Scope 2 shared market-data sufficiency

- [ ] Satisfy the [market contract](market-data-contract.md): permitted sources,
  identity/class mapping, prices/actions, adjustment bases, timing and vintages.
- [ ] Record metric-level coverage/definitions and availability. Review quarterly/
  TTM extensions separately from the annual package.
- [ ] Verify manual refresh/export/versioning and browser-only consumption without
  exposing provider keys or changing the original Python pipeline.

## Gate D — separate acceptance for each Scope 2 feature

- [ ] **S2.1 Overview:** supported metrics, truthful frequency/units, traceable
  tooltips, normalized/linked panels, missing/stale states and accessible controls.
- [ ] **S2.2 Return drivers:** compatible EPS/price/share/split basis, positive
  denominator gate, exact factor reconciliation and separate dividend treatment.
- [ ] **S2.3 Events:** sourced release timing, calendar mapping, benchmark/window
  rules, sufficient history, reproducible AR/CAR and disclosed exclusions/sample.
- [ ] **S2.4 Dip finder:** separately approved current-date valuation contract,
  complete scenario equity/share bridges, compatible price date/class/currency,
  distinct discount/upside/drawdown and explicit freshness/threshold controls.
- [ ] Record feature status independently. An available price chart does not
  establish DCF readiness; a qualified DCF does not establish event-study coverage.
- [ ] Keep S2.4H historical value curves deferred until its own vintage acceptance.

## Per-issuer acceptance record template

| Field | Required record |
| --- | --- |
| Authorized work | User request/date; issuer/security; named consumer |
| Preparation | Evidence-accounted status and limitations |
| Scope 1 | Financial-input sufficiency; acceptance/qualifications; remaining blockers |
| Scope 2 | Separate S2.0/S2.1/S2.2/S2.3/S2.4 statuses and evidence |
| Sources and dates | Package/filing IDs, periods, available-at precision, data/model dates |
| Methodology | Versioned definitions, approved estimates and rejected alternatives |
| Validation | Tie-outs, tests, independent review and browser/release evidence |
| Maintenance | Refresh owner/procedure, dependency changes and invalidation rules |
| Next action | Specific unmet gate or bounded next milestone |

Maintain the [Scope 2 ticker register](scope-2-ticker-register.md) alongside issuer
records. A completed implementation step cannot close an unmet parent scope.
