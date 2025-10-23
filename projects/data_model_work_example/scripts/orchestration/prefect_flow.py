# orchestration/prefect_flow.py
from prefect import flow, task
import subprocess

@task
def dq_task(cfg_path="checks.yml"):
    res = subprocess.run(["python","dq_check_advanced.py", cfg_path])
    if res.returncode != 0:
        raise RuntimeError("DQ failed")

@task
def perf_task():
    res = subprocess.run(["python","snowflake_perf_audit_advanced.py"])
    if res.returncode != 0:
        raise RuntimeError("Perf audit failed")

@flow(name="DQ-and-Perf")
def main(cfg_path="checks.yml"):
    try:
        dq_task(cfg_path)
    finally:
        perf_task()

if __name__ == "__main__":
    main()