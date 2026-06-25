import os
import boto3

from transformations import build_item, validate_record
from utils import generate_timestamp, load_json_from_s3


def lambda_handler(event, context):

    bucket_name = os.environ["BUCKET_NAME"]
    object_key = os.environ["OBJECT_KEY"]
    table_name = os.environ["TABLE_NAME"]

    records = load_json_from_s3(bucket_name, object_key)

    processed_at = generate_timestamp()

    table = boto3.resource("dynamodb").Table(table_name)

    inserted = 0
    rejected = 0

    with table.batch_writer(overwrite_by_pkeys=["country"]) as batch:
        for record in records:

            if not validate_record(record):
                rejected += 1
                continue

            item = build_item(record, processed_at)
            batch.put_item(Item=item)
            inserted += 1

    return {
        "statusCode": 200,
        "message": "ETL Completed Successfully",
        "records_processed": len(records),
        "records_inserted": inserted,
        "records_rejected": rejected,
    }