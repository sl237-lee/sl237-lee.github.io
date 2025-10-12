
-- dbt/models/staging/stg_claims.sql
{{ config(materialized='view') }}

with claims as (
  select * from {{ source('raw', 'claims_line') }}
)
select
  upper(trim(icd_code)) as icd_code,
  upper(trim(cpt_code)) as cpt_code,
  cast(billed_amount as numeric(18,2)) as billed_amount,
  cast(allowed_amount as numeric(18,2)) as allowed_amount,
  cast(paid_amount as numeric(18,2)) as paid_amount,
  claim_number,
  member_id,
  provider_id,
  service_start_date,
  service_end_date
from claims
