# snowflake_perf_audit_advanced.py
"""
Snowflake performance audit:
- Heavy query scan detection (+ hints)
- Query signature clustering (repeat offenders)
- Warehouse load + metering analysis => sizing & autosuspend guidance
- Markdown report output + optional Slack summary
"""

import os, re, datetime as dt, snowflake.connector

BYTES = 1
MB = 1024*1024
GB = 1024*MB

def connect():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE","SYSADMIN"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE","COMPUTE_WH")
    )

def norm_signature(sql: str) -> str:
    s = re.sub(r"'[^']*'", "?", sql, flags=re.S)          # mask string literals
    s = re.sub(r"\b\d+\b", "?", s)                        # mask numeric literals
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s[:300]

def human_bytes(n):
    for unit in ["B","KB","MB","GB","TB","PB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}EB"

def fetch(cur, sql):
    cur.execute(sql)
    return cur.fetchall()

def audit():
    lookback_h = int(os.getenv("LOOKBACK_HOURS","24"))
    min_scan = int(os.getenv("MIN_BYTES_SCANNED", str(500*MB)))
    top_n    = int(os.getenv("TOP_N","30"))
    now = "CURRENT_TIMESTAMP()"

    with connect() as conn, conn.cursor() as cur:
        # Heavy queries
        qh = fetch(cur, f"""
        SELECT QUERY_ID, USER_NAME, WAREHOUSE_NAME, DATABASE_NAME, SCHEMA_NAME,
               EXECUTION_TIME, BYTES_SCANNED, ROWS_PRODUCED, START_TIME, QUERY_TEXT
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE START_TIME >= DATEADD('hour', -{lookback_h}, {now})
          AND EXECUTION_STATUS='SUCCESS'
          AND BYTES_SCANNED >= {min_scan}
        ORDER BY BYTES_SCANNED DESC
        LIMIT {top_n}
        """)

        # Warehouse load and metering
        wl = fetch(cur, f"""
        SELECT WAREHOUSE_NAME, DATE_TRUNC('hour', START_TIME) AS HOUR,
               AVG(AVG_RUNNING) AS AVG_RUNNING, AVG(AVG_QUEUED_LOAD) AS AVG_QUEUED_LOAD,
               AVG(AVG_QUEUED_PROVISIONING) AS AVG_QUEUED_PROV
        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_LOAD_HISTORY
        WHERE START_TIME >= DATEADD('hour', -{lookback_h}, {now})
        GROUP BY 1,2
        ORDER BY 1,2
        """)

        wm = fetch(cur, f"""
        SELECT WAREHOUSE_NAME, START_TIME, CREDITS_USED, CREDITS_USED_COMPUTE, CREDITS_USED_CLOUD_SERVICES
        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
        WHERE START_TIME >= DATEADD('day', -7, {now})
        ORDER BY 1,2 DESC
        """)

    # Aggregate load stats per warehouse
    load_by_wh = {}
    for wh, hour, avg_run, avg_q, avg_qp in wl:
        d = load_by_wh.setdefault(wh, {"avg_run":[], "avg_q":[], "avg_qp":[]})
        d["avg_run"].append(float(avg_run or 0))
        d["avg_q"].append(float(avg_q or 0))
        d["avg_qp"].append(float(avg_qp or 0))

    # Metering last 7d
    meter_by_wh = {}
    for wh, ts, credits, comp, svc in wm:
        m = meter_by_wh.setdefault(wh, {"credits":0.0, "compute":0.0, "svcs":0.0})
        m["credits"] += float(credits or 0)
        m["compute"] += float(comp or 0)
        m["svcs"] += float(svc or 0)

    # Query signatures and hints
    items = []
    sig_count = {}
    for (qid, user, wh, db, sch, exec_ms, bytes_scanned, rows_prod, start, text) in qh:
        sig = norm_signature(text or "")
        sig_count[sig] = sig_count.get(sig,0)+1
        ratio = (bytes_scanned / max(rows_prod, 1)) if rows_prod else float('inf')
        hints = []
        if "select *" in (text or "").lower(): hints.append("Project only needed columns (avoid SELECT *).")
        if " join " in (text or "").lower(): hints.append("Verify join keys/selectivity; consider pre-aggregations.")
        if ratio > 50_000: hints.append("High scan-to-row: push filters down; consider clustering on filter columns.")
        if "order by" in (text or "").lower(): hints.append("Avoid unnecessary ORDER BY or sort late.")
        if "group by" in (text or "").lower(): hints.append("Consider incremental/summary models in dbt.")
        if not hints: hints.append("Consider clustering, incremental dbt models, and avoiding full scans.")
        items.append({
            "qid": qid, "user": user, "wh": wh, "db": db, "sch": sch,
            "ms": int(exec_ms or 0), "scan": int(bytes_scanned or 0),
            "rows": int(rows_prod or 0), "ratio": ratio, "sig": sig,
            "text": " ".join((text or "").split())[:300], "hints": hints
        })

    # Warehouse sizing guidance
    def avg(lst): return sum(lst)/len(lst) if lst else 0.0
    wh_guidance = {}
    for wh, stats in load_by_wh.items():
        run = avg(stats["avg_run"])
        ql  = avg(stats["avg_q"])
        qp  = avg(stats["avg_qp"])
        credits = meter_by_wh.get(wh,{}).get("credits",0.0)
        guidance = []
        if ql > 0.5:
            guidance.append("Frequent queueing detected; consider 1) larger warehouse size or 2) job staggering.")
        if qp > 0.1:
            guidance.append("Provisioning queue suggests frequent spin-ups; tune auto-resume/suspend and schedule consolidation.")
        if run < 0.5 and credits > 0:
            guidance.append("Low average usage; evaluate smaller size or stricter auto-suspend.")
        wh_guidance[wh] = {
            "avg_running": round(run,2), "avg_queued": round(ql,2), "avg_queued_prov": round(qp,2),
            "credits_7d": round(credits,2), "advice": guidance or ["Usage looks balanced."]
        }

    # Markdown report
    md = ["# Snowflake Performance Audit",
          f"_Lookback: {lookback_h}h; Threshold: ≥ {human_bytes(min_scan)}; Generated: {dt.datetime.utcnow():%Y-%m-%d %H:%M UTC}_",
          "\n## Heavy Queries"]
    for it in items:
        md.append(f"- **{it['qid']}** | WH: `{it['wh']}` | {human_bytes(it['scan'])} scanned | rows: {it['rows']} | time: {it['ms']} ms")
        md.append(f"  - Text: `{it['text']}`")
        md.append(f"  - Hints: " + "; ".join(it['hints']))
    md.append("\n## Repeated Query Signatures (Top Patterns)")
    for sig, cnt in sorted(sig_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        md.append(f"- Count {cnt}: `{sig}`")
    md.append("\n## Warehouse Guidance")
    for wh, g in wh_guidance.items():
        md.append(f"- **{wh}** | avg_running={g['avg_running']} | avg_queued={g['avg_queued']} | credits_7d={g['credits_7d']}")
        for a in g["advice"]:
            md.append(f"  - {a}")

    report_path = os.getenv("PERF_REPORT_PATH","perf_report.md")
    with open(report_path,"w") as f:
        f.write("\n".join(md))

    # Optional Slack summary
    url = os.getenv("SLACK_WEBHOOK_URL")
    if url:
        import urllib.request, json
        summary = f"Snowflake Audit: {len(items)} heavy queries; {len(wh_guidance)} warehouses analyzed.\nReport: {report_path}"
        try:
            req = urllib.request.Request(url, data=json.dumps({"text":summary}).encode("utf-8"), headers={"Content-Type":"application/json"})
            urllib.request.urlopen(req, timeout=10).read()
        except Exception:
            pass

    print(f"Wrote report: {report_path}")

if __name__ == "__main__":
    audit()