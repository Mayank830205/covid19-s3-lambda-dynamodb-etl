"""Unit tests for Lambda handler."""

import sys
from pathlib import Path
from unittest.mock import patch

LAMBDA_DIR = Path(__file__).resolve().parents[1] / "lambda"
sys.path.insert(0, str(LAMBDA_DIR))

import lambda_function


class FakeBatchWriter:

    def __init__(self):
        self.items = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def put_item(self, Item):
        self.items.append(Item)


class FakeTable:

    def __init__(self):
        self.writer = FakeBatchWriter()

    def batch_writer(self, overwrite_by_pkeys=None):
        return self.writer


class FakeDynamoDB:

    def __init__(self):
        self.table = FakeTable()

    def Table(self, table_name):
        return self.table


fake_event = {
    "Records": [
        {
            "s3": {
                "bucket": {
                    "name": "test-bucket"
                },
                "object": {
                    "key": "raw/json/covid_data.json"
                }
            }
        }
    ]
}


fake_records = [
    {
        "country": "India",
        "continent": "Asia",
        "population": 1400000000,
        "cases": 100,
        "active": 10,
        "recovered": 80,
        "deaths": 10,
        "critical": 1,
        "casesPerOneMillion": 75,
    }
]


@patch("lambda_function.load_json_from_s3")
@patch("lambda_function.generate_timestamp")
@patch("lambda_function.boto3.resource")
def test_lambda_handler(
    mock_resource,
    mock_timestamp,
    mock_load_json,
):

    mock_load_json.return_value = fake_records
    mock_timestamp.return_value = "2026-06-30T12:00:00Z"

    mock_resource.return_value = FakeDynamoDB()

    response = lambda_function.lambda_handler(
        fake_event,
        None,
    )

    assert response["statusCode"] == 200
    assert response["records_processed"] == 1
    assert response["records_inserted"] == 1
    assert response["records_rejected"] == 0