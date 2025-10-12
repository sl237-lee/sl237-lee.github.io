# Data Model & Pipeline Work Example

> A production-style demonstration of end-to-end data engineering, featuring data modeling, orchestration, automation, and infrastructure-as-code.

---

This project showcases a **realistic data engineering and modeling workflow** that demonstrates my technical approach to designing scalable, cloud-based data pipelines.  
It’s adapted from my real-world experience developing **pharmaceutical claims ETL systems**, fully generalized and anonymized for demonstration.

---

> ### **View Full Source**
> Explore all code files and folder structure on  
> [**GitHub → sl237-lee.github.io / data_model_work_example**](https://github.com/sl237-lee/sl237-lee.github.io/tree/main/projects/data_model_work_example)

---

## Project Overview
For a detailed technical summary, see the [**Case Study →**](CASE_STUDY.md).

This project highlights skills in:
- **Data Modeling & Schema Design**
- **Workflow Orchestration (Prefect, Airflow, DBT)**
- **Data Quality Assurance (Great Expectations)**
- **Infrastructure-as-Code (Terraform on AWS)**
- **CI/CD Integration (GitHub Actions)**

---

## Project Structure

| Folder | Description |
|:-------|:-------------|
| `models/` | Data model schemas (DDL) for Snowflake/Delta. |
| `sql/` | Modular SQL scripts for normalize → assemble → enrich → aggregate → publish. |
| `orchestration/` | Prefect v2 pipeline orchestrator with automated DQ checks. |
| `airflow/` | Equivalent Airflow DAG for job scheduling and monitoring. |
| `dbt/` | DBT project for modular transformations and testing. |
| `dq/` | Great Expectations-style data validation and monitoring config. |
| `automation/` | GitHub Actions CI for linting and pipeline verification. |
| `aws/` | Terraform + architecture diagram for PrivateLink and VPC setup. |
| `scripts/` | RBAC configuration and cost monitoring SQL queries. |
| `local.env.example` | Example environment variables for secure configuration. |

---

## How to Run (Conceptual)

1. **Set up the environment**
   ```bash
   pip install -r requirements.txt