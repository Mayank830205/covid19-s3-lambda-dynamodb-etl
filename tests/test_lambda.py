"""Unit tests for Lambda handler."""

import sys
from pathlib import Path

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
        self

