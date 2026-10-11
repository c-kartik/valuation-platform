# GE Capex cash, business and separation perimeter

Phase 1H.4 Wave 45; starting HEAD
`447fdc8c7e413aa22f03a3a6f9a5016cfbc379b2`. Bounded documentation-only
review of [three frozen periods](capex-inventory.json), with a
[machine-checkable supplement](capex-ge-scope-inventory.json) and
[original response-body evidence](evidence/ge-capex-response-bodies.json).

**NO-GO; zero safe additional coverage.** All three retain `METHODOLOGY_BLOCKER`
/ `BUSINESS_AND_ASSET_PERIMETER_GATED`. No industrial-only equation, reported-value
acceptance, generic fallback, or specialized methodology is approved. This does
not dispute the reported cash values or change their production missing states.

## Exact selected annual candidates

CIK 40545; nonamended selected 10-Ks. Candidate
`us-gaap:PaymentsToAcquireProductiveAssets`; cash caption **Additions to property,
plant and equipment and internal-use software**. Each has one eligible fact:
context `c-1`, empty dimensions, non-nil, exact USD (`usd`), decimals `-6`,
positive expenditure magnitude and negative statement cash outflow in millions.

| Selected accession | Annual dates | Namespace | Original ordinal | USD magnitude |
| --- | --- | --- | ---: | ---: |
| 0000040545-24-000027 | 2023-01-01–2023-12-31 | http://fasb.org/us-gaap/2023 | 323 | 1,595,000,000 |
| 0000040545-25-000015 | 2024-01-01–2024-12-31 | http://fasb.org/us-gaap/2024 | 352 | 1,032,000,000 |
| 0000040545-26-000008 | 2025-01-01–2025-12-31 | http://fasb.org/us-gaap/2025 | 343 | 1,273,000,000 |

DEI annual resolution independently matches all frozen dates. Exact entity,
context, unit, raw/numeric values, nil/dimensions, relevant supporting original
occurrences and submitted presentation/calculation relationships are retained.
No conflicting eligible signature was found. Million-to-USD conversion and sign
reconcile exactly, without a scope inference from numerical agreement.

## Selected statement and note evidence

All links identify verified original bodies in the evidence fixture. Cash-flow,
basis, PP&E/leases, intangible and insurance notes were reviewed in each selected
filing; primary filings supplement the continuing/discontinued and separation
perimeter. Book additions and dimensioned support are not approved cash operands.

| Period | Cash / basis | PP&E and leases / intangibles / insurance | Discontinued scope / primary |
| --- | --- | --- | --- |
| 2023 | [R5](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R5.htm), [R9](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R9.htm) | [R14](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R14.htm), [R15](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R15.htm), [R20](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R20.htm) | [R10](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R10.htm), [10-K](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/ge-20231231.htm) |
| 2024 | [R6](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R6.htm), [R10](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R10.htm) | [R15](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R15.htm), [R16](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R16.htm), [R21](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R21.htm) | [R11](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R11.htm), [10-K](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/ge-20241231.htm) |
| 2025 | [R6](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R6.htm), [R10](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R10.htm) | [R15](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R15.htm), [R16](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R16.htm), [R21](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R21.htm) | [R11](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R11.htm), [10-K](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/ge-20251231.htm) |

## Per-period and component conclusions

- **2023:** the selected continuing cash presentation includes the pre-Vernova
  industrial portfolio and continuing insurance. HealthCare and other discontinued
  businesses are separately reported. The $1.595bn candidate is not a standalone
  Aerospace subtotal. Later filings recast 2023; their different comparative
  candidate must not replace this frozen selected-accession observation.
- **2024:** following the April 2 Vernova separation, its historical results are
  discontinued in the selected Aerospace filing. The $1.032bn candidate belongs
  to that continuing consolidated perimeter, still including run-off insurance;
  separation alone does not establish a pure industrial cash perimeter.
- **2025:** $1.273bn is the selected continuing consolidated PP&E/software cash
  line, with insurance still present. PP&E additions by Commercial Engines &
  Services, Defense & Propulsion Technologies and Corporate/Other total $1.153bn
  in the asset note. That is not proven to be a complete cash operand. The $119m
  capitalized-software book addition is not an independently evidenced cash
  payment; approximate agreement cannot justify adding it to manufacture Capex.

**Software and PP&E:** intangible notes identify capitalized software alongside
customer-related assets, patents/technology and other intangibles. Qualifying
operational software can fit the [existing primitive](financial-methodology.md);
intangibles placement alone does not establish rejection. Neither the combined
cash caption nor book categories exhaust qualifying software cash scope. Do not
subtract all software, include all intangible additions, or silently approve
extensions. PP&E book cost, depreciation and unpaid additions are not cash.

**Leases/noncash:** PP&E includes ROU operating lease assets; notes distinguish
operating lease cash from ROU assets obtained for new liabilities. Neither is
an additive cash-purchase operand. Do not infer lease principal, noncash additions
or asset-transfer amounts from balances; noncash impairments are not purchases.

**Acquisitions/proceeds:** cash statements separately report principal businesses
purchased, PP&E dispositions, retained ownership sales, insurance securities and
discontinued investing cash. Business consideration is not ordinary PP&E cash;
proceeds must not be netted. Separate lines prove those presentation boundaries,
not exhaustive software/lease/noncash exclusions within the candidate.

**Industrial versus financial:** continuing insurance is evidenced, not presumed
absent because GE operates as Aerospace. Separate insurance investment cash does
not prove zero insurance/shared PP&E or software purchases. No complete industrial
cash allocation or common-period operating-company scope bridge is reported in
the reviewed evidence. Existing [GE operating-perimeter research](operating-income-cvx-ge-perimeter.md)
remains authoritative; do not force insurance through industrial FCFF.

**Separations:** continuing/discontinued classifications are specific to each
selected filing; held-for-sale assets, spin-off cash transfers and transition or
separation expenses are not automatic purchase components. No predecessor
reconstruction, hypothetical standalone expense allocation or later recast
substitution is authorized. GEV's separate decisions remain unchanged.

Reopening requires affirmative exact-period eligible purchase-cash mapping,
an independently evidenced industrial/insurance/shared-asset allocation consistent
with the methodology, and an explicit continuing/discontinued/separation bridge
where required. Component acceptance additionally requires complete cash operands,
signs and non-overlap. Book additions, residuals and recurring labels cannot fill
these gaps. Evidence is exhausted for this bounded pass; no broad retry is planned.

## Remaining inventory and research-pass closure

The original **57 identities = 20 implemented curated approvals + 37 unapproved**.
The **147 direct results** are separate, unchanged preservation scope.

| Remaining classification | Issuers and periods | Total |
| --- | --- | ---: |
| `CONCEPT_POLICY` / `SCOPE_RESEARCH_REQUIRED` | HD 5, QCOM 5, PEP 5, MRK 2 | 17 |
| `DERIVATION` / `COMPONENT_SCOPE_UNPROVED` | NVDA 5, LRCX 5, VZ 5, GEV 2 | 17 |
| `METHODOLOGY_BLOCKER` / `BUSINESS_AND_ASSET_PERIMETER_GATED` | GE 3 | 3 |

AMZN/LLY 10, CVX 5 and Visa 5 remain implemented approvals. NVDA extensions
remain separately gated. These are evidence-backed research outcomes, not a
fresh blanket denial of every control. This closes the current bounded remaining-
issuer Capex research pass, not Phase 1H.4 or historical normalization v1.
No additional safe coverage or approved equations emerge.

Next bounded milestone: consolidate remaining Phase 1H.4 failure priorities and
evidence-exhausted exclusions across measures, using this completed 57-period
Capex reconciliation; select one remaining reusable normalization/design task
before the documented Phase 1H.5 all-constituent validation pass. Do not reopen
blocked issuers without the specified new evidence or jump to valuation/freeze.

## Validation and unchanged production

Three frozen accession/annual identities, three eligible occurrences, exact cash
arithmetic and classification totals reconcile. Forty-two original response bodies
have typed verified byte digests: thirty-nine reused, three primary-filing gap
retrievals. Historical fingerprints and extracted-text representations remain
separate; table equality is not byte equality. Provenance and local/SEC evidence
links are validated; `git diff --check` passes. Frozen inventory, prior issuer
evidence, methodology, production code/policies/tests remain unchanged.

Production carried forward, not remeasured: Capex **167/37/0**, aggregate
**1,905/1,483/11/27/42**, total **3,468**. No tests or corpus rerun.
