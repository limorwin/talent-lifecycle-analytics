
import sqlite3
from pathlib import Path

import os
from dotenv import load_dotenv
from openai import OpenAI

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "recruitment_synthetic.db"


def get_database_schema():
    """Return the structure of the recruitment database."""

    with sqlite3.connect(DB_PATH) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()

        schema = {}

        for (table_name,) in tables:
            columns = conn.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()

            schema[table_name] = [
                {"name": column[1], "type": column[2]}
                for column in columns
            ]

    return schema




def execute_read_only_query(query):
    """Execute a read-only SQL query with safety limits."""

    import pandas as pd
    import time

    query = query.strip()

    # Allow only a single SELECT statement
    if not query.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")

    # Reject multiple statements
    if ";" in query.rstrip(";"):
        raise ValueError("Multiple SQL statements are not allowed.")

    start_time = time.monotonic()

    def check_timeout():
        return int(time.monotonic() - start_time > 5)

    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
        conn.execute("PRAGMA query_only = ON")
        conn.set_progress_handler(check_timeout, 1000)

        # Prevent access to database internals
        def authorize(action, arg1, arg2, db_name, trigger):
            allowed = {
                sqlite3.SQLITE_SELECT,
                sqlite3.SQLITE_READ,
                sqlite3.SQLITE_FUNCTION,
            }
            if action not in allowed:
                return sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_READ and arg1 not in {
                "candidates", "jobs", "applications", "stage_events"
            }:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        conn.set_authorizer(authorize)

        result = pd.read_sql_query(
            f"SELECT * FROM ({query.rstrip(';')}) LIMIT 100",
            conn
        )

    return result



def generate_sql(question):
    """Convert a natural-language question into SQL."""

    load_dotenv(PROJECT_ROOT / ".env")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    schema = get_database_schema()

    schema_text = "\n".join(
        f"{table}: " + ", ".join(
            column["name"] for column in columns
        )
        for table, columns in schema.items()
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        max_output_tokens=300,
        instructions=(
            "You are an expert recruitment analytics SQL assistant. "
            "Generate exactly one SQLite SELECT query that answers the question. "
            "Return only SQL, without Markdown or explanations.\n\n"

            f"Database schema:\n{schema_text}\n\n"

            "TABLE RELATIONSHIPS:\n"
            "- applications.job_id = jobs.job_id\n"
            "- applications.candidate_id = candidates.candidate_id\n"
            "- stage_events.application_id = applications.application_id\n\n"

            "BUSINESS DEFINITIONS:\n"
            "- An application is one row in applications.\n"
            "- Recruitment sources are stored in applications.source.\n"
            "- Departments are stored in jobs.department.\n"
            "- A hire is an application with a stage_events record "
            "where stage = 'Hired'.\n"
            "- Do NOT use applications.status to identify hires.\n"
            "- Hiring rate (%) = 100 * distinct hired applications / "
            "total applications for the group.\n"
            "- Count DISTINCT application_id when joining stage_events "
            "to avoid duplicate applications.\n"
            "- Funnel stages are Applied, Screening, Interview, Offer, Hired.\n"
            "- Applied is counted from applications; subsequent stages "
            "are identified using stage_events.stage.\n"
            "- Time to hire is the number of days between "
            "applications.applied_at and the Hired stage entered_at.\n\n"

            "SQL RULES:\n"
            "- Use only the provided tables and columns.\n"
            "- Use LEFT JOIN when calculating hiring rates so "
            "applications without hires remain in the denominator.\n"
            "- Use NULLIF to avoid division by zero.\n"
            "- Use SQLite-compatible syntax.\n"
            "- Return only the columns necessary to answer the question.\n"
        ),
        input=question,
    )

    return response.output_text.strip()


def explain_results(question, result):
    """Generate a concise explanation grounded in SQL results."""

    load_dotenv(PROJECT_ROOT / ".env")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if result.empty:
        return "No matching records were found."

    response = client.responses.create(
        model="gpt-4.1-mini",
        max_output_tokens=150,
        instructions=(
            "You are a recruitment analytics assistant. "
            "Answer the user's question using ONLY the SQL results provided. "
            "Write one or two concise, natural sentences. "
            "Always include relevant numeric values and units when present, "
            "such as hiring rates (%), days, or application counts. "
            "If the result includes a category and a metric, mention BOTH. "
            "For example: 'Other has the highest hiring rate at 5.13%.' "
            "Do not invent values, comparisons, or explanations. "
            "If the results are insufficient, say so. "
            "Do not include Markdown tables."
        ),
        input=(
            f"Question: {question}\n\n"
            f"SQL results:\n{result.to_json(orient='records')}"
        ),
    )

    return response.output_text.strip()


if __name__ == "__main__":
    schema = get_database_schema()

    for table, columns in schema.items():
        print(f"\n{table}")
        for column in columns:
            print(f"  {column['name']}: {column['type']}")

    # Test SQL execution once, after printing the schema
    print("\nTesting SQL execution:")

    result = execute_read_only_query("""
        SELECT source, COUNT(*) AS applications
        FROM applications
        GROUP BY source
        ORDER BY applications DESC
    """)

    print(result)

    print("\nTesting SQL security:")

    unsafe_queries = [
        "DELETE FROM applications",
        "SELECT * FROM sqlite_master",
        "SELECT * FROM applications; DROP TABLE applications",
    ]

    for query in unsafe_queries:
        try:
            execute_read_only_query(query)
            print(f"FAIL: Query was allowed: {query}")
        except Exception as error:
            print(f"PASS: Query blocked ({type(error).__name__})")
