-- =====================================================================
-- 01_schema.sql
-- Netflix Analytics — Relational Schema
-- =====================================================================
-- NOTE ON EXECUTION: src/db_utils.py builds this exact schema
-- programmatically via pandas.to_sql() so that the Python pipeline and
-- the SQL layer never drift out of sync. This file is the canonical,
-- human-readable DDL reference — run it directly if you are loading the
-- cleaned CSVs into Postgres / MySQL / SQL Server instead of SQLite.
--
-- Dialect notes:
--   * SQLite has no native BOOLEAN/DATE types (stored as INTEGER/TEXT) —
--     swap DATE_ADDED_PARSED to a real DATE type on Postgres/SQL Server.
--   * AUTOINCREMENT is SQLite syntax; use SERIAL (Postgres) or
--     IDENTITY(1,1) (SQL Server) on other engines.
-- =====================================================================

DROP TABLE IF EXISTS titles;
CREATE TABLE titles (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    show_id             TEXT NOT NULL UNIQUE,       -- natural key from source (s1, s2, ...)
    type                TEXT NOT NULL,              -- 'Movie' | 'TV Show'
    title               TEXT NOT NULL,
    director            TEXT,                       -- raw comma-separated; see bridge_director
    cast                TEXT,                       -- raw comma-separated; see bridge_cast
    country             TEXT,                       -- raw comma-separated; see bridge_country
    date_added          TEXT,                       -- original free-text date string
    date_added_parsed   TEXT,                       -- ISO-8601 parsed date (TEXT in SQLite)
    date_added_missing  INTEGER,                     -- 1 if date_added could not be parsed
    year_added          INTEGER,
    month_added         INTEGER,
    month_name_added    TEXT,
    quarter_added       INTEGER,
    day_of_week_added   TEXT,
    release_year        INTEGER NOT NULL,
    rating              TEXT,
    maturity_level      TEXT,                       -- Kids/Family/Teens/Adults/Unrated bucket
    duration            TEXT,                       -- raw string, e.g. "90 min" / "3 Seasons"
    duration_minutes    REAL,                        -- populated only for type = 'Movie'
    duration_seasons    REAL,                        -- populated only for type = 'TV Show'
    listed_in           TEXT,                       -- raw comma-separated genres; see bridge_genre
    primary_genre       TEXT,                       -- first listed genre (single-attribution)
    primary_country     TEXT,                       -- first listed country (single-attribution)
    num_countries        INTEGER,
    description         TEXT
);

-- ---------------------------------------------------------------------
-- Bridge (junction) tables — one row per (show_id, value) pair.
-- These normalize the comma-separated multi-valued columns above so we
-- can JOIN and GROUP BY country / genre / cast / director correctly,
-- instead of relying on fragile LIKE '%X%' string matching.
-- ---------------------------------------------------------------------

DROP TABLE IF EXISTS bridge_country;
CREATE TABLE bridge_country (
    show_id      TEXT NOT NULL REFERENCES titles(show_id),
    country_name TEXT NOT NULL
);

DROP TABLE IF EXISTS bridge_genre;
CREATE TABLE bridge_genre (
    show_id    TEXT NOT NULL REFERENCES titles(show_id),
    genre_name TEXT NOT NULL
);

DROP TABLE IF EXISTS bridge_cast;
CREATE TABLE bridge_cast (
    show_id   TEXT NOT NULL REFERENCES titles(show_id),
    cast_name TEXT NOT NULL
);

DROP TABLE IF EXISTS bridge_director;
CREATE TABLE bridge_director (
    show_id       TEXT NOT NULL REFERENCES titles(show_id),
    director_name TEXT NOT NULL
);

CREATE INDEX idx_titles_show_id   ON titles(show_id);
CREATE INDEX idx_bc_show_id       ON bridge_country(show_id);
CREATE INDEX idx_bg_show_id       ON bridge_genre(show_id);
CREATE INDEX idx_bcast_show_id    ON bridge_cast(show_id);
CREATE INDEX idx_bd_show_id       ON bridge_director(show_id);
CREATE INDEX idx_bc_country       ON bridge_country(country_name);
CREATE INDEX idx_bg_genre         ON bridge_genre(genre_name);
