import hashlib
import json
from datetime import date
from decimal import Decimal


def deterministic_transaction_id(
    *,
    bank: str,
    account: str,
    transaction_date: date,
    description_raw: str,
    amount: Decimal,
    currency: str,
    bank_reference: str | None = None,
    occurrence: int | None = None,
) -> str:
    """Build a stable ID, preferring a bank's own transaction reference.

    ``occurrence`` must distinguish genuinely separate rows that otherwise have
    identical fallback attributes. Parsers should derive it deterministically
    from a bank export, never silently discard the duplicate-looking rows.
    """
    if not bank_reference and occurrence is None:
        raise ValueError("occurrence is required when no bank reference is available")

    identity = {
        "bank": bank.strip().casefold(),
        "account": account.strip().casefold(),
        "bank_reference": bank_reference.strip() if bank_reference else None,
    }
    if not bank_reference:
        identity.update(
            {
                "transaction_date": transaction_date.isoformat(),
                "description_raw": " ".join(description_raw.split()).casefold(),
                "amount": format(amount, "f"),
                "currency": currency.upper(),
                "occurrence": occurrence,
            }
        )
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
