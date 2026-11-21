import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "recruitment.db"

JOBS_SQL = PROJECT_ROOT / "sql" / "insert_jobs.sql"
APPLICATIONS_SQL = PROJECT_ROOT / "sql" / "insert_applications.sql"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")

try:
    conn.executescript(JOBS_SQL.read_text(encoding="utf-8"))
    conn.executescript(APPLICATIONS_SQL.read_text(encoding="utf-8"))
    print("Jobs and applications inserted successfully!")

except sqlite3.IntegrityError as error:
    print("Insert failed:", error)

finally:
    conn.close()