from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ingestion.models import CanonicalTransaction, SpendingType


def transaction(**changes: object) -> CanonicalTransaction:
    values = {
        "transaction_id": "abc",
        "transaction_date": date(2026, 1, 1),
        "bank": "Example Bank",
        "account": "checking",
        "description_raw": "Laptop",
        "amount": Decimal("-1500.00"),
        "currency": "eur",
        "source_file": "sanitized.csv",
        "source_row_number": 2,
    }
    values.update(changes)
    return CanonicalTransaction.model_validate(values)


def test_currency_is_normalized_and_decimal_is_preserved() -> None:
    item = transaction()
    assert item.currency == "EUR"
    assert item.amount == Decimal("-1500.00")


def test_one_off_remains_a_transaction_and_can_be_excluded_from_baseline() -> None:
    item = transaction(spending_type=SpendingType.ONE_OFF, exclude_from_baseline=True)
    assert item.amount == Decimal("-1500.00")
    assert item.exclude_from_baseline is True


def test_invalid_currency_fails_explicitly() -> None:
    with pytest.raises(ValidationError):
        transaction(currency="€")
