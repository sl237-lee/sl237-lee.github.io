# Data Model & Pipeline Work Example

This project showcases a production-style **data engineering and modeling workflow** that I built to demonstrate my technical approach to designing scalable, cloud-based data pipelines.  
It is adapted from my real-world experience building **pharmaceutical claims ETL systems**, generalized and scrubbed of all client identifiers.


> ### **View Full Source**
> Explore all scripts and folders for this project on  
> [**GitHub → sl237-lee.github.io / data_model_work_example**](https://github.com/sl237-lee/sl237-lee.github.io/tree/main/projects/data_model_work_example)


The goal is to highlight my skills across:
- **Data modeling & schema design**
- **Orchestration & automation (Prefect, Airflow, DBT)**
- **Data quality assurance (Great Expectations)**
- **Infrastructure-as-code (Terraform on AWS)**
- **CI/CD integration (GitHub Actions)**

---

## Project Overview
For a detailed technical summary, see the [Case Study](CASE_STUDY.md).

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