from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
from pathlib import Path

app = FastAPI(
    title="QVC Unified Vendor Data Foundation API",
    description="Unified metrics and data quality insights across vendor marketing feeds (Meta, TikTok, YouTube).",
    version="1.0.0",
)

curated_file = Path("data/curated/unified_campaign_performance.csv")

# Load curated data safely
def load_curated_data():
    if curated_file.exists():
        df = pd.read_csv(curated_file)
        return df
    else:
        print("[WARN] Curated dataset not found.")
        return pd.DataFrame()

@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Welcome to the QVC Unified Vendor Data Foundation API 🚀",
        "endpoints": [
            "/api/vendor_summary",
            "/api/top_products",
            "/api/vendor_performance",
            "/api/data_quality_summary"
        ]
    }

@app.get("/api/vendor_summary")
def vendor_summary():
    """Returns total impressions, clicks, spend, and conversions per vendor"""
    df = load_curated_data()
    if df.empty:
        return JSONResponse({"error": "No curated data found."}, status_code=404)
    summary = (
        df.groupby("vendor")[["impressions", "clicks", "spend", "conversions"]]
        .sum()
        .reset_index()
        .sort_values("spend", ascending=False)
    )
    return summary.to_dict(orient="records")

@app.get("/api/top_products")
def top_products():
    """Returns top 5 products by conversions across all vendors"""
    df = load_curated_data()
    if df.empty:
        return JSONResponse({"error": "No curated data found."}, status_code=404)
    top = (
        df.groupby(["vendor", "product"])["conversions"]
        .sum()
        .reset_index()
        .sort_values("conversions", ascending=False)
        .head(5)
    )
    return top.to_dict(orient="records")

@app.get("/api/vendor_performance")
def vendor_performance():
    """Calculates CTR and conversion rate by vendor"""
    df = load_curated_data()
    if df.empty:
        return JSONResponse({"error": "No curated data found."}, status_code=404)
    df["ctr"] = df["clicks"] / df["impressions"]
    df["conversion_rate"] = df["conversions"] / df["clicks"].replace(0, pd.NA)
    perf = (
        df.groupby("vendor")[["ctr", "conversion_rate", "spend"]]
        .mean()
        .reset_index()
    )
    return perf.to_dict(orient="records")

@app.get("/api/data_quality_summary")
def data_quality_summary():
    """Returns basic data quality metrics"""
    df = load_curated_data()
    if df.empty:
        return JSONResponse({"error": "No curated data found."}, status_code=404)
    null_counts = df.isnull().sum().to_dict()
    total_rows = len(df)
    dq_report = {
        "total_rows": total_rows,
        "columns_with_nulls": {k: v for k, v in null_counts.items() if v > 0},
        "valid_rows": total_rows - sum(null_counts.values()),
    }
    return dq_report