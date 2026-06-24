"""
data_cleaning.py
=================
Production-grade cleaning pipeline for the Netflix Titles dataset.

This module is imported by every notebook, the SQL loader, and the
Streamlit dashboard so that there is exactly ONE source of truth for how
raw data becomes analysis-ready data (no copy-pasted cleaning logic).

Pipeline steps
--------------
1. load_raw()                  -> read the raw CSV
2. standardize_columns()       -> lowercase/trim headers
3. handle_missing_values()     -> documented, defensible fill strategy
4. remove_duplicates()         -> exact + fuzzy (title+type+country+year) dupes
5. standardize_dates()         -> parse date_added into real datetime
6. clean_text_fields()         -> trim/normalize text columns
7. parse_duration()            -> split into duration_minutes / duration_seasons
8. standardize_categories()    -> fix inconsistent rating / country labels
9. explode_helper tables       -> long-format country / genre / cast / director
   tables used for groupby-heavy analysis (these mirror what the SQL
   bridge tables do, see sql/01_schema.sql)

Run as a script to produce data/netflix_titles_clean.csv plus the four
exploded helper CSVs in one shot:

    python src/data_cleaning.py
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path

RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "netflix_titles_raw.csv"
CLEAN_PATH = Path(__file__).resolve().parent.parent / "data" / "netflix_titles_clean.csv"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# A small, defensible set of category fixes discovered during EDA.
# Real-world ratings systems mix US movie ratings (PG-13, R) with US TV
# ratings (TV-MA, TV-14) and a few legacy/inconsistent labels (NR, UR =
# "Not/Unrated"). We standardize the labels but do NOT collapse
# movie-rating buckets into TV-rating buckets - that's a business decision
# documented in the README, not silently hidden in code.
RATING_FIXES = {
    "UR": "NR",       # UR ("Unrated") and NR ("Not Rated") are the same concept
    "NR": "NR",
}

MATURITY_BUCKET = {
    "G": "Kids", "TV-Y": "Kids", "TV-Y7": "Kids", "TV-Y7-FV": "Kids", "TV-G": "Kids",
    "PG": "Family", "TV-PG": "Family",
    "PG-13": "Teens", "TV-14": "Teens",
    "R": "Adults", "TV-MA": "Adults", "NC-17": "Adults",
    "NR": "Unrated",
}


def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    """Load the raw Netflix Titles CSV exactly as downloaded."""
    df = pd.read_csv(path)
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase column names and strip whitespace (defensive - source is
    already clean, but this protects against future re-exports)."""
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def clean_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Trim stray whitespace and normalize casing-sensitive join keys.

    We intentionally keep `title` and `description` in their original
    casing (display fields) but trim whitespace that breaks GROUP BY /
    JOIN logic in the country, genre, cast and director columns.
    """
    df = df.copy()
    text_cols = ["title", "director", "cast", "country", "rating", "listed_in", "description", "type"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
            # collapse "Country1 ,  Country2" -> "Country1, Country2"
            df[col] = df[col].str.replace(r"\s*,\s*", ", ", regex=True)
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Documented missing-value strategy (no silent imputation of facts):

    - director / cast / country -> 'Unknown' (categorical placeholder;
      these are genuinely unrecorded, not numerically interpolable)
    - date_added                -> left as NaT, EXCLUDED from any
      time-trend analysis that uses it (flagged via `date_added_missing`)
    - rating                    -> 'Not Rated' (8 rows industry-wide; a
      title without a rating is functionally "unrated")
    """
    df = df.copy()
    df["director"] = df["director"].fillna("Unknown")
    df["cast"] = df["cast"].fillna("Unknown")
    df["country"] = df["country"].fillna("Unknown")
    df["rating"] = df["rating"].fillna("Not Rated")
    df["date_added_missing"] = df["date_added"].isna()
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows, then fuzzy duplicates defined as the
    same (title, type, release_year) appearing more than once - a strong
    signal of a re-listed catalog entry rather than a genuinely distinct
    title."""
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["title", "type", "release_year"], keep="first")
    after = len(df)
    df.attrs["duplicates_removed"] = before - after
    return df


def standardize_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse `date_added` (free-text "August 14, 2020") into a real
    datetime, and derive year/month/day-of-week/quarter helper columns
    used throughout the EDA and SQL date-function exercises."""
    df = df.copy()
    df["date_added"] = df["date_added"].astype("string").str.strip()
    df["date_added_parsed"] = pd.to_datetime(df["date_added"], format="%B %d, %Y", errors="coerce")
    df["year_added"] = df["date_added_parsed"].dt.year
    df["month_added"] = df["date_added_parsed"].dt.month
    df["month_name_added"] = df["date_added_parsed"].dt.month_name()
    df["quarter_added"] = df["date_added_parsed"].dt.quarter
    df["day_of_week_added"] = df["date_added_parsed"].dt.day_name()
    return df


def parse_duration(df: pd.DataFrame) -> pd.DataFrame:
    """Movies report duration in minutes; TV Shows report duration in
    seasons. These are NOT comparable on one axis, so we split them into
    two explicit numeric columns rather than coercing into a single
    misleading number."""
    df = df.copy()
    duration_num = df["duration"].astype("string").str.extract(r"(\d+)").astype(float)[0]
    df["duration_minutes"] = np.where(df["type"] == "Movie", duration_num, np.nan)
    df["duration_seasons"] = np.where(df["type"] == "TV Show", duration_num, np.nan)
    return df


def standardize_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Fix inconsistent rating labels and derive a maturity-level bucket
    that is meaningful across BOTH movies and TV shows for cross-content
    comparisons (a common exec-dashboard ask: 'how much of our catalog is
    kid-safe?')."""
    df = df.copy()
    df["rating"] = df["rating"].replace(RATING_FIXES)
    df["maturity_level"] = df["rating"].map(MATURITY_BUCKET).fillna("Unrated")
    # primary_country = first listed country, used for single-attribution
    # analyses (e.g. choropleth maps) where a title can't be split across N countries
    df["primary_country"] = df["country"].str.split(",").str[0].str.strip()
    df["primary_genre"] = df["listed_in"].str.split(",").str[0].str.strip()
    df["num_countries"] = df["country"].apply(
        lambda x: 0 if x == "Unknown" else len(str(x).split(","))
    )
    return df


def build_exploded_tables(df: pd.DataFrame) -> dict:
    """Create long-format ('exploded') helper tables for multi-valued
    columns (country, genre, cast, director). These power any analysis
    that needs one-row-per-country or one-row-per-genre, e.g. "which
    country produces the most content" - a title listed in 3 countries
    should count toward all 3, not just the first.
    """
    tables = {}

    def explode_col(df, col, new_name):
        tmp = df[["show_id", col]].copy()
        tmp = tmp[tmp[col] != "Unknown"]
        tmp[col] = tmp[col].str.split(",")
        tmp = tmp.explode(col)
        tmp[new_name] = tmp[col].str.strip()
        return tmp[["show_id", new_name]].dropna()

    tables["country"] = explode_col(df, "country", "country_name")
    tables["genre"] = explode_col(df, "listed_in", "genre_name")
    tables["cast"] = explode_col(df, "cast", "cast_name")
    tables["director"] = explode_col(df, "director", "director_name")
    return tables


def run_pipeline(raw_path: Path = RAW_PATH) -> tuple[pd.DataFrame, dict]:
    """Execute the full cleaning pipeline end-to-end and return the
    cleaned dataframe plus the dict of exploded helper tables."""
    df = load_raw(raw_path)
    n_raw = len(df)

    df = standardize_columns(df)
    df = clean_text_fields(df)
    df = handle_missing_values(df)
    df = remove_duplicates(df)
    df = standardize_dates(df)
    df = parse_duration(df)
    df = standardize_categories(df)

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)  # clean surrogate key for SQL primary key

    exploded = build_exploded_tables(df)

    print(f"[cleaning] raw rows: {n_raw}  ->  clean rows: {len(df)}  "
          f"(duplicates removed: {df.attrs.get('duplicates_removed', 0)})")
    return df, exploded


if __name__ == "__main__":
    clean_df, exploded_tables = run_pipeline()
    clean_df.to_csv(CLEAN_PATH, index=False)
    for name, tbl in exploded_tables.items():
        tbl.to_csv(DATA_DIR / f"bridge_{name}.csv", index=False)
    print(f"Saved cleaned dataset -> {CLEAN_PATH}")
    print(f"Saved bridge tables -> {DATA_DIR}/bridge_*.csv")
    print("\nMissing values after cleaning:")
    print(clean_df.isnull().sum()[clean_df.isnull().sum() > 0])
