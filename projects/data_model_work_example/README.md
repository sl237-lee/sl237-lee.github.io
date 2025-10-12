
# BXTI-Style Claims Pipeline (Sample Work Files)

This package contains a realistic, production-leaning example of a healthcare claims data pipeline aligned to Blackstone BXTI's Data Engineer role. It is adapted from my real-world pharmaceutical analytics work (claims ETL), generalized and scrubbed of client identifiers.

## Contents
- `models/` — Data model schemas (DDL) for Snowflake/Delta.
- `sql/` — Modular SQL for normalize → assemble → enrich → aggregate → publish.
- `orchestration/` — Prefect v2 flow orchestrating the pipeline and DQ checks.
- `dq/` — Great Expectations-style data quality configurations.
- `automation/` — GitHub Actions CI job for linting and pipeline tests.
- `scripts/` — RBAC setup and cost monitoring queries.
- `local.env.example` — Example environment variables.

## How to run (conceptual)
1. Provision Snowflake (or Databricks/Delta) schemas noted in `models/`.
2. Set env vars from `local.env.example` and install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Register Prefect blocks or provide connection strings; then run:
   ```bash
   python orchestration/prefect_flow.py --run-all
   ```
4. CI will validate SQL format & run lightweight checks via GitHub Actions in `automation/`.

> Note: SQL is Snowflake/Delta-friendly. Replace placeholders (SCHEMA names, roles) per environment.
