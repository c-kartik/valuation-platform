# Valuation landing and portfolio discovery

November 9, 2026. Presentation/navigation scope for the three prepared issuers.

`frontend/src/workspace/PlatformApp.tsx` owns the landing page and company query
parameter. `/valuation/` loads only the prepared catalog and displays a brief
introduction, central name/ticker search, supported-company count, three suggested
companies and existing feature summaries. No model runs until a company is chosen.
The count and suggestions come from unique prepared catalog entries; the wider
review universe is not advertised as supported. Search filters on each keystroke
and supports keyboard/pointer selection.

`/valuation/?company=AAPL` (also GOOGL/META) opens the existing workspace.
Company selection updates browser history; Back/Forward and reload honor the URL.
The workspace has an All companies link. Unsupported tickers show the landing
page with a clear message. Catalog failures offer explicit retry. The original
workspace component retains its existing default only when mounted independently
without a requested company. Within-tab model memory remains existing behavior;
these URLs identify companies and do not serialize assumptions.

The portfolio source repository remains authoritative for `index.html`,
`work.html`, the shared stylesheet and navigation on all five pages. Selected Work
shows the platform as the full-width navy feature, Alphabet below left, and the
systematic pipeline below right. The website CV list has the platform first.
The downloadable resume PDF is unchanged. Navigation reads Valuation.

No acquisition, financial normalization, DCF engine, source data, model defaults,
Excel workbook logic or reporting contracts change. Wider issuer work remains
paused. When future issuers are accepted, adding them to the reviewed catalog
updates the platform count; portfolio promotional copy must be reviewed separately.

Validation: frontend regression suite, browser-only build, preserved-asset hash
verification, packaged static-site validation, and actual browser checks of
search, all three selections, direct links/reload/Back, portfolio/CV structure and
phone layouts. Publication evidence is recorded in `valuation-landing-release.json`.

## Copy refinement — November 9, 2026

Public platform naming is Equity Valuation Platform. Removed Automated from
website HTML, including portfolio/CV naming. The search placeholder retains its
dynamic count; the redundant count above it is removed. Feature headings are
Filings Insight, Cash Flow Analysis and Test your assumptions. The user selected Financial Analysis & Equity Valuation as the main hero
headline, with consistent navy styling across both lines. This is copy/style only with no model or data changes.


## Search prominence — November 9, 2026

Reduced the hero headline from 66px to 54px on desktop, 47px to 38px on
phones, and 40px to 34px on narrow phones. Tightened hero padding and the
spacing around the intro and suggested companies so search appears higher.
Search width, input size, typography family, colors and company behavior stay
the same. CSS-only change; no financial or model changes.


## Layout rollback — November 9, 2026

At the user’s request, restored the exact headline sizes and spacing from before
the search-prominence adjustment. The compact layout is superseded. A shorter
headline is being selected separately; feature names, search and company data
remain unchanged.
