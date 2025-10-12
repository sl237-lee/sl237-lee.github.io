
-- sql/01_etl_claims_medical_monthly_fact.sql
-- Phases: normalize → assemble → enrich → aggregate → publish → cleanup
USE SCHEMA {stage_schema};

-- Cleanup old staging
DROP TABLE IF EXISTS {stage_schema}.claims_normalized;
DROP TABLE IF EXISTS {stage_schema}.claims_assembled;
DROP TABLE IF EXISTS {stage_schema}.claims_enriched;
DROP TABLE IF EXISTS {stage_schema}.claims_agg_monthly;

-- Normalize
CREATE OR REPLACE TABLE {stage_schema}.claims_normalized AS
SELECT
  hdr.claim_number,
  hdr.claim_type,
  hdr.member_id,
  hdr.provider_id,
  hdr.service_start_date,
  hdr.service_end_date,
  hdr.claim_status,
  l.line_number,
  UPPER(TRIM(l.icd_code))     AS icd_code,
  UPPER(TRIM(l.cpt_code))     AS cpt_code,
  CAST(l.billed_amount  AS DECIMAL(18,2)) AS billed_amount,
  CAST(l.allowed_amount AS DECIMAL(18,2)) AS allowed_amount,
  CAST(l.paid_amount    AS DECIMAL(18,2)) AS paid_amount,
  CURRENT_TIMESTAMP AS dmax_inserted_at,
  CURRENT_USER      AS dmax_inserted_by
FROM {raw_schema}.claims_header hdr
JOIN {raw_schema}.claims_line   l
  ON hdr.claim_number = l.claim_number
WHERE COALESCE(hdr.is_deleted, FALSE) = FALSE
  AND COALESCE(l.is_deleted, FALSE) = FALSE;

-- Assemble
CREATE OR REPLACE TABLE {stage_schema}.claims_assembled AS
SELECT
  claim_number,
  claim_type,
  member_id,
  provider_id,
  service_start_date,
  service_end_date,
  claim_status,
  COUNT(line_number)             AS line_count,
  SUM(billed_amount)             AS total_billed,
  SUM(allowed_amount)            AS total_allowed,
  SUM(paid_amount)               AS total_paid,
  MAX(dmax_inserted_at)          AS dmax_inserted_at,
  MAX(dmax_inserted_by)          AS dmax_inserted_by
FROM {stage_schema}.claims_normalized
GROUP BY 1,2,3,4,5,6,7;

-- Enrich
CREATE OR REPLACE TABLE {stage_schema}.claims_enriched AS
SELECT
  asm.claim_number,
  asm.claim_type,
  m.member_sid,
  p.provider_sid,
  m.plan_sid,
  CASE
    WHEN DATEDIFF('year', m.dob, asm.service_start_date) < 18 THEN 'CHILD'
    WHEN DATEDIFF('year', m.dob, asm.service_start_date) < 65 THEN 'ADULT'
    ELSE 'SENIOR'
  END AS member_age_group,
  p.provider_specialty,
  p.network_tier,
  asm.service_start_date,
  asm.service_end_date,
  asm.claim_status,
  asm.line_count,
  asm.total_billed,
  asm.total_allowed,
  asm.total_paid,
  COALESCE(adj.adjustment_amount, 0) AS adjustment_amount,
  asm.total_paid + COALESCE(adj.adjustment_amount,0) AS net_paid,
  CURRENT_TIMESTAMP AS dmax_inserted_at,
  CURRENT_USER      AS dmax_inserted_by
FROM {stage_schema}.claims_assembled asm
JOIN {dim_schema}.member   m ON asm.member_id  = m.member_natural_key AND COALESCE(m.is_current, TRUE)
JOIN {dim_schema}.provider p ON asm.provider_id = p.provider_natural_key AND COALESCE(p.is_current, TRUE)
LEFT JOIN {finance_schema}.payment_adjustments adj ON asm.claim_number = adj.claim_number;

-- Aggregate
CREATE OR REPLACE TABLE {stage_schema}.claims_agg_monthly AS
SELECT
  e.member_sid,
  e.plan_sid,
  e.provider_sid,
  e.provider_specialty,
  e.network_tier,
  DATE_TRUNC('month', e.service_end_date) AS month_ending_date,
  e.claim_type,
  COUNT(DISTINCT e.claim_number) AS claim_count,
  SUM(e.line_count)        AS service_count,
  SUM(e.total_billed)      AS billed_amount,
  SUM(e.total_allowed)     AS allowed_amount,
  SUM(e.total_paid)        AS paid_amount,
  SUM(e.adjustment_amount) AS adjustment_amount,
  SUM(e.net_paid)          AS net_paid,
  CURRENT_TIMESTAMP AS dmax_inserted_at,
  CURRENT_USER      AS dmax_inserted_by
FROM {stage_schema}.claims_enriched e
GROUP BY 1,2,3,4,5,6,7;

-- Publish (MERGE for idempotency)
MERGE INTO {sales_schema}.claims_medical_monthly_fact AS tgt
USING {stage_schema}.claims_agg_monthly AS src
ON  tgt.member_sid       = src.member_sid
AND tgt.provider_sid     = src.provider_sid
AND tgt.plan_sid         = src.plan_sid
AND tgt.month_ending_date= src.month_ending_date
AND tgt.claim_type       = src.claim_type
WHEN MATCHED THEN UPDATE SET
  provider_specialty = src.provider_specialty,
  network_tier       = src.network_tier,
  claim_count        = src.claim_count,
  service_count      = src.service_count,
  billed_amount      = src.billed_amount,
  allowed_amount     = src.allowed_amount,
  paid_amount        = src.paid_amount,
  adjustment_amount  = src.adjustment_amount,
  net_paid           = src.net_paid,
  dmax_inserted_at   = src.dmax_inserted_at,
  dmax_inserted_by   = src.dmax_inserted_by
WHEN NOT MATCHED THEN INSERT (
  member_sid, provider_sid, plan_sid, month_ending_date, claim_type,
  provider_specialty, network_tier, claim_count, service_count,
  billed_amount, allowed_amount, paid_amount, adjustment_amount, net_paid,
  dmax_inserted_at, dmax_inserted_by
) VALUES (
  src.member_sid, src.provider_sid, src.plan_sid, src.month_ending_date, src.claim_type,
  src.provider_specialty, src.network_tier, src.claim_count, src.service_count,
  src.billed_amount, src.allowed_amount, src.paid_amount, src.adjustment_amount, src.net_paid,
  src.dmax_inserted_at, src.dmax_inserted_by
);
