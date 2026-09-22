#!/usr/bin/env python3
"""Validate SEC Company Facts parsing across a development ticker corpus."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Mapping, Sequence, TextIO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from valuation_platform.sec import (  # noqa: E402
    SECClient,
    fetch_company_facts,
    resolve_ticker,
)


DEFAULT_TICKERS = (
    "META",
    "GOOGL",
    "MSFT",
    "AAPL",
    "NVDA",
    "AMZN",
    "WMT",
    "COST",
    "HD",
    "KO",
    "PG",
    "NKE",
    "CAT",
    "BA",
    "UPS",
    "XOM",
    "CVX",
    "JNJ",
    "PFE",
    "T",
)


@dataclass(frozen=True)
class ValidationSuccess:
    ticker: str
    cik: int
    entity_name: str
    concept_count: int
    observation_count: int
    taxonomy_count: int
    missing_labels: int
    missing_descriptions: int
    value_types: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class ValidationFailure:
    ticker: str
    stage: str
    exception_type: str
    message: str


ValidationResult = ValidationSuccess | ValidationFailure


def validate_company_facts(
    client: SECClient,
    tickers: Sequence[str],
) -> tuple[ValidationResult, ...]:
    """Run the existing SEC APIs sequentially and retain every result."""
    results: list[ValidationResult] = []

    for requested_ticker in tickers:
        ticker = requested_ticker.strip().upper()
        try:
            company = resolve_ticker(ticker, client)
        except Exception as exc:  # Diagnostic boundary intentionally continues.
            results.append(
                ValidationFailure(
                    ticker=ticker,
                    stage="ticker resolution",
                    exception_type=type(exc).__name__,
                    message=str(exc),
                )
            )
            continue

        try:
            company_facts = fetch_company_facts(client, company)
        except Exception as exc:  # Diagnostic boundary intentionally continues.
            results.append(
                ValidationFailure(
                    ticker=company.ticker,
                    stage="Company Facts retrieval/parsing",
                    exception_type=type(exc).__name__,
                    message=str(exc),
                )
            )
            continue

        concepts = company_facts.concepts
        observation_count = sum(len(concept.observations) for concept in concepts)
        value_types = Counter(
            type(observation.value).__name__
            for concept in concepts
            for observation in concept.observations
        )
        results.append(
            ValidationSuccess(
                ticker=company.ticker,
                cik=company.cik,
                entity_name=company_facts.entity_name,
                concept_count=len(concepts),
                observation_count=observation_count,
                taxonomy_count=len({concept.taxonomy for concept in concepts}),
                missing_labels=sum(concept.label is None for concept in concepts),
                missing_descriptions=sum(
                    concept.description is None for concept in concepts
                ),
                value_types=tuple(sorted(value_types.items())),
            )
        )

    return tuple(results)


def print_report(results: Sequence[ValidationResult], output: TextIO) -> None:
    """Print detailed results followed by a compact run summary."""
    successes = [result for result in results if isinstance(result, ValidationSuccess)]
    failures = [result for result in results if isinstance(result, ValidationFailure)]

    for result in successes:
        value_types = ", ".join(
            f"{type_name}={count}" for type_name, count in result.value_types
        ) or "none"
        print(
            f"{result.ticker}: CIK={result.cik}; entity={result.entity_name}; "
            f"concepts={result.concept_count}; "
            f"observations={result.observation_count}; "
            f"taxonomies={result.taxonomy_count}; "
            f"missing labels={result.missing_labels}; "
            f"missing descriptions={result.missing_descriptions}; "
            f"value types={value_types}",
            file=output,
        )

    print("\nSummary", file=output)
    print(f"Companies attempted: {len(results)}", file=output)
    print(f"Companies succeeded: {len(successes)}", file=output)
    print(f"Companies failed: {len(failures)}", file=output)
    print(
        f"Total concepts parsed: {sum(result.concept_count for result in successes)}",
        file=output,
    )
    print(
        "Total observations parsed: "
        f"{sum(result.observation_count for result in successes)}",
        file=output,
    )
    print(
        "\nticker | result | concepts | observations | missing labels | "
        "missing descriptions",
        file=output,
    )
    for result in results:
        if isinstance(result, ValidationSuccess):
            print(
                f"{result.ticker} | success | {result.concept_count} | "
                f"{result.observation_count} | {result.missing_labels} | "
                f"{result.missing_descriptions}",
                file=output,
            )
        else:
            print(f"{result.ticker} | failure | - | - | - | -", file=output)

    if failures:
        print("\nFailures", file=output)
        for failure in failures:
            print(
                f"{failure.ticker} | {failure.stage} | "
                f"{failure.exception_type}: {failure.message}",
                file=output,
            )


def run(client: SECClient, tickers: Sequence[str], output: TextIO) -> int:
    """Run validation and return a process-compatible status code."""
    results = validate_company_facts(client, tickers)
    print_report(results, output)
    return 1 if any(isinstance(result, ValidationFailure) for result in results) else 0


def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    output: TextIO = sys.stdout,
) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the existing SEC Company Facts parser across companies."
    )
    parser.add_argument(
        "tickers",
        nargs="*",
        help="Tickers to validate; defaults to the built-in 20-company corpus.",
    )
    args = parser.parse_args(argv)

    environment = os.environ if environ is None else environ
    user_agent = environment.get("SEC_USER_AGENT", "").strip()
    if not user_agent:
        parser.error(
            "SEC_USER_AGENT must contain an identifying SEC User-Agent, for example "
            "'Valuation Platform contact@example.com'"
        )

    tickers = args.tickers or DEFAULT_TICKERS
    return run(SECClient(user_agent), tickers, output)


if __name__ == "__main__":
    raise SystemExit(main())
