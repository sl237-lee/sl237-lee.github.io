import json
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

DDL = """
CREATE TABLE IF NOT EXISTS raw_events (
  event_time TIMESTAMPTZ NOT NULL,
  account_id TEXT NOT NULL,
  user_id TEXT NULL,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_raw_events_account_time
  ON raw_events(account_id, event_time);

CREATE INDEX IF NOT EXISTS idx_raw_events_type_time
  ON raw_events(event_type, event_time);
"""

INSERT_SQL = """
INSERT INTO raw_events (event_time, account_id, user_id, event_type, payload)
VALUES (:event_time, :account_id, :user_id, :event_type, (:payload)::jsonb);
"""

def main():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL missing. Create .env with DATABASE_URL=...")

    events_path = Path("data/raw/events.jsonl")
    if not events_path.exists():
        raise FileNotFoundError("data/raw/events.jsonl not found. Run ingestion/generate_events.py first.")

    engine = create_engine(db_url, future=True)

    with engine.begin() as conn:
        conn.execute(text(DDL))
        print("Ensured table raw_events exists.")

        batch = []
        inserted = 0
        batch_size = 5000

        with events_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                evt = json.loads(line)

                batch.append(
                    {
                        "event_time": evt["event_time"],
                        "account_id": evt["account_id"],
                        "user_id": evt.get("user_id"),
                        "event_type": evt["event_type"],
                        "payload": json.dumps(evt["payload"]),
                    }
                )

                if len(batch) >= batch_size:
                    conn.execute(text(INSERT_SQL), batch)
                    inserted += len(batch)
                    print(f"Inserted {inserted:,} rows...")
                    batch.clear()

        if batch:
            conn.execute(text(INSERT_SQL), batch)
            inserted += len(batch)
            print(f"Inserted {inserted:,} rows...")

        total = conn.execute(text("SELECT COUNT(*) FROM raw_events;")).scalar_one()
        print(f"Done. raw_events row count = {total:,}")

if __name__ == "__main__":
    main()
