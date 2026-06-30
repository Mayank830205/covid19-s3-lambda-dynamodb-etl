"""AWS Lambda function to process COVID-19 JSON data."""

from decimal import Decimal

import boto3

from utils import generate_timestamp, load_json_from_s3


# -----------------------------
# Helper Functions
# -----------------------------

def decimal(value):
    """Convert value to Decimal."""

    if value in (None, ""):
        return Decimal("0")

    return Decimal(str(value))


def get_risk_level(active_cases):
    """Return COVID risk level."""

    active_cases = decimal(active_cases)

    if active_cases >= Decimal("100000"):
        return "HIGH"

    elif active_cases >= Decimal("10000"):
        return "MEDIUM"

    return "LOW"


def validate_record(record):
    """Validate COVID record."""

    if not record.get("country"):
        return False

    try:
        population = int(record.get("population", 0))
    except (TypeError, ValueError):
        return False

    return population > 0


def build_item(record, processed_at):
    """Build DynamoDB item."""

    return {

        "country": record["country"].strip().upper(),

        "continent": record.get("continent", "UNKNOWN"),

        "population": decimal(record.get("population")),

        "total_cases": decimal(record.get("cases")),

        "active_cases": decimal(record.get("active")),

        "recovered": decimal(record.get("recovered")),

        "deaths": decimal(record.get("deaths")),

        "critical": decimal(record.get("critical")),

        "cases_per_million":
            decimal(record.get("casesPerOneMillion")),

        "risk_level":
            get_risk_level(record.get("active")),

        "processed_at_utc":
            processed_at,
    }


# -----------------------------
# Lambda Handler
# -----------------------------

def lambda_handler(event, context):

    print("=" * 60)
    print("COVID JSON ETL Started")
    print("=" * 60)

    record = event["Records"][0]

    bucket_name = record["s3"]["bucket"]["name"]
    object_key = record["s3"]["object"]["key"]

    print(f"Bucket : {bucket_name}")
    print(f"Key    : {object_key}")

    records = load_json_from_s3(
        bucket_name,
        object_key,
    )

    print(f"Records Loaded : {len(records)}")

    processed_at = generate_timestamp()

    table = boto3.resource("dynamodb").Table("covid-table")

    inserted = 0
    rejected = 0

    with table.batch_writer(
        overwrite_by_pkeys=["country"]
    ) as batch:

        for record in records:

            if not validate_record(record):
                rejected += 1
                continue

            item = build_item(
                record,
                processed_at,
            )

            batch.put_item(Item=item)

            inserted += 1

    print("=" * 60)
    print("COVID ETL Completed")
    print("=" * 60)

    print(f"Inserted : {inserted}")
    print(f"Rejected : {rejected}")

    return {

        "statusCode": 200,

        "message": "COVID JSON processed successfully.",

        "records_processed": len(records),

        "records_inserted": inserted,

        "records_rejected": rejected,

        "processed_at": processed_at,
    }