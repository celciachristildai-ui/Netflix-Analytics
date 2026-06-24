"""
run_all_queries.py
===================
Executes every query in sql/02_queries.sql against data/netflix.db and
writes the results to reports/query_results.md. This is how every query
in the SQL library was validated — if a query has a bug, this script
will surface the sqlite3 error with the query number attached.
"""
import re
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "netflix.db"
SQL_PATH = ROOT / "sql" / "02_queries.sql"
OUT_PATH = ROOT / "reports" / "query_results.md"


def split_queries(sql_text: str):
    """Split the file into (label, comment, query) chunks based on the
    '-- Qn:' markers used throughout 02_queries.sql."""
    pattern = re.compile(r"-- (Q\d+): (.*)")
    chunks = []
    current_label, current_comment, current_sql = None, None, []
    for line in sql_text.splitlines():
        m = pattern.match(line.strip())
        if m:
            if current_label:
                chunks.append((current_label, current_comment, "\n".join(current_sql).strip()))
            current_label, current_comment = m.group(1), m.group(2)
            current_sql = []
        elif current_label and not line.strip().startswith("--"):
            current_sql.append(line)
    if current_label:
        chunks.append((current_label, current_comment, "\n".join(current_sql).strip()))
    return chunks


def main():
    sql_text = SQL_PATH.read_text()
    queries = split_queries(sql_text)
    conn = sqlite3.connect(DB_PATH)

    lines = ["# Netflix Analytics — SQL Query Results\n",
             f"Executed {len(queries)} queries from `sql/02_queries.sql` against `data/netflix.db`.\n"]

    n_ok, n_fail = 0, 0
    for label, comment, query in queries:
        lines.append(f"\n## {label}: {comment}\n")
        lines.append(f"```sql\n{query.strip()}\n```\n")
        try:
            df = pd.read_sql_query(query, conn)
            lines.append(f"**Rows returned:** {len(df)}\n")
            lines.append(df.head(10).to_markdown(index=False))
            n_ok += 1
        except Exception as e:
            lines.append(f"**ERROR:** {e}")
            n_fail += 1
        lines.append("\n")

    OUT_PATH.write_text("\n".join(lines))
    conn.close()
    print(f"Executed {len(queries)} queries: {n_ok} succeeded, {n_fail} failed.")
    print(f"Full results written to {OUT_PATH}")


if __name__ == "__main__":
    main()
