# dq_check_advanced.py
"""
Advanced Snowflake DQ Runner:
- YAML-driven rules + schema drift checks
- Historical baseline deltas (persisted in SNOWFLAKE_DATABASE.SCHEMA_DQ.METRICS)
- Partition coverage checks
- Quarantine failed records into error tables (optional)
- Slack webhook summary (optional)
- JUnit XML for CI

Env:
  SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ROLE,
  SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA
  DQ_DATABASE (optional, default = SNOWFLAKE_DATABASE)
  DQ_SCHEMA (optional, default = "DQ")
  SLACK_WEBHOOK_URL (optional)
"""

import os, sys, yaml, json, datetime as dt, xml.etree.ElementTree as ET
import snowflake.connector
from typing import Dict, Any, List, Tuple

def connect_sf():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE", "SYSADMIN"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "ANALYTICS"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
    )

def fetch(cur, sql, params=None):
    cur.execute(sql, params or {})
    try:
        return cur.fetchall()
    except Exception:
        return []

def execq(cur, sql):
    cur.execute(sql)

def idq(name: str) -> str:
    # conservative quoting
    return f'"{name}"'

def fq(db, sc, obj) -> str:
    return f'{idq(db)}.{idq(sc)}.{idq(obj)}'

def ensure_dq_schema(cur):
    dq_db = os.getenv("DQ_DATABASE") or os.getenv("SNOWFLAKE_DATABASE", "ANALYTICS")
    dq_sc = os.getenv("DQ_SCHEMA", "DQ")
    execq(cur, f'CREATE SCHEMA IF NOT EXISTS {fq(dq_db, dq_sc, "")[:-1]}')
    execq(cur, f"""
    CREATE TABLE IF NOT EXISTS {fq(dq_db, dq_sc, "METRICS")} (
      METRIC_DATE DATE,
      DB STRING, SCHEMA STRING, TABLE STRING, METRIC STRING, VALUE NUMBER,
      PRIMARY KEY (METRIC_DATE, DB, SCHEMA, TABLE, METRIC)
    )
    """)
    return dq_db, dq_sc

# --- Checks ---
def row_count(cur, table_fq) -> int:
    (cnt,) = fetch(cur, f"SELECT COUNT(*) FROM {table_fq}")[0]
    return int(cnt)

def check_row_count_min(cur, table_fq, min_value):
    cnt = row_count(cur, table_fq)
    ok = cnt >= int(min_value)
    return ok, f"row_count_min >= {min_value} (actual={cnt})", {"row_count": cnt}

def check_not_null(cur, table_fq, col):
    (n,) = fetch(cur, f"SELECT COUNT(*) FROM {table_fq} WHERE {idq(col)} IS NULL")[0]
    ok = n == 0
    return ok, f"not_null {col} (nulls={n})", {"nulls": int(n)}

def check_unique(cur, table_fq, col):
    (d,) = fetch(cur, f"""
    SELECT COUNT(*) FROM (
      SELECT {idq(col)}, COUNT(*) c
      FROM {table_fq} GROUP BY {idq(col)} HAVING COUNT(*) > 1
    )""")[0]
    ok = d == 0
    return ok, f"unique {col} (duplicates={d})", {"duplicates": int(d)}

def check_accepted_values(cur, table_fq, col, values, quarantine=False, q_schema=None):
    placeholders = ", ".join([f"'{v}'" for v in values])
    (bad,) = fetch(cur, f"""
      SELECT COUNT(*) FROM {table_fq}
      WHERE {idq(col)} IS NULL OR {idq(col)} NOT IN ({placeholders})
    """)[0]
    ok = bad == 0
    msg = f"accepted_values {col} in {values} (violations={bad})"
    if not ok and quarantine and q_schema:
        # Create error table with offending rows
        execq(cur, f"""
          CREATE TABLE IF NOT EXISTS {q_schema} AS
          SELECT * FROM {table_fq} WHERE 1=0
        """)
        execq(cur, f"""
          INSERT INTO {q_schema}
          SELECT * FROM {table_fq}
          WHERE {idq(col)} IS NULL OR {idq(col)} NOT IN ({placeholders})
        """)
        msg += f" [quarantined->{q_schema}]"
    return ok, msg, {"violations": int(bad)}

def check_foreign_key(cur, table_fq, col, ref_table_fq, ref_col, quarantine=False, q_schema=None):
    (orphans,) = fetch(cur, f"""
    SELECT COUNT(*) FROM {table_fq} t
    LEFT JOIN {ref_table_fq} r
      ON t.{idq(col)} = r.{idq(ref_col)}
    WHERE r.{idq(ref_col)} IS NULL AND t.{idq(col)} IS NOT NULL
    """)[0]
    ok = orphans == 0
    msg = f"foreign_key {col}->{ref_table_fq}.{ref_col} (orphans={orphans})"
    if not ok and quarantine and q_schema:
        execq(cur, f"CREATE TABLE IF NOT EXISTS {q_schema} AS SELECT * FROM {table_fq} WHERE 1=0")
        execq(cur, f"""
        INSERT INTO {q_schema}
        SELECT t.* FROM {table_fq} t
        LEFT JOIN {ref_table_fq} r
          ON t.{idq(col)} = r.{idq(ref_col)}
        WHERE r.{idq(ref_col)} IS NULL AND t.{idq(col)} IS NOT NULL
        """)
        msg += f" [quarantined->{q_schema}]"
    return ok, msg, {"orphans": int(orphans)}

def check_freshness(cur, table_fq, ts_col, max_age_hours):
    (mx,) = fetch(cur, f"SELECT MAX({idq(ts_col)}) FROM {table_fq}")[0]
    if mx is None:
        return False, f"freshness {ts_col} (no rows)", {"age_hours": None}
    age = (dt.datetime.utcnow() - mx.replace(tzinfo=None)).total_seconds()/3600
    ok = age <= float(max_age_hours)
    return ok, f"freshness {ts_col} <= {max_age_hours}h (age={age:.2f}h)", {"age_hours": round(age,2)}

def check_partition_coverage(cur, table_fq, date_col, days):
    (miss,) = fetch(cur, f"""
    WITH d AS (
      SELECT DATEADD('day', -seq4(), CURRENT_DATE()) AS d
      FROM TABLE(GENERATOR(ROWCOUNT => {days}))
    )
    SELECT COUNT(*) FROM d
    WHERE d NOT IN (SELECT DISTINCT CAST({idq(date_col)} AS DATE) FROM {table_fq})
    """)[0]
    ok = miss == 0
    return ok, f"partition_coverage last {days} days (missing={miss})", {"missing_days": int(miss)}

# --- Schema drift ---
def check_schema(cur, table_db, table_sc, table_name, expected_cols: List[Dict[str, str]]):
    rows = fetch(cur, f"""
    SELECT COLUMN_NAME, DATA_TYPE
    FROM {idq(table_db)}.INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
    """, (table_sc.upper(), table_name.upper()))
    actual = {r[0].upper(): r[1].upper() for r in rows}
    expected = {c['name'].upper(): c['type'].upper() for c in expected_cols}
    missing = [c for c in expected if c not in actual]
    extra = [c for c in actual if c not in expected]
    type_mismatch = [c for c in expected if c in actual and expected[c] != actual[c]]
    ok = not missing and not extra and not type_mismatch
    msg = f"schema_drift (missing={missing}, extra={extra}, type_mismatch={[(c,expected[c],actual[c]) for c in type_mismatch]})"
    return ok, msg, {"missing": missing, "extra": extra, "type_mismatch": type_mismatch}

# --- Baseline metrics ---
def upsert_metric(cur, dq_db, dq_sc, db, sc, tbl, metric, value):
    execq(cur, f"""
    MERGE INTO {fq(dq_db, dq_sc, "METRICS")} t
    USING (SELECT CURRENT_DATE::DATE AS d, %s AS db, %s AS sc, %s AS tbl, %s AS m, %s AS v) s
      ON t.METRIC_DATE = s.d AND t.DB = s.db AND t.SCHEMA = s.sc AND t.TABLE = s.tbl AND t.METRIC = s.m
    WHEN MATCHED THEN UPDATE SET VALUE = s.v
    WHEN NOT MATCHED THEN INSERT (METRIC_DATE, DB, SCHEMA, TABLE, METRIC, VALUE)
      VALUES (s.d, s.db, s.sc, s.tbl, s.m, s.v)
    """)
def baseline_compare(cur, dq_db, dq_sc, db, sc, tbl, metric, current_value, tolerance_pct=50):
    # compare to trailing 7 days median
    rows = fetch(cur, f"""
      WITH w AS (
        SELECT VALUE FROM {fq(dq_db, dq_sc, "METRICS")}
        WHERE DB=%s AND SCHEMA=%s AND TABLE=%s AND METRIC=%s
          AND METRIC_DATE >= DATEADD('day', -7, CURRENT_DATE())
      )
      SELECT MEDIAN(VALUE) FROM w
    """, (db, sc, tbl, metric))
    med = rows[0][0] if rows and rows[0][0] is not None else None
    if med is None:
        return True, f"baseline {metric}: bootstrap"
    delta = (current_value - med) / med * 100 if med else 0
    ok = abs(delta) <= tolerance_pct
    return ok, f"baseline {metric}: current={current_value}, median_7d={med}, delta={delta:.1f}% (tol={tolerance_pct}%)"

# --- Slack + JUnit ---
def maybe_slack(summary_lines: List[str]):
    url = os.getenv("SLACK_WEBHOOK_URL")
    if not url: return
    import urllib.request, json
    data = {"text": "DQ Summary\n" + "\n".join(summary_lines[:40])}
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type":"application/json"})
        urllib.request.urlopen(req, timeout=10).read()
    except Exception:
        pass

def write_junit(results: List[Tuple[str,str,bool,str]], path="dq_results_junit.xml"):
    # results: (table, test_name, ok, message)
    testsuite = ET.Element("testsuite", name="dq", tests=str(len(results)), failures=str(sum(0 if r[2] else 1 for r in results)))
    for tbl, name, ok, msg in results:
        tc = ET.SubElement(testsuite, "testcase", classname=tbl, name=name)
        if not ok:
            fail = ET.SubElement(tc, "failure", message="failed")
            fail.text = msg
    ET.ElementTree(testsuite).write(path, encoding="utf-8", xml_declaration=True)

def main(cfg_path="checks.yml"):
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)

    failures, summary, junit = [], [], []
    dq_db = os.getenv("DQ_DATABASE") or os.getenv("SNOWFLAKE_DATABASE", "ANALYTICS")
    dq_sc = os.getenv("DQ_SCHEMA", "DQ")

    with connect_sf() as conn, conn.cursor() as cur:
        dq_db, dq_sc = ensure_dq_schema(cur)

        for t in cfg.get("tables", []):
            db = t.get("database") or os.getenv("SNOWFLAKE_DATABASE", "ANALYTICS")
            sc = t.get("schema") or os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
            name = t["name"]
            table_fq = fq(db, sc, name)
            summary.append(f"== {table_fq} ==")

            # optional schema drift section
            if "expect_schema" in t:
                ok, msg, _ = check_schema(cur, db, sc, name, t["expect_schema"])
                summary.append(("PASS " if ok else "FAIL ") + msg)
                junit.append((table_fq, "schema_drift", ok, msg))
                if not ok: failures.append((table_fq, msg))

            # run checks
            quarantine = t.get("quarantine", False)
            q_target = None
            if quarantine:
                q_target = fq(db, sc, f"{name}_ERRORS")

            for c in t.get("checks", []):
                ctype = c["type"]
                if ctype == "row_count_min":
                    ok, msg, meta = check_row_count_min(cur, table_fq, c["value"])
                    upsert_metric(cur, dq_db, dq_sc, db, sc, name, "row_count", meta["row_count"])
                    # baseline compare (optional tolerance%)
                    tol = c.get("tolerance_pct", 50)
                    bok, bmsg = baseline_compare(cur, dq_db, dq_sc, db, sc, name, "row_count", meta["row_count"], tol)
                    summary.append(("PASS " if ok else "FAIL ") + msg)
                    junit.append((table_fq, ctype, ok, msg))
                    summary.append(("PASS " if bok else "FAIL ") + bmsg)
                    junit.append((table_fq, "baseline_row_count", bok, bmsg))
                    if not ok: failures.append((table_fq, msg))
                    if not bok: failures.append((table_fq, bmsg))
                elif ctype == "not_null":
                    ok, msg, _ = check_not_null(cur, table_fq, c["column"])
                    summary.append(("PASS " if ok else "FAIL ") + msg)
                    junit.append((table_fq, f"not_null_{c['column']}", ok, msg))
                    if not ok: failures.append((table_fq, msg))
                elif ctype == "unique":
                    ok, msg, _ = check_unique(cur, table_fq, c["column"])
                    summary.append(("PASS " if ok else "FAIL ") + msg)
                    junit.append((table_fq, f"unique_{c['column']}", ok, msg))
                    if not ok: failures.append((table_fq, msg))
                elif ctype == "accepted_values":
                    ok, msg, _ = check_accepted_values(cur, table_fq, c["column"], c["values"], quarantine, q_target)
                    summary.append(("PASS " if ok else "FAIL ") + msg)
                    junit.append((table_fq, f"accepted_values_{c['column']}", ok, msg))
                    if not ok: failures.append((table_fq, msg))
                elif ctype == "foreign_key":
                    ref = c["ref_table"]  # fully-qualified 'DB.SCHEMA.TABLE'
                    ref_col = c.get("ref_column", c["column"])
                    ok, msg, _ = check_foreign_key(cur, table_fq, c["column"], ref, ref_col, quarantine, q_target)
                    summary.append(("PASS " if ok else "FAIL ") + msg)
                    junit.append((table_fq, f"foreign_key_{c['column']}", ok, msg))
                    if not ok: failures.append((table_fq, msg))
                elif ctype == "freshness":
                    ok, msg, _ = check_freshness(cur, table_fq, c["column"], c["max_age_hours"])
                    summary.append(("PASS " if ok else "FAIL ") + msg)
                    junit.append((table_fq, f"freshness_{c['column']}", ok, msg))
                    if not ok: failures.append((table_fq, msg))
                elif ctype == "partition_coverage":
                    ok, msg, _ = check_partition_coverage(cur, table_fq, c["date_column"], c["days"])
                    summary.append(("PASS " if ok else "FAIL ") + msg)
                    junit.append((table_fq, "partition_coverage", ok, msg))
                    if not ok: failures.append((table_fq, msg))
                else:
                    msg = f"Unknown check type: {ctype}"
                    summary.append("FAIL " + msg)
                    junit.append((table_fq, ctype, False, msg))
                    failures.append((table_fq, msg))

        write_junit(junit)
        conn.commit()

    # Slack summary if configured
    maybe_slack(summary)

    print("\n".join(summary))
    if failures:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    cfg = sys.argv[1] if len(sys.argv) > 1 else "checks.yml"
    main(cfg)
    
    
    
    
    
    
    
# Example YAML configuration file: checks.yml

# tables:
#   - database: ANALYTICS
#     schema: V2_DWH_SALES
#     name: FACT_CLAIMS
#     quarantine: true
#     expect_schema:
#       - { name: CLAIM_ID,        type: NUMBER }
#       - { name: MEMBER_ID,       type: NUMBER }
#       - { name: CLAIM_STATUS,    type: TEXT }
#       - { name: LOAD_TS,         type: TIMESTAMP_NTZ }
#     checks:
#       - type: row_count_min
#         value: 1000
#         tolerance_pct: 40
#       - type: not_null
#         column: CLAIM_ID
#       - type: unique
#         column: CLAIM_ID
#       - type: accepted_values
#         column: CLAIM_STATUS
#         values: ["PAID","DENIED","PENDED"]
#       - type: foreign_key
#         column: MEMBER_ID
#         ref_table: ANALYTICS.V2_DWH_CUSTOMER.DIM_MEMBER
#         ref_column: MEMBER_ID
#       - type: freshness
#         column: LOAD_TS
#         max_age_hours: 24
#       - type: partition_coverage
#         date_column: LOAD_TS
#         days: 7

