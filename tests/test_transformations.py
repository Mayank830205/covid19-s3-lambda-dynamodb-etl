"""Unit tests for pure transformation behavior."""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

LAMBDA_DIRECTORY = Path(__file__).resolve().parents[1] / "lambda"
sys.path.insert(0, str(LAMBDA_DIRECTORY))

from transformations import build_item, get_risk_level, validate_record


def test_get_risk_level() -> None:
    """Risk thresholds should include their lower boundary."""
    assert get_risk_level(9_999) == "LOW"
    assert get_risk_level(10_000) == "MEDIUM"
    assert get_risk_level(99_999) == "MEDIUM"
    assert get_risk_level(100_000) == "HIGH"


def test_validate_record() -> None:
    """Country and a positive population are required."""
    assert validate_record({"country": "India", "population": 1_000})
    assert not validate_record({"country": "", "population": 1_000})
    assert not validate_record({"population": 1_000})
    assert not validate_record({"country": "India", "population": 0})
    assert not validate_record({"country": "India", "population": None})


def test_build_item() -> None:
    """Source fields should map to a typed, enriched DynamoDB item."""
    source_record = {
        "country": "  India ",
        "continent": "Asia",
        "population": 1_400_000_000,
        "cases": 45_000_000,
        "active": 12_000,
        "recovered": 44_400_000,
        "deaths": 533_000,
        "critical": 100,
        "casesPerOneMillion": 32_143.5,
    }
    timestamp = "2026-01-01T00:00:00+00:00"

    item = build_item(source_record, timestamp)

    assert item["country"] == "INDIA"
    assert item["continent"] == "Asia"
    assert item["risk_level"] == "MEDIUM"
    assert item["processed_at_utc"] == timestamp
    for field_name in (
        "population",
        "total_cases",
        "active_cases",
        "recovered",
        "deaths",
        "critical",
        "cases_per_million",
    ):
        assert isinstance(item[field_name], Decimal)

