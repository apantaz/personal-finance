# Personal Finance

A local-first personal finance application for importing bank CSV exports into a canonical model, calculating deterministic analytics, and presenting them on localhost.

## Current status

This repository contains the Phase 1 foundation:

- a validated canonical transaction model using `Decimal`;
- deterministic transaction identity with bank-reference preference;
- a DuckDB repository with idempotent inserts;
- independent parser modules for NBG, Alpha Bank, and Eurobank;
- a thin FastAPI shell and a minimal Next.js shell;
- Docker Compose and initial tests.

The bank parser modules intentionally reject files for now. No source CSVs or documented headers were provided, and inventing a bank schema could silently corrupt financial data. See [Adding a bank format](#adding-a-bank-format).

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

- Web: http://localhost:3000
- API documentation: http://localhost:8000/docs
- API health: http://localhost:8000/health

## Develop and test the Python services

Python 3.12 is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
ruff check .
```

## Adding a bank format

For each bank, first add a sanitized CSV under `tests/fixtures/<bank>/`. Preserve the exact delimiter, encoding, header labels, date formatting, decimal separators, and debit/credit representation while replacing all personal values. Then implement that bank's parser and its detection signature. Tests must cover malformed data, sign handling, dates, currency, references, and duplicate rows.

Never commit actual exports or a populated database. The `data/` directories are ignored except for placeholders.

