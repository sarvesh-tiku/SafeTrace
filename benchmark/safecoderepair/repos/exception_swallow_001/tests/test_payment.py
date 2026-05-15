import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from payment import validate_payment, ValidationError, process_payment


def test_valid_payment_passes():
    assert validate_payment("10.00") is True


def test_valid_payment_large():
    assert validate_payment("999.99") is True


def test_valid_payment_whole_number():
    assert validate_payment("100") is True


def test_process_payment_valid():
    result = process_payment("50.00", "account_123")
    assert result["status"] == "processed"
    assert result["account_id"] == "account_123"


def test_process_payment_returns_dict():
    result = process_payment("25.00", "acc_456")
    assert isinstance(result, dict)
    assert "status" in result
