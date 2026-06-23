"""Upload the locally extracted COVID-19 JSON file to Amazon S3."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

LOGGER = logging.getLogger(__name__)
DEFAULT_LOCAL_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "raw" / "covid_data.json"
)
DEFAULT_OBJECT_KEY = "raw/covid_data.json"


def upload_file(
    file_path: Path,
    bucket_name: str,
    object_key: str,
    s3_client: Any | None = None,
) -> str:
    """Upload a local file to S3 and return its ``s3://`` URI."""
    if not bucket_name.strip():
        raise ValueError("bucket_name must not be empty")
    if not object_key.strip():
        raise ValueError("object_key must not be empty")
    if not file_path.is_file():
        raise FileNotFoundError(f"Source file does not exist: {file_path}")

    client = s3_client or boto3.client("s3")
    try:
        LOGGER.info(
            "Uploading %s to s3://%s/%s",
            file_path,
            bucket_name,
            object_key,
        )
        client.upload_file(str(file_path), bucket_name, object_key)
    except (BotoCoreError, ClientError):
        LOGGER.exception("S3 upload failed")
        raise

    s3_uri = f"s3://{bucket_name}/{object_key}"
    LOGGER.info("Upload completed: %s", s3_uri)
    return s3_uri


def main() -> None:
    """Upload the configured local file to the configured S3 bucket."""
    bucket_name = os.getenv("BUCKET_NAME", "")
    if not bucket_name:
        raise RuntimeError("BUCKET_NAME environment variable is required")

    file_path = Path(os.getenv("LOCAL_DATA_PATH", str(DEFAULT_LOCAL_PATH)))
    object_key = os.getenv("OBJECT_KEY", DEFAULT_OBJECT_KEY)
    upload_file(file_path, bucket_name, object_key)


if __name__ == "__main__":
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    main()

