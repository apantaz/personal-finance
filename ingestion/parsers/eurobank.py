from collections.abc import Sequence
from pathlib import Path

from ingestion.errors import BankSchemaNotConfiguredError
from ingestion.models import CanonicalTransaction
from ingestion.parsers.base import BankParser, CsvHeader


class EurobankParser(BankParser):
    bank_name = "Eurobank"

    def recognizes(self, header: CsvHeader) -> bool:
        return False

    def parse(self, path: Path) -> Sequence[CanonicalTransaction]:
        raise BankSchemaNotConfiguredError(
            "Eurobank CSV schema is not configured; add a sanitized fixture before implementing it"
        )
