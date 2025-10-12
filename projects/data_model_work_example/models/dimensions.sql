
-- models/dimensions.sql
-- Minimal dimensions referenced by the fact

CREATE TABLE IF NOT EXISTS {dim_schema}.member (
  member_sid BIGINT PRIMARY KEY,
  member_natural_key STRING,
  dob DATE,
  gender STRING,
  is_current BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS {dim_schema}.provider (
  provider_sid BIGINT PRIMARY KEY,
  provider_natural_key STRING,
  provider_specialty STRING,
  network_tier STRING,
  is_current BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS {dim_schema}.plan (
  plan_sid BIGINT PRIMARY KEY,
  plan_code STRING,
  plan_name STRING,
  is_current BOOLEAN DEFAULT TRUE
);

-- calendar dimension is assumed existing as {common_schema}.calendar(calendar_date DATE PRIMARY KEY)
