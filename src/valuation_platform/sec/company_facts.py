"""Retrieve and faithfully represent SEC Company Facts data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, TypeAlias

from .client import SECClient
from .tickers import SECCompanyIdentity


COMPANY_FACTS_URL_TEMPLATE = (
    "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
)

SECFactValue: TypeAlias = str | int | float | bool | None

_MISSING = object()


class CompanyFactsDataError(Exception):
    """Raised when SEC Company Facts data is malformed or inconsistent."""


@dataclass(frozen=True)
class SECFactObservation:
    """One observation from an SEC Company Facts unit bucket."""

    unit: str
    value: SECFactValue
    start: date | None
    end: date
    accession_number: str
    fiscal_year: int | None
    fiscal_period: str | None
    form: str
    filed: date
    frame: str | None


@dataclass(frozen=True)
class SECFactConcept:
    """One taxonomy concept and all observations returned for it."""

    taxonomy: str
    name: str
    label: str | None
    description: str | None
    observations: tuple[SECFactObservation, ...]


@dataclass(frozen=True)
class SECCompanyFacts:
    """A company's complete typed SEC Company Facts response."""

    company: SECCompanyIdentity
    entity_name: str
    concepts: tuple[SECFactConcept, ...]
    source_url: str
    retrieved_at: datetime


def fetch_company_facts(
    client: SECClient,
    company: SECCompanyIdentity,
) -> SECCompanyFacts:
    """Fetch and parse all SEC Company Facts for a resolved company."""
    source_url = COMPANY_FACTS_URL_TEMPLATE.format(cik_padded=company.cik_padded)
    payload = client.get_json(source_url)
    entity_name, concepts = _parse_company_facts(payload, company)

    return SECCompanyFacts(
        company=company,
        entity_name=entity_name,
        concepts=concepts,
        source_url=source_url,
        retrieved_at=datetime.now(timezone.utc),
    )


def _parse_company_facts(
    payload: Any,
    company: SECCompanyIdentity,
) -> tuple[str, tuple[SECFactConcept, ...]]:
    if not isinstance(payload, dict):
        raise CompanyFactsDataError("SEC Company Facts response must be an object")

    returned_cik = payload.get("cik", _MISSING)
    if (
        not isinstance(returned_cik, int)
        or isinstance(returned_cik, bool)
        or returned_cik < 0
    ):
        raise CompanyFactsDataError("SEC Company Facts response has an invalid CIK")
    if returned_cik != company.cik:
        raise CompanyFactsDataError(
            f"SEC Company Facts CIK {returned_cik} does not match "
            f"requested CIK {company.cik}"
        )

    entity_name = payload.get("entityName")
    if not isinstance(entity_name, str) or not entity_name:
        raise CompanyFactsDataError(
            "SEC Company Facts response has an invalid entityName"
        )

    facts = payload.get("facts")
    if not isinstance(facts, dict):
        raise CompanyFactsDataError(
            "SEC Company Facts response must contain a facts object"
        )

    concepts = []
    for taxonomy in _sorted_object_keys(facts, "facts"):
        taxonomy_concepts = facts[taxonomy]
        if not isinstance(taxonomy_concepts, dict):
            raise CompanyFactsDataError(
                f"SEC Company Facts taxonomy {taxonomy!r} must be an object"
            )

        for concept_name in _sorted_object_keys(
            taxonomy_concepts, f"taxonomy {taxonomy!r}"
        ):
            concepts.append(
                _parse_concept(
                    taxonomy,
                    concept_name,
                    taxonomy_concepts[concept_name],
                )
            )

    return entity_name, tuple(concepts)


def _parse_concept(taxonomy: str, name: str, value: Any) -> SECFactConcept:
    location = f"concept {taxonomy}:{name}"
    if not isinstance(value, dict):
        raise CompanyFactsDataError(f"SEC Company Facts {location} must be an object")

    label = _optional_string(value, "label", location)
    description = _optional_string(value, "description", location)
    units = value.get("units")
    if not isinstance(units, dict):
        raise CompanyFactsDataError(
            f"SEC Company Facts {location} must contain a units object"
        )

    observations = []
    for unit in _sorted_object_keys(units, f"units for {location}"):
        unit_observations = units[unit]
        if not isinstance(unit_observations, list):
            raise CompanyFactsDataError(
                f"SEC Company Facts unit {unit!r} for {location} must be an array"
            )
        for observation_index, observation in enumerate(unit_observations):
            observations.append(
                _parse_observation(
                    unit,
                    observation,
                    f"{location}, unit {unit!r}, observation {observation_index}",
                )
            )

    return SECFactConcept(
        taxonomy=taxonomy,
        name=name,
        label=label,
        description=description,
        observations=tuple(observations),
    )


def _parse_observation(
    unit: str,
    value: Any,
    location: str,
) -> SECFactObservation:
    if not isinstance(value, dict):
        raise CompanyFactsDataError(
            f"SEC Company Facts {location} must be an object"
        )

    fact_value = value.get("val", _MISSING)
    if fact_value is _MISSING or not _is_json_scalar(fact_value):
        raise CompanyFactsDataError(
            f"SEC Company Facts {location} has an invalid or missing val"
        )

    return SECFactObservation(
        unit=unit,
        value=fact_value,
        start=_optional_date(value, "start", location),
        end=_required_date(value, "end", location),
        accession_number=_required_string(value, "accn", location),
        fiscal_year=_optional_integer(value, "fy", location),
        fiscal_period=_optional_string(value, "fp", location),
        form=_required_string(value, "form", location),
        filed=_required_date(value, "filed", location),
        frame=_optional_string(value, "frame", location),
    )


def _sorted_object_keys(value: dict[Any, Any], location: str) -> list[str]:
    for key in value:
        if not isinstance(key, str) or not key:
            raise CompanyFactsDataError(
                f"SEC Company Facts {location} contains an invalid object key"
            )
    return sorted(value)


def _required_string(value: dict[str, Any], field: str, location: str) -> str:
    field_value = value.get(field)
    if not isinstance(field_value, str) or not field_value:
        raise CompanyFactsDataError(
            f"SEC Company Facts {location} has invalid or missing {field}"
        )
    return field_value


def _optional_string(
    value: dict[str, Any],
    field: str,
    location: str,
) -> str | None:
    field_value = value.get(field, _MISSING)
    if field_value is _MISSING or field_value is None:
        return None
    if not isinstance(field_value, str):
        raise CompanyFactsDataError(
            f"SEC Company Facts {location} has invalid {field}"
        )
    return field_value


def _optional_integer(
    value: dict[str, Any],
    field: str,
    location: str,
) -> int | None:
    field_value = value.get(field, _MISSING)
    if field_value is _MISSING or field_value is None:
        return None
    if not isinstance(field_value, int) or isinstance(field_value, bool):
        raise CompanyFactsDataError(
            f"SEC Company Facts {location} has invalid {field}"
        )
    return field_value


def _required_date(value: dict[str, Any], field: str, location: str) -> date:
    field_value = value.get(field)
    if not isinstance(field_value, str) or not field_value:
        raise CompanyFactsDataError(
            f"SEC Company Facts {location} has invalid or missing {field}"
        )
    return _parse_date(field_value, field, location)


def _optional_date(
    value: dict[str, Any],
    field: str,
    location: str,
) -> date | None:
    field_value = value.get(field, _MISSING)
    if field_value is _MISSING or field_value is None:
        return None
    if not isinstance(field_value, str) or not field_value:
        raise CompanyFactsDataError(
            f"SEC Company Facts {location} has invalid {field}"
        )
    return _parse_date(field_value, field, location)


def _parse_date(value: str, field: str, location: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise CompanyFactsDataError(
            f"SEC Company Facts {location} has invalid {field} date {value!r}"
        ) from exc
    if parsed.isoformat() != value:
        raise CompanyFactsDataError(
            f"SEC Company Facts {location} field {field} must use YYYY-MM-DD"
        )
    return parsed


def _is_json_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))
