import sqlite3
from pathlib import Path

# Find the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define the database location
DB_PATH = PROJECT_ROOT / "data" / "processed" / "recruitment.db"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"

# Read our SQL file
schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

# Connect to the database
conn = sqlite3.connect(DB_PATH)

# Enable foreign key enforcement
conn.execute("PRAGMA foreign_keys = ON;")

# Execute the SQL statements
conn.executescript(schema_sql)

# Close the connection
conn.close()

print("Database schema initialized successfully!")
