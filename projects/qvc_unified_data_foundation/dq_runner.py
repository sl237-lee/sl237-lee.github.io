import pandas as pd
import yaml
import json
from pathlib import Path
from datetime import datetime

def load_contract(vendor):
    """Load YAML contract for the vendor."""
    contracts_dir = Path("contracts")
    contract_file = contracts_dir / f"{vendor}_ads.yaml"
    if not contract_file.exists():
        print(f"[WARN] No contract found for {vendor}. Skipping schema validation.")
        return None
    with open(contract_file) as f:
        return yaml.safe_load(f)

def dq_check(df, vendor):
    """Perform multiple data quality checks for a given vendor dataset."""
    print(f"\n=== Running DQ Checks for {vendor.capitalize()} ===")
    issues = []
    dq_summary = {"vendor": vendor, "timestamp": datetime.now().isoformat()}
    total_rows = len(df)
    dq_summary["total_rows"] = total_rows

    # --- 1. Null Check ---
    null_counts = df.isnull().sum().to_dict()
    dq_summary["null_counts"] = null_counts
    for col, n in null_counts.items():
        if n > 0:
            issues.append(f"{col} has {n} nulls")

    # --- 2. Duplicate Check ---
    if "campaign_id" in df.columns:
        dupes = df["campaign_id"].duplicated().sum()
        dq_summary["duplicate_rows"] = int(dupes)
        if dupes > 0:
            issues.append(f"{dupes} duplicate campaign_id values")
    else:
        dq_summary["duplicate_rows"] = None

    # --- 3. Schema Check ---
    contract = load_contract(vendor)
    if contract:
        contract_fields = [f["name"] for f in contract["fields"]]
        missing = [f for f in contract_fields if f not in df.columns]
        extra = [f for f in df.columns if f not in contract_fields]
        dq_summary["missing_columns"] = missing
        dq_summary["extra_columns"] = extra

        if missing:
            issues.append(f"Missing columns: {missing}")
        if extra:
            issues.append(f"Extra columns not in contract: {extra}")

        # --- 4. Data Type Validation ---
        type_map = {"string": "object", "integer": "int64", "float": "float64"}
        invalid_types = []
        for field in contract["fields"]:
            name, expected_type = field["name"], field["type"]
            if name in df.columns:
                actual_type = str(df[name].dtype)
                if expected_type in type_map and type_map[expected_type] not in actual_type:
                    invalid_types.append({name: {"expected": expected_type, "found": actual_type}})
        dq_summary["invalid_types"] = invalid_types
        if invalid_types:
            issues.append(f"Columns with invalid types: {invalid_types}")

    # --- 5. Range and Logical Rules ---
    range_issues = {}
    if "spend" in df.columns:
        neg_spend = (df["spend"] < 0).sum()
        range_issues["negative_spend"] = int(neg_spend)
        if neg_spend > 0:
            issues.append(f"{neg_spend} rows with negative spend")
    if "impressions" in df.columns:
        zero_imps = (df["impressions"] <= 0).sum()
        range_issues["zero_impressions"] = int(zero_imps)
        if zero_imps > 0:
            issues.append(f"{zero_imps} rows with zero or negative impressions")
    if all(col in df.columns for col in ["clicks", "impressions"]):
        invalid_clicks = (df["clicks"] > df["impressions"]).sum()
        range_issues["clicks_gt_impressions"] = int(invalid_clicks)
        if invalid_clicks > 0:
            issues.append(f"{invalid_clicks} rows where clicks > impressions")
    dq_summary["range_issues"] = range_issues

    # --- 6. Summary + Pass/Fail ---
    dq_summary["status"] = "PASS" if not issues else "FAIL"
    dq_summary["issue_count"] = len(issues)
    dq_summary["issues"] = issues

    if issues:
        print(f"[WARN] {len(issues)} DQ issue(s) found for {vendor}:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"[PASS] {vendor}: All data quality checks passed")

    print(f"=== Completed DQ for {vendor.capitalize()} ===\n")
    return dq_summary

if __name__ == "__main__":
    raw_dir = Path("data/raw")
    report_dir = Path("data/dq_reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.exists():
        print("❌ No data/raw directory found.")
    else:
        all_summaries = []
        for f in raw_dir.glob("*_ads_sample.json"):
            vendor = f.stem.split("_")[0]
            df = pd.read_json(f)
            summary = dq_check(df, vendor)
            all_summaries.append(summary)

            # Write per-vendor JSON summary
            out_path = report_dir / f"{vendor}_dq_summary.json"
            with open(out_path, "w") as outfile:
                json.dump(summary, outfile, indent=4)

        # Write combined master report
        master_path = report_dir / "dq_master_summary.json"
        with open(master_path, "w") as masterfile:
            json.dump(all_summaries, masterfile, indent=4)

        print(f"DQ Reports saved to {report_dir}/")