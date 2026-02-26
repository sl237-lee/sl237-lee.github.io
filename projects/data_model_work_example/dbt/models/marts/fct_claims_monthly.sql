
-- dbt/models/marts/fct_claims_monthly.sql
{{ config(materialized='table') }}

with e as (
  select * from {{ ref('int_claims_enriched') }}
)
select
  e.member_sid,
  e.plan_sid,
  e.provider_sid,
  e.provider_specialty,
  e.network_tier,
  date_trunc('month', e.service_end_date) as month_ending_date,
  e.claim_type,
  count(distinct e.claim_number) as claim_count,
  sum(e.line_count) as service_count,
  sum(e.total_billed) as billed_amount,
  sum(e.total_allowed) as allowed_amount,
  sum(e.total_paid) as paid_amount,
  sum(e.adjustment_amount) as adjustment_amount,
  sum(e.net_paid) as net_paid
from e
group by 1,2,3,4,5,6,7
