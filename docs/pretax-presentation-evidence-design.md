# Pretax presentation-evidence research design

## Scope and decision

Phase 1H.4 Wave 8 defines the evidence needed to investigate the 33 Pretax
candidate periods identified in `pretax-income-concepts.md`. It does not approve
the recurring standard concept, change the Pretax primitive, or authorize a
normalization fallback.

The design decision is **PARTIAL GO FOR A READ-ONLY RESEARCH DIAGNOSTIC**.
Filer-submitted presentation relationships can establish that a concept belongs
to an ordered presentation group whose role definition classifies it as a
`Statement`. The extracted instance can then bind the exact candidate fact to
its context, unit, dimensions, accession, and authoritative annual period. SEC
render artifacts can cross-check report classification and rendered membership.

That combined evidence can classify statement membership, but it cannot by
itself establish equivalence to the project's current equity-method-inclusive
Pretax primitive. Amazon and Chevron already demonstrate different economic
relationships between the recurring concept, equity-method activity, and the
reported tax denominator. Production policy therefore remains blocked.

## Standards-backed evidence boundary

The [SEC EDGAR XBRL Guide, August 2026](https://www.sec.gov/files/edgar/filer-information/specifications/xbrl-guide-2026-08-14.pdf)
provides the relevant structural rules:

- Section 7.2 defines a presentation group as an ordered parent-child graph
  with one role URI and one role-definition string.
- Section 7.3 explains that rendered fact selection depends on concept, period,
  entity, unit, language, and taxonomy-defined dimensions. A presentation
  relationship alone still does not identify one fact occurrence or context.
- Section 7.18 describes `FilingSummary.xml` as an SEC-renderer output that
  records each rendered report and its computed menu category.
- Section 9.2 requires role definitions to follow
  `SortCode - Type - Title`; face financial statements use type `Statement`,
  while notes use `Disclosure`.

The [SEC Inline XBRL overview](https://www.sec.gov/data-research/structured-data/inline-xbrl)
confirms that tagged facts are embedded in the human-readable filing. Inline
placement can therefore corroborate the visible statement location of a fact,
but issuer-authored HTML structure is not a stable generic selection rule.

Evidence authority is deliberately layered:

| Evidence | What it can establish | Research role | Production authority |
|---|---|---|---|
| Selected filing and directory index | Exact accession, primary document, and available artifacts | Required identity and discovery boundary | Existing authority |
| Extracted filing XBRL instance | Exact fact, context, annual period, unit, dimensions, and source identity | Required fact-level join | Existing authority |
| Filer-submitted schema and presentation linkbase | Role definition, statement/disclosure type, concept membership, graph path, and order | Primary presentation evidence | Not yet approved |
| Primary Inline XBRL document | Visible tagged occurrence and local table/section placement | Targeted audit evidence | Research only |
| SEC-generated `FilingSummary.xml`, `MetaLinks.json`, and R-files | Renderer-classified report and rendered fact membership | Strong cross-check and diagnostic shortcut | Derivative; never sole authority |
| Equity-method note disclosures | Whether affiliate activity is included, excluded, separately presented, or net of tax | Required semantic evidence when material | Manual research until a generic rule is proven |

## Research evidence model

The diagnostic should preserve evidence rather than return a normalized value.
For each selected accession and candidate fact it should record:

1. Filing identity: CIK, accession, form, report date, primary document, and
   every source URL used.
2. Candidate identity: namespace, concept, context ID, exact annual start/end,
   unit, dimensions, numeric value, and extracted-instance provenance.
3. Presentation role: role URI, complete role definition, parsed sort code,
   type, and title.
4. Graph membership: root concept, ordered ancestor path, candidate concept,
   relationship order, preferred label, and whether the concept occurs in more
   than one role.
5. Renderer cross-check: Filing Summary report identifier, menu category,
   rendered report name, and matching `MetaLinks.json` or R-file evidence when
   available.
6. Inline occurrence audit: visible caption, document section/table identity,
   and every matching occurrence for the exact concept and context.
7. Equity-method scope: `INCLUDED_PRETAX`, `SEPARATE_PRETAX`,
   `SEPARATE_NET_OF_TAX`, `NO_MATERIAL_ACTIVITY_FOUND`, or `UNRESOLVED`, with
   direct filing evidence. `NO_MATERIAL_ACTIVITY_FOUND` must not be inferred
   from silence.

The output classifications should remain evidentiary:

- `PRIMARY_STATEMENT_MEMBER`
- `DISCLOSURE_ONLY_MEMBER`
- `MULTIPLE_ROLE_MEMBERSHIP`
- `NO_PRESENTATION_MEMBERSHIP`
- `PRESENTATION_DATA_ERROR`
- `EQUITY_METHOD_SCOPE_UNRESOLVED`

None of these classifications means `APPROVED_EQUIVALENT`.

## Deterministic safeguards

- Require the exact selected 10-K accession and the already resolved annual
  period; never select a filing or context from presentation frequency.
- Discover artifacts from the exact SEC filing directory. Do not guess an
  artifact name when the directory is missing or ambiguous.
- Parse the complete role-definition grammar. Do not classify a role as a face
  statement from title keywords alone.
- Preserve every role containing the candidate concept. Do not select the first
  role, smallest sort code, or first rendered occurrence.
- Treat statement membership and fact placement as separate from economic
  scope. A concept on a primary income statement can still be incompatible with
  the current primitive.
- Do not infer equivalence from equal values, ETR plausibility, statement order,
  label similarity, or the absence of a disclosed equity-method adjustment.
- Treat missing, malformed, or inconsistent presentation artifacts as typed
  research failures, not permission to fall back to Company Facts alone.
- Keep SEC retrieval outside normalization. The research diagnostic may fetch
  artifacts, but production normalization must remain pure and network-free.

## Implementation boundary

The smallest next implementation is a development-only diagnostic, separate
from `valuation_platform.normalization` and the production corpus runner. It
should first use the extracted instance plus SEC render artifacts to inventory
all 33 periods because those artifacts expose the renderer's report grouping
without requiring an immediate full DTS processor. A second pass should compare
that output with the filer-submitted schema and presentation linkbase for every
period before any production design is proposed.

Do not add presentation fields to `SECFilingXBRL`, change
`PRETAX_INCOME_POLICY`, or add fallback precedence during this diagnostic.
Inline HTML parsing should remain targeted audit tooling unless the first two
passes show that submitted role evidence is insufficient and a stable generic
HTML rule can be stated and tested.

## Acceptance criteria for the research diagnostic

The diagnostic is complete only when it:

1. attempts all 33 candidate issuer-periods and emits one typed result per
   period;
2. reconciles each candidate to the exact selected accession and annual
   context;
3. preserves every qualifying and conflicting presentation role;
4. distinguishes submitted presentation evidence from SEC-renderer
   derivatives;
5. records explicit failures without dropping a period;
6. produces an issuer-by-issuer equity-method evidence matrix for AMZN, MU, MA,
   CVX, CAT, PM, and LIN; and
7. ends with a separate policy decision: approve, reject, or retain
   `NEEDS_MORE_RESEARCH` for each proven evidence pattern.

Even perfect statement-membership coverage is not a GO condition. A production
fallback requires independently established economic equivalence to the current
Pretax primitive, deterministic machine-checkable evidence, explicit ambiguity
behavior, and regression tests across all affected periods.

## Next step

**Wave 9 result:** the read-only diagnostic and deterministic fixtures are now
implemented. The live 33-period inventory is recorded in
`pretax-presentation-evidence-results.md`. All 33 exact annual candidates occur
in one submitted `Statement` role and one or more submitted `Disclosure` roles,
so all classify as `MULTIPLE_ROLE_MEMBERSHIP`; SEC-renderer artifacts corroborate
all 33. There were no typed data errors.

The policy decision remains **NEEDS_MORE_RESEARCH**. Presentation membership
does not close the equity-method semantic gate, safe new Pretax resolutions
remain zero, and the 12 issuer-extension periods remain outside this pass.

The next step is exact-period equity-method note-evidence research across the
seven candidate issuers, followed by a separately reviewed production design
only if a deterministic economic-equivalence rule is established.
