# %% [markdown]
# # Netflix Titles — Data Collection & Cleaning (Phases 1-2)
#
# This notebook documents and demonstrates the cleaning pipeline that lives
# in `src/data_cleaning.py` (the single source of truth used by every other
# notebook, the SQL loader, and the dashboard). Running this notebook shows
# you exactly what changes between raw and clean data, with before/after
# evidence at every step.

# %%
import sys
sys.path.append("..")
import pandas as pd
from src.data_cleaning import (
    load_raw, standardize_columns, clean_text_fields, handle_missing_values,
    remove_duplicates, standardize_dates, parse_duration, standardize_categories,
    build_exploded_tables, RAW_PATH
)

pd.set_option("display.max_columns", 30)

# %% [markdown]
# ## Phase 1 — Data Collection
# Source: Netflix Titles dataset (Shivam Bansal / Kaggle, mirrored via the
# `rfordatascience/tidytuesday` GitHub repository for reproducible access).
# 7,787 raw rows, 12 source columns.

# %%
raw = load_raw(RAW_PATH)
print("Shape:", raw.shape)
raw.head(3)

# %%
raw.info()

# %% [markdown]
# ## Phase 2 — Data Cleaning
# ### Step 1: Handle missing values

# %%
print("Missing values BEFORE cleaning:")
print(raw.isnull().sum()[raw.isnull().sum() > 0])

df = standardize_columns(raw)
df = clean_text_fields(df)
df = handle_missing_values(df)

print("\nMissing values AFTER handle_missing_values():")
print(df.isnull().sum()[df.isnull().sum() > 0])
print("\nStrategy: director/cast/country -> 'Unknown' placeholder (genuinely unrecorded, "
      "not numerically interpolable). rating -> 'Not Rated'. date_added left as NaT and "
      "flagged via date_added_missing, since the original release date is NOT a safe "
      "substitute for 'when it was added to Netflix' in trend analysis.")

# %% [markdown]
# ### Step 2: Remove duplicates

# %%
before = len(df)
df = remove_duplicates(df)
print(f"Rows before dedup: {before}  ->  after: {len(df)}  "
      f"(removed {df.attrs.get('duplicates_removed', 0)} exact/fuzzy duplicates)")

# %% [markdown]
# ### Step 3: Standardize date formats
# Source dates arrive as free text like `"August 14, 2020"`. We parse to a
# real datetime and derive year/month/quarter/day-of-week helper columns so
# every downstream notebook uses identical date logic.

# %%
print("Sample raw date_added values:", df["date_added"].dropna().unique()[:3].tolist())
df = standardize_dates(df)
df[["date_added", "date_added_parsed", "year_added", "month_name_added", "day_of_week_added"]].dropna().head(3)

# %% [markdown]
# ### Step 4: Parse duration into comparable numeric fields
# `duration` mixes two incompatible units — "90 min" for movies and
# "3 Seasons" for TV shows. We split into two explicit columns rather than
# coercing into one misleading number.

# %%
print("Raw duration samples:", df["duration"].unique()[:6].tolist())
df = parse_duration(df)
df[["type", "duration", "duration_minutes", "duration_seasons"]].drop_duplicates(subset=["type"]).head(2)

# %% [markdown]
# ### Step 5: Detect & standardize inconsistent categories
# The `rating` column mixes movie ratings (PG-13, R) with TV ratings
# (TV-MA, TV-14) and legacy synonyms (`UR` vs `NR` both mean "Unrated").

# %%
print("Raw rating values:", sorted(df["rating"].dropna().unique().tolist()))
df = standardize_categories(df)
print("\nDerived maturity_level buckets:", df["maturity_level"].value_counts().to_dict())
print("\nNote: 'UR' was merged into 'NR' (both mean Unrated) — see RATING_FIXES in src/data_cleaning.py.")

# %% [markdown]
# ### Step 6: Build exploded bridge tables
# `country`, `cast`, `director`, and `listed_in` are comma-separated
# multi-valued fields. We explode them into long-format bridge tables so
# SQL JOINs and Pandas groupbys attribute a title to ALL of its countries/
# genres/cast members, not just the first one.

# %%
exploded = build_exploded_tables(df)
for name, tbl in exploded.items():
    print(f"bridge_{name}: {len(tbl)} rows (vs {df.shape[0]} titles — confirms multi-value expansion)")
exploded["country"].head(5)

# %% [markdown]
# ## Final Cleaned Dataset

# %%
print("Final shape:", df.shape)
df.isnull().sum()[df.isnull().sum() > 0]

# %% [markdown]
# Remaining "missing" values above are all expected and correct:
# `duration_minutes` is null for TV Shows (they use `duration_seasons`
# instead) and vice versa, and `date_added*` fields are null for the 10
# titles where Netflix never recorded an add-date — these are excluded from
# time-trend analysis, not silently imputed.
#
# Run `python src/data_cleaning.py` from the project root to regenerate
# `data/netflix_titles_clean.csv` and the four `data/bridge_*.csv` files
# used everywhere else in this project.
