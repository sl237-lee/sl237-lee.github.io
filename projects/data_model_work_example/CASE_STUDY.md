# Case Study — Data Model & Pipeline Work Example

## Objective
To demonstrate my ability to design, implement, and automate an **end-to-end data engineering workflow** — from raw data ingestion through analytics-ready modeling — using modern cloud and DevOps practices.

This project is inspired by my real experience building pharmaceutical claims ETL systems and is generalized for demonstration purposes.  
It highlights practical skills in **data modeling, orchestration, data quality, and infrastructure automation**.

---

## Architecture Overview

**Key Components**
| Layer | Technology | Purpose |
|:------|:------------|:--------|
| Data Warehouse | **Snowflake / Databricks** | Central data platform for raw, staging, and marts layers. |
| Transformation | **SQL + DBT** | Modular ELT models for normalize → enrich → aggregate. |
| Orchestration | **Prefect v2 / Airflow** | Pipeline scheduling, monitoring, and alerting. |
| Data Quality | **Great Expectations** | Automated validation and schema integrity checks. |
| CI/CD | **GitHub Actions** | Linting, syntax validation, and lightweight test automation. |
| Infrastructure | **Terraform + AWS VPC/PrivateLink** | Secure network connectivity and reproducible deployment. |

---

## Data Flow Design

**ETL Stages**
1. **Normalize** — Standardize raw claim headers and lines (cleanse codes, amounts, IDs).  
2. **Assemble** — Merge header-line data into unified claims.  
3. **Enrich** — Join member, provider, and plan dimensions; apply adjustments.  
4. **Aggregate** — Summarize to `(member, provider, plan, month, claim_type)` grain.  
5. **Publish** — Upsert results into analytics-ready fact tables.

Each stage is modular, version-controlled in Git, and orchestrated using Prefect or Airflow for daily or monthly execution.

---

## ⚙️ Technical Highlights

- **Data Modeling:** Designed 3-layer model (staging → intermediate → marts) with surrogate keys and referential integrity.  
- **Orchestration:** Implemented both Prefect flow and Airflow DAG for flexible scheduling and retries.  
- **Data Quality:** Configured Great Expectations tests for row counts, null checks, and key uniqueness.  
- **Automation:** Added GitHub Actions pipeline to lint SQL, test orchestration syntax, and validate DQ configs.  
- **Infrastructure:** Created Terraform templates and VPC diagram for secure AWS-Snowflake connectivity via PrivateLink.  

---

## Skills Demonstrated
**Languages & Tools:**  
`Python`, `SQL`, `DBT`, `Snowflake`, `Databricks`, `Prefect`, `Airflow`, `Terraform`, `AWS`, `GitHub Actions`, `Great Expectations`

**Concepts:**  
Data Modeling · ETL/ELT Pipelines · Data Quality Frameworks · Workflow Orchestration · Infrastructure as Code · CI/CD Automation

---

## Outcome
This project demonstrates my approach to building **scalable, maintainable, and secure data pipelines**.  
It shows how I combine strong SQL foundations with cloud architecture, automation, and data governance to deliver reliable, production-ready solutions.