from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SpendingType(StrEnum):
    RECURRING = "RECURRING"
    VARIABLE = "VARIABLE"
    ONE_OFF = "ONE_OFF"


class Essentiality(StrEnum):
    ESSENTIAL = "ESSENTIAL"
    DISCRETIONARY = "DISCRETIONARY"


class TransactionKind(StrEnum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"
    REFUND = "REFUND"
    REVERSAL = "REVERSAL"
    UNKNOWN = "UNKNOWN"


class CanonicalTransaction(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    transaction_id: str = Field(min_length=1)
    transaction_date: date
    bank: str = Field(min_length=1)
    account: str = Field(min_length=1)
    description_raw: str = Field(min_length=1)
    merchant: str | None = None
    amount: Decimal
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    category: str | None = None
    subcategory: str | None = None
    transaction_kind: TransactionKind = TransactionKind.UNKNOWN
    spending_type: SpendingType | None = None
    essentiality: Essentiality | None = None
    exclude_from_baseline: bool = False
    bank_reference: str | None = None
    source_file: str = Field(min_length=1)
    source_row_number: int = Field(ge=1)
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        normalized = value.upper()
        if not normalized.isalpha():
            raise ValueError("currency must be a three-letter alphabetic code")
        return normalized
