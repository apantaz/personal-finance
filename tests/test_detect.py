from pathlib import Path

import pytest

from ingestion.detect import detect_parser, read_header
from ingestion.errors import InvalidBankFileError, UnknownBankFormatError


def test_rejects_non_csv(tmp_path: Path) -> None:
    path = tmp_path / "transactions.txt"
    path.write_text("a,b\n1,2\n")
    with pytest.raises(InvalidBankFileError, match="only .csv"):
        read_header(path)


def test_unknown_schema_fails_instead_of_guessing(tmp_path: Path) -> None:
    path = tmp_path / "transactions.csv"
    path.write_text("date,amount\n2026-01-01,10.00\n")
    with pytest.raises(UnknownBankFormatError, match="not recognized"):
        detect_parser(path)
