# QVC Unified Vendor Data Foundation (Azure Demo)

This project simulates how **QVC’s Social Commerce data engineering team** could build a unified foundation that integrates marketing and engagement data from multiple vendors — **TikTok, Meta, and YouTube** — into a single governed and analytics-ready data platform on **Azure**.

It demonstrates how to:
- Ingest and normalize **multi-vendor campaign data**
- Apply **YAML-based data contracts** for schema consistency
- Run automated **data-quality validation** and filtering
- Generate a unified, curated dataset for **analytics and personalization**
- Expose metrics via a **FastAPI** service (similar to an internal data API at QVC)

---

## 1. Architecture Overview

![Architecture Diagram](architecture_diagram.png)

### **End-to-End Flow**
```
ADF → ADLS → Databricks (PySpark) → Synapse → FastAPI
```

1. **Ingestion (ADF simulation)**  
   Vendor data from TikTok, Meta, and YouTube is stored in `/data/raw` as JSON files.  

2. **Transformation & Normalization**  
   `normalize_vendor_data.py` reads each file, applies vendor-specific data contracts, performs cleaning and data-quality checks, and merges the results into one curated dataset.

3. **Validation (Data Quality)**  
   `dq_runner.py` validates all vendor feeds — checking for missing fields, invalid values, or schema mismatches defined in the YAML contracts.

4. **Curation & Modeling**  
   The cleaned, unified dataset is saved in `/data/curated/unified_campaign_performance.csv`, representing the “single source of truth” for campaign analytics.

5. **API & Serving Layer**  
   `main.py` uses **FastAPI** to serve unified analytics endpoints (e.g., `/api/vendor_summary`, `/api/top_products`, `/api/data_quality_summary`) that could power internal dashboards, recommendation systems, or downstream AI models.

---

## 2. Key Components

| File | Purpose |
|------|----------|
| `contracts/*.yaml` | Data contracts defining schema, field types, and validation rules for each vendor |
| `data/raw/*.json` | Raw sample vendor feeds (Meta, TikTok, YouTube) |
| `dq_runner.py` | Runs schema validation and reports data-quality issues |
| `normalize_vendor_data.py` | Cleans, merges, and applies data-quality filters to unify all vendor data |
| `main.py` | FastAPI service exposing analytics and data-quality metrics |
| `data/curated/unified_campaign_performance.csv` | Final unified dataset used by the API |

---

## 3. How It Works

### **Step 1 — Define Data Contracts**
Each vendor has a YAML file in `/contracts` defining:
- Required fields (e.g., `campaign_id`, `impressions`, `spend`)
- Data types  
- Business rules (e.g., spend ≥ 0, impressions > 0)
- Freshness SLAs  

Example (`contracts/meta_ads.yaml`):
```yaml
fields:
  - name: campaign_id
    type: string
    required: true
  - name: impressions
    type: integer
    required: true
  - name: spend
    type: float
    required: true
validation_rules:
  - rule: not_null
    fields: [campaign_id, impressions, spend]
  - rule: min_value
    field: spend
    value: 0
```

---

### **Step 2 — Validate Vendor Feeds**
Run quick validations to ensure each dataset matches its schema:
```bash
python3 dq_runner.py
```
Expected output:
```
[PASS] meta: All data quality checks passed ✅
[PASS] tiktok: All data quality checks passed ✅
[PASS] youtube: All data quality checks passed ✅
```

---

### **Step 3 — Normalize and Unify Data**
Clean, validate, and merge all vendor datasets into a single unified model:
```bash
python3 normalize_vendor_data.py
```

This applies filters for:
- Missing or invalid campaign IDs  
- Negative spend values  
- Zero-impression records  

Output:
```
[DQ] Meta: Removed 0 invalid rows (kept 2)
[DQ] TikTok: Removed 0 invalid rows (kept 2)
[DQ] YouTube: Removed 0 invalid rows (kept 2)
[SUCCESS] Unified dataset saved to data/curated/unified_campaign_performance.csv
```

---

### **Step 4 — Launch the API**
Start the FastAPI service:
```bash
uvicorn main:app --reload
```

Visit:
- **http://127.0.0.1:8000/** → API welcome page  
- **http://127.0.0.1:8000/api/vendor_summary** → Unified metrics  
- **http://127.0.0.1:8000/api/top_products** → Top product performance  
- **http://127.0.0.1:8000/api/data_quality_summary** → Data-quality report  

---

## 4. Example Outputs

**GET `/api/vendor_summary`**
```json
[
  {"vendor": "Meta", "impressions": 38000, "clicks": 1700, "spend": 530.8, "conversions": 117},
  {"vendor": "TikTok", "impressions": 19500, "clicks": 1420, "spend": 283.6, "conversions": 95},
  {"vendor": "YouTube", "impressions": 28200, "clicks": 1230, "spend": 374.3, "conversions": 84}
]
```

**GET `/api/data_quality_summary`**
```json
{
  "total_rows": 6,
  "columns_with_nulls": {},
  "valid_rows": 6
}
```

---

## 5. Why This Matters (QVC Context)

This demo mirrors QVC’s **United Data Foundation** initiative — integrating vendor ecosystems (TikTok, Meta, YouTube) under a single governed model.

It shows how to:
- Standardize metrics and schemas via **data contracts**
- Enforce **data-quality validation** programmatically
- Serve unified analytics through **APIs** instead of static reports
- Build a foundation that scales to **real-time social commerce personalization**

---

## 6. Requirements
Install dependencies:
```bash
pip3 install fastapi uvicorn pandas pyyaml
```

(Optional) Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 7. Folder Structure
```
qvc_unified_data_foundation/
│
├── contracts/                     # Data contracts per vendor
│   ├── meta_ads.yaml
│   ├── tiktok_ads.yaml
│   └── youtube_ads.yaml
│
├── data/
│   ├── raw/                       # Sample vendor feeds (JSON)
│   │   ├── meta_ads_sample.json
│   │   ├── tiktok_ads_sample.json
│   │   └── youtube_ads_sample.json
│   └── curated/
│       └── unified_campaign_performance.csv
│
├── dq_runner.py                   # Runs schema validation
├── normalize_vendor_data.py       # Cleans, merges, and filters data
├── main.py                        # FastAPI analytics service
└── README.md
```

---

## 8. Key Takeaways
- Built an end-to-end Azure-style **data foundation prototype**
- Demonstrated **vendor-agnostic schema standardization**
- Included **data-quality automation and validation**
- Delivered **API-ready unified dataset** for analytics and personalization

---

## 9. Future Enhancements
- Integrate live APIs from TikTok, Meta, and YouTube  
- Add **Copilot Studio** integration to auto-generate validation code and API specs  
- Deploy on **Azure Container Apps** for scalability  
- Extend FastAPI layer with **real-time personalization metrics**

---

### Author
**Seungryul (Andrew) Lee**  
💼 https://github.com/sl237-lee
