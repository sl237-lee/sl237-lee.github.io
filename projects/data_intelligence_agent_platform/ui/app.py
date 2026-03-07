import streamlit as st
import duckdb
import pandas as pd
import requests

st.set_page_config(page_title="Data Intelligence Agent Platform", layout="wide")

st.title("Data Intelligence Agent Platform")
st.write("AI-powered analytics assistant with SQL generation.")

API_URL = "http://127.0.0.1:8000"

st.subheader("Ask the AI about your data")

question = st.text_input(
    "Example: Which campaign generated the highest revenue?"
)

if st.button("Run AI Query"):
    if question:
        with st.spinner("AI generating SQL..."):
            response = requests.post(
                f"{API_URL}/ask-sql",
                json={"question": question}
            )

        if response.status_code == 200:
            result = response.json()

            st.subheader("Generated SQL")
            st.code(result["sql"], language="sql")

            df_result = pd.DataFrame(result["rows"])

            st.subheader("Query Results")
            st.dataframe(df_result, width="stretch")
        else:
            st.error(f"AI query failed: {response.text}")

st.subheader("Campaign Metrics")

conn = duckdb.connect("analytics.duckdb", read_only=True)
try:
    df = conn.execute("SELECT * FROM campaign_metrics").df()
finally:
    conn.close()

st.dataframe(df, width="stretch")

st.subheader("Revenue by Campaign")
chart_df = df.groupby("campaign_name", as_index=False)["revenue"].sum()
st.bar_chart(chart_df.set_index("campaign_name"))
