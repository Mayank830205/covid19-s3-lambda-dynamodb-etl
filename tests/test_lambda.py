"""Unit tests for orchestration in the Lambda handler."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

LAMBDA_DIRECTORY = Path(__file__).resolve().parents[1] / "lambda"
sys.path.insert(0, str(LAMBDA_DIRECTORY))

import lambda_function


class FakeBatchWriter:
    """Capture items written through the DynamoDB batch writer context."""

    def __init__(self, items: list[dict[str, Any]]) -> None:
        self.items = items

    def __enter__(self) -> "FakeBatchWriter":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def put_item(self, Item: dict[str, Any]) -> None:
        """Record one emulated PutRequest."""
        self.items.append(Item)


class FakeTable:
    """Minimal DynamoDB Table test double."""

    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []
        self.overwrite_keys: list[str] = []

    def batch_writer(self, overwrite_by_pkeys: list[str]) -> FakeBatchWriter:
        """Return a fake writer and capture its deduplication keys."""
        self.overwrite_keys = overwrite_by_pkeys
        return FakeBatchWriter(self.items)


class FakeDynamoDBResource:
    """Minimal DynamoDB resource test double."""

    def __init__(self, table: FakeTable) -> None:
        self.table = table
        self.requested_table_name = ""

    def Table(self, table_name: str) -> FakeTable:
        """Return the configured fake table."""
        self.requested_table_name = table_name
        return self.table


def test_lambda_handler(monkeypatch: Any) -> None:
    """The handler should reject invalid rows and audit successful writes."""
    source_records = [
        {
            "country": "India",
            "continent": "Asia",
            "population": 1_400_000_000,
            "cases": 45_000_000,
            "active": 12_000,
            "recovered": 44_400_000,
            "deaths": 533_000,
            "critical": 100,
            "casesPerOneMillion": 32_143.5,
        },
        {"country": "", "population": 10},
        {"country": "Unknown", "population": 0},
    ]
    fake_table = FakeTable()
    fake_resource = FakeDynamoDBResource(fake_table)

    monkeypatch.setenv("BUCKET_NAME", "portfolio-covid-data")
    monkeypatch.setenv("OBJECT_KEY", "raw/covid_data.json")
    monkeypatch.setenv("TABLE_NAME", "covid_country_stats")
    monkeypatch.setattr(
        lambda_function,
        "load_json_from_s3",
        lambda bucket, key: source_records,
    )
    monkeypatch.setattr(
        lambda_function,
        "generate_timestamp",
        lambda: "2026-01-01T00:00:00+00:00",
    )
    monkeypatch.setattr(
        lambda_function.boto3,
        "resource",
        lambda service_name: fake_resource,
    )

    result = lambda_function.lambda_handler({}, None)

    assert result == {
        "source_file": "s3://portfolio-covid-data/raw/covid_data.json",
        "target_table": "covid_country_stats",
        "input_records": 3,
        "clean_records": 1,
        "rejected_records": 2,
        "inserted_records": 1,
        "processed_at_utc": "2026-01-01T00:00:00+00:00",
    }
    assert fake_resource.requested_table_name == "covid_country_stats"
    assert fake_table.overwrite_keys == ["country"]
    assert fake_table.items[0]["country"] == "INDIA"

