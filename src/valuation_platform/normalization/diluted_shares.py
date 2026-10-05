"""Resolve the narrow filing-XBRL-backed Alphabet diluted-share derivation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from valuation_platform.sec.fact_selection import FilingFactObservations
from valuation_platform.sec.filing_xbrl import (
    FilingXBRLDimension,
    FilingXBRLFact,
    SECFilingXBRL,
)
from valuation_platform.sec.submissions import SECFiling

from .concepts import ConceptKey, FinancialMetric
from .models import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    DerivationOperation,
    DerivedHistoricalValue,
    EvidenceSourceKind,
    FilingXBRLEvidence,
    HistoricalMetricResult,
    HistoricalPeriod,
    MissingHistoricalMetric,
    MissingReason,
)


GOOGL_CIK = 1652044
_DILUTED_SHARES_CONCEPT = ConceptKey(
    "us-gaap",
    "WeightedAverageNumberOfDilutedSharesOutstanding",
)
_XBRLI_NAMESPACE = "http://www.xbrl.org/2003/instance"


class DilutedSharesDerivationError(ValueError):
    """Raised when diluted-share derivation inputs violate their boundary."""


@dataclass(frozen=True)
class DilutedSharesFilingIdentity:
    """One selected filing and taxonomy identity approved by research."""

    accession_number: str
    report_date: date
    us_gaap_namespace: str

    def __post_init__(self) -> None:
        if not self.accession_number or not self.us_gaap_namespace:
            raise DilutedSharesDerivationError(
                "Diluted-share filing identity fields must not be empty"
            )


@dataclass(frozen=True)
class DilutedSharesDerivationPolicy:
    """Approved filing-XBRL derivation for selected Alphabet annual filings."""

    policy_id: str
    company_cik: int
    metric: FinancialMetric
    operation: DerivationOperation
    supported_filings: tuple[DilutedSharesFilingIdentity, ...]

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise DilutedSharesDerivationError("Derivation policy ID must not be empty")
        if self.metric is not FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES:
            raise DilutedSharesDerivationError("Derivation policy has the wrong metric")
        if self.operation is not DerivationOperation.ADD:
            raise DilutedSharesDerivationError("Derivation policy must use ADD")
        if not self.supported_filings or len(
            {item.accession_number for item in self.supported_filings}
        ) != len(self.supported_filings):
            raise DilutedSharesDerivationError(
                "Derivation policy filing identities must be nonempty and unique"
            )


GOOGL_DILUTED_SHARES_DERIVATION_POLICY = DilutedSharesDerivationPolicy(
    policy_id="googl_annual_diluted_weighted_average_shares_v1",
    company_cik=GOOGL_CIK,
    metric=FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES,
    operation=DerivationOperation.ADD,
    supported_filings=(
        DilutedSharesFilingIdentity(
            "0001652044-22-000019",
            date(2021, 12, 31),
            "http://fasb.org/us-gaap/2021-01-31",
        ),
        DilutedSharesFilingIdentity(
            "0001652044-23-000016",
            date(2022, 12, 31),
            "http://fasb.org/us-gaap/2022",
        ),
        DilutedSharesFilingIdentity(
            "0001652044-24-000022",
            date(2023, 12, 31),
            "http://fasb.org/us-gaap/2023",
        ),
    ),
)


def derive_googl_diluted_weighted_average_shares(
    bucket: FilingFactObservations,
    direct_result: HistoricalMetricResult,
    filing_xbrl: SECFilingXBRL | None,
    company_cik: int,
    policy: DilutedSharesDerivationPolicy = GOOGL_DILUTED_SHARES_DERIVATION_POLICY,
) -> HistoricalMetricResult:
    """Apply direct-first precedence and the approved Alphabet A-plus-C rule."""
    if not isinstance(direct_result, MissingHistoricalMetric):
        return direct_result
    filing = bucket.filing
    if company_cik != policy.company_cik:
        return direct_result
    _validate_filing(filing)
    filing_identity = next(
        (
            item
            for item in policy.supported_filings
            if item.accession_number == filing.accession_number
            and item.report_date == filing.report_date
        ),
        None,
    )
    if filing_identity is None:
        return direct_result
    if filing_xbrl is None:
        return _missing(policy)
    if filing_xbrl.company.cik != company_cik:
        raise DilutedSharesDerivationError(
            "Filing-XBRL company does not match selected company"
        )
    if filing_xbrl.filing != filing:
        raise DilutedSharesDerivationError(
            "Filing-XBRL metadata does not match selected filing"
        )

    report_date = filing.report_date
    assert report_date is not None
    class_a = _eligible_class_facts(
        filing_xbrl,
        filing_identity.us_gaap_namespace,
        report_date,
        "A",
    )
    class_c = _eligible_class_facts(
        filing_xbrl,
        filing_identity.us_gaap_namespace,
        report_date,
        "C",
    )
    if not class_a or not class_c:
        return _missing(policy)
    if len(class_a) != 1 or len(class_c) != 1:
        return _ambiguous(policy, (*class_a, *class_c), filing_xbrl)

    operands = (class_a[0], class_c[0])
    periods = {(fact.start, fact.end) for fact in operands}
    if len(periods) != 1:
        return _ambiguous(policy, operands, filing_xbrl)
    start, end = next(iter(periods))
    if start is None:
        return _missing(policy)

    evidence = tuple(
        _evidence(fact, filing, filing_xbrl.retrieved_at) for fact in operands
    )
    return DerivedHistoricalValue(
        metric=policy.metric,
        value=sum((item.value for item in evidence), Decimal(0)),
        unit="shares",
        period=HistoricalPeriod(start=start, end=end),
        policy_id=policy.policy_id,
        operation=policy.operation,
        operands=evidence,
    )


def _validate_filing(filing: SECFiling) -> None:
    if filing.form != "10-K" or filing.report_date is None:
        raise DilutedSharesDerivationError(
            "Diluted-share derivation requires an exact 10-K with a report date"
        )


def _eligible_class_facts(
    filing_xbrl: SECFilingXBRL,
    us_gaap_namespace: str,
    report_date: date,
    share_class: str,
) -> tuple[FilingXBRLFact, ...]:
    facts = tuple(
        fact
        for fact in filing_xbrl.facts
        if _is_eligible_fact(
            fact,
            us_gaap_namespace,
            report_date,
            filing_xbrl.filing.accession_number,
            share_class,
        )
    )
    return tuple(sorted(facts, key=_fact_order_key))


def _is_eligible_fact(
    fact: FilingXBRLFact,
    us_gaap_namespace: str,
    report_date: date,
    accession_number: str,
    share_class: str,
) -> bool:
    if (
        fact.namespace != us_gaap_namespace
        or fact.concept != _DILUTED_SHARES_CONCEPT.name
        or fact.accession_number != accession_number
        or fact.start is None
        or fact.end != report_date
        or not _unit_is_shares(fact)
        or not _is_integer_decimal(fact.numeric_value)
        or fact.is_nil
        or len(fact.dimensions) != 1
    ):
        return False
    dimension = fact.dimensions[0]
    member = dimension.explicit_member
    if (
        dimension.typed_member_xml is not None
        or member is None
        or dimension.dimension.namespace != fact.namespace
        or dimension.dimension.local_name != "StatementClassOfStockAxis"
    ):
        return False
    if share_class == "A":
        return (
            member.namespace == fact.namespace
            and member.local_name == "CommonClassAMember"
        )
    return (
        member.namespace == f"http://www.google.com/{report_date:%Y%m%d}"
        and member.local_name == "CapitalClassCMember"
    )


def _unit_is_shares(fact: FilingXBRLFact) -> bool:
    unit = fact.unit
    return (
        fact.unit_ref is not None
        and unit is not None
        and not unit.denominator_measures
        and len(unit.numerator_measures) == 1
        and unit.numerator_measures[0].namespace == _XBRLI_NAMESPACE
        and unit.numerator_measures[0].local_name == "shares"
    )


def _is_integer_decimal(value: object) -> bool:
    return isinstance(value, Decimal) and value.is_finite() and value == value.to_integral_value()


def _missing(policy: DilutedSharesDerivationPolicy) -> MissingHistoricalMetric:
    return MissingHistoricalMetric(
        metric=policy.metric,
        reason=MissingReason.NO_VALID_DERIVATION_OPERANDS,
        examined_concepts=(_DILUTED_SHARES_CONCEPT,),
    )


def _ambiguous(
    policy: DilutedSharesDerivationPolicy,
    facts: tuple[FilingXBRLFact, ...],
    filing_xbrl: SECFilingXBRL,
) -> AmbiguousHistoricalMetric:
    ordered = tuple(sorted(facts, key=_fact_order_key))
    return AmbiguousHistoricalMetric(
        metric=policy.metric,
        reason=AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS,
        candidates=tuple(
            _evidence(fact, filing_xbrl.filing, filing_xbrl.retrieved_at)
            for fact in ordered
        ),
    )


def _evidence(
    fact: FilingXBRLFact,
    filing: SECFiling,
    retrieved_at: datetime,
) -> FilingXBRLEvidence:
    value = fact.numeric_value
    if not _is_integer_decimal(value):
        raise DilutedSharesDerivationError(
            "Diluted-share filing-XBRL evidence is not an integer"
        )
    assert isinstance(value, Decimal)
    return FilingXBRLEvidence(
        source_kind=EvidenceSourceKind.FILING_XBRL,
        source_url=fact.source_url,
        namespace=fact.namespace,
        concept=fact.concept,
        raw_value=fact.raw_value,
        value=value,
        unit="shares",
        start=fact.start,
        end=fact.end,
        accession_number=fact.accession_number,
        observation_form=filing.form,
        observation_filed=filing.filing_date,
        filing_report_date=filing.report_date,
        primary_document=filing.primary_document,
        retrieved_at=retrieved_at,
        context_id=fact.context_id,
        dimensions=fact.dimensions,
        decimals=fact.decimals,
        is_nil=fact.is_nil,
    )


def _fact_order_key(fact: FilingXBRLFact) -> tuple[object, ...]:
    dimension_key = tuple(
        (
            item.dimension.namespace,
            item.dimension.local_name,
            None if item.explicit_member is None else item.explicit_member.namespace,
            None if item.explicit_member is None else item.explicit_member.local_name,
            item.typed_member_xml,
        )
        for item in fact.dimensions
    )
    return (
        fact.namespace,
        fact.concept,
        fact.start or date.min,
        fact.end,
        dimension_key,
        "" if fact.raw_value is None else fact.raw_value,
        fact.context_id,
    )
