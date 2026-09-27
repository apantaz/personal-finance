class IngestionError(Exception):
    """Base error for failures that should be reported to an importer."""


class UnknownBankFormatError(IngestionError):
    """Raised when no parser recognizes a CSV header."""


class BankSchemaNotConfiguredError(IngestionError):
    """Raised until a parser is implemented from a real, sanitized fixture."""


class InvalidBankFileError(IngestionError):
    """Raised when a recognized file contains invalid or unsupported data."""
