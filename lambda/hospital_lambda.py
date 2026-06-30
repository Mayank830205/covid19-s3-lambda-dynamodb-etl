"""AWS Lambda function to process Hospital Parquet data."""

from decimal import Decimal
import os

import boto3

from utils import generate_timestamp, load_parquet_from_s3


def decimal(value):
    if value in (None, ""):
        return Decimal("0")

    return Decimal(str(value))


def validate_record(record):
    """Validate hospital record."""

    return bool(record.get("location_key"))


def build_item(record, processed_at):
    """Build DynamoDB item."""

    return {

        "location_key": record["location_key"],

        "date": record["date"],

        "new_hospitalized_patients":
            decimal(record.get("new_hospitalized_patients")),

        "cumulative_hospitalized_patients":
            decimal(record.get("cumulative_hospitalized_patients")),

        "current_hospitalized_patients":
            decimal(record.get("current_hospitalized_patients")),

        "new_intensive_care_patients":
            decimal(record.get("new_intensive_care_patients")),

        "cumulative_intensive_care_patients":
            decimal(record.get("cumulative_intensive_care_patients")),

        "current_intensive_care_patients":
            decimal(record.get("current_intensive_care_patients")),

        "new_ventilator_patients":
            decimal(record.get("new_ventilator_patients")),

        "cumulative_ventilator_patients":
            decimal(record.get("cumulative_ventilator_patients")),

        "current_ventilator_patients":
            decimal(record.get("current_ventilator_patients")),

        "processed_at_utc":
            processed_at,
    }


def lambda_handler(event, context):

    print("=" * 60)
    print("Hospital Parquet ETL Started")
    print("=" * 60)

    record = event["Records"][0]

    bucket_name = record["s3"]["bucket"]["name"]
    object_key = record["s3"]["object"]["key"]

    print(f"Bucket : {bucket_name}")
    print(f"Key    : {object_key}")

    records = load_parquet_from_s3(
        bucket_name,
        object_key,
    )

    print(f"Records Loaded : {len(records)}")

    processed_at = generate_timestamp()

    table = boto3.resource("dynamodb").Table(
        os.environ["TABLE_NAME"]
    )

    inserted = 0
    rejected = 0

    with table.batch_writer(
        overwrite_by_pkeys=["location_key", "date"]
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
    print("Hospital ETL Completed")
    print("=" * 60)

    return {
        "statusCode": 200,
        "records_processed": len(records),
        "records_inserted": inserted,
        "records_rejected": rejected,
        "processed_at": processed_at,
    }