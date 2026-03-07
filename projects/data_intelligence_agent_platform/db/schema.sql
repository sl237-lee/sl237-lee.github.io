CREATE TABLE IF NOT EXISTS campaign_metrics (
    date DATE,
    platform VARCHAR,
    campaign_name VARCHAR,
    impressions BIGINT,
    clicks BIGINT,
    spend DOUBLE,
    conversions BIGINT,
    revenue DOUBLE
);
