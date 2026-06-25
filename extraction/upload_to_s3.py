"""Upload COVID-19 JSON data to Amazon S3."""

import os
from pathlib import Path

import boto3

LOCAL_FILE = Path("data/raw/covid_data.json")
OBJECT_KEY = "raw/covid_data.json"


def upload_file():

    bucket_name = os.environ["BUCKET_NAME"]

    print("========== Upload Started ==========")
    print(f"Bucket : {bucket_name}")
    print(f"File   : {LOCAL_FILE}")

    s3 = boto3.client("s3")

    s3.upload_file(
        str(LOCAL_FILE),
        bucket_name,
        OBJECT_KEY,
    )

    print(f"Successfully uploaded to s3://{bucket_name}/{OBJECT_KEY}")
    print("========== Upload Completed ==========")


if __name__ == "__main__":
    upload_file()

