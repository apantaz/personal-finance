from datetime import date
from decimal import Decimal

import pytest

from ingestion.identity import deterministic_transaction_id

BASE = {
    "bank": "Example Bank",
    "account": "checking-1",
    "transaction_date": date(2026, 1, 2),
    "description_raw": "Example merchant",
    "amount": Decimal("-12.30"),
    "currency": "EUR",
}


def test_reference_identity_is_stable_and_ignores_mutable_description() -> None:
    first = deterministic_transaction_id(**BASE, bank_reference="ref-123")
    changed = {**BASE, "description_raw": "Changed wording", "amount": Decimal("-99.00")}
    second = deterministic_transaction_id(**changed, bank_reference="ref-123")
    assert first == second


def test_fallback_requires_occurrence_to_preserve_legitimate_identical_rows() -> None:
    with pytest.raises(ValueError, match="occurrence is required"):
        deterministic_transaction_id(**BASE)
    assert deterministic_transaction_id(**BASE, occurrence=1) != deterministic_transaction_id(
        **BASE, occurrence=2
    )
