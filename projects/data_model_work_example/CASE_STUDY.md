# Case Study — Data Model & Pipeline Work Example

> A demonstration of modern data engineering architecture — showcasing end-to-end automation, orchestration, and data modeling practices.

---

## Objective
This project demonstrates my ability to **design, implement, and automate an end-to-end data engineering workflow** — from raw data ingestion to analytics-ready modeling — using modern cloud and DevOps practices.

It’s inspired by my real experience building **pharmaceutical claims ETL systems** and has been fully generalized for demonstration purposes.  
It highlights practical skills in **data modeling, orchestration, data quality, and infrastructure automation**.

---

> ### **View Full Source**
> Explore all scripts and folders for this project on  
> [**GitHub → sl237-lee.github.io / data_model_work_example**](https://github.com/sl237-lee/sl237-lee.github.io/tree/main/projects/data_model_work_example)

---

## Architecture Overview

<div align="center">

<table style="width:100%; border-collapse:collapse;">
  <thead>
    <tr>
      <th style="text-align:left; padding:10px; border-bottom:2px solid #ddd;">Layer</th>
      <th style="text-align:left; padding:10px; border-bottom:2px solid #ddd;">Technology</th>
      <th style="text-align:left; padding:10px; border-bottom:2px solid #ddd;">Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:10px;">Data Warehouse</td>
      <td style="padding:10px;"><strong>Snowflake / Databricks</strong></td>
      <td style="padding:10px;">Central data platform for raw, staging, and marts layers.</td>
    </tr>
    <tr>
      <td style="padding:10px;">Transformation</td>
      <td style="padding:10px;"><strong>SQL + DBT</strong></td>
      <td style="padding:10px;">Modular ELT models for normalize → enrich → aggregate.</td>
    </tr>
    <tr>
      <td style="padding:10px;">Orchestration</td>
      <td style="padding:10px;"><strong>Prefect v2 / Airflow</strong></td>
      <td style="padding:10px;">Pipeline scheduling, monitoring, and alerting.</td>
    </tr>
    <tr>
      <td style="padding:10px;">Data Quality</td>
      <td style="padding:10px;"><strong>Great Expectations</strong></td>
      <td style="padding:10px;">Automated validation and schema integrity checks.</td>
    </tr>
    <tr>
      <td style="padding:10px;">CI/CD</td>
      <td style="padding:10px;"><strong>GitHub Actions</strong></td>
      <td style="padding:10px;">Linting, syntax validation, and lightweight test automation.</td>
    </tr>
    <tr>
      <td style="padding:10px;">Infrastructure</td>
      <td style="padding:10px;"><strong>Terraform + AWS VPC / PrivateLink</strong></td>
      <td style="padding:10px;">Secure network connectivity and reproducible deployment.</td>
    </tr>
  </tbody>
</table>

</div>

---

## Data Flow Design

**ETL Workflow Stages**
1. **Normalize** — Standardize raw claim headers and lines (cleanse codes, amounts, IDs).  
2. **Assemble** — Merge header-line data into unified claim records.  
3. **Enrich** — Join member, provider, and plan dimensions; apply adjustments.  
4. **Aggregate** — Summarize to `(member, provider, plan, month, claim_type)` grain.  
5. **Publish** — Upsert results into analytics-ready fact tables.

Each stage is modular, version-controlled in Git, and orchestrated using Prefect or Airflow for daily or monthly execution.

---

## Technical Highlights

- **Data Modeling:** 3-layer design (staging → intermediate → marts) with surrogate keys and referential integrity.  
- **Orchestration:** Prefect flow and Airflow DAG for flexible scheduling, monitoring, and retries.  
- **Data Quality:** Great Expectations tests for row counts, null checks, and key uniqueness.  
- **Automation:** GitHub Actions pipeline for linting SQL, validating flows, and running lightweight DQ checks.  
- **Infrastructure:** Terraform templates and VPC diagram for secure AWS-Snowflake connectivity via PrivateLink.  

---

## Skills Demonstrated

**Languages & Tools:**  
`Python`, `SQL`, `DBT`, `Snowflake`, `Databricks`, `Prefect`, `Airflow`, `Terraform`, `AWS`, `GitHub Actions`, `Great Expectations`

**Concepts:**  
Data Modeling · ETL/ELT Pipelines · Data Quality Frameworks · Workflow Orchestration · Infrastructure as Code · CI/CD Automation

---

## Outcome
This project reflects my approach to building **scalable, maintainable, and secure data pipelines**.  
It demonstrates how I combine strong SQL foundations with modern cloud architecture, automation, and data governance to deliver **reliable, production-ready solutions**.