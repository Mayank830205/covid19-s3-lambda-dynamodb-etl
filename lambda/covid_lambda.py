"""Process COVID-19 JSON data from S3 and load it into DynamoDB."""

from decimal import Decimal

import boto3

from utils import generate_timestamp, load_json_from_s3


def to_decimal(value):
    if value in (None, ""):
        return Decimal("0")
    return Decimal(str(value))


def get_risk_level(active_cases):
    active_cases = to_decimal(active_cases)

    if active_cases >= Decimal("100000"):
        return "HIGH"
    if active_cases >= Decimal("10000"):
        return "MEDIUM"
    return "LOW"


def validate_record(record):
    if not record.get("country"):
        return False

    try:
        population = int(record.get("population", 0))
    except (TypeError, ValueError):
        return False

    return population > 0


def transform_record(record, processed_at):
    return {
        "country": record["country"].strip().upper(),
        "continent": record.get("continent", "UNKNOWN"),
        "population": to_decimal(record.get("population")),
        "total_cases": to_decimal(record.get("cases")),
        "active_cases": to_decimal(record.get("active")),
        "recovered": to_decimal(record.get("recovered")),
        "deaths": to_decimal(record.get("deaths")),
        "critical": to_decimal(record.get("critical")),
        "cases_per_million": to_decimal(record.get("casesPerOneMillion")),
        "risk_level": get_risk_level(record.get("active")),
        "processed_at_utc": processed_at,
    }


def lambda_handler(event, context):
    print("COVID JSON ETL started")

    s3_record = event["Records"][0]
    bucket_name = s3_record["s3"]["bucket"]["name"]
    object_key = s3_record["s3"]["object"]["key"]

    print(f"Bucket: {bucket_name}")
    print(f"Key: {object_key}")

    records = load_json_from_s3(bucket_name, object_key)
    processed_at = generate_timestamp()
    table = boto3.resource("dynamodb").Table("covid-table")

    inserted = 0
    rejected = 0

    with table.batch_writer(overwrite_by_pkeys=["country"]) as batch:
        for record in records:
            if not validate_record(record):
                rejected += 1
                continue

            batch.put_item(Item=transform_record(record, processed_at))
            inserted += 1

    print("COVID JSON ETL completed")
    print(f"Inserted: {inserted}")
    print(f"Rejected: {rejected}")

    return {
        "statusCode": 200,
        "message": "COVID JSON processed successfully.",
        "records_processed": len(records),
        "records_inserted": inserted,
        "records_rejected": rejected,
        "processed_at": processed_at,
    }
