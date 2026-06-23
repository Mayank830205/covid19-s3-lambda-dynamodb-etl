"""AWS Lambda entry point for the S3-to-DynamoDB COVID-19 ETL job."""

from __future__ import annotations

import logging
import os
from typing import Any, Mapping
from urllib.parse import unquote_plus

import boto3

try:
    from .transformations import build_item, validate_record
    from .utils import generate_timestamp, load_json_from_s3
except ImportError:  # Supports uploading the lambda directory as a flat ZIP.
    from transformations import build_item, validate_record
    from utils import generate_timestamp, load_json_from_s3

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())


def _required_environment_variable(name: str) -> str:
    """Return a required environment variable or raise a clear error."""
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} environment variable is required")
    return value


def _resolve_s3_source(
    event: Mapping[str, Any] | None,
    default_bucket: str,
    default_key: str,
) -> tuple[str, str]:
    """Use an S3 notification source when present, otherwise use configured values."""
    try:
        record = event["Records"][0] if event else None
        if record and record.get("eventSource") == "aws:s3":
            bucket = record["s3"]["bucket"]["name"]
            object_key = unquote_plus(record["s3"]["object"]["key"])
            return bucket, object_key
    except (KeyError, IndexError, TypeError):
        LOGGER.warning("Malformed S3 event; using configured source location")

    return default_bucket, default_key


def lambda_handler(
    event: Mapping[str, Any] | None,
    context: Any,
) -> dict[str, Any]:
    """Transform a country data file from S3 and batch-load DynamoDB."""
    del context  # The current workflow does not require Lambda context metadata.

    configured_bucket = _required_environment_variable("BUCKET_NAME")
    configured_key = _required_environment_variable("OBJECT_KEY")
    table_name = _required_environment_variable("TABLE_NAME")
    bucket_name, object_key = _resolve_s3_source(
        event,
        configured_bucket,
        configured_key,
    )
    processed_at = generate_timestamp()
    source_file = f"s3://{bucket_name}/{object_key}"

    LOGGER.info("Starting ETL from %s into DynamoDB table %s", source_file, table_name)
    source_records = load_json_from_s3(bucket_name, object_key)

    clean_items: list[dict[str, Any]] = []
    rejected_records = 0
    for index, record in enumerate(source_records):
        if not validate_record(record):
            rejected_records += 1
            LOGGER.warning("Rejected source record at index %d", index)
            continue
        try:
            clean_items.append(build_item(record, processed_at))
        except ValueError:
            rejected_records += 1
            LOGGER.exception(
                "Transformation failed for source record at index %d",
                index,
            )

    table = boto3.resource("dynamodb").Table(table_name)
    inserted_records = 0
    if clean_items:
        with table.batch_writer(overwrite_by_pkeys=["country"]) as batch:
            for item in clean_items:
                batch.put_item(Item=item)
                inserted_records += 1

    summary = {
        "source_file": source_file,
        "target_table": table_name,
        "input_records": len(source_records),
        "clean_records": len(clean_items),
        "rejected_records": rejected_records,
        "inserted_records": inserted_records,
        "processed_at_utc": processed_at,
    }
    LOGGER.info("ETL completed: %s", summary)
    return summary
