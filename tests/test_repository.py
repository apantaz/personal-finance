from datetime import date
from decimal import Decimal
from pathlib import Path

from ingestion.models import CanonicalTransaction
from ingestion.repository import TransactionRepository


def test_insert_is_idempotent(tmp_path: Path) -> None:
    repository = TransactionRepository(tmp_path / "finance.duckdb")
    item = CanonicalTransaction(
        transaction_id="stable-id",
        transaction_date=date(2026, 1, 1),
        bank="Example Bank",
        account="checking",
        description_raw="Example",
        amount=Decimal("-10.25"),
        currency="EUR",
        source_file="sanitized.csv",
        source_row_number=2,
    )
    assert repository.insert([item]) == 1
    assert repository.insert([item]) == 0
