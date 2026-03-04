import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])

query = """
SELECT
  f.*,
  c.churn_30d,
  r.revenue_90d
FROM account_day_features f
JOIN labels_churn_30d c
  ON f.account_id = c.account_id AND f.event_date = c.event_date
JOIN labels_revenue_90d r
  ON f.account_id = r.account_id AND f.event_date = r.event_date
"""
df = pd.read_sql(query, engine)

os.makedirs("data", exist_ok=True)
df.to_parquet("data/training_dataset.parquet", index=False)
print("Exported rows:", len(df))
print("Churn rate:", df["churn_30d"].mean())
