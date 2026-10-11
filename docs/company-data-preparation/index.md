# Company data preparation register

Preparation records for all **40 GENERALIZATION_REQUIRED issuers** in the frozen
[validation matrix](../universe/phase-1h5-issuer-validation.json). Alphabet has one
record for GOOG/GOOGL. The other ten issuers remain in that authoritative matrix,
not omitted from universe validation. This is preparation, not fresh SEC review,
new support certification or a replacement for historical normalization v1.

## Shared measure contracts and provenance

### Standing maintenance requirement

As required by [AGENTS.md](../../AGENTS.md), any milestone changing retrieval,
filing/period selection, sorting/classification, normalization, derivation or
valuation-input preparation must update each affected issuer record in that
same milestone. Update this index when shared contracts or issuer mapping change.
This applies to documentation/input preparation as well as executable changes.

Each update must explain the original conflict, exact sources/evidence,
considered treatments, chosen resolution/rationale, affected periods/policies,
validation and unresolved limitations. Distinguish facts, SEC-supported
derivations, analyst classifications/estimates, manual inputs and external data.
Preserve superseded decisions with their date/version and replacement reference;
link detailed evidence, mark unreviewed details, and explain limitations relevant
to eventual valuation use. Preparation is not fresh review or readiness approval.

The [MSFT bundle review](MSFT.md#reviewed-fy20252026-partial-input-bundles)
applies this requirement to two exact periods without changing other records'
carried-forward financial conclusions.

Every record tracks all 17 measures, frozen history, retained execution/retrieval
outcomes, normalization/source kinds, policy references, unresolved states,
assumption/external-input status and validation tasks. Counts are carried forward,
not a new corpus run. Direct output can include curated scope approval; it is
not necessarily generic Company Facts alone. Exact accessions/occurrences/digests
must come from linked inventories; missing compact-corpus metadata stays unreviewed.

- SEC-reported: original reported observations, including submitted precision.
- SEC-supported derivation: approved formula and operands; never an estimate.
- Analyst classification/estimate: separate scenario and reviewed assumptions;
  no estimates have been approved/populated by preparation.
- Manual inputs: none in the initial register/frozen historical outputs. The
  subsequent Alphabet FY2024 bundle includes an explicit source-verified rounded
  note transcription, not an allocation estimate; future overrides still need
  explicit provenance.
- External data: none supplied here; valuation reference links are methodology,
  not issuer input values.

Generic policies are fixed by the [v1 contract](../historical-normalization-v1-freeze.md)
and source snapshot, not invented per-measure version numbers. See
[concept policies](../../src/valuation_platform/normalization/concepts.py),
[balance policies](../../src/valuation_platform/normalization/balance_sheet.py),
[shares](../../src/valuation_platform/normalization/diluted_shares.py),
[derived ETR/MSFT D&A](../../src/valuation_platform/normalization/derived.py),
[NWC policies](../../src/valuation_platform/normalization/operating_nwc.py).
Curated families: Pretax v1 (MA/CVX), Operating Income derivation v1
(LLY/JNJ/MRK/KLAC/IBM), D&A v1 (Visa), Capex v1 (AMZN/LLY), v2 (CVX),
v3 (Visa). Registries remain exact-accession only. No future/amended extension.

Unknown compatibility is not incompatibility; an analyst subtotal cannot remove
normalization blockers or certify FCFF. [Timing contract](../financial-timing-readiness-design.md).

Reviewed bundles are opt-in preparation, not automatic policies/defaults:
[MSFT pair](MSFT.md#reviewed-fy20252026-partial-input-bundles),
[AAPL single level](AAPL.md#reviewed-fy2025-partial-input-bundle), and
[Alphabet single rounded level](GOOGL.md#reviewed-fy2024-partial-input-bundle).
The Alphabet duration-tagged note is not fabricated as an instant SEC fact;
manual interpretation, raw source metadata and rounded precision remain explicit.
[Practical-use obstacles and one bounded decision](../analyst-operating-nwc-design.md#remaining-obstacles-and-bounded-valuation-use-decision)
keep all three diagnostic-only, without another broad research queue or new
AAPL/MSFT financial approvals.

## Issuer records

Register mapping/680 measure rows and local references were checked in this
milestone. The separate analyst foundation passed 41 focused and 640 full-suite
tests, including retained AAPL/MSFT/GOOGL arithmetic. These checks do not certify
unreviewed company disclosures or turn GENERALIZATION_REQUIRED into SUPPORTED.

| Issuer securities | CIK | Selected history | Record |
| --- | ---: | ---: | --- |
| NVDA | 1045810 | 5 | [NVDA](NVDA.md) |
| AAPL | 320193 | 5 | [AAPL](AAPL.md) |
| MSFT | 789019 | 5 | [MSFT](MSFT.md) |
| AMZN | 1018724 | 5 | [AMZN](AMZN.md) |
| GOOGL, GOOG | 1652044 | 5 | [GOOGL](GOOGL.md) |
| AVGO | 1730168 | 5 | [AVGO](AVGO.md) |
| MU | 723125 | 5 | [MU](MU.md) |
| TSLA | 1318605 | 5 | [TSLA](TSLA.md) |
| AMD | 2488 | 5 | [AMD](AMD.md) |
| LLY | 59478 | 5 | [LLY](LLY.md) |
| XOM | 2115436 | 0 | [XOM](XOM.md) |
| JNJ | 200406 | 5 | [JNJ](JNJ.md) |
| V | 1403161 | 5 | [V](V.md) |
| INTC | 50863 | 5 | [INTC](INTC.md) |
| WMT | 104169 | 5 | [WMT](WMT.md) |
| ABBV | 1551152 | 5 | [ABBV](ABBV.md) |
| MA | 1141391 | 5 | [MA](MA.md) |
| CSCO | 858877 | 5 | [CSCO](CSCO.md) |
| LRCX | 707549 | 5 | [LRCX](LRCX.md) |
| PLTR | 1321655 | 5 | [PLTR](PLTR.md) |
| AMAT | 6951 | 5 | [AMAT](AMAT.md) |
| CVX | 93410 | 5 | [CVX](CVX.md) |
| CAT | 18230 | 5 | [CAT](CAT.md) |
| MRK | 310158 | 5 | [MRK](MRK.md) |
| PG | 80424 | 5 | [PG](PG.md) |
| KO | 21344 | 5 | [KO](KO.md) |
| PM | 1413329 | 5 | [PM](PM.md) |
| HD | 354950 | 5 | [HD](HD.md) |
| NFLX | 1065280 | 5 | [NFLX](NFLX.md) |
| KLAC | 319201 | 5 | [KLAC](KLAC.md) |
| TXN | 97476 | 5 | [TXN](TXN.md) |
| GEV | 1996810 | 2 | [GEV](GEV.md) |
| SNDK | 2023554 | 2 | [SNDK](SNDK.md) |
| ORCL | 1341439 | 5 | [ORCL](ORCL.md) |
| LIN | 1707925 | 5 | [LIN](LIN.md) |
| IBM | 51143 | 5 | [IBM](IBM.md) |
| QCOM | 804328 | 5 | [QCOM](QCOM.md) |
| VZ | 732712 | 5 | [VZ](VZ.md) |
| PEP | 77476 | 5 | [PEP](PEP.md) |
| MCD | 63908 | 5 | [MCD](MCD.md) |
