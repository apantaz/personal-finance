from dataclasses import dataclass
from pathlib import Path

from ingestion.detect import detect_parser
from ingestion.repository import TransactionRepository


@dataclass(frozen=True)
class ImportResult:
    rows_read: int
    inserted: int
    duplicates: int


def ingest_file(path: Path, repository: TransactionRepository) -> ImportResult:
    parser = detect_parser(path)
    transactions = parser.parse(path)
    inserted = repository.insert(transactions)
    return ImportResult(
        rows_read=len(transactions),
        inserted=inserted,
        duplicates=len(transactions) - inserted,
    )
