import csv
from pathlib import Path

from ingestion.errors import InvalidBankFileError, UnknownBankFormatError
from ingestion.parsers import PARSERS
from ingestion.parsers.base import BankParser, CsvHeader


def read_header(path: Path) -> CsvHeader:
    if path.suffix.casefold() != ".csv":
        raise InvalidBankFileError("only .csv files are supported")
    try:
        sample = path.read_text(encoding="utf-8-sig")[:8192]
    except UnicodeDecodeError as error:
        raise InvalidBankFileError("CSV must use UTF-8 or UTF-8 with BOM") from error
    if not sample.strip():
        raise InvalidBankFileError("CSV is empty")
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        columns = next(csv.reader(sample.splitlines(), dialect=dialect))
    except (csv.Error, StopIteration) as error:
        raise InvalidBankFileError("CSV header could not be parsed") from error
    return CsvHeader(tuple(column.strip() for column in columns), dialect.delimiter, "utf-8-sig")


def detect_parser(path: Path) -> BankParser:
    header = read_header(path)
    matches = [parser for parser in PARSERS if parser.recognizes(header)]
    if len(matches) != 1:
        raise UnknownBankFormatError(
            "CSV format is not recognized; add an exact sanitized fixture and parser signature"
        )
    return matches[0]
