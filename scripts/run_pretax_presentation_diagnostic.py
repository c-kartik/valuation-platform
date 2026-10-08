#!/usr/bin/env python3
"""Run the development-only 33-period Pretax presentation diagnostic."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import os
from pathlib import Path
import sys
from typing import Mapping, Sequence, TextIO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from valuation_platform.research.pretax_presentation import (  # noqa: E402
    EvidenceOutcome,
    PeriodEvidenceResult,
    analyze_period,
    discover_artifacts,
    equity_method_matrix,
    failure_result,
    parse_presentation_memberships,
    parse_renderer_evidence,
    parse_role_definitions,
    serialize_inventory,
)
from valuation_platform.sec import (  # noqa: E402
    ResolvedAnnualPeriod,
    SECClient,
    fetch_filing_xbrl,
    load_and_select_filings,
    resolve_annual_period,
    resolve_ticker,
)


CANDIDATE_ACCESSIONS: Mapping[str, tuple[str, ...]] = {
    "AMZN": ("0001018724-22-000005", "0001018724-23-000004", "0001018724-24-000008", "0001018724-25-000004", "0001018724-26-000004"),
    "MU": ("0000723125-21-000065", "0000723125-22-000048", "0000723125-23-000054", "0000723125-24-000027", "0000723125-25-000028"),
    "MA": ("0001141391-22-000023", "0001141391-23-000020", "0001141391-24-000022"),
    "CVX": ("0000093410-22-000019", "0000093410-23-000009", "0000093410-24-000013", "0000093410-25-000009", "0000093410-26-000078"),
    "CAT": ("0000018230-22-000050", "0000018230-23-000011", "0000018230-24-000009", "0000018230-25-000008", "0000018230-26-000008"),
    "PM": ("0001413329-22-000011", "0001413329-23-000025", "0001413329-24-000013", "0001413329-25-000013", "0001628280-26-005939"),
    "LIN": ("0001628280-22-004180", "0001628280-23-005434", "0001628280-24-007424", "0001628280-25-007990", "0001628280-26-011430"),
}
EXPECTED_PERIOD_COUNT = 33


def run_diagnostic(client: SECClient) -> tuple[PeriodEvidenceResult, ...]:
    """Attempt each frozen candidate accession, preserving every failure."""
    results: list[PeriodEvidenceResult] = []
    for ticker, expected_accessions in CANDIDATE_ACCESSIONS.items():
        try:
            company = resolve_ticker(ticker, client)
            selected = load_and_select_filings(client, company, annual_limit=5)
            filings = {filing.accession_number: filing for filing in selected.annual}
        except Exception as exc:  # Development diagnostic must continue.
            results.extend(
                failure_result(ticker=ticker, accession_number=accession, error=f"Filing selection failed: {type(exc).__name__}: {exc}")
                for accession in expected_accessions
            )
            continue
        for accession in expected_accessions:
            filing = filings.get(accession)
            if filing is None:
                results.append(failure_result(ticker=ticker, accession_number=accession, error="Frozen candidate accession was not among the five exact selected 10-Ks"))
                continue
            try:
                directory = _directory_url(company.cik, accession)
                inventory = discover_artifacts(
                    client.get_json(f"{directory}/index.json"),
                    directory_url=directory,
                    primary_document=filing.primary_document,
                )
                filing_xbrl = fetch_filing_xbrl(client, company, filing)
                annual = resolve_annual_period(filing_xbrl)
                if not isinstance(annual, ResolvedAnnualPeriod):
                    raise ValueError(f"Annual-period result was {annual.status.value}")
                schemas = {inventory.source_url(name): client.get_bytes(inventory.source_url(name)) for name in inventory.schema_names}
                presentations = {inventory.source_url(name): client.get_bytes(inventory.source_url(name)) for name in inventory.presentation_names}

                # Determine applicable renderer reports from submitted role URIs.
                roles = parse_role_definitions(schemas)
                memberships = parse_presentation_memberships(presentations, roles)
                summary = None
                summary_bytes = None
                if inventory.filing_summary_name:
                    summary_url = inventory.source_url(inventory.filing_summary_name)
                    summary_bytes = client.get_bytes(summary_url)
                    summary = (summary_url, summary_bytes)
                metalinks = None
                if inventory.metalinks_name:
                    metalinks_url = inventory.source_url(inventory.metalinks_name)
                    metalinks = (metalinks_url, client.get_bytes(metalinks_url))
                applicable_names = _applicable_renderer_names(
                    summary_bytes,
                    {membership.role.role_uri for membership in memberships},
                    inventory.renderer_names,
                )
                renderer_files = {inventory.source_url(name): client.get_bytes(inventory.source_url(name)) for name in applicable_names}
                renderer = parse_renderer_evidence(
                    filing_summary=summary,
                    metalinks=metalinks,
                    renderer_files=renderer_files,
                )
                results.append(analyze_period(
                    ticker=ticker, filing_xbrl=filing_xbrl,
                    annual_period=annual, inventory=inventory,
                    schema_documents=schemas, presentation_documents=presentations,
                    renderer=renderer,
                ))
            except Exception as exc:  # One typed result per frozen period.
                results.append(failure_result(
                    ticker=ticker, accession_number=accession,
                    report_date=filing.report_date or date.min,
                    error=f"{type(exc).__name__}: {exc}",
                ))
    if len(results) != EXPECTED_PERIOD_COUNT:
        raise AssertionError(f"Diagnostic emitted {len(results)} results, expected 33")
    return tuple(results)


def _applicable_renderer_names(summary: bytes | None, role_uris: set[str], discovered: Sequence[str]) -> tuple[str, ...]:
    if summary is None:
        return ()
    # FilingSummary is renderer-derived. This extraction only limits retrieval;
    # the pure parser retains submitted and renderer evidence separately.
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(summary)
    except ET.ParseError:
        return ()
    discovered_by_lower = {name.lower(): name for name in discovered}
    names = set()
    for report in root.iter("Report"):
        role = report.findtext("Role")
        if role not in role_uris:
            continue
        for field in ("HtmlFileName", "XmlFileName"):
            value = report.findtext(field)
            if value and value.lower() in discovered_by_lower:
                names.add(discovered_by_lower[value.lower()])
    return tuple(sorted(names))


def _directory_url(cik: int, accession: str) -> str:
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}"


def print_summary(results: Sequence[PeriodEvidenceResult], output: TextIO) -> None:
    counts = Counter(outcome.value for result in results for outcome in result.outcomes)
    print(f"Periods attempted: {len(results)}", file=output)
    print(f"Unique frozen accessions: {len({r.accession_number for r in results})}", file=output)
    for outcome in EvidenceOutcome:
        print(f"{outcome.value}: {counts[outcome.value]}", file=output)
    print("Policy decision: NEEDS_MORE_RESEARCH", file=output)
    print("Safe new Pretax resolutions: 0", file=output)
    print("Equity-method evidence matrix:", file=output)
    for entry in equity_method_matrix():
        print(f"  {entry.ticker}: {entry.scope.value} ({entry.candidate_periods} periods)", file=output)


def main(argv: Sequence[str] | None = None, *, environ: Mapping[str, str] | None = None, output: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="JSON inventory destination")
    args = parser.parse_args(argv)
    environment = os.environ if environ is None else environ
    user_agent = environment.get("SEC_USER_AGENT", "").strip()
    if not user_agent:
        parser.error("SEC_USER_AGENT must contain an identifying SEC User-Agent")
    results = run_diagnostic(SECClient(user_agent, timeout=30.0))
    args.output.write_text(serialize_inventory(results), encoding="utf-8")
    print_summary(results, output)
    return 1 if any(EvidenceOutcome.PRESENTATION_DATA_ERROR in result.outcomes for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
