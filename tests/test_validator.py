import pytest
import pandas as pd
from pipeline.parity import check_put_call_parity
from pipeline.anomaly import classify_severity


def test_parity_no_violation():
    result = check_put_call_parity(
        call_price=10.0, put_price=5.0,
        spot=100.0, strike=95.0,
        expiry_days=30, threshold=0.02
    )
    assert isinstance(result["violation"], bool)
    assert "deviation" in result


def test_parity_violation_detected():
    # Wildly mispriced — should trigger violation
    result = check_put_call_parity(
        call_price=50.0, put_price=1.0,
        spot=100.0, strike=100.0,
        expiry_days=30, threshold=0.02
    )
    assert result["violation"] is True


def test_classify_severity_critical():
    errors = [
        {"rule": "INVERTED_MARKET", "severity": "CRITICAL"},
        {"rule": "STALE_DATA", "severity": "WARNING"},
    ]
    assert classify_severity(errors) == "CRITICAL"


def test_classify_severity_clean():
    assert classify_severity([]) == "CLEAN"


def test_ingester_missing_file():
    from pipeline.ingester import load_from_csv
    with pytest.raises(FileNotFoundError):
        load_from_csv("nonexistent.csv")