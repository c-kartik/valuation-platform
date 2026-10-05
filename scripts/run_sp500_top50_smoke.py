#!/usr/bin/env python3
"""Run the production historical pipeline across the frozen Top 50 corpus."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Protocol, Sequence, TextIO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from valuation_platform.normalization import (  # noqa: E402
    ANNUAL_BALANCE_SHEET_POLICIES,
    AmbiguousStandardizedMeasure,
    CalculatedOperatingNWC,
    EvidenceSourceKind,
    GOOGL_DILUTED_SHARES_DERIVATION_POLICY,
    HistoricalAvailability,
    OperatingNWCReadinessError,
    ResolvedHistoricalMeasure,
    UnavailableHistoricalMeasure,
    assemble_standardized_annual_history,
    calculate_operating_nwc_change,
    calculate_operating_nwc_level,
    normalize_annual_balance_sheets,
    normalize_annual_financials,
    operating_nwc_valuation_policy_for_cik,
)
from valuation_platform.sec import (  # noqa: E402
    FilingSelectionError,
    SECClient,
    SECClientError,
    SECCompanyIdentity,
    SubmissionsDataError,
    SelectedFactObservations,
    SelectedFilings,
    fetch_company_facts,
    fetch_filing_xbrl,
    load_and_select_filings,
    resolve_ticker,
    select_fact_observations,
)
from valuation_platform.sec.tickers import COMPANY_TICKERS_URL  # noqa: E402


DEFAULT_SNAPSHOT = PROJECT_ROOT / "docs/universe/sp500-top-50-2026-10-02.csv"
DEFAULT_OUTPUT = Path("/tmp/valuation-platform-sp500-top50-smoke.json")
EXPECTED_SECURITY_COUNT = 51
EXPECTED_ISSUER_COUNT = 50
EXPECTED_GENERIC_ISSUER_COUNT = 43
EXPECTED_WAVE_ISSUER_COUNTS = {"SEED": 5, "A": 20, "B": 18, "SPECIALIZED": 7}
SPECIALIZED_CLASSIFICATION = "SPECIALIZED_METHODOLOGY_CANDIDATE"
GENERIC_CLASSIFICATIONS = frozenset(
    {"SUPPORTED_SEED", "OPERATING_COMPANY_CANDIDATE"}
)
FILING_XBRL_CIKS = frozenset(
    {
        cik
        for policy in ANNUAL_BALANCE_SHEET_POLICIES
        for candidate in policy.candidates
        if candidate.source_kind is EvidenceSourceKind.FILING_XBRL
        for cik in candidate.applicable_ciks or ()
    }
    | {GOOGL_DILUTED_SHARES_DERIVATION_POLICY.company_cik}
)


class SmokeRunnerError(ValueError):
    """Raised when the frozen corpus or runner configuration is invalid."""


class ExecutionStage(str, Enum):
    """Coarse pipeline boundary reached by one issuer execution."""

    TICKER_RESOLUTION = "ticker_resolution"
    SUBMISSIONS = "submissions"
    FILING_SELECTION = "filing_selection"
    COMPANY_FACTS = "company_facts"
    FILING_ASSOCIATION = "filing_association"
    NORMALIZATION = "normalization"
    STANDARDIZED_OUTPUT = "standardized_output"
    COMPLETE = "complete"
    SPECIALIZED_SKIPPED = "specialized_skipped"


PIPELINE_STAGES = (
    ExecutionStage.TICKER_RESOLUTION,
    ExecutionStage.SUBMISSIONS,
    ExecutionStage.FILING_SELECTION,
    ExecutionStage.COMPANY_FACTS,
    ExecutionStage.FILING_ASSOCIATION,
    ExecutionStage.NORMALIZATION,
    ExecutionStage.STANDARDIZED_OUTPUT,
)


@dataclass(frozen=True)
class UniverseSecurity:
    """One immutable row from the frozen security-level snapshot."""

    snapshot_date: str
    source_ticker: str
    project_ticker: str
    company_name: str
    classification: str
    already_validated: bool
    cik: int
    wave: str


@dataclass(frozen=True)
class IssuerPlan:
    """One deterministic CIK-grouped execution plan."""

    snapshot_date: str
    source_tickers: tuple[str, ...]
    project_tickers: tuple[str, ...]
    execution_ticker: str
    cik: int
    classification: str
    wave: str


@dataclass(frozen=True)
class NormalizedIssuerInputs:
    """Normalized production inputs required by standardized output."""

    historical: Any
    balance_sheets: Any
    operating_nwc_results: tuple[Any, ...]
    operating_nwc_changes: tuple[Any, ...]


@dataclass(frozen=True)
class IssuerSmokeResult:
    """Structured outcome for one issuer plan."""

    plan: IssuerPlan
    attempted: bool
    completed: bool
    stage: ExecutionStage
    stage_statuses: tuple[tuple[str, str], ...]
    exception_type: str | None
    error_message: str | None
    selected_annual_filings: int
    selected_annual_periods: tuple[str, ...]
    standardized_annual_periods: int
    typed_status_counts: tuple[tuple[str, int], ...]
    measure_status_counts: tuple[tuple[str, int], ...]
    measure_resolution_counts: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class CorpusSmokeResult:
    """One complete deterministic corpus run."""

    snapshot_file: str
    snapshot_date: str
    run_timestamp: str
    repository_commit: str
    repository_dirty: bool
    securities: tuple[UniverseSecurity, ...]
    issuers: tuple[IssuerSmokeResult, ...]


class CorpusPipeline(Protocol):
    """Production-stage interface used by the diagnostic orchestrator."""

    def resolve_company(self, ticker: str) -> SECCompanyIdentity: ...

    def select_filings(self, company: SECCompanyIdentity) -> SelectedFilings: ...

    def company_facts(self, company: SECCompanyIdentity) -> Any: ...

    def associate_facts(
        self, filings: SelectedFilings, company_facts: Any
    ) -> SelectedFactObservations: ...

    def normalize(
        self,
        company: SECCompanyIdentity,
        filings: SelectedFilings,
        selected_facts: SelectedFactObservations,
    ) -> NormalizedIssuerInputs: ...

    def standardize(self, inputs: NormalizedIssuerInputs) -> Any: ...


class _CompanyTickersOnceClient:
    """Deduplicate the one shared ticker-dataset request within a corpus run."""

    def __init__(self, client: SECClient) -> None:
        self._client = client
        self._payload: Any | None = None

    def get_json(self, url: str) -> Any:
        if url != COMPANY_TICKERS_URL:
            raise SmokeRunnerError("Ticker resolver requested an unexpected URL")
        if self._payload is None:
            self._payload = self._client.get_json(url)
        return self._payload


class ProductionCorpusPipeline:
    """Thin stage adapter over the existing production APIs."""

    def __init__(self, client: SECClient, annual_limit: int = 5) -> None:
        self._client = client
        self._ticker_client = _CompanyTickersOnceClient(client)
        self._annual_limit = annual_limit

    def resolve_company(self, ticker: str) -> SECCompanyIdentity:
        return resolve_ticker(ticker, self._ticker_client)  # type: ignore[arg-type]

    def select_filings(self, company: SECCompanyIdentity) -> SelectedFilings:
        return load_and_select_filings(
            self._client,
            company,
            annual_limit=self._annual_limit,
        )

    def company_facts(self, company: SECCompanyIdentity) -> Any:
        return fetch_company_facts(self._client, company)

    def associate_facts(
        self,
        filings: SelectedFilings,
        company_facts: Any,
    ) -> SelectedFactObservations:
        return select_fact_observations(filings, company_facts)

    def normalize(
        self,
        company: SECCompanyIdentity,
        filings: SelectedFilings,
        selected_facts: SelectedFactObservations,
    ) -> NormalizedIssuerInputs:
        filing_xbrl = (
            tuple(
                fetch_filing_xbrl(self._client, company, filing)
                for filing in filings.annual
            )
            if company.cik in FILING_XBRL_CIKS
            else ()
        )
        historical = normalize_annual_financials(
            selected_facts,
            filing_xbrl=filing_xbrl,
        )
        balance_sheets = normalize_annual_balance_sheets(
            selected_facts,
            filing_xbrl=filing_xbrl,
        )
        nwc_results: tuple[Any, ...] = ()
        nwc_changes: tuple[Any, ...] = ()
        try:
            nwc_policy = operating_nwc_valuation_policy_for_cik(company.cik)
        except OperatingNWCReadinessError:
            pass
        else:
            nwc_results = tuple(
                calculate_operating_nwc_level(balance_sheets, result, nwc_policy)
                for result in balance_sheets.annual
            )
            changes = []
            for opening, closing in zip(nwc_results, nwc_results[1:]):
                if isinstance(opening, CalculatedOperatingNWC) and isinstance(
                    closing, CalculatedOperatingNWC
                ):
                    changes.append(calculate_operating_nwc_change(opening, closing))
            nwc_changes = tuple(changes)
        return NormalizedIssuerInputs(
            historical,
            balance_sheets,
            nwc_results,
            nwc_changes,
        )

    def standardize(self, inputs: NormalizedIssuerInputs) -> Any:
        return assemble_standardized_annual_history(
            inputs.historical,
            inputs.balance_sheets,
            operating_nwc_results=inputs.operating_nwc_results,
            operating_nwc_changes=inputs.operating_nwc_changes,
        )


def load_snapshot(path: Path) -> tuple[UniverseSecurity, ...]:
    """Load and strictly validate the immutable Phase 1H.1 snapshot."""
    content = path.read_text(encoding="utf-8")
    reader = csv.DictReader(content.splitlines())
    required = {
        "snapshot_date",
        "source_ticker",
        "project_ticker",
        "company_name",
        "preliminary_classification",
        "already_validated",
        "sec_cik",
        "validation_wave",
    }
    if reader.fieldnames is None or not required.issubset(reader.fieldnames):
        raise SmokeRunnerError("Universe snapshot is missing required columns")

    rows: list[UniverseSecurity] = []
    raw_identities: set[tuple[str, str, str]] = set()
    for line_number, row in enumerate(reader, start=2):
        if any(not (row.get(field) or "").strip() for field in required):
            raise SmokeRunnerError(
                f"Universe snapshot row {line_number} has blank required fields"
            )
        raw_identity = (
            row["snapshot_date"],
            row["source_ticker"],
            row["project_ticker"],
        )
        if raw_identity in raw_identities:
            raise SmokeRunnerError(
                f"Universe snapshot contains duplicate row identity {raw_identity!r}"
            )
        raw_identities.add(raw_identity)
        validated_text = row["already_validated"].strip().lower()
        if validated_text not in {"true", "false"}:
            raise SmokeRunnerError(
                f"Universe snapshot row {line_number} has invalid Boolean"
            )
        try:
            cik = int(row["sec_cik"])
        except ValueError as exc:
            raise SmokeRunnerError(
                f"Universe snapshot row {line_number} has invalid CIK"
            ) from exc
        rows.append(
            UniverseSecurity(
                snapshot_date=row["snapshot_date"],
                source_ticker=row["source_ticker"],
                project_ticker=row["project_ticker"],
                company_name=row["company_name"],
                classification=row["preliminary_classification"],
                already_validated=validated_text == "true",
                cik=cik,
                wave=row["validation_wave"],
            )
        )

    securities = tuple(rows)
    if len(securities) != EXPECTED_SECURITY_COUNT:
        raise SmokeRunnerError("Universe snapshot must contain exactly 51 securities")
    if len({item.cik for item in securities}) != EXPECTED_ISSUER_COUNT:
        raise SmokeRunnerError("Universe snapshot must contain exactly 50 issuers")
    if len({item.source_ticker for item in securities}) != len(securities):
        raise SmokeRunnerError("Universe source tickers must be unique")
    if len({item.project_ticker for item in securities}) != len(securities):
        raise SmokeRunnerError("Universe project tickers must be unique")
    if len({item.snapshot_date for item in securities}) != 1:
        raise SmokeRunnerError("Universe snapshot dates must be identical")
    return securities


def group_issuers(securities: Sequence[UniverseSecurity]) -> tuple[IssuerPlan, ...]:
    """Group security rows by CIK while preserving first-snapshot order."""
    grouped: dict[int, list[UniverseSecurity]] = {}
    for security in securities:
        grouped.setdefault(security.cik, []).append(security)

    plans: list[IssuerPlan] = []
    for cik, rows in grouped.items():
        classifications = {row.classification for row in rows}
        waves = {row.wave for row in rows}
        dates = {row.snapshot_date for row in rows}
        if len(classifications) != 1 or len(waves) != 1 or len(dates) != 1:
            raise SmokeRunnerError(
                f"Issuer CIK {cik} has inconsistent snapshot metadata"
            )
        validated = [row for row in rows if row.already_validated]
        execution = validated[0] if validated else rows[0]
        plans.append(
            IssuerPlan(
                snapshot_date=rows[0].snapshot_date,
                source_tickers=tuple(row.source_ticker for row in rows),
                project_tickers=tuple(row.project_ticker for row in rows),
                execution_ticker=execution.project_ticker,
                cik=cik,
                classification=rows[0].classification,
                wave=rows[0].wave,
            )
        )
    return tuple(plans)


def run_corpus(
    securities: tuple[UniverseSecurity, ...],
    pipeline: CorpusPipeline,
    *,
    snapshot_file: str,
    repository_commit: str,
    repository_dirty: bool,
    run_timestamp: datetime | None = None,
) -> CorpusSmokeResult:
    """Run every issuer independently and retain failures without aborting."""
    plans = group_issuers(securities)
    generic_count = sum(plan.classification in GENERIC_CLASSIFICATIONS for plan in plans)
    if generic_count != EXPECTED_GENERIC_ISSUER_COUNT:
        raise SmokeRunnerError("Universe must contain exactly 43 generic issuers")
    wave_counts = Counter(plan.wave for plan in plans)
    if dict(wave_counts) != EXPECTED_WAVE_ISSUER_COUNTS:
        raise SmokeRunnerError("Universe issuer wave counts are inconsistent")

    results: list[IssuerSmokeResult] = []
    for plan in plans:
        if plan.classification == SPECIALIZED_CLASSIFICATION:
            results.append(_specialized_result(plan))
            continue
        if plan.classification not in GENERIC_CLASSIFICATIONS:
            raise SmokeRunnerError(
                f"Issuer {plan.execution_ticker} has unsupported classification"
            )
        results.append(_run_issuer(plan, pipeline))

    timestamp = run_timestamp or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise SmokeRunnerError("Run timestamp must be timezone-aware")
    return CorpusSmokeResult(
        snapshot_file=snapshot_file,
        snapshot_date=securities[0].snapshot_date,
        run_timestamp=timestamp.isoformat(),
        repository_commit=repository_commit,
        repository_dirty=repository_dirty,
        securities=securities,
        issuers=tuple(results),
    )


def _run_issuer(plan: IssuerPlan, pipeline: CorpusPipeline) -> IssuerSmokeResult:
    statuses = {stage.value: "not_started" for stage in PIPELINE_STAGES}
    selected_count = 0
    selected_periods: tuple[str, ...] = ()
    try:
        company = _stage_call(
            ExecutionStage.TICKER_RESOLUTION,
            statuses,
            pipeline.resolve_company,
            plan.execution_ticker,
        )
        if company.cik != plan.cik:
            statuses[ExecutionStage.TICKER_RESOLUTION.value] = "failed"
            raise _StageFailure(
                ExecutionStage.TICKER_RESOLUTION,
                SmokeRunnerError(
                    f"Resolved CIK {company.cik} does not match snapshot CIK {plan.cik}"
                ),
            )
        try:
            filings = pipeline.select_filings(company)
        except Exception as exc:
            failed_stage = (
                ExecutionStage.SUBMISSIONS
                if isinstance(exc, (SECClientError, SubmissionsDataError))
                else ExecutionStage.FILING_SELECTION
            )
            statuses[failed_stage.value] = "failed"
            raise _StageFailure(failed_stage, exc) from exc
        statuses[ExecutionStage.SUBMISSIONS.value] = "completed"
        statuses[ExecutionStage.FILING_SELECTION.value] = "completed"
        selected_count = len(filings.annual)
        selected_periods = tuple(
            filing.report_date.isoformat() if filing.report_date is not None else ""
            for filing in filings.annual
        )
        facts = _stage_call(
            ExecutionStage.COMPANY_FACTS,
            statuses,
            pipeline.company_facts,
            company,
        )
        selected_facts = _stage_call(
            ExecutionStage.FILING_ASSOCIATION,
            statuses,
            pipeline.associate_facts,
            filings,
            facts,
        )
        normalized = _stage_call(
            ExecutionStage.NORMALIZATION,
            statuses,
            pipeline.normalize,
            company,
            filings,
            selected_facts,
        )
        output = _stage_call(
            ExecutionStage.STANDARDIZED_OUTPUT,
            statuses,
            pipeline.standardize,
            normalized,
        )
    except _StageFailure as failure:
        return IssuerSmokeResult(
            plan,
            True,
            False,
            failure.stage,
            tuple(statuses.items()),
            type(failure.error).__name__,
            _concise_message(failure.error),
            selected_count,
            selected_periods,
            0,
            (),
            (),
            (),
        )

    return IssuerSmokeResult(
        plan,
        True,
        True,
        ExecutionStage.COMPLETE,
        tuple(statuses.items()),
        None,
        None,
        selected_count,
        selected_periods,
        len(output.annual),
        _typed_status_counts(output),
        _measure_status_counts(output),
        _measure_resolution_counts(output),
    )


class _StageFailure(Exception):
    def __init__(self, stage: ExecutionStage, error: Exception) -> None:
        super().__init__(str(error))
        self.stage = stage
        self.error = error


def _stage_call(
    stage: ExecutionStage,
    statuses: dict[str, str],
    operation: Any,
    *args: Any,
) -> Any:
    try:
        result = operation(*args)
    except Exception as exc:
        statuses[stage.value] = "failed"
        raise _StageFailure(stage, exc) from exc
    statuses[stage.value] = "completed"
    return result


def _specialized_result(plan: IssuerPlan) -> IssuerSmokeResult:
    return IssuerSmokeResult(
        plan,
        False,
        False,
        ExecutionStage.SPECIALIZED_SKIPPED,
        tuple((stage.value, "skipped") for stage in PIPELINE_STAGES),
        None,
        None,
        0,
        (),
        0,
        (),
        (),
        (),
    )


def _typed_status_counts(output: Any) -> tuple[tuple[str, int], ...]:
    counts: Counter[str] = Counter()
    for annual in output.annual:
        for measure in annual.measures:
            counts[_measure_status(measure)] += 1
    order = ("resolved", *(status.value for status in HistoricalAvailability))
    return tuple((name, counts[name]) for name in order if counts[name])


def _measure_status_counts(output: Any) -> tuple[tuple[str, int], ...]:
    counts: Counter[str] = Counter()
    for annual in output.annual:
        for measure in annual.measures:
            counts[f"{measure.measure.value}:{_measure_status(measure)}"] += 1
    return tuple(sorted(counts.items()))


def _measure_status(measure: Any) -> str:
    if isinstance(measure, ResolvedHistoricalMeasure):
        return "resolved"
    if isinstance(measure, AmbiguousStandardizedMeasure):
        return HistoricalAvailability.AMBIGUOUS.value
    if isinstance(measure, UnavailableHistoricalMeasure):
        return measure.status.value
    raise SmokeRunnerError("Standardized output has an unknown measure type")


def _measure_resolution_counts(output: Any) -> tuple[tuple[str, int], ...]:
    counts: Counter[str] = Counter()
    for annual in output.annual:
        for measure in annual.measures:
            if isinstance(measure, ResolvedHistoricalMeasure):
                counts[f"{measure.measure.value}:{measure.resolution.value}"] += 1
    return tuple(sorted(counts.items()))


def _concise_message(error: Exception, limit: int = 500) -> str:
    message = " ".join(str(error).split())
    return message if len(message) <= limit else f"{message[: limit - 3]}..."


def corpus_result_to_dict(result: CorpusSmokeResult) -> dict[str, object]:
    """Serialize one corpus result with stable list and field ordering."""
    issuer_by_cik = {issuer.plan.cik: issuer for issuer in result.issuers}
    security_rows = [
        {
            "snapshot_date": item.snapshot_date,
            "source_ticker": item.source_ticker,
            "project_ticker": item.project_ticker,
            "company_name": item.company_name,
            "cik": item.cik,
            "preliminary_classification": item.classification,
            "already_validated": item.already_validated,
            "wave": item.wave,
            "execution_ticker": issuer_by_cik[item.cik].plan.execution_ticker,
            "issuer_stage": issuer_by_cik[item.cik].stage.value,
        }
        for item in result.securities
    ]
    issuer_rows = []
    for item in result.issuers:
        issuer_rows.append(
            {
                "snapshot_date": item.plan.snapshot_date,
                "source_tickers": list(item.plan.source_tickers),
                "project_tickers": list(item.plan.project_tickers),
                "execution_ticker": item.plan.execution_ticker,
                "cik": item.plan.cik,
                "preliminary_classification": item.plan.classification,
                "wave": item.plan.wave,
                "attempted": item.attempted,
                "completed": item.completed,
                "stage": item.stage.value,
                "stage_statuses": dict(item.stage_statuses),
                "exception_type": item.exception_type,
                "error_message": item.error_message,
                "selected_annual_filings": item.selected_annual_filings,
                "selected_annual_periods": list(item.selected_annual_periods),
                "standardized_annual_periods": item.standardized_annual_periods,
                "typed_status_counts": dict(item.typed_status_counts),
                "measure_status_counts": dict(item.measure_status_counts),
                "measure_resolution_counts": dict(item.measure_resolution_counts),
            }
        )
    return {
        "snapshot_file": result.snapshot_file,
        "snapshot_date": result.snapshot_date,
        "run_timestamp": result.run_timestamp,
        "repository_commit": result.repository_commit,
        "repository_dirty": result.repository_dirty,
        "security_count": len(result.securities),
        "issuer_count": len(result.issuers),
        "generic_execution_count": sum(item.attempted for item in result.issuers),
        "specialized_skip_count": sum(
            item.stage is ExecutionStage.SPECIALIZED_SKIPPED for item in result.issuers
        ),
        "securities": security_rows,
        "issuers": issuer_rows,
    }


def write_result(result: CorpusSmokeResult, path: Path) -> None:
    """Write deterministic formatted JSON to the requested ephemeral path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(corpus_result_to_dict(result), indent=2) + "\n",
        encoding="utf-8",
    )


def print_summary(result: CorpusSmokeResult, output: TextIO) -> None:
    """Print the compact aggregate needed for diagnostic review."""
    attempted = [item for item in result.issuers if item.attempted]
    completed = [item for item in attempted if item.completed]
    failed = [item for item in attempted if not item.completed]
    failure_stages = Counter(item.stage.value for item in failed)
    typed = Counter(
        {
            name: sum(dict(item.typed_status_counts).get(name, 0) for item in completed)
            for name in (
                "resolved",
                "missing",
                "ambiguous",
                "methodology_blocked",
                "not_comparable",
                "unsupported",
                "not_applicable",
                "out_of_perimeter",
            )
        }
    )
    print(f"Securities: {len(result.securities)}", file=output)
    print(f"Issuers: {len(result.issuers)}", file=output)
    print(f"Generic attempts: {len(attempted)}", file=output)
    print(f"Completed: {len(completed)}", file=output)
    print(f"Failed: {len(failed)}", file=output)
    print(
        "Specialized skipped: "
        f"{sum(item.stage is ExecutionStage.SPECIALIZED_SKIPPED for item in result.issuers)}",
        file=output,
    )
    print(f"Failure stages: {dict(sorted(failure_stages.items()))}", file=output)
    print(f"Typed statuses: {dict(typed)}", file=output)
    incomplete = [
        item.plan.execution_ticker
        for item in completed
        if item.selected_annual_filings < 5
    ]
    print(f"Issuers with fewer than five annual filings: {incomplete}", file=output)
    for wave in ("SEED", "A", "B", "SPECIALIZED"):
        members = [item for item in result.issuers if item.plan.wave == wave]
        print(
            f"Wave {wave}: issuers={len(members)}; "
            f"attempted={sum(item.attempted for item in members)}; "
            f"completed={sum(item.completed for item in members)}",
            file=output,
        )
    for item in failed:
        print(
            f"FAIL {item.plan.execution_ticker} [{item.stage.value}] "
            f"{item.exception_type}: {item.error_message}",
            file=output,
        )


def _repository_state() -> tuple[str, bool]:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip(), bool(status.stdout.strip())


def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    output: TextIO = sys.stdout,
) -> int:
    parser = argparse.ArgumentParser(
        description="Run the production historical pipeline across the frozen corpus."
    )
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--annual-limit", type=int, default=5)
    args = parser.parse_args(argv)
    environment = os.environ if environ is None else environ
    user_agent = environment.get("SEC_USER_AGENT", "").strip()
    if not user_agent:
        parser.error("SEC_USER_AGENT must contain an identifying SEC User-Agent")

    snapshot = load_snapshot(args.snapshot)
    repository_commit, repository_dirty = _repository_state()
    result = run_corpus(
        snapshot,
        ProductionCorpusPipeline(SECClient(user_agent), args.annual_limit),
        snapshot_file=str(args.snapshot.relative_to(PROJECT_ROOT)),
        repository_commit=repository_commit,
        repository_dirty=repository_dirty,
    )
    write_result(result, args.output)
    print_summary(result, output)
    print(f"Artifact: {args.output}", file=output)
    return 1 if any(item.attempted and not item.completed for item in result.issuers) else 0


if __name__ == "__main__":
    raise SystemExit(main())
