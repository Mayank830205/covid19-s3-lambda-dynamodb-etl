"""Process vaccine CSV data from S3 and load it into DynamoDB."""

from decimal import Decimal

import boto3

from utils import generate_timestamp, load_csv_from_s3


def to_decimal(value):
    if value in (None, ""):
        return Decimal("0")
    return Decimal(str(value))


def validate_record(record):
    has_country = bool(record.get("country"))
    has_timeline = any(column.startswith("timeline.") for column in record)

    return has_country and has_timeline


def transform_record(record, processed_at):
    vaccine_column = next(
        column for column in record if column.startswith("timeline.")
    )

    return {
        "country": record["country"].strip().upper(),
        "vaccinations": to_decimal(record[vaccine_column]),
        "processed_at_utc": processed_at,
    }


def lambda_handler(event, context):
    print("Vaccine CSV ETL started")

    s3_record = event["Records"][0]
    bucket_name = s3_record["s3"]["bucket"]["name"]
    object_key = s3_record["s3"]["object"]["key"]

    print(f"Bucket: {bucket_name}")
    print(f"Key: {object_key}")

    records = load_csv_from_s3(bucket_name, object_key)
    processed_at = generate_timestamp()
    table = boto3.resource("dynamodb").Table("vaccine-table")

    inserted = 0
    rejected = 0

    with table.batch_writer(overwrite_by_pkeys=["country"]) as batch:
        for record in records:
            if not validate_record(record):
                rejected += 1
                continue

            batch.put_item(Item=transform_record(record, processed_at))
            inserted += 1

    print("Vaccine CSV ETL completed")
    print(f"Inserted: {inserted}")
    print(f"Rejected: {rejected}")

    return {
        "statusCode": 200,
        "message": "Vaccine CSV processed successfully.",
        "records_processed": len(records),
        "records_inserted": inserted,
        "records_rejected": rejected,
        "processed_at": processed_at,
    }
