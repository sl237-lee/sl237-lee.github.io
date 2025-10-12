
-- dbt/models/intermediate/int_claims_enriched.sql
{{ config(materialized='view') }}

with hdr as (select * from {{ source('raw', 'claims_header') }}),
stg as (select * from {{ ref('stg_claims') }}),
m as (select * from {{ source('dim', 'member') }}),
p as (select * from {{ source('dim', 'provider') }}),
adj as (select * from {{ source('finance', 'payment_adjustments') }})
select
  h.claim_number,
  h.claim_type,
  m.member_sid,
  p.provider_sid,
  m.plan_sid,
  case
    when datediff('year', m.dob, stg.service_start_date) < 18 then 'CHILD'
    when datediff('year', m.dob, stg.service_start_date) < 65 then 'ADULT'
    else 'SENIOR'
  end as member_age_group,
  p.provider_specialty,
  p.network_tier,
  stg.service_start_date,
  stg.service_end_date,
  count(*) over (partition by h.claim_number) as line_count,
  sum(stg.billed_amount) over (partition by h.claim_number) as total_billed,
  sum(stg.allowed_amount) over (partition by h.claim_number) as total_allowed,
  sum(stg.paid_amount) over (partition by h.claim_number) as total_paid,
  coalesce(adj.adjustment_amount, 0) as adjustment_amount,
  coalesce(sum(stg.paid_amount) over (partition by h.claim_number),0) + coalesce(adj.adjustment_amount,0) as net_paid
from hdr h
join stg on h.claim_number = stg.claim_number
join m on h.member_id = m.member_natural_key
join p on h.provider_id = p.provider_natural_key
left join adj on h.claim_number = adj.claim_number
