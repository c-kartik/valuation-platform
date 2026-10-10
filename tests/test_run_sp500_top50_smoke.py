from datetime import date, datetime, timezone
from decimal import Decimal
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import call, patch

from scripts.run_sp500_top50_smoke import (
    DEFAULT_SNAPSHOT,
    ExecutionStage,
    ProductionCorpusPipeline,
    SPECIALIZED_CLASSIFICATION,
    corpus_result_to_dict,
    group_issuers,
    load_snapshot,
    print_summary,
    run_corpus,
    write_result,
)
from valuation_platform.normalization import (
    AmbiguousStandardizedMeasure,
    EvidenceSourceKind,
    HistoricalAvailability,
    HistoricalMeasure,
    HistoricalMeasureKind,
    HistoricalResolutionKind,
    HistoricalSourceReference,
    ResolvedHistoricalMeasure,
    UnavailableHistoricalMeasure,
)
from valuation_platform.sec import SECCompanyIdentity, SECRequestError


NOW = datetime(2026, 10, 5, tzinfo=timezone.utc)


class FakePipeline:
    def __init__(self, securities, *, failure_ticker=None, failure_stage=None):
        self.cik_by_ticker = {item.project_ticker: item.cik for item in securities}
        self.failure_ticker = failure_ticker
        self.failure_stage = failure_stage
        self.execution_tickers = []

    def _fail(self, ticker, stage):
        if ticker == self.failure_ticker and stage == self.failure_stage:
            raise RuntimeError(f"{ticker} failed at {stage}")

    def resolve_company(self, ticker):
        self.execution_tickers.append(ticker)
        self._fail(ticker, "ticker")
        cik = self.cik_by_ticker[ticker]
        return SECCompanyIdentity(
            ticker,
            cik,
            f"{cik:010d}",
            f"{ticker} Inc.",
            "ticker-source",
            NOW,
        )

    def select_filings(self, company):
        self._fail(company.ticker, "filings")
        return SimpleNamespace(
            annual=tuple(
                SimpleNamespace(report_date=date(year, 12, 31))
                for year in range(2021, 2026)
            ),
            interim=(),
        )

    def company_facts(self, company):
        self._fail(company.ticker, "facts")
        return SimpleNamespace(company=company)

    def associate_facts(self, filings, company_facts):
        self._fail(company_facts.company.ticker, "association")
        return SimpleNamespace(company=company_facts.company)

    def normalize(self, company, filings, selected_facts):
        self._fail(company.ticker, "normalization")
        return SimpleNamespace(company=company)

    def standardize(self, inputs):
        self._fail(inputs.company.ticker, "output")
        annual = tuple(SimpleNamespace(measures=()) for _ in range(5))
        return SimpleNamespace(annual=annual)


class SubmissionsFailurePipeline(FakePipeline):
    def select_filings(self, company):
        if company.ticker == self.failure_ticker:
            raise SECRequestError("submissions unavailable")
        return super().select_filings(company)


class CIKMismatchPipeline(FakePipeline):
    def __init__(self, securities, mismatch_ticker):
        super().__init__(securities)
        self.mismatch_ticker = mismatch_ticker
        self.selected_tickers = []

    def resolve_company(self, ticker):
        company = super().resolve_company(ticker)
        if ticker != self.mismatch_ticker:
            return company
        return SECCompanyIdentity(
            company.ticker,
            company.cik + 1,
            f"{company.cik + 1:010d}",
            company.company_name,
            company.source_url,
            company.retrieved_at,
        )

    def select_filings(self, company):
        self.selected_tickers.append(company.ticker)
        return super().select_filings(company)


class ZeroPeriodPipeline(FakePipeline):
    def select_filings(self, company):
        if company.ticker == "XOM":
            return SimpleNamespace(
                annual=(),
                interim=(),
                requested_annual_periods=5,
                has_complete_annual_history=False,
            )
        return super().select_filings(company)

    def standardize(self, inputs):
        if inputs.company.ticker == "XOM":
            return SimpleNamespace(annual=())
        return super().standardize(inputs)


class StatusPipeline(FakePipeline):
    def standardize(self, inputs):
        end = date(2025, 12, 31)
        source = HistoricalSourceReference(
            EvidenceSourceKind.COMPANY_FACTS,
            "facts-source",
            "accession",
            "us-gaap",
            "OperatingIncomeLoss",
        )
        measures = (
            ResolvedHistoricalMeasure(
                HistoricalMeasure.REVENUE,
                HistoricalMeasureKind.DURATION,
                Decimal("1"),
                "USD",
                date(2025, 1, 1),
                end,
                None,
                HistoricalResolutionKind.DIRECT,
                None,
                (source,),
            ),
            UnavailableHistoricalMeasure(
                HistoricalMeasure.D_AND_A,
                HistoricalMeasureKind.DURATION,
                HistoricalAvailability.MISSING,
                "missing",
                "USD",
                None,
                end,
                None,
            ),
            AmbiguousStandardizedMeasure(
                HistoricalMeasure.CAPEX,
                HistoricalMeasureKind.DURATION,
                "ambiguous",
                "USD",
                None,
                end,
                None,
                None,
                (source,),
            ),
        )
        return SimpleNamespace(annual=(SimpleNamespace(measures=measures),))


class CorpusSmokeRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.securities = load_snapshot(DEFAULT_SNAPSHOT)

    def run_fake(self, pipeline=None):
        return run_corpus(
            self.securities,
            pipeline or FakePipeline(self.securities),
            snapshot_file="docs/universe/sp500-top-50-2026-10-02.csv",
            repository_commit="abc123",
            repository_dirty=True,
            run_timestamp=NOW,
        )

    def test_snapshot_loads_expected_security_and_issuer_counts(self):
        self.assertEqual(len(self.securities), 51)
        self.assertEqual(len({item.cik for item in self.securities}), 50)
        self.assertEqual(
            sum(item.classification == SPECIALIZED_CLASSIFICATION for item in self.securities),
            7,
        )

    def test_snapshot_has_exact_issuer_classification_split(self):
        plans = group_issuers(self.securities)
        counts = {
            classification: sum(
                plan.classification == classification for plan in plans
            )
            for classification in (
                "SUPPORTED_SEED",
                "OPERATING_COMPANY_CANDIDATE",
                "SPECIALIZED_METHODOLOGY_CANDIDATE",
            )
        }
        self.assertEqual(len(self.securities), 51)
        self.assertEqual(len(plans), 50)
        self.assertEqual(
            counts,
            {
                "SUPPORTED_SEED": 5,
                "OPERATING_COMPANY_CANDIDATE": 38,
                "SPECIALIZED_METHODOLOGY_CANDIDATE": 7,
            },
        )
        self.assertEqual(
            sum(
                plan.classification != SPECIALIZED_CLASSIFICATION
                for plan in plans
            ),
            43,
        )

    def test_grouping_preserves_order_and_alphabet_dual_security_identity(self):
        plans = group_issuers(self.securities)
        self.assertEqual(len(plans), 50)
        alphabet = next(plan for plan in plans if plan.cik == 1652044)
        self.assertEqual(alphabet.source_tickers, ("GOOGL", "GOOG"))
        self.assertEqual(alphabet.project_tickers, ("GOOGL", "GOOG"))
        self.assertEqual(alphabet.execution_ticker, "GOOGL")
        self.assertEqual(plans[0].execution_ticker, "NVDA")

    def test_run_attempts_43_generic_issuers_and_skips_seven_specialized(self):
        pipeline = FakePipeline(self.securities)
        result = self.run_fake(pipeline)
        self.assertEqual(sum(item.attempted for item in result.issuers), 43)
        self.assertEqual(sum(item.completed for item in result.issuers), 43)
        skipped = [
            item
            for item in result.issuers
            if item.stage is ExecutionStage.SPECIALIZED_SKIPPED
        ]
        self.assertEqual(len(skipped), 7)
        self.assertTrue(all(not item.attempted for item in skipped))
        self.assertNotIn("BRK-B", pipeline.execution_tickers)

    def test_alphabet_executes_once_and_security_rows_share_result(self):
        pipeline = FakePipeline(self.securities)
        result = self.run_fake(pipeline)
        self.assertEqual(pipeline.execution_tickers.count("GOOGL"), 1)
        self.assertNotIn("GOOG", pipeline.execution_tickers)
        serialized = corpus_result_to_dict(result)
        alphabet_rows = [
            row for row in serialized["securities"] if row["cik"] == 1652044
        ]
        self.assertEqual(len(alphabet_rows), 2)
        self.assertEqual(
            {row["execution_ticker"] for row in alphabet_rows}, {"GOOGL"}
        )

    def test_result_order_is_deterministic(self):
        first = corpus_result_to_dict(self.run_fake())
        second = corpus_result_to_dict(self.run_fake())
        self.assertEqual(first, second)

    def test_one_failure_does_not_abort_later_issuers(self):
        pipeline = FakePipeline(
            self.securities,
            failure_ticker="NVDA",
            failure_stage="facts",
        )
        result = self.run_fake(pipeline)
        nvda = result.issuers[0]
        self.assertFalse(nvda.completed)
        self.assertEqual(nvda.stage, ExecutionStage.COMPANY_FACTS)
        self.assertEqual(nvda.exception_type, "RuntimeError")
        self.assertIn("NVDA failed", nvda.error_message)
        self.assertIn("AAPL", pipeline.execution_tickers)
        self.assertEqual(sum(item.completed for item in result.issuers), 42)

    def test_submissions_transport_failure_has_explicit_stage(self):
        pipeline = SubmissionsFailurePipeline(
            self.securities,
            failure_ticker="NVDA",
        )
        result = self.run_fake(pipeline)
        failure = result.issuers[0]
        self.assertEqual(failure.stage, ExecutionStage.SUBMISSIONS)
        self.assertEqual(failure.exception_type, "SECRequestError")
        self.assertEqual(dict(failure.stage_statuses)["submissions"], "failed")

    def test_ticker_cik_mismatch_marks_stage_failed_and_continues(self):
        pipeline = CIKMismatchPipeline(self.securities, "NVDA")
        result = self.run_fake(pipeline)
        failure = result.issuers[0]
        statuses = dict(failure.stage_statuses)

        self.assertFalse(failure.completed)
        self.assertEqual(failure.stage, ExecutionStage.TICKER_RESOLUTION)
        self.assertEqual(statuses["ticker_resolution"], "failed")
        self.assertTrue(
            all(
                status == "not_started"
                for stage, status in statuses.items()
                if stage != "ticker_resolution"
            )
        )
        self.assertEqual(failure.exception_type, "SmokeRunnerError")
        self.assertIn("does not match snapshot CIK", failure.error_message)
        self.assertNotIn("NVDA", pipeline.selected_tickers)
        self.assertIn("AAPL", pipeline.execution_tickers)
        self.assertEqual(sum(item.completed for item in result.issuers), 42)

    def test_success_records_selected_and_standardized_period_counts(self):
        result = self.run_fake()
        nvda = result.issuers[0]
        self.assertEqual(nvda.stage, ExecutionStage.COMPLETE)
        self.assertEqual(nvda.selected_annual_filings, 5)
        self.assertEqual(
            nvda.selected_annual_periods,
            tuple(f"{year}-12-31" for year in range(2021, 2026)),
        )
        self.assertEqual(nvda.standardized_annual_periods, 5)
        self.assertTrue(all(value == "completed" for _, value in nvda.stage_statuses))

    def test_zero_period_execution_completes_but_summary_marks_it_incomplete(self):
        result = self.run_fake(ZeroPeriodPipeline(self.securities))
        xom = next(item for item in result.issuers if item.plan.execution_ticker == "XOM")

        self.assertTrue(xom.completed)
        self.assertEqual(xom.stage, ExecutionStage.COMPLETE)
        self.assertEqual(xom.selected_annual_filings, 0)
        self.assertEqual(xom.selected_annual_periods, ())
        self.assertEqual(xom.standardized_annual_periods, 0)
        self.assertTrue(all(value == "completed" for _, value in xom.stage_statuses))

        output = io.StringIO()
        print_summary(result, output)
        self.assertIn("Issuers with fewer than five annual filings: ['XOM']", output.getvalue())

    def test_serialization_contains_run_metadata_and_stable_stage_data(self):
        serialized = corpus_result_to_dict(self.run_fake())
        self.assertEqual(serialized["snapshot_date"], "2026-10-02")
        self.assertEqual(serialized["repository_commit"], "abc123")
        self.assertIs(serialized["repository_dirty"], True)
        self.assertEqual(serialized["security_count"], 51)
        self.assertEqual(serialized["issuer_count"], 50)
        self.assertEqual(serialized["generic_execution_count"], 43)
        self.assertEqual(serialized["specialized_skip_count"], 7)

    def test_serialization_preserves_typed_and_resolution_counts(self):
        result = self.run_fake(StatusPipeline(self.securities))
        nvda = corpus_result_to_dict(result)["issuers"][0]
        self.assertEqual(
            nvda["typed_status_counts"],
            {"resolved": 1, "missing": 1, "ambiguous": 1},
        )
        self.assertEqual(
            nvda["measure_status_counts"],
            {
                "capex:ambiguous": 1,
                "depreciation_and_amortization:missing": 1,
                "revenue:resolved": 1,
            },
        )
        self.assertEqual(
            nvda["measure_resolution_counts"], {"revenue:direct": 1}
        )

    def test_json_writer_and_summary_are_machine_and_human_readable(self):
        result = self.run_fake()
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            write_result(result, path)
            payload = json.loads(path.read_text())
        self.assertEqual(payload["issuer_count"], 50)
        output = io.StringIO()
        print_summary(result, output)
        self.assertIn("Generic attempts: 43", output.getvalue())
        self.assertIn("Specialized skipped: 7", output.getvalue())

    def test_runner_never_mutates_snapshot(self):
        before = DEFAULT_SNAPSHOT.read_bytes()
        self.run_fake()
        self.assertEqual(DEFAULT_SNAPSHOT.read_bytes(), before)

    def test_production_pipeline_reuses_one_ticker_dataset_request(self):
        class FakeClient:
            def __init__(self):
                self.calls = []

            def get_json(self, url):
                self.calls.append(url)
                return {
                    "0": {"cik_str": 1, "ticker": "AAA", "title": "A Inc."},
                    "1": {"cik_str": 2, "ticker": "BBB", "title": "B Inc."},
                }

        client = FakeClient()
        pipeline = ProductionCorpusPipeline(client)  # type: ignore[arg-type]
        self.assertEqual(pipeline.resolve_company("AAA").cik, 1)
        self.assertEqual(pipeline.resolve_company("BBB").cik, 2)
        self.assertEqual(len(client.calls), 1)

    def test_production_pipeline_supplies_resolved_annual_periods_to_normalization(self):
        company = SECCompanyIdentity(
            "AAA",
            1,
            "0000000001",
            "A Inc.",
            "ticker-source",
            NOW,
        )
        first_filing = SimpleNamespace(accession_number="first")
        second_filing = SimpleNamespace(accession_number="second")
        filings = SimpleNamespace(annual=(first_filing, second_filing))
        selected_facts = SimpleNamespace(company=company)
        artifacts = (object(), object())
        periods = (object(), object())
        historical = object()
        balance_sheets = object()
        client = object()
        pipeline = ProductionCorpusPipeline(client)  # type: ignore[arg-type]

        with (
            patch(
                "scripts.run_sp500_top50_smoke.fetch_filing_xbrl",
                side_effect=artifacts,
            ) as fetch,
            patch(
                "scripts.run_sp500_top50_smoke.resolve_annual_period",
                side_effect=periods,
            ) as resolve,
            patch(
                "scripts.run_sp500_top50_smoke.normalize_annual_financials",
                return_value=historical,
            ) as normalize_historical,
            patch(
                "scripts.run_sp500_top50_smoke.normalize_annual_balance_sheets",
                return_value=balance_sheets,
            ),
        ):
            result = pipeline.normalize(company, filings, selected_facts)

        self.assertEqual(
            fetch.call_args_list,
            [
                call(client, company, first_filing),
                call(client, company, second_filing),
            ],
        )
        self.assertEqual(resolve.call_args_list, [call(item) for item in artifacts])
        normalize_historical.assert_called_once_with(
            selected_facts,
            filing_xbrl=artifacts,
            annual_periods=periods,
            d_and_a_artifacts=(),
        )
        self.assertIs(result.historical, historical)


if __name__ == "__main__":
    unittest.main()
