import os
import boto3

from transformations import build_item, validate_record
from utils import generate_timestamp, load_json_from_s3


def lambda_handler(event, context):

    print("========== COVID-19 ETL Pipeline Started ==========")

    bucket_name = os.environ["BUCKET_NAME"]
    object_key = os.environ["OBJECT_KEY"]
    table_name = os.environ["TABLE_NAME"]

    print(f"Reading data from S3 Bucket: {bucket_name}")
    print(f"Object Key: {object_key}")

    records = load_json_from_s3(bucket_name, object_key)

    print(f"Total records loaded: {len(records)}")

    processed_at = generate_timestamp()

    table = boto3.resource("dynamodb").Table(table_name)

    inserted = 0
    rejected = 0

    print("Starting data transformation...")

    with table.batch_writer(overwrite_by_pkeys=["country"]) as batch:

        for record in records:

            if not validate_record(record):
                rejected += 1
                continue

            item = build_item(record, processed_at)
            batch.put_item(Item=item)
            inserted += 1

    print("Data successfully loaded into DynamoDB")
    print(f"Inserted Records : {inserted}")
    print(f"Rejected Records : {rejected}")
    print(f"Processed Time   : {processed_at}")

    print("========== ETL Pipeline Completed ==========")

    return {
        "statusCode": 200,
        "message": "COVID-19 ETL Completed Successfully",
        "records_processed": len(records),
        "records_inserted": inserted,
        "records_rejected": rejected,
        "processed_at": processed_at,
    }