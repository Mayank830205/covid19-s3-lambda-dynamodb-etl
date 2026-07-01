"""Shared utility functions for Lambda ETL jobs."""

import csv
import io
import json
from datetime import datetime, timezone
from decimal import Decimal

import boto3
import pandas as pd


def load_json_from_s3(bucket_name, object_key):
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket_name, Key=object_key)

    return json.loads(
        response["Body"].read().decode("utf-8"),
        parse_float=Decimal,
        parse_int=Decimal,
    )


def load_csv_from_s3(bucket_name, object_key):
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    data = response["Body"].read().decode("utf-8")

    return list(csv.DictReader(io.StringIO(data)))


def load_parquet_from_s3(bucket_name, object_key):
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    data = io.BytesIO(response["Body"].read())

    dataframe = pd.read_parquet(data)
    dataframe = dataframe.astype(object).where(pd.notnull(dataframe), None)

    return dataframe.to_dict(orient="records")


def generate_timestamp():
    return datetime.now(timezone.utc).isoformat()
