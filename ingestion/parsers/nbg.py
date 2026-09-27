from collections.abc import Sequence
from pathlib import Path

from ingestion.errors import BankSchemaNotConfiguredError
from ingestion.models import CanonicalTransaction
from ingestion.parsers.base import BankParser, CsvHeader


class NbgParser(BankParser):
    bank_name = "National Bank of Greece"

    def recognizes(self, header: CsvHeader) -> bool:
        return False

    def parse(self, path: Path) -> Sequence[CanonicalTransaction]:
        raise BankSchemaNotConfiguredError(
            "NBG CSV schema is not configured; add a sanitized fixture before implementing it"
        )
