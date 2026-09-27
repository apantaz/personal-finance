from collections.abc import Sequence
from pathlib import Path

from ingestion.errors import BankSchemaNotConfiguredError
from ingestion.models import CanonicalTransaction
from ingestion.parsers.base import BankParser, CsvHeader


class AlphaBankParser(BankParser):
    bank_name = "Alpha Bank"

    def recognizes(self, header: CsvHeader) -> bool:
        return False

    def parse(self, path: Path) -> Sequence[CanonicalTransaction]:
        raise BankSchemaNotConfiguredError(
            "Alpha Bank CSV schema is not configured; "
            "add a sanitized fixture before implementing it"
        )
