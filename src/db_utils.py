"""
db_utils.py
===========
Loads the cleaned Netflix dataset into a SQLite database with a proper
relational schema. SQLite is used because it requires zero server setup
and ships with Python, but every query in sql/02_queries.sql is written
in portable ANSI-ish SQL that runs on PostgreSQL/MySQL/SQL Server with
only trivial dialect tweaks (documented in sql/README.md).

Schema
------
titles            -- one row per Netflix title (the cleaned fact table)
bridge_country    -- (show_id, country_name)   one-to-many
bridge_genre      -- (show_id, genre_name)      one-to-many
bridge_cast       -- (show_id, cast_name)       one-to-many
bridge_director   -- (show_id, director_name)   one-to-many

The bridge tables exist because `country`, `cast`, `director`, and
`listed_in` (genre) are comma-separated multi-valued fields in the source
data. Storing them as bridge tables is what lets us write real JOINs
instead of fragile LIKE '%Comedy%' string matching.
"""

import sqlite3
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "netflix.db"


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def load_to_sql(db_path: Path = DB_PATH):
    """(Re)build the SQLite database from the cleaned CSVs."""
    titles = pd.read_csv(DATA_DIR / "netflix_titles_clean.csv")
    bridge_country = pd.read_csv(DATA_DIR / "bridge_country.csv")
    bridge_genre = pd.read_csv(DATA_DIR / "bridge_genre.csv")
    bridge_cast = pd.read_csv(DATA_DIR / "bridge_cast.csv")
    bridge_director = pd.read_csv(DATA_DIR / "bridge_director.csv")

    if db_path.exists():
        db_path.unlink()  # clean rebuild every run, keeps schema/script in sync

    conn = get_connection(db_path)

    titles.to_sql("titles", conn, index=False, if_exists="replace")
    bridge_country.to_sql("bridge_country", conn, index=False, if_exists="replace")
    bridge_genre.to_sql("bridge_genre", conn, index=False, if_exists="replace")
    bridge_cast.to_sql("bridge_cast", conn, index=False, if_exists="replace")
    bridge_director.to_sql("bridge_director", conn, index=False, if_exists="replace")

    # Indexes -- bridge tables are queried via show_id constantly
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_titles_show_id ON titles(show_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bc_show_id ON bridge_country(show_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bg_show_id ON bridge_genre(show_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bcast_show_id ON bridge_cast(show_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bd_show_id ON bridge_director(show_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bc_country ON bridge_country(country_name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bg_genre ON bridge_genre(genre_name)")
    conn.commit()

    # Build views (from sql/03_views.sql) so the dashboard and BI tools
    # can query pre-aggregated, business-friendly objects directly.
    views_sql = (Path(__file__).resolve().parent.parent / "sql" / "03_views.sql").read_text()
    cur.executescript(views_sql)
    conn.commit()

    print(f"[db] Loaded {len(titles)} titles, "
          f"{len(bridge_country)} country rows, {len(bridge_genre)} genre rows, "
          f"{len(bridge_cast)} cast rows, {len(bridge_director)} director rows "
          f"into {db_path}")
    conn.close()


def run_query(sql: str, db_path: Path = DB_PATH) -> pd.DataFrame:
    """Convenience helper used by notebooks/dashboard to run a query and
    get a DataFrame back."""
    conn = get_connection(db_path)
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()


if __name__ == "__main__":
    load_to_sql()
