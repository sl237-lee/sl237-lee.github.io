import duckdb

conn = duckdb.connect("analytics.duckdb")
with open("db/schema.sql", "r") as f:
    conn.execute(f.read())
with open("db/seed.sql", "r") as f:
    conn.execute(f.read())
print("DuckDB initialized: analytics.duckdb")
