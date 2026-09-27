# AGENTS.md

## Project: Personal Finance

This repository contains a local-first personal finance web application.

The application imports transaction CSV files exported from multiple banks, normalizes them into a common data model, calculates financial analytics, and presents the results through a localhost web application.

The primary purpose is to answer:

1. How much money do I currently have?
2. How much money did I spend this month?
3. Where did I spend it?
4. What is my normal monthly spending?
5. Which expenses are unusually high?
6. Which expenses are recurring?
7. Which expenses are one-offs?
8. Where could spending potentially be reduced?
9. How is my total financial position changing over time?

Historical data should initially support transactions from `2026-01-01` onward.

---

# 1. Core Engineering Principles

## Local First

Financial data is private and must remain local by default.

Do not introduce cloud infrastructure unless explicitly requested.

The application should run on a personal machine or mini-PC using Docker Compose.

Expected access:

`http://localhost:3000`

or through the mini-PC hostname on the local network.

## Keep the Architecture Simple

Do not introduce infrastructure that is unnecessary for a single-user personal application.

Avoid introducing:

- Kubernetes
- Airflow
- Kafka
- Snowflake
- Redis
- Celery
- Cloud databases
- Microservices
- Complex distributed systems

unless explicitly requested.

Prefer the simplest solution that satisfies the requirement.

---

# 2. Technology Stack

Use the following stack unless explicitly instructed otherwise.

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- Recharts

## Backend

- Python
- FastAPI
- Pydantic

## Data

- DuckDB
- dbt
- dbt-duckdb

## Infrastructure

- Docker
- Docker Compose

Do not replace major technologies without discussing the reason first.

---

# 3. High-Level Architecture

```text
Bank CSV Files
      │
      ▼
Bank-specific parsers
      │
      ▼
Canonical raw transactions
      │
      ▼
DuckDB
      │
      ▼
dbt transformations
      │
      ▼
Analytics marts
      │
      ▼
FastAPI
      │
      ▼
Next.js
      │
      ▼
Browser
```

AI functionality is an enrichment layer and must not become a dependency for core financial calculations.

---

# 4. Repository Structure

Prefer the following structure:

```text
personal-finance/
│
├── frontend/
├── backend/
├── ingestion/
│   ├── parsers/
│   │   ├── nbg.py
│   │   ├── alpha.py
│   │   └── eurobank.py
│   └── ingest.py
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   └── dbt_project.yml
├── data/
│   ├── inbox/
│   ├── processed/
│   └── database/
├── tests/
├── docker-compose.yml
├── README.md
└── AGENTS.md
```

The exact structure may evolve when there is a clear engineering reason.

Avoid unnecessary abstraction.

---

# 5. CSV Ingestion

Different banks export different CSV structures.

Initially support:

- National Bank of Greece
- Alpha Bank
- Eurobank

Each bank must have an independent parser.

Bank-specific logic must remain inside the parser layer.

Do not spread bank-specific column names or parsing logic throughout the application.

---

# 6. Canonical Transaction Model

All bank transactions must eventually map to a common representation.

Target fields:

```text
transaction_id
transaction_date
bank
account
description_raw
merchant
amount
currency
category
subcategory
spending_type
essentiality
exclude_from_baseline
source_file
ingested_at
```

Additional fields may be introduced when justified.

---

# 7. Transaction Identity and Idempotency

CSV ingestion must be idempotent.

Importing the same CSV multiple times must not create duplicate transactions.

Do not rely only on filenames for deduplication.

Generate a deterministic transaction identifier from stable transaction attributes when the bank does not provide a reliable unique transaction ID.

Possible inputs include:

```text
bank
account
transaction_date
description_raw
amount
bank_reference
```

Be careful: legitimate transactions may have identical dates, descriptions, and amounts.

Prefer bank-provided transaction/reference identifiers whenever available.

Never silently discard transactions because they merely look similar.

---

# 8. Money Representation

Financial values must never use binary floating-point arithmetic.

Use:

- Python `Decimal`
- DuckDB `DECIMAL`

where appropriate.

Currency must be represented explicitly.

Initial primary currency: `EUR`.

Do not assume that every future transaction will necessarily be EUR.

---

# 9. Transaction Semantics

A transaction can have multiple independent classifications.

## Category

Examples:

- Groceries
- Delivery
- Restaurants
- Coffee
- Shopping
- Electronics
- Transport
- Utilities
- Subscriptions
- Entertainment
- Healthcare
- Travel
- Income
- Transfer
- Other

## Spending Type

Supported initial values:

```text
RECURRING
VARIABLE
ONE_OFF
```

## Essentiality

Supported values:

```text
ESSENTIAL
DISCRETIONARY
```

These dimensions must remain separate.

---

# 10. One-Off Expenses

One-off purchases must remain part of actual spending.

For example, a €1,500 laptop must contribute to `actual_spending`, but may be excluded from `regular_spending` and historical spending baselines.

Use:

```text
spending_type = ONE_OFF
exclude_from_baseline = true
```

Do not delete or hide one-off expenses from financial totals.

---

# 11. Transfers

Transfers between accounts owned by the same person must not be treated as income or spending.

Internal transfer handling is therefore a core requirement.

The data model should eventually support matching both sides of an internal transfer.

---

# 12. Refunds and Reversals

Refunds must not automatically be treated as ordinary income.

Where possible, associate refunds with spending or represent them separately.

The system should distinguish between:

- salary/income
- refund
- transfer
- expense
- transaction reversal

Do not artificially inflate income because a merchant refunded a purchase.

---

# 13. Merchant Normalization

Raw bank descriptions are often inconsistent.

For example:

```text
WOLT*12345
WOLT ATHENS
WOLT.COM
```

should potentially normalize to `Wolt`.

Normalization priority:

```text
Existing confirmed mapping
        ↓
Deterministic rule
        ↓
AI suggestion
        ↓
Manual review
```

Do not call an LLM for merchants already covered by a deterministic mapping.

---

# 14. Human Corrections

User corrections are authoritative.

If the user changes merchant, category, subcategory, spending type, essentiality, or baseline inclusion, the system must preserve that correction.

Automated classification must not silently overwrite manually confirmed values.

Where appropriate, allow a correction to create a reusable rule for future transactions.

---

# 15. dbt Modeling

Follow a layered dbt architecture:

```text
sources
   ↓
staging
   ↓
intermediate
   ↓
marts
```

Suggested models:

```text
stg_transactions

int_transactions_enriched
int_internal_transfers
int_recurring_transactions

fct_transactions
fct_monthly_spending
fct_account_balances
fct_net_worth

dim_merchants
dim_categories
dim_accounts
```

Do not create layers simply to satisfy naming conventions.

Every intermediate model should have a clear transformation purpose.

---

# 16. Financial Calculations

Financial calculations must be deterministic.

Examples:

```text
total_income
total_expenses
net_savings
savings_rate
actual_spending
regular_spending
one_off_spending
average_monthly_spending
average_monthly_income
average_monthly_savings
spending_by_category
spending_by_merchant
recurring_monthly_cost
recurring_annual_cost
```

These calculations belong in SQL/dbt or deterministic application code.

They do not belong in an LLM prompt.

---

# 17. Spending Baseline

The application should calculate a historical baseline representing normal spending.

The exact algorithm can evolve.

Initial implementation should favor a simple, explainable method, such as average eligible monthly spending over previous completed months.

Transactions where `exclude_from_baseline = true` must not influence the baseline.

Do not include the current incomplete month in historical averages unless explicitly intended.

Later versions may use more robust statistics such as medians or rolling windows.

Do not introduce complex statistical models before they are needed.

---

# 18. Spending Anomalies

Anomaly detection must initially be deterministic and explainable.

The application should detect unusual spending at least by:

- category
- merchant

An LLM may explain an anomaly.

An LLM must not invent or calculate the underlying anomaly.

---

# 19. Recurring Payments

Recurring payment detection should primarily use transaction history.

Signals may include:

- normalized merchant
- similar amount
- approximately regular interval
- repeated monthly occurrence

Do not require exact amounts.

Utility bills can recur monthly while changing in value.

The system should distinguish between fixed recurring and variable recurring payments when useful.

---

# 20. AI / Agent Architecture

AI is optional enrichment.

The application must remain functional when AI is disabled or unavailable.

Agents should operate on structured application data rather than directly parsing arbitrary financial CSV files whenever possible.

---

# 21. Classification Agent

Purpose:

- Suggest merchant normalization
- Suggest category
- Suggest subcategory
- Suggest spending type
- Suggest essentiality

Expected structured output:

```json
{
  "merchant": "Spotify",
  "category": "Entertainment",
  "subcategory": "Music",
  "spending_type": "RECURRING",
  "essentiality": "DISCRETIONARY",
  "confidence": 0.97
}
```

Do not allow free-form LLM output to directly mutate transaction data.

Validate agent output using a schema.

Low-confidence classifications should go to manual review.

---

# 22. Financial Insight Agent

The Financial Insight Agent should consume precomputed analytics.

Example inputs:

```text
monthly_summary
category_spending
merchant_spending
historical_baselines
spending_anomalies
recurring_payments
one_off_transactions
```

Every number presented by the agent must originate from application data.

The agent must not independently calculate or fabricate financial values.

---

# 23. Potential Savings

Potential savings should be presented as observations rather than financial advice.

The application may highlight differences between current spending and historical baselines.

It should not assume that the user should eliminate a category.

---

# 24. Backend

FastAPI should expose clear APIs around domain concepts.

Possible endpoints:

```text
POST /imports
GET  /transactions
PATCH /transactions/{id}

GET /overview
GET /spending
GET /spending/categories
GET /spending/merchants

GET /net-worth
GET /recurring
GET /insights

GET /review
POST /review/{id}
```

Exact endpoint design may evolve.

Keep business logic outside route handlers.

Routes should remain thin.

---

# 25. Frontend

The initial application should contain:

```text
Overview
Transactions
Spending
Net Worth
Insights
```

The interface should prioritize clarity over information density.

This is a personal finance application, not a generic BI dashboard.

---

# 26. Overview

The Overview should immediately answer:

- How much money do I have?
- How much came in this month?
- How much went out?
- How much did I save?
- How much of my spending was regular?
- How much was one-off?
- Am I spending more than usual?

Do not overload the landing page with secondary metrics.

---

# 27. Transactions

The transaction view should support:

- Search
- Date filtering
- Bank filtering
- Account filtering
- Merchant filtering
- Category filtering
- Transaction editing
- One-off marking
- Baseline inclusion/exclusion

Manual edits must be persisted.

---

# 28. Spending

The Spending view should support analysis by:

- Month
- Category
- Merchant
- Spending Type
- Essentiality

Users should be able to drill from:

```text
Category
   ↓
Merchant
   ↓
Transaction
```

---

# 29. Review Inbox

Transactions requiring manual attention should appear in a dedicated queue.

Examples:

- Unknown merchant
- Unknown category
- Low AI confidence
- Possible internal transfer
- Possible recurring payment
- Potential duplicate

The review workflow should be fast.

A corrected transaction should not repeatedly return to the review queue unless new evidence requires it.

---

# 30. Net Worth

The application should eventually track total financial position over time.

Do not derive historical bank balances purely from incomplete transaction data unless the necessary opening balances are known.

Prefer explicit account balance snapshots when required.

Future support may include:

- Cash
- Bank accounts
- Investments
- ETFs
- Other assets
- Liabilities

Keep transaction analytics and net-worth accounting conceptually separate.

---

# 31. Security and Privacy

Financial data is sensitive.

Never:

- Commit real CSV exports
- Commit the DuckDB database containing real financial data
- Commit API keys
- Commit `.env`
- Log full sensitive transaction data unnecessarily
- Send transaction history to external services without explicit configuration

Ensure `.gitignore` protects at least:

```text
.env
data/inbox/*
data/processed/*
data/database/*
*.duckdb
*.db
```

Keep placeholder files such as `.gitkeep` where required.

---

# 32. Testing

Important financial logic requires tests.

At minimum test:

- Bank CSV parsing
- Date parsing
- Amount parsing
- Debit/credit sign normalization
- Duplicate prevention
- Merchant normalization
- Manual override precedence
- Internal transfers
- Refund handling
- One-off exclusion
- Monthly aggregation
- Baseline calculations

For every bank parser, maintain sanitized fixtures that contain no real personal financial information.

---

# 33. Data Quality

Prefer explicit failures over silently corrupting financial data.

Validate:

- Required columns
- Dates
- Amounts
- Currency
- Bank parser compatibility

If a bank changes its CSV format, ingestion should fail clearly rather than silently producing incorrect transactions.

---

# 34. Observability

Keep local observability simple.

Important operations should provide useful logs such as:

```text
Import started
Bank detected: Eurobank
Rows read: 124
Rows valid: 124
New transactions: 119
Duplicates: 5
Transactions requiring review: 7
Import completed
```

Never log secrets.

Avoid logging unnecessary full transaction descriptions.

---

# 35. Development Workflow for Coding Agents

When implementing a feature:

1. Understand the existing architecture before changing it.
2. Inspect relevant existing code and tests.
3. Make the smallest coherent change that solves the requirement.
4. Preserve existing behavior unless the task explicitly changes it.
5. Add or update tests for financial logic.
6. Run relevant tests.
7. Run formatting/linting when configured.
8. Explain any architectural decision that introduces meaningful complexity.

Do not perform unrelated refactors while implementing a focused feature.

---

# 36. Agent Guardrails

Coding agents working on this repository must not:

- Invent bank CSV schemas.
- Guess financial values.
- Generate fake mappings for real transactions without marking them as suggestions.
- Replace deterministic financial logic with LLM calls.
- Add external services without justification.
- Add infrastructure simply because it is common in production systems.
- Store secrets in source code.
- Commit personal financial data.
- Silently change financial semantics.
- Automatically overwrite user-confirmed classifications.
- Treat internal transfers as spending/income.
- Treat refunds as normal income without explicit logic.

When information is missing, implement an explicit interface or TODO rather than inventing financial behavior.

---

# 37. Development Priorities

When trade-offs are necessary, prioritize in this order:

```text
1. Financial correctness
2. Data integrity
3. Privacy
4. Explainability
5. Simplicity
6. User experience
7. Performance
8. Architectural sophistication
```

The expected data volume is small.

Optimize for correctness and maintainability rather than scale.

---

# 38. Implementation Roadmap

## Phase 1 — Foundation

Implement:

- Project structure
- DuckDB
- Canonical schema
- Bank parsers
- CSV validation
- Idempotent ingestion
- Sanitized parser tests

Do not implement AI yet.

## Phase 2 — Transaction Intelligence

Implement:

- Merchant normalization
- Categories
- Spending types
- Essentiality
- One-off handling
- Manual overrides
- Classification mappings
- Transfer handling
- Refund handling

## Phase 3 — Analytics

Introduce dbt.

Implement:

- Staging models
- Intermediate models
- Transaction fact
- Monthly spending
- Category analytics
- Merchant analytics
- Income
- Expenses
- Savings
- Savings rate
- Regular spending
- One-off spending

## Phase 4 — Web Application

Implement FastAPI and Next.js.

Build:

- Overview
- Transactions
- Spending
- CSV Import
- Review Inbox

Focus on functionality before visual polish.

## Phase 5 — Spending Intelligence

Implement:

- Historical baselines
- Category anomalies
- Merchant anomalies
- Recurring payment detection
- Annualized recurring costs
- Potential savings calculations

## Phase 6 — AI Classification

Add AI only after deterministic classification infrastructure exists.

Implement:

- Structured classification
- Confidence scores
- Review workflow
- Mapping creation from confirmed corrections

AI must be optional.

## Phase 7 — AI Insights

Implement the Financial Insight Agent.

The agent should explain already-computed analytics and surface relevant observations.

Do not give the agent responsibility for financial calculations.

## Phase 8 — Net Worth

Implement:

- Account balance snapshots
- Total money
- Historical total money
- Net-worth trend

Later extend to investments if desired.

---

# 39. Definition of Done

A feature is not complete simply because the UI works.

For financial functionality, Definition of Done includes:

```text
Implementation
+
Validation
+
Tests
+
Correct financial semantics
+
No accidental exposure of personal data
```

---

# 40. Product Goal

Do not lose sight of the purpose of the project.

The application exists to make the following obvious:

> How much money do I have?

> Where is my money going?

> What does a normal month cost me?

> What changed this month?

> Which expenses are unusually high?

> Which expenses repeat every month?

> Which large expenses were one-offs?

> How much am I actually saving?

> Where could I reduce spending if I choose to?

Prefer features that improve these answers over features that merely make the architecture more sophisticated.
