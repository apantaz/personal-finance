from collections.abc import Sequence
from pathlib import Path

import duckdb

from ingestion.models import CanonicalTransaction

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS raw_transactions (
    transaction_id VARCHAR PRIMARY KEY,
    transaction_date DATE NOT NULL,
    bank VARCHAR NOT NULL,
    account VARCHAR NOT NULL,
    description_raw VARCHAR NOT NULL,
    merchant VARCHAR,
    amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    category VARCHAR,
    subcategory VARCHAR,
    transaction_kind VARCHAR NOT NULL,
    spending_type VARCHAR,
    essentiality VARCHAR,
    exclude_from_baseline BOOLEAN NOT NULL DEFAULT FALSE,
    bank_reference VARCHAR,
    source_file VARCHAR NOT NULL,
    source_row_number INTEGER NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL
)
"""

INSERT_SQL = """
INSERT INTO raw_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT (transaction_id) DO NOTHING
"""


class TransactionRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with duckdb.connect(str(self.path)) as connection:
            connection.execute(SCHEMA_SQL)

    def insert(self, transactions: Sequence[CanonicalTransaction]) -> int:
        self.initialize()
        rows = [
            (
                item.transaction_id,
                item.transaction_date,
                item.bank,
                item.account,
                item.description_raw,
                item.merchant,
                item.amount,
                item.currency,
                item.category,
                item.subcategory,
                item.transaction_kind.value,
                item.spending_type.value if item.spending_type else None,
                item.essentiality.value if item.essentiality else None,
                item.exclude_from_baseline,
                item.bank_reference,
                item.source_file,
                item.source_row_number,
                item.ingested_at,
            )
            for item in transactions
        ]
        if not rows:
            return 0
        with duckdb.connect(str(self.path)) as connection:
            before = connection.execute("SELECT count(*) FROM raw_transactions").fetchone()[0]
            connection.executemany(INSERT_SQL, rows)
            after = connection.execute("SELECT count(*) FROM raw_transactions").fetchone()[0]
        return after - before
