# SEC registrant-succession identity linkage

## Decision and scope

This document records the Phase 1H.4 Wave 1B design for linking a current
ticker-resolved SEC registrant to a legally continuous historical registrant.
It is an identity and provenance design, not an implementation or a financial
methodology rule.

**Implementation decision: NO-GO.** The SEC evidence establishes the XOM
succession for a human reviewer, but the public structured sources inspected in
this milestone do not expose a stable, directed predecessor-CIK to
successor-CIK relationship. Cross-listed accessions and multiple DEI identities
discover candidates but cannot distinguish succession from joint filing,
parent/subsidiary, co-obligor, or other multi-registrant relationships. The
directional evidence is in narrative filing text whose phrasing and location
are not a stable structured interface. A generic automated resolver is
therefore not approved. XOM remains unresolved in production.

The design below defines the evidence and safety boundary that a later proposal
must satisfy. It does not authorize an XOM mapping, fuzzy matching, or ticker
history traversal.

## Terminology

- **Current ticker-resolved registrant:** the company identity returned for the
  requested ticker by the current official SEC `company_tickers.json` dataset.
  This is always the starting identity.
- **Historical filing registrant:** the legal registrant whose CIK owns or is
  identified on a historical filing needed for the requested period.
- **Accession owner:** the filing identity SEC associates with the submitted
  accession when that identity is explicit. An accession can be indexed under
  multiple registrant CIK archives, so archive placement, submissions
  cross-listing, and the accession-number prefix are candidate evidence rather
  than independent ownership proof.
- **Predecessor registrant:** a registrant whose Exchange Act registration and
  reporting status was legally succeeded by another registrant.
- **Successor registrant:** the registrant that explicitly succeeded to the
  predecessor's registration or reporting status.
- **Joint or multiple-registrant filing:** one filing made for more than one
  registrant. Shared filing metadata does not establish succession.
- **Parent/subsidiary filing relationship:** a filing association caused by
  corporate control, guarantees, or consolidated reporting. Control alone does
  not establish registrant succession.
- **Unrelated ticker reuse:** use of the same symbol by legally unrelated
  issuers at different times. Ticker equality is never continuity evidence.

These identities and relationships are not interchangeable. Historical filing
CIKs must never be rewritten to the current CIK.

## Starting identity and candidate discovery

Resolution must begin with the current official SEC ticker-resolved CIK. A
future workflow may look for a link only after the current registrant's complete
recent and supplemental submissions history cannot satisfy the requested
filing coverage.

Candidate historical CIKs may be discovered only through official SEC
artifacts associated with the current registrant, such as a filing also hosted
under another CIK or filing-level registrant metadata. Candidate discovery is
not link acceptance. The workflow must not begin from a manually selected CIK,
search arbitrary same-name entities, follow historical ticker use, or compare
names approximately.

## Official SEC evidence hierarchy

| Evidence | Authority and machine-readability | Permitted use | Ambiguity risk |
|---|---|---|---|
| Explicit structured predecessor/successor CIK relationship, direction, and effective date in an official SEC artifact | Highest; deterministic if all fields are present | May establish the legal edge without narrative inference | No such public structured field was found in the sources inspected for XOM |
| Filing text explicitly naming the predecessor and successor registrants, legal direction, governing succession rule, and effective date | Authoritative primary filing evidence; narrative rather than schema-stable | Required legal-continuity evidence for XOM; a future parser would also need exact CIK binding and conservative grammar | Wording, section, and document type vary; names alone do not bind CIKs safely |
| Filing cover page and inline XBRL DEI registrant identities | Official and structured within a filing | Bind exact registrant names and CIKs appearing in the filing and corroborate narrative evidence | Multiple identities establish participation, not relationship or direction |
| Transaction, merger, redomiciliation, or registration filing | Authoritative when it explicitly states succession and effective date | Corroborate the legal event and chronology | A merger, common parent, or reorganization does not necessarily transfer registrant status |
| Submissions JSON and supplemental submissions history | Official and machine-readable | Establish filing association, form, dates, and candidate CIKs; determine whether current history is insufficient | Cross-listing can arise from many non-succession relationships |
| SEC archive path and filing detail page | Official and stable | Establish the CIK archive hosting the accession and its filing metadata | Hosting or association alone does not establish legal continuity |
| Accession-number prefix | Stable identifier component but not a complete relationship field | Corroborative only | Filing-agent and multi-registrant patterns make prefix-only ownership inference unsafe |
| Same ticker, similar name, address, SIC, or business description | Weak contextual evidence | Never used for discovery or acceptance | Ticker reuse, reorganizations, affiliates, and coincidental similarity |

No external company-name matching service is required or permitted by this
design.

## Deterministic acceptance gate

A future link may be accepted only if one of these evidence tracks succeeds:

1. **Structured relationship track:** one official SEC source provides the
   exact predecessor CIK, exact successor CIK, directed succession
   relationship, and effective date; or
2. **Corroborated filing track:** one official SEC filing explicitly states the
   predecessor and successor legal roles, direction, and effective date, and
   filing cover or DEI metadata deterministically binds both named legal
   entities to their exact CIKs. A separate official transaction filing may
   supply the same effective date and CIK bindings when the primary filing
   distributes those fields across documents.

Both tracks must also pass every condition below:

- the successor CIK equals the current official ticker-resolved CIK;
- the predecessor candidate was discovered through an official SEC artifact
  associated with the current registrant, not through name or ticker search;
- the evidence explicitly concerns registrant succession, not merely a merger,
  parent/subsidiary relationship, joint filing, guarantee, or consolidation;
- all source CIKs, names, accessions, dates, and direction agree;
- the predecessor's eligible historical filings precede the effective date;
- filing candidates satisfy the effective-interval and collision rules below,
  with no unresolved competing accessions for the requested economic period;
- exactly one predecessor candidate satisfies the gate; and
- following the edge would not repeat a CIK or exceed the traversal limit.

The gate is conjunctive. Cross-listing plus matching names or tickers is not an
alternative evidence track. A form such as `8-K12B` is strong discovery and
corroboration evidence, but the form value alone does not identify both CIKs or
prove the directed edge.

The corroborated filing track is a design requirement, not an approved parser.
Implementation remains blocked until tests across varied real SEC succession
filings demonstrate that exact CIK binding and legal-direction extraction can
be performed without fuzzy names or permissive narrative matching.

## Rejection rules

The future resolver must return a typed unresolved result and must not traverse
when any of these conditions holds:

- no official SEC link evidence is available;
- ticker equality, company-name similarity, shared address, or SIC is the only
  relationship;
- the only evidence is an accession appearing under multiple CIKs;
- the filing establishes only joint registrants, co-obligors,
  parent/subsidiary status, common control, or consolidated reporting;
- legal succession is stated but the exact predecessor or successor CIK cannot
  be bound deterministically;
- relationship direction or effective date is absent or unclear;
- multiple predecessor candidates satisfy candidate discovery and no unique
  candidate satisfies the full acceptance gate;
- evidence sources disagree on CIK, legal role, direction, or date;
- the candidate filing chronology overlaps or follows the transition in a way
  inconsistent with the proposed edge;
- a CIK repeats in the chain; or
- maximum traversal depth is reached before the requested history is satisfied.

No fallback may silently substitute a candidate historical CIK.

## Registrant effective intervals and filing collisions

For an accepted `predecessor_cik -> successor_cik` edge with effective date
`D`, the predecessor conceptually governs historical registrant continuity
before `D`, and the successor governs continuity from `D` onward. This is a
validation interval, not a rule that filing date alone determines ownership.
The actual registrant identity, report period, accession provenance, and legal
transition evidence remain authoritative. A filing that crosses or reports on
the transition boundary requires explicit filing-level evidence.

Filing candidates follow these deterministic rules:

1. **Same accession, multiple CIK indexes:** one accession number is one filing
   candidate even when it appears in multiple linked registrants' submissions
   histories. Preserve every submissions-history association, actual filing
   registrant or accession-owner metadata when SEC exposes it, and all source
   URLs as provenance. Duplicate indexing does not create competing filings and
   must not be silently discarded.
2. **Distinct accessions, same period:** distinct accessions for the same form
   family and report date or economic period remain separate. Evaluate each
   against its actual registrant identity, provenance, and the registrant's
   legal effective interval. Do not merge them or select by filing recency,
   current CIK, predecessor CIK, or input order.
3. **Competing valid candidates:** if distinct accessions remain valid for the
   same requested economic period after applying registrant identity, effective
   interval, form, and filing provenance, do not choose one. If multiple
   plausible identity links remain, return `LINK_AMBIGUOUS`; if identity
   evidence is contradictory, return `LINK_CONFLICT`. If the identity chain is
   already settled, preserve the distinct candidates for the existing filing
   selector, whose same-form/report-date rule fails explicitly with
   `FilingSelectionError`. A future independently approved filing-selection
   rule may resolve the filing choice only after the identity decision is
   settled.
4. **Joint transition filing:** a joint filing may corroborate succession and
   is one provenance-bearing candidate when it has one accession. Its existence
   alone does not determine which registrant governs earlier historical
   periods.

## Chain semantics

The model should support multiple directed edges, for example
`CIK A -> CIK B -> CIK C`, because legal continuity may involve more than one
reorganization. The chain starts at the current CIK and traverses predecessor
edges backward in time. Each edge must independently pass the acceptance gate.

A future implementation should:

- order both registrants and links in current-to-oldest traversal order while
  preserving the legal direction on every link;
- detect a repeated CIK before adding an edge;
- impose a small explicit maximum of eight links as a resource and error bound,
  not as identity evidence;
- require strictly earlier effective dates while traversing backward;
- stop as soon as requested filing coverage is available; and
- return ambiguity or conflict rather than choose among branches.

## Filing-selection interaction

The safe orchestration sequence is:

1. resolve the ticker to the current CIK;
2. retrieve the current registrant's complete submissions metadata;
3. run the existing filing selector for the requested coverage;
4. only if coverage is insufficient, request a registrant-link decision;
5. traverse only an accepted, provenance-bearing predecessor edge;
6. retrieve that predecessor's submissions separately;
7. associate each filing with its actual registrant CIK and applicable chain
   interval; and
8. run selection over the ordered, legally continuous filing candidates.

Histories must not be concatenated first and validated afterward. Candidate
filings must respect the link effective date, retain their actual registrant
CIK, and apply the filing-collision rules above. Existing selection rules remain
unchanged; a future orchestration layer supplies an already validated candidate
sequence.

## Company Facts interaction

Company Facts must be retrieved separately for every registrant CIK whose
filings are selected. Current-CIK facts are not assumed to contain predecessor
history. Observations remain associated by their actual Company Facts source
URL, source CIK, and selected filing accession.

The pipeline must not merge complete Company Facts graphs across registrants or
rewrite predecessor observations to the successor CIK. Only observations tied
to selected filings may proceed to fact selection and normalization. This
avoids accidental mixing of joint filers, post-transition facts, or unrelated
entities while preserving the current company as the output identity.

## Current and historical identity treatment

The standardized company identity remains the current ticker, current CIK, and
current SEC company name. Each historical filing and observation preserves its
actual registrant CIK, accession, and source URL. Chain provenance explains why
that historical registrant is legally continuous with the current company.

This requires a future standardized-output extension before linked history can
be exposed. Historical CIKs must not be overwritten merely to satisfy current
container ownership checks.

## Proposed typed model

The future boundary should remain small and immutable. Illustrative types are:

```python
class RegistrantLinkDecisionStatus(Enum):
    NO_LINK_REQUIRED = "no_link_required"
    LINK_ACCEPTED = "link_accepted"
    LINK_NOT_FOUND = "link_not_found"
    LINK_AMBIGUOUS = "link_ambiguous"
    LINK_CONFLICT = "link_conflict"
    LINK_UNSUPPORTED = "link_unsupported"


class RegistrantRelationshipType(Enum):
    EXCHANGE_ACT_SUCCESSION = "exchange_act_succession"


class RegistrantEvidenceType(Enum):
    STRUCTURED_SUCCESSION = "structured_succession"
    EXPLICIT_SUCCESSOR_DISCLOSURE = "explicit_successor_disclosure"
    TRANSACTION_DISCLOSURE = "transaction_disclosure"
    FILING_REGISTRANT_METADATA = "filing_registrant_metadata"
    SUBMISSIONS_ASSOCIATION = "submissions_association"


@dataclass(frozen=True)
class RegistrantEvidenceParty:
    cik: int
    legal_name: str
    commission_file_number: str | None


@dataclass(frozen=True)
class RegistrantLinkEvidence:
    evidence_type: RegistrantEvidenceType
    source_url: str
    accession_number: str
    form: str
    filing_date: date
    registrants: tuple[RegistrantEvidenceParty, ...]


@dataclass(frozen=True)
class RegistrantLink:
    predecessor_cik: int
    successor_cik: int
    relationship_type: RegistrantRelationshipType
    effective_date: date
    evidence: tuple[RegistrantLinkEvidence, ...]


@dataclass(frozen=True)
class RegistrantLinkDecision:
    current_ticker: str
    current_cik: int
    candidate_historical_ciks: tuple[int, ...]
    status: RegistrantLinkDecisionStatus
    link: RegistrantLink | None
    evidence: tuple[RegistrantLinkEvidence, ...]


@dataclass(frozen=True)
class RegistrantChain:
    current_ticker: str
    current_cik: int
    registrant_ciks: tuple[int, ...]
    links: tuple[RegistrantLink, ...]
```

`registrant_ciks` should be ordered current-to-oldest to match backward
traversal. `links` use the same traversal order, although each link retains its
legal predecessor-to-successor direction. For example, a chain with
`registrant_ciks == (C, B, A)` has `links == (B -> C, A -> B)`. Accepted results
contain exactly one link at each step; unresolved results retain candidates and
evidence without a selected link. No numeric confidence score is appropriate:
the gate passes or yields a typed unresolved status.

Status meanings are exact:

- `NO_LINK_REQUIRED`: current-CIK history already satisfies the request;
- `LINK_ACCEPTED`: exactly one link passes every acceptance condition;
- `LINK_NOT_FOUND`: official sources expose no candidate link evidence;
- `LINK_AMBIGUOUS`: more than one candidate remains viable after validation;
- `LINK_CONFLICT`: official evidence or chronology conflicts, including cycles;
  and
- `LINK_UNSUPPORTED`: successfully retrieved and structurally valid SEC
  evidence describes a relationship or candidate linkage that cannot be
  represented or validated under the approved succession grammar. This
  includes a clear relationship outside predecessor/successor chain semantics.

A relationship decision is emitted only after all evidence required for that
decision has been retrieved and validated enough to evaluate the relationship.
Transport and data failures are domain errors outside this status model:

- existing `SECRequestError` and `SECResponseError` remain the retrieval and
  response-decoding boundary;
- a future `RegistrantHistoryDataError` would cover malformed or invalid SEC
  registrant/linkage metadata; and
- an unexpected parser or schema failure must be raised explicitly, either as
  that domain data error or as its preserved cause, rather than converted into
  a link decision.

An HTTP failure, timeout, unavailable source, malformed JSON, corrupted
response, or schema failure must never become `LINK_NOT_FOUND` or
`LINK_UNSUPPORTED`. The resolver fails explicitly and does not guess. A full
new exception hierarchy is not required by this design.

The evidence model preserves compact facts rather than copied filing prose.
Where a narrative assertion is used, its evidence type and source identify the
filing; a future implementation may additionally preserve a stable document
section identifier if SEC exposes one.

## XOM walkthrough

1. The official ticker dataset resolves `XOM` to current CIK `2115436`,
   ExxonMobil Holdings Corp. The algorithm does not start from CIK `34088`.
2. Current CIK `2115436` has no exact 10-K and no supplemental submissions
   history sufficient for the requested 2021–2025 annual periods.
3. Its submissions associate accession `0000034088-26-000093`, a 2026-08-03
   10-Q for the period ended 2026-06-30, with both CIK `2115436` and archive CIK
   `34088`. This is one accession and therefore one filing candidate, with both
   submissions-history associations preserved as provenance. It discovers CIK
   `34088`; duplicate indexing does not create a competing filing and does not
   accept the link.
4. The 10-Q cover lists ExxonMobil Holdings Corporation and Exxon Mobil
   Corporation as separate registrants with different Commission file numbers.
   Its explanatory note says the filing is separately filed by both entities.
   The filing can corroborate the legal transition, but its joint status does
   not assign earlier historical periods to either registrant. Those facts
   demonstrate why cross-listing alone could be a false positive.
5. The same 10-Q separately states that Holdings became the publicly traded
   parent and successor registrant, that each predecessor share was exchanged
   one-for-one, and that the reorganization did not change consolidated
   business, operations, assets, liabilities, or financial-reporting basis.
6. The current registrant's 2026-07-01 Form 8-K12B, accession
   `0001193125-26-291990`, explicitly identifies Exxon Mobil Corporation as the
   predecessor registrant, ExxonMobil Holdings Corporation as successor under
   Rule 12g-3(a), and 2026-07-01 as the effective date.
7. CIK `34088` contains the required 2021–2025 exact 10-K filings, all before
   that effective date. No competing predecessor was observed.
8. Ticker reuse is rejected as an alternative explanation because ticker
   equality is not used: the legal-direction and effective-date evidence comes
   from the SEC filings, and the two exact CIK identities are corroborated by
   filing metadata.

The evidence therefore supports the human-reviewed directed edge
`34088 -> 2115436`, effective 2026-07-01, and a conceptual chain
`2115436, 34088`. It does not support generic automated acceptance today,
because exact legal-role-to-CIK binding still depends on interpreting variable
narrative text. A future resolver operating under this design would report
`LINK_UNSUPPORTED`; current production has no such status layer and continues
to return no XOM annual history until that parser boundary is separately
designed and validated.

Official XOM evidence:

- [successor Form 8-K12B](https://www.sec.gov/Archives/edgar/data/2115436/000119312526291990/d71068d8k12b.htm)
- [joint 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/2115436/000003408826000093/xom-20260630.htm)
- [SEC filing detail for the joint 10-Q](https://www.sec.gov/Archives/edgar/data/2115436/000003408826000093/0000034088-26-000093-index.htm)

## Required adversarial tests for any future implementation

| Scenario | Required result |
|---|---|
| Same ticker used by an unrelated old issuer | `LINK_NOT_FOUND`; ticker history is ignored |
| Joint filing with two registrants and no succession statement | `LINK_UNSUPPORTED`; relationship observed but no accepted succession edge |
| Parent/subsidiary filing with a shared accession but no registrant succession | `LINK_UNSUPPORTED`; no traversal |
| Multiple predecessor candidates satisfying discovery | `LINK_AMBIGUOUS` unless exactly one passes the full gate |
| Circular A -> B -> A evidence | `LINK_CONFLICT`; cycle rejected |
| Malformed or unavailable SEC source | Explicit retrieval/data error; no link decision emitted |
| Successfully parsed evidence outside supported succession grammar | `LINK_UNSUPPORTED`; no traversal |
| No authoritative linkage evidence | `LINK_NOT_FOUND`; no traversal |
| Explicit successor language with inconsistent effective date or filing chronology | `LINK_CONFLICT` |
| Distinct accessions remain valid for the same period but support multiple plausible links | `LINK_AMBIGUOUS` |
| Distinct accessions contain contradictory identity or chronology evidence | `LINK_CONFLICT` |
| Accepted chain still has distinct same-form/report-date filing candidates | Preserve both; existing selector raises `FilingSelectionError` |
| Valid one-step structured succession | One accepted edge with complete provenance |
| Valid A -> B -> C chain | Two independently accepted edges in order, with cycle and depth checks |
| Same evidence supplied in different order | Identical decision and evidence ordering |

Tests must also cover shared names, addresses, and SICs without succession;
conflicting direction; duplicate evidence; and a chain reaching the depth limit.

## Recommended future module boundary

Ticker resolution should remain exactly `ticker -> current SEC identity`. A
future `src/valuation_platform/sec/registrant_history.py` would own candidate
discovery, evidence validation, typed link decisions, and bounded chain
traversal. It would use `SECClient` and existing submissions models but would
not alter ticker parsing, pure filing selection, Company Facts parsing, or
financial normalization.

A separate orchestration change would later ask this module for a chain only
when current history is insufficient, retrieve predecessor submissions and
Company Facts independently, and pass provenance-bearing filing candidates to
the existing pure selectors. No database or persistent identity registry is
proposed.

Because the current decision is NO-GO, neither module nor orchestration change
is approved in Wave 1B. The next generalization work should proceed without
silently resolving XOM.
