import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DB_PATH = PROJECT_ROOT / "data" / "processed" / "recruitment.db"
SQL_PATH = PROJECT_ROOT / "sql" / "insert_stage_events.sql"

# Read the SQL file
insert_sql = SQL_PATH.read_text(encoding="utf-8")

# Connect to the database
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")

# Execute the INSERT statements
conn.executescript(insert_sql)

# Save changes
conn.commit()

# Close connection
conn.close()

print("Stage events inserted successfully!")