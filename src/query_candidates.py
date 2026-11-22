import sqlite3
from pathlib import Path
import pandas as pd

# Define project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DB_PATH = PROJECT_ROOT / "data" / "processed" / "recruitment.db"

SQL_PATH = (
    PROJECT_ROOT
    / "sql"
    / "analytics"
    / "average_stage_durations.sql"
)

# Read the SQL query from a file
query = SQL_PATH.read_text(encoding="utf-8")

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# Execute SQL and load results into pandas
df = pd.read_sql_query(query, conn)

# Display results
print(df)

# Close database connection
conn.close()