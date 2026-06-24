"""
data_loader.py
===============
Cached data-loading layer for the Streamlit dashboard. Reuses the exact
same cleaning pipeline as the notebooks (src/data_cleaning.py) so the
dashboard and the analysis notebooks never disagree on numbers.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.data_cleaning import run_pipeline


@st.cache_data(show_spinner="Loading and cleaning Netflix catalog...")
def load_data():
    df, exploded = run_pipeline()
    season_map = {12: "Winter", 1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring", 5: "Spring",
                  6: "Summer", 7: "Summer", 8: "Summer", 9: "Fall", 10: "Fall", 11: "Fall"}
    df["season_added"] = df["month_added"].map(season_map)
    return df, exploded


@st.cache_resource(show_spinner="Building recommendation engine...")
def build_recommender(df: pd.DataFrame):
    """TF-IDF content-based recommender — same approach as
    notebooks/04_machine_learning.ipynb, cached as a resource since the
    fitted matrix is reused across every dashboard interaction."""
    combined = (df["listed_in"].fillna("") + " " + df["description"].fillna(""))
    tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
    matrix = tfidf.fit_transform(combined)
    title_to_idx = pd.Series(df.index, index=df["title"]).drop_duplicates()
    return matrix, title_to_idx


def get_similar_titles(df, matrix, title_to_idx, title, n=6):
    if title not in title_to_idx:
        return pd.DataFrame()
    idx = title_to_idx[title]
    sims = cosine_similarity(matrix[idx], matrix).flatten()
    similar_idx = sims.argsort()[::-1][1:n + 1]
    out = df.iloc[similar_idx][["title", "type", "listed_in", "release_year", "rating"]].copy()
    out["similarity"] = sims[similar_idx].round(3)
    return out


def apply_global_filters(df, exploded, year_range, countries, genres, ratings, content_type):
    """Apply the sidebar's global filters and return the filtered fact
    table plus the matching show_id set used to filter bridge tables."""
    f = df[(df["release_year"] >= year_range[0]) & (df["release_year"] <= year_range[1])]

    if content_type != "All":
        f = f[f["type"] == content_type]

    if countries:
        valid_ids = exploded["country"][exploded["country"]["country_name"].isin(countries)]["show_id"]
        f = f[f["show_id"].isin(valid_ids)]

    if genres:
        valid_ids = exploded["genre"][exploded["genre"]["genre_name"].isin(genres)]["show_id"]
        f = f[f["show_id"].isin(valid_ids)]

    if ratings:
        f = f[f["rating"].isin(ratings)]

    show_ids = set(f["show_id"])
    f_exploded = {name: tbl[tbl["show_id"].isin(show_ids)] for name, tbl in exploded.items()}
    return f, f_exploded
