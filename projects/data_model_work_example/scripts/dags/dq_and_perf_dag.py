# dags/dq_and_perf_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os, subprocess, sys

default_args = {
    "owner": "data-eng",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def run_cmd(cmd: str):
    print(f"Running: {cmd}")
    proc = subprocess.run(cmd, shell=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")

with DAG(
    dag_id="dq_and_perf_audit",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 6 * * *",  # daily 6am
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    tags=["dq","audit","snowflake"],
) as dag:

    dq = PythonOperator(
        task_id="run_dq",
        python_callable=run_cmd,
        op_args=["python /opt/airflow/dags/code/dq_check_advanced.py /opt/airflow/dags/code/checks.yml"],
    )

    perf = PythonOperator(
        task_id="run_perf_audit",
        python_callable=run_cmd,
        op_args=["python /opt/airflow/dags/code/snowflake_perf_audit_advanced.py"],
        trigger_rule="all_done",  # run even if dq failed, so we still get a report
    )

    dq >> perf