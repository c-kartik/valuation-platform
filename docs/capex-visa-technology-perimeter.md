# Visa Capex cash technology/software perimeter

Phase 1H.4 Wave 35; starting HEAD
`362c6d22631b9a873153cb0c26d0ef273df6490d`, clean `main`, thirteen ahead
of origin. Documentation-only; no push, policy change, tests or corpus rerun.

## Decision

**NO-GO for current acceptance or a component equation; PARTIAL GO for a
bounded technology-perimeter methodology review.** All five frozen Visa
periods retain `CONCEPT_POLICY` / `SCOPE_RESEARCH_REQUIRED`, with zero approved
additional coverage. This is an unresolved eligibility question, not a
demonstrated economic denial or a claim that software cash is zero.

The selected filings evidence consolidated cash purchases of property,
equipment and technology. Their technology class includes purchased and
internally developed software, with acquisition-origin technology also entering
the book class. The existing [Capex primitive](financial-methodology.md) is
gross cash expenditure to acquire PP&E; it does not approve every capitalized
software payment simply because reported alongside PP&E. This research does
not redefine that primitive. An explicit application of its asset perimeter
to Visa's technology is needed before exact reported-value acceptance can be
designed. If technology must instead be stripped out, no exhaustive cash
technology operand or independently complete PP&E-only cash total is evidenced.

Five reported-value candidates could become design candidates **conditionally**
on that methodology decision; none is presently approved. There is no generic
productive-assets fallback, issuer-extension approval or component equation.
Visa's [D&A approvals](depreciation-amortization-scope-evidence-design.md)
establish an expense scope, not the cash purchase perimeter or FCFF readiness.

## Frozen identities and reported cash

The [five-row supplement](capex-visa-technology-inventory.json) records exact
contexts, original occurrence ordinals, namespace, unit, raw/numeric value,
decimals, nil status, dimensions, supporting occurrences and selected source
relationships. It extends research without editing the frozen
[57-row inventory](capex-inventory.json).

| FY / selected accession and cash-flow statement | Exact annual dates | Reported cash USD | Context / ordinal | Classification |
| --- | --- | ---: | --- | --- |
| [2021 / 0001403161-21-000060](https://www.sec.gov/Archives/edgar/data/1403161/000140316121000060/R8.htm) | 2020-10-01–2021-09-30 | 705,000,000 | `ia9ffd445549f441e9121047e42233bae_D20201001-20210930` / 547 | Scope research required |
| [2022 / 0001403161-22-000081](https://www.sec.gov/Archives/edgar/data/1403161/000140316122000081/R9.htm) | 2021-10-01–2022-09-30 | 970,000,000 | `i501005a952cc4b068e83ae86d38ef829_D20211001-20220930` / 556 | Scope research required |
| [2023 / 0001403161-23-000099](https://www.sec.gov/Archives/edgar/data/1403161/000140316123000099/R9.htm) | 2022-10-01–2023-09-30 | 1,059,000,000 | `c-1` / 541 | Scope research required |
| [2024 / 0001403161-24-000058](https://www.sec.gov/Archives/edgar/data/1403161/000140316124000058/R9.htm) | 2023-10-01–2024-09-30 | 1,257,000,000 | `c-1` / 516 | Scope research required |
| [2025 / 0001403161-25-000089](https://www.sec.gov/Archives/edgar/data/1403161/000140316125000089/R9.htm) | 2024-10-01–2025-09-30 | 1,482,000,000 | `c-1` / 546 | Scope research required |

Each is one eligible annual nondimensional non-nil exact-USD occurrence of
`us-gaap:PaymentsToAcquireProductiveAssets`, positive XBRL magnitude, decimals
`-6`, displayed as a negative outflow in USD millions under “Purchases of
property, equipment and technology.” The namespaces are
`http://fasb.org/us-gaap/2021-01-31` and `http://fasb.org/us-gaap/{2022…2025}`.
CIK 1403161 and annual DEI reconcile to the frozen accession/period identity.
The investing calculation weight is `-1.0`; it does not decompose technology
cash. No exact annual nondimensional direct PP&E or intangible cash-payment
fact was found in these selected instances. Repeated note prose is not a
second cash occurrence; dimensioned book assets are not annual cash operands.

## Evidence and component findings

The selected accounting policy consistently describes purchased and internally
developed software and acquisition-origin technology. Preliminary-stage
internal/external costs are expensed; qualifying application-development costs
are capitalized, then amortized when ready for use. Earlier filings explicitly
identify internally developed software primarily with VisaNet. Acquired
technology enters at fair value, so technology book additions do not identify
organic cash purchases. Customer relationships, trade names and other acquired
rights are separately presented as intangible assets, not conflated with the
technology class. These are asset-accounting facts, not cash allocation proofs.

| FY | Property/technology evidence | Acquisition and software-cash limitation |
| --- | --- | --- |
| 2021 | [Property note](https://www.sec.gov/Archives/edgar/data/1403161/000140316121000060/R15.htm): technology gross $4,320m within total property/equipment/technology $7,674m; net total $2,715m. | Acquisition cash $75m is separate; pending Tink/Currencycloud deals are not current cash operands. License commitments are future payments, not current software cash. |
| 2022 | [Property note](https://www.sec.gov/Archives/edgar/data/1403161/000140316122000081/R16.htm): technology gross $5,291m; total gross $8,881m; net $3,223m. | Acquisition cash $1,948m is separate. Tink PPA identifies $245m technology and $90m customer relationships; Currencycloud allocation mixes asset classes. These are acquired fair values, not components to subtract from the $970m cash line. |
| 2023 | [Property note](https://www.sec.gov/Archives/edgar/data/1403161/000140316123000099/R16.htm): technology gross $5,197m; total gross $8,780m; net $3,425m. | Actual reported acquisition cash zero does not prove zero technology payments. Prior-year Tink PPA and pending Pismo consideration are not current purchase operands. |
| 2024 | [Property note](https://www.sec.gov/Archives/edgar/data/1403161/000140316124000058/R16.htm): technology gross $5,660m; total gross $9,297m; net $3,824m. | Acquisition cash $915m is separate. Pismo's $929m consideration includes a $139m mixed non-goodwill allocation; it does not quantify technology cash in the $1,257m line. |
| 2025 | [Property note](https://www.sec.gov/Archives/edgar/data/1403161/000140316125000089/R17.htm): technology gross $6,599m; total gross $10,106m; net $4,236m. Assets not yet placed in service replace the prior construction-in-progress caption. | Acquisition cash $887m is separate. Featurespace's $946m consideration and $152m mixed non-goodwill allocation are not a cash technology operand. Commitments now combine sponsorships/software arrangements, not an annual Capex allocation. |

The machine-readable supplement retains each selected acquisition, intangible,
lease and commitment note's text and binds it to original response bytes in
the [evidence fixture](evidence/visa-capex-response-bodies.json). Acquired
technology and customer relationships can both be part of a business purchase;
do not add acquisition cash to Capex or allocate consideration by PPA ratios.
Separate acquisition cash presentation supports non-overlap of reported lines,
not an independently complete PP&E-only technology exclusion equation.

Unpaid purchases are disclosed separately in the cash-flow supplemental
schedule: $41m / $56m / $96m / $52m / $59m for 2021–2025. They are not cash
paid and are not added or used to turn book growth into cash. Operating ROU
assets obtained in exchange for obligations are $96m / $74m / $82m / $410m /
$231m, respectively; these are noncash, not investing purchases. ROU assets
are in Other assets and operating lease costs are separately described.
2021/2022 state no finance leases at the balance-sheet date; later silence
does not prove annual finance-lease cash or additions are zero. No isolated
lease adjustment is approved.

Investment-security proceeds, derivative settlements and other investing
cash are separately presented. Other investing cash is not an exhaustive
PP&E-disposal schedule in this review; no proceeds netting, gross-up or
zero-proceeds assumption is justified. Software-license commitments through
2024, and the broader 2025 commitments, establish future obligations rather
than actual annual paid amounts or their capitalization. No missing component
is inferred to be zero. No hosting/service amount or incentive allocation is
invented from silence or a book balance.

## Completeness, reconciliation and next step

The reported composite cash fact is directly supported, but its technology
eligibility has not been decided under the current primitive. The files do
not establish separable annual cash expenditures for all purchased versus
developed software, acquisition-origin technology versus ordinary purchases,
or a complete traditional-PP&E-only subtotal. Do not manufacture such a split.
This does not mean every composite component is economically ineligible.

All five displayed cash amounts reconcile exactly to the selected facts
(USD millions × 1,000,000); no rounding tolerance is needed. Total property/
equipment/technology gross less accumulated depreciation/amortization equals
net exactly at disclosed precision: 7,674−4,959=2,715; 8,881−5,658=3,223;
8,780−5,355=3,425; 9,297−5,473=3,824; 10,106−5,870=4,236 (USD m).
These book identities are not purchase equations, timing bridges or proof
of cash completeness. No book delta, residual or D&A total is used as approval.

Next bounded milestone: methodology review of the five Visa technology
perimeters against the existing cash PP&E primitive. Explicitly decide whether
the evidenced purchased/developed operational software asset class is already
eligible, or whether accepting it would change the contract. Compare the
existing generic, META gross-cash and AMZN/LLY/CVX treatments only for impact;
do not broadly re-research issuers or retrospectively invalidate approvals.
If inclusion is justified, the smallest following step is exact-accession
reported-value scope design. If exclusion is required, the unquantified cash
split remains a durable blocker without new independent allocation evidence.
No primitive change or impact decision is implemented by this research.

## Provenance and validation

Sixty-five original response bodies are retained as lossless gzip/base64 with
`sha256_sec_response_body_bytes`, byte lengths, exact accession and URL. Fifty-five
are reused and ten are targeted gap retrievals; forty-five prior mandatory
artifact/note hashes match retained original bytes. Reused retrieval metadata
is unknown rather than fabricated; new requests record HTTP status/time.
Derived report text is not the hashed representation. Five historical index
fingerprints remain separately labeled not independently verified in this
milestone and are not acceptance evidence; no historical hash is overwritten.

Validation covers five unique frozen identities, entity/annual contexts,
occurrence/unit/sign provenance, classification counts, raw calculation
relationships, supported cash/book arithmetic and relevant local/SEC evidence
links. The 57-row inventory is byte-unchanged; its five Visa and other 37
unapproved controls remain unapproved. No code, policies, schemas or tests
changed. Production is carried forward, not remeasured: Capex **162/42/0**;
aggregate **1,900/1,488/11/27/42**, total **3,468**. No tests or corpus rerun.
