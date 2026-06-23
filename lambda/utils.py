"""Shared utilities for S3 loading, numeric conversion, and timestamps."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping, Sequence

import boto3
from botocore.exceptions import BotoCoreError, ClientError

LOGGER = logging.getLogger(__name__)


def load_json_from_s3(
    bucket_name: str,
    object_key: str,
    s3_client: Any | None = None,
) -> list[dict[str, Any]]:
    """Read a JSON array from S3 while preserving numbers as ``Decimal``."""
    if not bucket_name or not object_key:
        raise ValueError("Both bucket_name and object_key are required")

    client = s3_client or boto3.client("s3")
    try:
        response = client.get_object(Bucket=bucket_name, Key=object_key)
        raw_content = response["Body"].read().decode("utf-8")
        payload = json.loads(
            raw_content,
            parse_float=Decimal,
            parse_int=Decimal,
        )
    except (
        BotoCoreError,
        ClientError,
        KeyError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        LOGGER.exception("Could not load s3://%s/%s", bucket_name, object_key)
        raise

    if not isinstance(payload, list):
        raise ValueError("The S3 source file must contain a JSON array")
    if not all(isinstance(record, dict) for record in payload):
        raise ValueError("Every source array element must be a JSON object")

    return payload


def convert_to_decimal(value: Any) -> Any:
    """Recursively convert Python numeric values to DynamoDB-safe decimals."""
    if isinstance(value, Decimal) or isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, Mapping):
        return {key: convert_to_decimal(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    ):
        return [convert_to_decimal(item) for item in value]
    return value


def generate_timestamp() -> str:
    """Return a timezone-aware UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
