"""Pure validation and transformation functions for COVID-19 records."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Mapping

try:
    from .utils import convert_to_decimal
except ImportError:  # Supports the flat directory layout used by AWS Lambda.
    from utils import convert_to_decimal

NUMERIC_FIELD_MAP = {
    "population": "population",
    "cases": "total_cases",
    "active": "active_cases",
    "recovered": "recovered",
    "deaths": "deaths",
    "critical": "critical",
    "casesPerOneMillion": "cases_per_million",
}


def _as_decimal(value: Any) -> Decimal:
    """Convert a source numeric value to a finite ``Decimal``."""
    normalized_value = 0 if value is None else value
    converted = convert_to_decimal(normalized_value)
    if not isinstance(converted, Decimal) or not converted.is_finite():
        raise ValueError(f"Expected a finite numeric value, got {value!r}")
    return converted


def get_risk_level(active_cases: Decimal | int | float) -> str:
    """Classify active case counts into LOW, MEDIUM, or HIGH risk."""
    active_case_count = _as_decimal(active_cases)
    if active_case_count >= Decimal("100000"):
        return "HIGH"
    if active_case_count >= Decimal("10000"):
        return "MEDIUM"
    return "LOW"


def clean_country(country: Any) -> str:
    """Trim and uppercase a country value, returning an empty string if absent."""
    if country is None:
        return ""
    return str(country).strip().upper()


def validate_record(record: Mapping[str, Any]) -> bool:
    """Return whether a source record has a country and positive population."""
    if not clean_country(record.get("country")):
        return False

    try:
        population = _as_decimal(record.get("population"))
    except ValueError:
        return False
    return population > 0


def build_item(
    record: Mapping[str, Any],
    processed_at: str,
) -> dict[str, Any]:
    """Build one validated DynamoDB item from a disease.sh source record."""
    if not validate_record(record):
        raise ValueError("Cannot build an item from an invalid source record")
    if not processed_at:
        raise ValueError("processed_at must not be empty")

    item: dict[str, Any] = {
        "country": clean_country(record.get("country")),
        "continent": str(record.get("continent") or "UNKNOWN").strip(),
        "processed_at_utc": processed_at,
    }
    for source_name, target_name in NUMERIC_FIELD_MAP.items():
        item[target_name] = _as_decimal(record.get(source_name))

    item["risk_level"] = get_risk_level(item["active_cases"])
    return item

