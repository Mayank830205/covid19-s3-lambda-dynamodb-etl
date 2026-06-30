"""AWS Lambda function to process Vaccine CSV data."""

from decimal import Decimal
import os

import boto3

from utils import generate_timestamp, load_csv_from_s3


def decimal(value):
    if value in (None, ""):
        return Decimal("0")
    return Decimal(str(value))


def validate_record(record):
    """Validate vaccine record."""

    return bool(record.get("country"))


def build_item(record, processed_at):
    """Build DynamoDB item."""

    vaccine_column = next(
        col
        for col in record.keys()
        if col.startswith("timeline.")
    )

    return {
        "country": record["country"].strip().upper(),
        "vaccinations": decimal(record[vaccine_column]),
        "processed_at_utc": processed_at,
    }


def lambda_handler(event, context):

    print("=" * 60)
    print("Vaccine CSV ETL Started")
    print("=" * 60)

    record = event["Records"][0]

    bucket_name = record["s3"]["bucket"]["name"]
    object_key = record["s3"]["object"]["key"]

    print(f"Bucket : {bucket_name}")
    print(f"Key    : {object_key}")

    records = load_csv_from_s3(bucket_name, object_key)

    print(f"Records Loaded : {len(records)}")

    processed_at = generate_timestamp()

    table = boto3.resource("dynamodb").Table(
        os.environ["TABLE_NAME"]
    )

    inserted = 0
    rejected = 0

    with table.batch_writer(
        overwrite_by_pkeys=["country"]
    ) as batch:

        for record in records:

            if not validate_record(record):
                rejected += 1
                continue

            batch.put_item(
                Item=build_item(
                    record,
                    processed_at,
                )
            )

            inserted += 1

    print("=" * 60)
    print("Vaccine ETL Completed")
    print("=" * 60)

    return {
        "statusCode": 200,
        "records_processed": len(records),
        "records_inserted": inserted,
        "records_rejected": rejected,
        "processed_at": processed_at,
    }