
-- models/fact_claims_monthly.sql
-- Grain: (member_sid, provider_sid, plan_sid, month_ending_date, claim_type)

CREATE TABLE IF NOT EXISTS {sales_schema}.claims_medical_monthly_fact (
  member_sid BIGINT NOT NULL,
  provider_sid BIGINT NOT NULL,
  plan_sid BIGINT NOT NULL,
  month_ending_date DATE NOT NULL,
  claim_type STRING NOT NULL,
  provider_specialty STRING,
  network_tier STRING,
  claim_count DECIMAL(18,2) DEFAULT 0,
  service_count DECIMAL(18,2) DEFAULT 0,
  billed_amount DECIMAL(18,2) DEFAULT 0,
  allowed_amount DECIMAL(18,2) DEFAULT 0,
  paid_amount DECIMAL(18,2) DEFAULT 0,
  adjustment_amount DECIMAL(18,2) DEFAULT 0,
  net_paid DECIMAL(18,2) DEFAULT 0,
  dmax_inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  dmax_inserted_by STRING DEFAULT CURRENT_USER
);

-- Optional clustering / Z-ORDER guidance (platform specific)
-- Snowflake: CLUSTER BY (month_ending_date, provider_sid);
-- Databricks Delta: OPTIMIZE ... ZORDER BY (member_sid, provider_sid, plan_sid);
