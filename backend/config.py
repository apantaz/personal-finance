import os
from pathlib import Path


def database_path() -> Path:
    return Path(os.getenv("FINANCE_DATABASE_PATH", "data/database/finance.duckdb"))
