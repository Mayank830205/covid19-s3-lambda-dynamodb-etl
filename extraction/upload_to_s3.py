"""Upload extracted COVID-19 datasets to Amazon S3."""

import os
from pathlib import Path

import boto3

RAW_DIR = Path("data/raw")

FILES_TO_UPLOAD = [
    ("covid_data.json", "raw/json/covid_data.json"),
    ("vaccine_data.csv", "raw/csv/vaccine_data.csv"),
    ("hospital_data.parquet", "raw/parquet/hospital_data.parquet"),
]


def upload_files():
    """Upload all extracted datasets to S3."""

    bucket_name = os.environ["BUCKET_NAME"]

    print("=" * 50)
    print("Uploading files to Amazon S3")
    print("=" * 50)
    print(f"Bucket: {bucket_name}")

    s3 = boto3.client("s3")

    for local_name, s3_key in FILES_TO_UPLOAD:

        local_path = RAW_DIR / local_name

        if not local_path.exists():
            print(f"Skipping {local_name} (File not found)")
            continue

        print(f"\nUploading: {local_name}")

        s3.upload_file(
            str(local_path),
            bucket_name,
            s3_key,
        )

        print(f"Uploaded -> s3://{bucket_name}/{s3_key}")

    print("\nAll uploads completed successfully.")
    print("=" * 50)


if __name__ == "__main__":
    upload_files()