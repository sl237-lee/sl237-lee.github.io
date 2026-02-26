import pandas as pd
import yaml
from pathlib import Path

contracts_dir = Path("contracts")
raw_dir = Path("data/raw")
curated_dir = Path("data/curated")
curated_dir.mkdir(parents=True, exist_ok=True)

def load_contract(vendor):
    """Load YAML data contract for a given vendor."""
    with open(contracts_dir / f"{vendor}_ads.yaml") as f:
        return yaml.safe_load(f)

def apply_data_quality_filters(df, vendor):
    """Apply basic data-quality rules."""
    original_count = len(df)

    # Drop rows missing key identifiers
    if "campaign_id" in df.columns:
        df = df.dropna(subset=["campaign_id"])

    # Remove rows with invalid spend or impressions
    if "spend" in df.columns:
        df = df[df["spend"] >= 0]
    if "impressions" in df.columns:
        df = df[df["impressions"] > 0]

    filtered_count = len(df)
    dropped = original_count - filtered_count

    print(f"[DQ] {vendor.capitalize()}: Removed {dropped} invalid rows (kept {filtered_count})")
    return df

def normalize_vendor(vendor):
    """Normalize and clean vendor data based on its data contract."""
    raw_path = raw_dir / f"{vendor}_ads_sample.json"
    if not raw_path.exists():
        print(f"[SKIP] No data found for {vendor}")
        return pd.DataFrame()

    df = pd.read_json(raw_path)
    contract = load_contract(vendor)
    fields = [f["name"] for f in contract["fields"] if f["name"] in df.columns]
    df = df[fields]

    # Add vendor column
    df["vendor"] = vendor.capitalize()

    # Apply DQ filters
    df = apply_data_quality_filters(df, vendor)

    print(f"[INFO] Normalized {vendor}: {len(df)} valid records")
    return df

if __name__ == "__main__":
    vendors = [f.stem.split("_")[0] for f in raw_dir.glob("*_ads_sample.json")]
    all_dfs = []

    for vendor in vendors:
        df = normalize_vendor(vendor)
        if not df.empty:
            all_dfs.append(df)

    if all_dfs:
        unified = pd.concat(all_dfs, ignore_index=True)
        output_path = curated_dir / "unified_campaign_performance.csv"
        unified.to_csv(output_path, index=False)
        print(f"[SUCCESS] Unified dataset saved to {output_path}")
        print(f"[SUMMARY] Total rows: {len(unified)} across {len(vendors)} vendors.")
    else:
        print("[WARN] No valid data to unify.")