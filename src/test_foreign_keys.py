import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "recruitment.db"

conn = sqlite3.connect(DB_PATH)

# Enable foreign key enforcement
conn.execute("PRAGMA foreign_keys = ON;")

# Check whether enforcement is enabled
result = conn.execute("PRAGMA foreign_keys;").fetchone()

print("Foreign keys enabled:", result[0])

try:
    conn.execute("""
        INSERT INTO applications (
            application_id,
            candidate_id,
            job_id,
            applied_at,
            source,
            status
        )
        VALUES (
            9999,
            999,
            999,
            '2026-01-15',
            'LinkedIn',
            'Active'
        );
    """)

    conn.commit()
    print("Application inserted successfully")

except sqlite3.IntegrityError as error:
    print("Insert failed:", error)
    conn.rollback()

finally:
    conn.close()
