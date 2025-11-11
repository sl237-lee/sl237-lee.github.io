import pandas as pd
import yaml
from pathlib import Path

def dq_check(df, vendor):
    results = []
    for col in df.columns:
        nulls = df[col].isnull().sum()
        if nulls > 0:
            results.append(f"{vendor}: {col} has {nulls} nulls")

    if not results:
        print(f"[PASS] {vendor}: All data quality checks passed ✅")
    else:
        for r in results:
            print(f"[WARN] {r}")

if __name__ == "__main__":
    raw_dir = Path("data/raw")
    for f in raw_dir.glob("*_ads_sample.json"):
        vendor = f.stem.split("_")[0]
        df = pd.read_json(f)
        dq_check(df, vendor)