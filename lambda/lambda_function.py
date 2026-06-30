import boto3

from transformations import build_item, validate_record
from utils import (
    generate_timestamp,
    load_json_from_s3,
    load_csv_from_s3,
    load_parquet_from_s3,
)


def lambda_handler(event, context):

    print("=" * 60)
    print("COVID-19 Multi-Format ETL Started")
    print("=" * 60)

    record = event["Records"][0]

    bucket_name = record["s3"]["bucket"]["name"]
    object_key = record["s3"]["object"]["key"]

    extension = object_key.rsplit(".", 1)[1].lower()

    print(f"Bucket : {bucket_name}")
    print(f"Key    : {object_key}")
    print(f"Type   : {extension}")

    if extension == "json":
        records = load_json_from_s3(bucket_name, object_key)

    elif extension == "csv":
        records = load_csv_from_s3(bucket_name, object_key)

    elif extension == "parquet":
        records = load_parquet_from_s3(bucket_name, object_key)

    else:
        raise Exception(f"Unsupported file type: {extension}")

    print(f"Records Loaded : {len(records)}")

    processed_at = generate_timestamp()

    table = boto3.resource("dynamodb").Table(
        f"{extension}-table"
    )

    partition_key = "location_key" if extension == "parquet" else "country"

    inserted = 0
    rejected = 0

    with table.batch_writer(
        overwrite_by_pkeys=[partition_key]
    ) as batch:

        for record in records:

            if not validate_record(record, extension):
                rejected += 1
                continue

            item = build_item(
                record,
                processed_at,
                extension
            )

            batch.put_item(Item=item)

            inserted += 1

    print(f"Inserted : {inserted}")
    print(f"Rejected : {rejected}")

    return {
        "statusCode": 200,
        "records_processed": len(records),
        "records_inserted": inserted,
        "records_rejected": rejected,
    }