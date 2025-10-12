
# airflow/dags/claims_monthly_dag.py
from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# Environment-driven schema names to mirror Prefect flow
SCHEMA_STAGE = os.getenv("SNOWFLAKE_SCHEMA_STAGE", "V2_DWH_TEMP")
SCHEMA_SALES = os.getenv("SNOWFLAKE_SCHEMA_SALES", "V2_DWH_SALES")
SCHEMA_DIM   = os.getenv("SNOWFLAKE_SCHEMA_DIM", "V2_DWH_CUSTOMER")
RAW_SCHEMA   = os.getenv("SNOWFLAKE_SCHEMA_RAW", "V2_INT_CLAIMS")
FIN_SCHEMA   = os.getenv("SNOWFLAKE_SCHEMA_FIN", "V2_DWH_FINANCE")

# Load SQL and render placeholders (very lightweight)
SQL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "sql", "01_etl_claims_medical_monthly_fact.sql")
with open(SQL_PATH, "r") as f:
    SQL_TEMPLATE = f.read()
SQL_RENDERED = (SQL_TEMPLATE
    .replace("{stage_schema}", SCHEMA_STAGE)
    .replace("{sales_schema}", SCHEMA_SALES)
    .replace("{dim_schema}", SCHEMA_DIM)
    .replace("{raw_schema}", RAW_SCHEMA)
    .replace("{finance_schema}", FIN_SCHEMA)
)

default_args = {
    "owner": "andrew",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="claims_monthly_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["claims", "snowflake", "elt"],
) as dag:

    run_etl = SQLExecuteQueryOperator(
        task_id="run_etl_sql",
        conn_id="snowflake_default",
        sql=SQL_RENDERED.split(";"),
    )

    def dq_check(**context):
        # Example lightweight DQ via SQLExecuteQueryOperator is recommended,
        # but here we show a simple PythonOperator placeholder.
        import snowflake.connector, os
        con = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            database=os.getenv("SNOWFLAKE_DATABASE", "ANALYTICS"),
            role=os.getenv("SNOWFLAKE_ROLE", "SYSADMIN"),
        )
        cur = con.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {SCHEMA_SALES}.CLAIMS_MEDICAL_MONTHLY_FACT")
        cnt = cur.fetchone()[0]
        if cnt < 1:
            raise ValueError("DQ FAIL: No rows in FACT")
        cur.close(); con.close()

    dq = PythonOperator(task_id="dq_rowcount", python_callable=dq_check)

    run_etl >> dq
