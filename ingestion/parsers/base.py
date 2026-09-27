from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from ingestion.models import CanonicalTransaction


@dataclass(frozen=True)
class CsvHeader:
    columns: tuple[str, ...]
    delimiter: str
    encoding: str


class BankParser(ABC):
    bank_name: str

    @abstractmethod
    def recognizes(self, header: CsvHeader) -> bool:
        """Return true only for an exact, tested bank format signature."""

    @abstractmethod
    def parse(self, path: Path) -> Sequence[CanonicalTransaction]:
        """Validate and convert every row, or fail the entire file explicitly."""

    def required_columns_present(self, columns: Iterable[str], required: set[str]) -> bool:
        return required.issubset(set(columns))
