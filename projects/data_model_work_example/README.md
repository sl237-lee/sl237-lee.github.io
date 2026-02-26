# Data Model & Pipeline Work Example

> A production-style demonstration of end-to-end data engineering, featuring data modeling, orchestration, automation, and infrastructure-as-code.

---

This project showcases a realistic **data engineering and data modeling workflow** that demonstrates my approach to designing scalable, cloud-based data pipelines.  
It is adapted from my real-world experience developing **pharmaceutical claims ETL systems**, generalized and anonymized for demonstration purposes.

---

> ### **View Full Source**
> Explore all code files and folder structure on  
> [**GitHub → sl237-lee.github.io / data_model_work_example**](https://github.com/sl237-lee/sl237-lee.github.io/tree/main/projects/data_model_work_example)

---

## Project Overview
For a detailed technical summary, see the [**Case Study →**](CASE_STUDY.md).

This project highlights skills in:
- Data Modeling & Schema Design  
- Workflow Orchestration (Prefect, Airflow, DBT)  
- Data Quality Assurance (Great Expectations)  
- Infrastructure-as-Code (Terraform on AWS)  
- CI/CD Integration (GitHub Actions)  

---

## Project Structure

| Folder | Description |
|:-------|:-------------|
| `models/` | Data model schemas (DDL) defining warehouse tables and relationships for Snowflake or Delta Lake. |
| `sql/` | Modular SQL scripts implementing the ELT pipeline (normalize → assemble → enrich → aggregate → publish). |
| `orchestration/` | Prefect v2 pipeline orchestrator for scheduling, dependencies, and data quality validation. |
| `airflow/` | Equivalent Airflow DAG for job scheduling and pipeline automation. |
| `dbt/` | DBT project for modular transformations, testing, and documentation. |
| `dq/` | Great Expectations configuration for automated data validation and schema testing. |
| `automation/` | GitHub Actions CI/CD pipeline for linting SQL, validating flows, and running lightweight checks. |
| `aws/` | Terraform templates and network architecture (VPC and PrivateLink setup) for secure cloud deployment. |
| `scripts/` | Administrative SQL scripts for RBAC configuration, performance monitoring, and cost optimization. |
| `local.env.example` | Example environment variable file for Snowflake, AWS, DBT, and orchestration setup. |
| `CASE_STUDY.md` | Technical summary describing architecture, design choices, and implementation approach. |
| `README.md` | Main project documentation and navigation guide. |

---

## Repository Contents

### 1. models/
Contains all **table definitions and DDL scripts** for Snowflake/Delta.  
Defines structured layers such as staging, intermediate, and marts.  
Ensures schema governance and reproducibility for analytics and reporting.

### 2. sql/
Implements **core transformation logic** for the ETL process:
- Normalize → Clean and standardize raw inputs.  
- Assemble → Join header and line data.  
- Enrich → Add dimensions and business context.  
- Aggregate → Create summary-level tables.  
- Publish → Output analytics-ready data marts.  

### 3. orchestration/
Contains a **Prefect v2 flow** that executes each ETL step, manages dependencies, and runs data quality validations.

### 4. airflow/
Provides an **Apache Airflow DAG** equivalent to the Prefect pipeline for organizations using Airflow-based orchestration.

### 5. dbt/
Includes a **DBT project** with staging, intermediate, and marts models to structure ELT transformations modularly.  
Supports built-in testing, lineage tracking, and documentation.

### 6. dq/
Houses **Great Expectations** configurations for automated data validation, schema checks, and metric tests.  
Ensures high data reliability and transparency in the pipeline.

### 7. automation/
Contains a **GitHub Actions CI/CD workflow** (`ci.yml`) that runs on every commit to:
- Lint SQL and Python files.  
- Validate orchestration scripts.  
- Run lightweight data quality checks.

### 8. aws/
Includes **Terraform scripts** and a **network diagram** describing AWS VPC, subnets, and PrivateLink setup.  
Demonstrates infrastructure-as-code and secure cloud deployment.

### 9. scripts/
Provides supporting **SQL utilities** such as:
- RBAC (Role-Based Access Control) configuration scripts.  
- Cost monitoring and warehouse performance queries.  
- Maintenance routines for Snowflake or Databricks environments.

### 10. local.env.example
Template configuration for environment variables used across the project.  
Separates credentials and connection strings from code for secure deployments.

### 11. CASE_STUDY.md
Detailed **technical summary** explaining architecture, workflow, and tools used.  
Serves as a narrative case study for engineering review or portfolio presentation.

### 12. README.md
The main **project index and documentation hub**, providing navigation, context, and setup instructions.

---

## How to Run (Conceptual)

1. **Set up the environment**
   ```bash
   pip install -r requirements.txt

# Configure dbt profile
Copy `dbt/profiles.yml.example` to `~/.dbt/profiles.yml` and update credentials or environment variables as needed.
For demonstration purposes, this project can also be compiled without a live Snowflake connection using:
```bash
dbt compile