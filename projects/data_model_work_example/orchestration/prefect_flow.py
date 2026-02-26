
# orchestration/prefect_flow.py
import os
import argparse
import time
from prefect import flow, task, get_run_logger
import pandas as pd
import sqlalchemy as sa

SNOWFLAKE_URL = os.getenv("SNOWFLAKE_URL")  # optional if using sqlalchemy snowflake dialect
ACCOUNT  = os.getenv("SNOWFLAKE_ACCOUNT")
USER     = os.getenv("SNOWFLAKE_USER")
PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
ROLE     = os.getenv("SNOWFLAKE_ROLE", "SYSADMIN")
WAREHOUSE= os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
DATABASE = os.getenv("SNOWFLAKE_DATABASE", "ANALYTICS")
SCHEMA_STAGE = os.getenv("SNOWFLAKE_SCHEMA_STAGE", "V2_DWH_TEMP")
SCHEMA_SALES = os.getenv("SNOWFLAKE_SCHEMA_SALES", "V2_DWH_SALES")
SCHEMA_DIM   = os.getenv("SNOWFLAKE_SCHEMA_DIM", "V2_DWH_CUSTOMER")
RAW_SCHEMA   = os.getenv("SNOWFLAKE_SCHEMA_RAW", "V2_INT_CLAIMS")
FIN_SCHEMA   = os.getenv("SNOWFLAKE_SCHEMA_FIN", "V2_DWH_FINANCE")

def render_sql(path):
    with open(path, "r") as f:
        sql = f.read()
    # Simple token replacement
    sql = (sql
        .replace("{stage_schema}", SCHEMA_STAGE)
        .replace("{sales_schema}", SCHEMA_SALES)
        .replace("{dim_schema}", SCHEMA_DIM)
        .replace("{raw_schema}", RAW_SCHEMA)
        .replace("{finance_schema}", FIN_SCHEMA)
    )
    return sql

def engine():
    # Using Snowflake SQLAlchemy URL
    url = sa.engine.URL.create(
        "snowflake",
        username=USER,
        password=PASSWORD,
        host=f"{ACCOUNT}.snowflakecomputing.com",
        query={
            "warehouse": WAREHOUSE,
            "database": DATABASE,
            "role": ROLE,
        }
    )
    return sa.create_engine(url)

@task(retries=2, retry_delay_seconds=5)
def run_sql(path):
    logger = get_run_logger()
    sql = render_sql(path)
    logger.info(f"Executing SQL: {path}")
    with engine().connect() as conn:
        for stmt in [s for s in sql.split(';') if s.strip()]:
            conn.execute(sa.text(stmt))
    logger.info(f"Completed: {path}")

@task
def dq_rowcount_check(table_fqn: str, min_rows: int = 1):
    logger = get_run_logger()
    with engine().connect() as conn:
        df = pd.read_sql(f"SELECT COUNT(*) AS cnt FROM {table_fqn}", conn)
    cnt = int(df.iloc[0,0])
    if cnt < min_rows:
        raise ValueError(f"DQ FAIL: {table_fqn} rowcount={cnt} < {min_rows}")
    logger.info(f"DQ PASS: {table_fqn} rowcount={cnt}")

@flow(name="claims_monthly_pipeline")
def claims_monthly_pipeline(run_all: bool = True):
    sql_path = os.path.join(os.path.dirname(__file__), "..", "sql", "01_etl_claims_medical_monthly_fact.sql")
    run_sql(sql_path)
    # Basic DQ: check aggregate table exists & non-empty
    dq_rowcount_check(f"{SCHEMA_SALES}.CLAIMS_MEDICAL_MONTHLY_FACT", min_rows=1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-all", action="store_true", help="Run full pipeline")
    args = parser.parse_args()
    claims_monthly_pipeline(run_all=args.run_all)
