from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import duckdb
import os
import re
import traceback
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = FastAPI(title="Data Intelligence Agent Platform")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


class QuestionRequest(BaseModel):
    question: str


def clean_sql(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```sql\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/top-campaigns")
def top_campaigns():
    conn = duckdb.connect("analytics.duckdb", read_only=True)
    try:
        rows = conn.execute("""
            SELECT platform, campaign_name, revenue
            FROM campaign_metrics
            ORDER BY revenue DESC
            LIMIT 5
        """).fetchall()
        return {"results": rows}
    finally:
        conn.close()


@app.post("/ask-sql")
def ask_sql(req: QuestionRequest):
    schema = """
    Table: campaign_metrics
    Columns:
    date DATE
    platform VARCHAR
    campaign_name VARCHAR
    impressions BIGINT
    clicks BIGINT
    spend DOUBLE
    conversions BIGINT
    revenue DOUBLE
    """

    prompt = f"""
Write a DuckDB SQL query using only this schema.

Schema:
{schema}

Question:
{req.question}

Return only SQL. No markdown fences. No explanation.
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        raw_sql = response.output_text.strip()
        sql = clean_sql(raw_sql)

        print("RAW SQL:", raw_sql)
        print("CLEAN SQL:", sql)

        conn = duckdb.connect("analytics.duckdb", read_only=True)
        try:
            df = conn.execute(sql).df()
        finally:
            conn.close()

        return {
            "question": req.question,
            "sql": sql,
            "rows": df.to_dict(orient="records")
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
