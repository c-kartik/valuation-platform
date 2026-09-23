"""Associate parsed Company Facts observations with selected SEC filings."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from .company_facts import SECCompanyFacts, SECFactObservation
from .filing_selection import SelectedFilings
from .submissions import SECFiling
from .tickers import SECCompanyIdentity


class FactSelectionError(Exception):
    """Raised when fact observations cannot be associated unambiguously."""


class ObservationPeriodType(Enum):
    INSTANT = "instant"
    DURATION = "duration"


class ObservationRelationship(Enum):
    CURRENT = "current"
    COMPARATIVE = "comparative"
    AFTER_REPORT_DATE = "after_report_date"


@dataclass(frozen=True)
class SelectedFactObservation:
    """One parsed fact associated with a selected filing."""

    taxonomy: str
    concept: str
    observation: SECFactObservation
    relationship: ObservationRelationship

    @property
    def period_type(self) -> ObservationPeriodType:
        """Classify the observation from its SEC period context."""
        if self.observation.start is None:
            return ObservationPeriodType.INSTANT
        return ObservationPeriodType.DURATION


@dataclass(frozen=True)
class FilingFactObservations:
    """Company Facts observations disclosed by one selected filing."""

    filing: SECFiling
    observations: tuple[SelectedFactObservation, ...]

    def for_concept(
        self,
        taxonomy: str,
        concept: str,
    ) -> tuple[SelectedFactObservation, ...]:
        """Return observations matching one exact taxonomy and concept."""
        return tuple(
            selected
            for selected in self.observations
            if selected.taxonomy == taxonomy and selected.concept == concept
        )


@dataclass(frozen=True)
class SelectedFactObservations:
    """Compact Company Facts subset associated with selected filings."""

    company: SECCompanyIdentity
    source_url: str
    retrieved_at: datetime
    annual: tuple[FilingFactObservations, ...]
    interim: tuple[FilingFactObservations, ...]


def select_fact_observations(
    selected_filings: SelectedFilings,
    company_facts: SECCompanyFacts,
) -> SelectedFactObservations:
    """Associate parsed facts with selected filings without network access."""
    annual_filings = tuple(selected_filings.annual)
    interim_filings = tuple(selected_filings.interim)
    all_filings = annual_filings + interim_filings
    filings_by_accession = _validate_selected_filings(all_filings)

    matched: dict[str, list[SelectedFactObservation]] = {
        accession: [] for accession in filings_by_accession
    }
    for concept in company_facts.concepts:
        for observation in concept.observations:
            filing = filings_by_accession.get(observation.accession_number)
            if filing is None:
                continue
            matched[observation.accession_number].append(
                SelectedFactObservation(
                    taxonomy=concept.taxonomy,
                    concept=concept.name,
                    observation=observation,
                    relationship=_classify_relationship(observation, filing),
                )
            )

    for accession, observations in matched.items():
        _reject_exact_duplicates(accession, observations)
        observations.sort(key=_observation_sort_key)

    return SelectedFactObservations(
        company=company_facts.company,
        source_url=company_facts.source_url,
        retrieved_at=company_facts.retrieved_at,
        annual=tuple(
            FilingFactObservations(
                filing=filing,
                observations=tuple(matched[filing.accession_number]),
            )
            for filing in annual_filings
        ),
        interim=tuple(
            FilingFactObservations(
                filing=filing,
                observations=tuple(matched[filing.accession_number]),
            )
            for filing in interim_filings
        ),
    )


def _validate_selected_filings(
    filings: tuple[SECFiling, ...],
) -> dict[str, SECFiling]:
    filings_by_accession: dict[str, SECFiling] = {}
    for filing in filings:
        if filing.report_date is None:
            raise FactSelectionError(
                f"Selected filing {filing.accession_number!r} has no report date"
            )
        if filing.accession_number in filings_by_accession:
            raise FactSelectionError(
                "Selected filings contain duplicate accession number "
                f"{filing.accession_number!r}"
            )
        filings_by_accession[filing.accession_number] = filing
    return filings_by_accession


def _classify_relationship(
    observation: SECFactObservation,
    filing: SECFiling,
) -> ObservationRelationship:
    report_date = filing.report_date
    if report_date is None:
        raise FactSelectionError(
            f"Selected filing {filing.accession_number!r} has no report date"
        )
    if observation.end < report_date:
        return ObservationRelationship.COMPARATIVE
    if observation.end > report_date:
        return ObservationRelationship.AFTER_REPORT_DATE
    return ObservationRelationship.CURRENT


def _reject_exact_duplicates(
    accession: str,
    observations: list[SelectedFactObservation],
) -> None:
    identities = Counter(_observation_identity(selected) for selected in observations)
    duplicates = [
        (identity, count) for identity, count in identities.items() if count > 1
    ]
    if not duplicates:
        return

    duplicates.sort(key=lambda duplicate: _identity_sort_key(duplicate[0]))
    (taxonomy, concept, unit, start, end), count = duplicates[0]
    raise FactSelectionError(
        f"Selected filing {accession!r} has {count} observations for exact identity "
        f"taxonomy={taxonomy!r}, concept={concept!r}, unit={unit!r}, "
        f"start={start!r}, end={end!r}"
    )


def _observation_identity(
    selected: SelectedFactObservation,
) -> tuple[str, str, str, date | None, date]:
    observation = selected.observation
    return (
        selected.taxonomy,
        selected.concept,
        observation.unit,
        observation.start,
        observation.end,
    )


def _observation_sort_key(
    selected: SelectedFactObservation,
) -> tuple[str, str, str, date, bool, date]:
    observation = selected.observation
    return (
        selected.taxonomy,
        selected.concept,
        observation.unit,
        observation.end,
        observation.start is not None,
        observation.start or date.min,
    )


def _identity_sort_key(
    identity: tuple[str, str, str, date | None, date],
) -> tuple[str, str, str, date, bool, date]:
    taxonomy, concept, unit, start, end = identity
    return (
        taxonomy,
        concept,
        unit,
        end,
        start is not None,
        start or date.min,
    )
