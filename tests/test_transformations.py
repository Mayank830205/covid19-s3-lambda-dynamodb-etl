"""Unit tests for transformation functions."""

import sys
from decimal import Decimal
from pathlib import Path

LAMBDA_DIR = Path(__file__).resolve().parents[1] / "lambda"
sys.path.insert(0, str(LAMBDA_DIR))

from transformations import (
    build_item,
    get_risk_level,
    validate_record,
)


def test_get_risk_level():
    assert get_risk_level(5000) == "LOW"
    assert get_risk_level(10000) == "MEDIUM"
    assert get

