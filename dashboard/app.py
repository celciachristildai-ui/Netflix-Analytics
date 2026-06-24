"""
app.py — Netflix Analytics Executive Dashboard
================================================
Run locally:    streamlit run dashboard/app.py
Deploy:         Streamlit Community Cloud (see dashboard/DEPLOYMENT.md)

This is the interactive dashboard layer of the project. Power BI Desktop
isn't available in a headless build environment, so this Streamlit app is
the real, running, clickable deliverable for Phase 6 — every KPI, filter,
chart and drill-through here is backed by the same cleaned SQLite/CSV data
used in the SQL and notebook layers. A page-by-page Power BI rebuild guide
(with DAX measures) lives in dashboard/powerbi_guide.md for anyone who
wants to reproduce this in Power BI Desktop.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from dashboard.data_loader import load_data, build_recommender, get_similar_titles, apply_global_filters

# ----------------------------------------------------------------------
# Page config & theme
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Netflix Analytics | Executive Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

NETFLIX_RED = "#E50914"
NETFLIX_DARK = "#221F1F"
PLOTLY_TEMPLATE = "plotly_dark"
SEQUENTIAL_RED = px.colors.sequential.Reds[::-1]

st.markdown(f"""
<style>
.kpi-card {{
    background: linear-gradient(135deg, {NETFLIX_DARK} 0%, #3a3535 100%);
    border-radius: 12px; padding: 18px 20px; border-left: 5px solid {NETFLIX_RED};
}}
.kpi-value {{ font-size: 30px; font-weight: 800; color: white; margin: 0; }}
.kpi-label {{ font-size: 13px; color: #c9c9c9; text-transform: uppercase; letter-spacing: 0.5px; }}
.kpi-delta {{ font-size: 13px; color: {NETFLIX_RED}; font-weight: 600; }}
h1, h2, h3 {{ color: {NETFLIX_DARK}; }}
[data-testid="stMetricValue"] {{ color: {NETFLIX_RED}; }}
</style>
""", unsafe_allow_html=True)


def kpi_card(label, value, delta=None):
    delta_html = f"<div class='kpi-delta'>{delta}</div>" if delta else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <p class="kpi-value">{value}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Load data
# ----------------------------------------------------------------------
df, exploded = load_data()
matrix, title_to_idx = build_recommender(df)

MIN_YEAR, MAX_YEAR = int(df["release_year"].min()), int(df["release_year"].max())
ALL_COUNTRIES = sorted(exploded["country"]["country_name"].unique())
ALL_GENRES = sorted(exploded["genre"]["genre_name"].unique())
ALL_RATINGS = sorted(df["rating"].dropna().unique())

# ----------------------------------------------------------------------
# Sidebar — navigation + GLOBAL FILTERS (Year, Country, Genre, Rating)
# ----------------------------------------------------------------------
st.sidebar.markdown("## Netflix Analytics")
st.sidebar.caption("Executive Dashboard — Content Strategy & Global Expansion")

PAGES = [
    "Executive Overview",
    "Global Content Map",
    "Genre Analysis",
    "Country Performance",
    "Release Trend Dashboard",
    "Ratings Dashboard",
    "Movie vs TV Dashboard",
    "Title Search & Detail",
    "Director & Actor Rankings",
    "Netflix Expansion Timeline",
    "Executive Summary & Recommendations",
]
page = st.sidebar.radio("Navigate", PAGES, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("### Global Filters")
year_range = st.sidebar.slider("Release Year", MIN_YEAR, MAX_YEAR, (2010, MAX_YEAR))
content_type = st.sidebar.selectbox("Content Type", ["All", "Movie", "TV Show"])
sel_countries = st.sidebar.multiselect("Country", ALL_COUNTRIES, default=[])
sel_genres = st.sidebar.multiselect("Genre", ALL_GENRES, default=[])
sel_ratings = st.sidebar.multiselect("Rating", ALL_RATINGS, default=[])

if st.sidebar.button("↺ Reset Filters"):
    st.rerun()

fdf, fexploded = apply_global_filters(df, exploded, year_range, sel_countries, sel_genres, sel_ratings, content_type)

# Dynamic title / filter summary shown on every page
filter_bits = [f"{year_range[0]}–{year_range[1]}"]
if content_type != "All": filter_bits.append(content_type + "s")
if sel_countries: filter_bits.append(", ".join(sel_countries[:2]) + (f" +{len(sel_countries)-2}" if len(sel_countries) > 2 else ""))
if sel_genres: filter_bits.append(", ".join(sel_genres[:2]) + (f" +{len(sel_genres)-2}" if len(sel_genres) > 2 else ""))
if sel_ratings: filter_bits.append(", ".join(sel_ratings[:2]) + (f" +{len(sel_ratings)-2}" if len(sel_ratings) > 2 else ""))
FILTER_SUMMARY = " · ".join(filter_bits)

st.sidebar.markdown("---")
st.sidebar.caption(f"📊 {len(fdf):,} titles match current filters (of {len(df):,} total)")
st.sidebar.caption("Data: Netflix Titles dataset · Built with Python, SQLite, Streamlit & Plotly")

# ========================================================================
# PAGE 1 — EXECUTIVE OVERVIEW
# ========================================================================
if page == "Executive Overview":
    st.title("Executive Overview")
    st.caption(f"Showing: **{FILTER_SUMMARY}**")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Total Titles", f"{len(fdf):,}")
    with c2: kpi_card("Movies", f"{(fdf['type']=='Movie').sum():,}",
                       f"{100*(fdf['type']=='Movie').mean():.0f}% of catalog")
    with c3: kpi_card("TV Shows", f"{(fdf['type']=='TV Show').sum():,}",
                       f"{100*(fdf['type']=='TV Show').mean():.0f}% of catalog")
    with c4: kpi_card("Countries Represented", f"{fexploded['country']['country_name'].nunique():,}")
    with c5: kpi_card("Distinct Genres", f"{fexploded['genre']['genre_name'].nunique():,}")

    st.markdown("###")
    col1, col2 = st.columns([1.3, 1])

    with col1:
        yearly = fdf.groupby(["release_year", "type"]).size().reset_index(name="count")
        fig = px.area(yearly, x="release_year", y="count", color="type",
                       title="Content Output by Release Year",
                       color_discrete_map={"Movie": NETFLIX_RED, "TV Show": "#564d4d"},
                       template=PLOTLY_TEMPLATE)
        fig.update_traces(hovertemplate="Year %{x}<br>%{y} titles<extra>%{fullData.name}</extra>")
        st.plotly_chart(fig, width='stretch')

    with col2:
        type_counts = fdf["type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig = px.pie(type_counts, names="type", values="count", hole=0.55,
                      title="Movie vs TV Show Split",
                      color="type", color_discrete_map={"Movie": NETFLIX_RED, "TV Show": NETFLIX_DARK},
                      template=PLOTLY_TEMPLATE)
        fig.update_traces(textinfo="percent+label", hovertemplate="%{label}: %{value} titles<extra></extra>")
        st.plotly_chart(fig, width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        top_c = fexploded["country"]["country_name"].value_counts().head(10).reset_index()
        top_c.columns = ["country", "count"]
        fig = px.bar(top_c, x="count", y="country", orientation="h",
                      title="Top 10 Countries by Title Count", template=PLOTLY_TEMPLATE,
                      color="count", color_continuous_scale="Reds")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        fig.update_traces(hovertemplate="%{y}: %{x} titles<extra></extra>")
        st.plotly_chart(fig, width='stretch')
    with col4:
        top_g = fexploded["genre"]["genre_name"].value_counts().head(10).reset_index()
        top_g.columns = ["genre", "count"]
        fig = px.bar(top_g, x="count", y="genre", orientation="h",
                      title="Top 10 Genres by Title Count", template=PLOTLY_TEMPLATE,
                      color="count", color_continuous_scale="Reds")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        fig.update_traces(hovertemplate="%{y}: %{x} titles<extra></extra>")
        st.plotly_chart(fig, width='stretch')

# ========================================================================
# PAGE 2 — GLOBAL CONTENT MAP
# ========================================================================
elif page == "Global Content Map":
    st.title("Global Content Map")
    st.caption(f"Showing: **{FILTER_SUMMARY}** — hover any country for details")

    country_counts = fexploded["country"]["country_name"].value_counts().reset_index()
    country_counts.columns = ["country", "titles"]

    fig = px.choropleth(
        country_counts, locations="country", locationmode="country names",
        color="titles", color_continuous_scale="Reds", hover_name="country",
        title="Netflix Content Footprint by Country",
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(hovertemplate="<b>%{location}</b><br>%{z} titles<extra></extra>")
    fig.update_geos(bgcolor="rgba(0,0,0,0)", showframe=False)
    fig.update_layout(height=560, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, width='stretch')

    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Top 15 Markets")
        st.dataframe(country_counts.head(15), width='stretch', hide_index=True)
    with c2:
        st.subheader("Emerging Markets")
        st.caption("Countries with a growing but still modest footprint (5-50 titles) — "
                    "candidates for expanded local content investment.")
        emerging = country_counts[(country_counts["titles"] >= 5) & (country_counts["titles"] <= 50)].head(15)
        st.dataframe(emerging, width='stretch', hide_index=True)

# ========================================================================
# PAGE 3 — GENRE ANALYSIS
# ========================================================================
elif page == "Genre Analysis":
    st.title("Genre Analysis")
    st.caption(f"Showing: **{FILTER_SUMMARY}**")

    genre_counts = fexploded["genre"]["genre_name"].value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]

    fig = px.treemap(genre_counts.head(25), path=["genre"], values="count",
                      title="Genre Distribution (Treemap)", color="count",
                      color_continuous_scale="Reds", template=PLOTLY_TEMPLATE)
    fig.update_traces(hovertemplate="<b>%{label}</b><br>%{value} titles<extra></extra>")
    st.plotly_chart(fig, width='stretch')

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Fastest-Growing Genres")
        st.caption("Title share growth: 2008-2015 vs 2016-2021 (full catalog, unaffected by sidebar year filter)")
        gy = exploded["genre"].merge(df[["show_id", "release_year"]], on="show_id")
        gy = gy[gy["release_year"].between(2008, 2021)]
        gy["period"] = np.where(gy["release_year"] >= 2016, "2016-2021", "2008-2015")
        pivot = gy.pivot_table(index="genre_name", columns="period", values="show_id", aggfunc="count", fill_value=0)
        pivot["growth_pct"] = ((pivot["2016-2021"] - pivot["2008-2015"]) / pivot["2008-2015"].replace(0, np.nan)) * 100
        top_growth = pivot[pivot["2008-2015"] >= 10].sort_values("growth_pct", ascending=False).head(10).reset_index()
        fig = px.bar(top_growth, x="growth_pct", y="genre_name", orientation="h",
                      template=PLOTLY_TEMPLATE, color="growth_pct", color_continuous_scale="Reds")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False,
                           xaxis_title="Growth %", yaxis_title="")
        fig.update_traces(hovertemplate="%{y}: +%{x:.0f}%<extra></extra>")
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.subheader("Underrepresented Genre Opportunities")
        st.caption("Below-average title count but present across many countries — diversification candidates")
        gc = exploded["genre"].merge(exploded["country"], on="show_id")
        gc = gc[gc["country_name"] != "Unknown"]
        opp = gc.groupby("genre_name").agg(
            total_titles=("show_id", "nunique"),
            countries=("country_name", "nunique")
        ).reset_index()
        avg_titles = opp["total_titles"].mean()
        opp = opp[opp["total_titles"] < avg_titles].sort_values("countries", ascending=False).head(10)
        fig = px.bar(opp, x="countries", y="genre_name", orientation="h",
                      template=PLOTLY_TEMPLATE, color="countries", color_continuous_scale="Reds")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False,
                           xaxis_title="Countries Present In", yaxis_title="")
        st.plotly_chart(fig, width='stretch')

    st.subheader("Average Movie Duration by Genre")
    movie_genre = exploded["genre"].merge(fdf[fdf["type"] == "Movie"][["show_id", "duration_minutes"]], on="show_id")
    avg_dur = movie_genre.groupby("genre_name")["duration_minutes"].mean().sort_values(ascending=False).head(12).reset_index()
    fig = px.bar(avg_dur, x="duration_minutes", y="genre_name", orientation="h",
                  template=PLOTLY_TEMPLATE, color="duration_minutes", color_continuous_scale="Reds")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False,
                       xaxis_title="Avg Duration (min)", yaxis_title="")
    st.plotly_chart(fig, width='stretch')

# ========================================================================
# PAGE 4 — COUNTRY PERFORMANCE (with drill-through)
# ========================================================================
elif page == "Country Performance":
    st.title("Country Performance")
    st.caption(f"Showing: **{FILTER_SUMMARY}** — click a bar below to drill through into that country")

    top_countries = fexploded["country"]["country_name"].value_counts().head(15).reset_index()
    top_countries.columns = ["country", "count"]

    fig = px.bar(top_countries, x="count", y="country", orientation="h",
                  template=PLOTLY_TEMPLATE, color="count", color_continuous_scale="Reds",
                  title="Click a country bar to drill through ↴")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x} titles — click to drill through<extra></extra>")

    event = st.plotly_chart(fig, width='stretch', on_select="rerun", key="country_chart")

    drill_country = None
    if event and event.get("selection") and event["selection"].get("points"):
        drill_country = event["selection"]["points"][0]["y"]

    drill_country = st.selectbox(
        "Or pick a country to drill through:", [""] + top_countries["country"].tolist(),
        index=(top_countries["country"].tolist().index(drill_country) + 1) if drill_country else 0
    ) or drill_country

    if drill_country:
        st.markdown(f"### Drill-through: {drill_country}")
        ids = fexploded["country"][fexploded["country"]["country_name"] == drill_country]["show_id"]
        sub = fdf[fdf["show_id"].isin(ids)]

        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi_card("Total Titles", f"{len(sub):,}")
        with c2: kpi_card("Movies", f"{(sub['type']=='Movie').sum():,}")
        with c3: kpi_card("TV Shows", f"{(sub['type']=='TV Show').sum():,}")
        with c4: kpi_card("Avg Movie Length", f"{sub.loc[sub['type']=='Movie','duration_minutes'].mean():.0f} min"
                           if (sub['type']=='Movie').any() else "N/A")

        cc1, cc2 = st.columns(2)
        with cc1:
            genre_sub = exploded["genre"][exploded["genre"]["show_id"].isin(ids)]
            top_genre_sub = genre_sub["genre_name"].value_counts().head(8).reset_index()
            top_genre_sub.columns = ["genre", "count"]
            fig2 = px.bar(top_genre_sub, x="count", y="genre", orientation="h", template=PLOTLY_TEMPLATE,
                          title=f"Top Genres — {drill_country}", color="count", color_continuous_scale="Reds")
            fig2.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
            st.plotly_chart(fig2, width='stretch')
        with cc2:
            rating_sub = sub["rating"].value_counts().reset_index()
            rating_sub.columns = ["rating", "count"]
            fig3 = px.pie(rating_sub, names="rating", values="count", hole=0.5, template=PLOTLY_TEMPLATE,
                          title=f"Rating Mix — {drill_country}", color_discrete_sequence=px.colors.sequential.Reds_r)
            st.plotly_chart(fig3, width='stretch')

        st.dataframe(sub[["title", "type", "release_year", "rating", "listed_in"]].sort_values("release_year", ascending=False),
                     width='stretch', hide_index=True, height=250)

# ========================================================================
# PAGE 5 — RELEASE TREND DASHBOARD
# ========================================================================
elif page == "Release Trend Dashboard":
    st.title("Release Trend Dashboard")
    st.caption(f"Showing: **{FILTER_SUMMARY}**")

    ts = fdf[fdf["date_added_parsed"].notna()].copy()
    ts["year_month"] = ts["date_added_parsed"].dt.to_period("M").astype(str)
    monthly = ts.groupby("year_month").size().reset_index(name="titles_added")

    fig = px.line(monthly, x="year_month", y="titles_added", template=PLOTLY_TEMPLATE,
                  title="Monthly Titles Added to Netflix", markers=True,
                  color_discrete_sequence=[NETFLIX_RED])
    fig.update_traces(hovertemplate="%{x}: %{y} titles<extra></extra>")
    st.plotly_chart(fig, width='stretch')

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Year-over-Year Growth")
        yoy = fdf.groupby("release_year").size().reset_index(name="titles")
        yoy["yoy_change"] = yoy["titles"].diff()
        yoy["yoy_pct"] = (yoy["titles"].pct_change() * 100).round(1)
        fig = px.bar(yoy, x="release_year", y="yoy_pct", template=PLOTLY_TEMPLATE,
                      color="yoy_pct", color_continuous_scale="RdGy_r",
                      title="YoY % Change in Titles Released")
        fig.update_traces(hovertemplate="Year %{x}: %{y:.1f}% YoY<extra></extra>")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.subheader("Seasonal Release Pattern")
        season_counts = fdf["season_added"].value_counts().reindex(["Winter", "Spring", "Summer", "Fall"]).reset_index()
        season_counts.columns = ["season", "count"]
        fig = px.pie(season_counts, names="season", values="count", hole=0.5, template=PLOTLY_TEMPLATE,
                      title="Releases by Season", color_discrete_sequence=px.colors.sequential.Reds_r)
        st.plotly_chart(fig, width='stretch')

    st.subheader("Day-of-Week Release Pattern")
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = fdf["day_of_week_added"].value_counts().reindex(dow_order).reset_index()
    dow.columns = ["day", "count"]
    fig = px.bar(dow, x="day", y="count", template=PLOTLY_TEMPLATE, color="count",
                  color_continuous_scale="Reds", title="Titles Added by Day of Week")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width='stretch')

# ========================================================================
# PAGE 6 — RATINGS DASHBOARD
# ========================================================================
elif page == "Ratings Dashboard":
    st.title("Ratings Dashboard")
    st.caption(f"Showing: **{FILTER_SUMMARY}**")

    c1, c2, c3 = st.columns(3)
    maturity_counts = fdf["maturity_level"].value_counts()
    with c1: kpi_card("Kid-Safe Titles", f"{maturity_counts.get('Kids',0) + maturity_counts.get('Family',0):,}",
                       f"{100*(maturity_counts.get('Kids',0)+maturity_counts.get('Family',0))/len(fdf):.0f}% of catalog")
    with c2: kpi_card("Mature (Adult) Titles", f"{maturity_counts.get('Adults',0):,}",
                       f"{100*maturity_counts.get('Adults',0)/len(fdf):.0f}% of catalog")
    with c3: kpi_card("Most Common Rating", fdf["rating"].mode()[0] if not fdf.empty else "N/A")

    col1, col2 = st.columns(2)
    with col1:
        rating_counts = fdf["rating"].value_counts().reset_index()
        rating_counts.columns = ["rating", "count"]
        fig = px.bar(rating_counts, x="rating", y="count", template=PLOTLY_TEMPLATE,
                      color="count", color_continuous_scale="Reds", title="Title Count by Rating")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, width='stretch')
    with col2:
        maturity_df = maturity_counts.reset_index()
        maturity_df.columns = ["maturity_level", "count"]
        fig = px.pie(maturity_df, names="maturity_level", values="count", hole=0.5,
                      template=PLOTLY_TEMPLATE, title="Maturity Level Mix",
                      color_discrete_sequence=px.colors.sequential.Reds_r)
        st.plotly_chart(fig, width='stretch')

    st.subheader("Which Rating Dominates Each Country?")
    top5 = fexploded["country"]["country_name"].value_counts().head(8).index.tolist()
    rc = fexploded["country"].merge(fdf[["show_id", "rating"]], on="show_id")
    rc = rc[rc["country_name"].isin(top5)]
    pivot = rc.pivot_table(index="country_name", columns="rating", values="show_id", aggfunc="count", fill_value=0)
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
    fig = px.imshow(pivot_pct.loc[top5], color_continuous_scale="Reds", template=PLOTLY_TEMPLATE,
                     title="Rating Mix (%) — Top 8 Countries", aspect="auto",
                     labels=dict(color="% of catalog"))
    fig.update_traces(hovertemplate="%{y} / %{x}: %{z:.1f}%<extra></extra>")
    st.plotly_chart(fig, width='stretch')

# ========================================================================
# PAGE 7 — MOVIE VS TV DASHBOARD
# ========================================================================
elif page == "Movie vs TV Dashboard":
    st.title("Movie vs TV Dashboard")
    st.caption(f"Showing: **{FILTER_SUMMARY}**")

    c1, c2, c3, c4 = st.columns(4)
    movies = fdf[fdf["type"] == "Movie"]
    shows = fdf[fdf["type"] == "TV Show"]
    with c1: kpi_card("Total Movies", f"{len(movies):,}")
    with c2: kpi_card("Total TV Shows", f"{len(shows):,}")
    with c3: kpi_card("Avg Movie Length", f"{movies['duration_minutes'].mean():.0f} min" if len(movies) else "N/A")
    with c4: kpi_card("Avg Seasons per Show", f"{shows['duration_seasons'].mean():.1f}" if len(shows) else "N/A")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(movies, x="duration_minutes", nbins=40, template=PLOTLY_TEMPLATE,
                           title="Movie Duration Distribution", color_discrete_sequence=[NETFLIX_RED])
        fig.update_layout(xaxis_title="Duration (minutes)")
        st.plotly_chart(fig, width='stretch')
    with col2:
        season_counts = shows["duration_seasons"].value_counts().sort_index().reset_index()
        season_counts.columns = ["seasons", "count"]
        fig = px.bar(season_counts, x="seasons", y="count", template=PLOTLY_TEMPLATE,
                      title="TV Show Season Count Distribution", color_discrete_sequence=[NETFLIX_DARK])
        st.plotly_chart(fig, width='stretch')

    st.subheader("Movie vs TV Production Over Time")
    yearly = fdf.groupby(["release_year", "type"]).size().reset_index(name="count")
    fig = px.line(yearly, x="release_year", y="count", color="type", markers=True,
                  template=PLOTLY_TEMPLATE, color_discrete_map={"Movie": NETFLIX_RED, "TV Show": "#999"})
    st.plotly_chart(fig, width='stretch')

# ========================================================================
# PAGE 8 — TITLE SEARCH & DETAIL
# ========================================================================
elif page == "Title Search & Detail":
    st.title("Search Any Movie or Show")
    st.caption("Full catalog search — ignores sidebar filters so you can always find any title")

    search = st.text_input("Search by title", placeholder="e.g. Stranger Things, Narcos, The Crown...")
    matches = df[df["title"].str.contains(search, case=False, na=False)] if search else pd.DataFrame()

    if search and matches.empty:
        st.warning(f"No titles found matching '{search}'.")
    elif search:
        chosen_title = st.selectbox(f"{len(matches)} match(es) found — select one:", matches["title"].tolist())
        row = df[df["title"] == chosen_title].iloc[0]

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"### {row['title']}")
            st.markdown(f"**Type:** {row['type']}")
            st.markdown(f"**Release Year:** {int(row['release_year'])}")
            st.markdown(f"**Rating:** {row['rating']} ({row['maturity_level']})")
            if row["type"] == "Movie":
                st.markdown(f"**Duration:** {row['duration']}")
            else:
                st.markdown(f"**Seasons:** {row['duration']}")
            st.markdown(f"**Country:** {row['country']}")
            st.markdown(f"**Added to Netflix:** {row['date_added'] if pd.notna(row['date_added']) else 'Unknown'}")
        with c2:
            st.markdown("**Description**")
            st.write(row["description"])
            st.markdown("**Genres**")
            st.write(row["listed_in"])
            st.markdown("**Director**")
            st.write(row["director"])
            st.markdown("**Cast**")
            st.write(row["cast"])

        st.markdown("### Because you watched this, you might like:")
        recs = get_similar_titles(df, matrix, title_to_idx, row["title"], n=6)
        if not recs.empty:
            st.dataframe(recs, width='stretch', hide_index=True)
        else:
            st.info("No similar-title recommendations available for this entry.")
    else:
        st.info("Start typing a title above to search the full Netflix catalog "
                 f"({len(df):,} titles).")
        st.markdown("##### 🎲 Or try one of these popular titles:")
        sample_titles = df.sample(6, random_state=42)["title"].tolist()
        cols = st.columns(3)
        for i, t in enumerate(sample_titles):
            cols[i % 3].button(t, key=f"sample_{i}", disabled=True)

# ========================================================================
# PAGE 9 — DIRECTOR & ACTOR RANKINGS
# ========================================================================
elif page == "Director & Actor Rankings":
    st.title("Director & Actor Rankings")
    st.caption(f"Showing: **{FILTER_SUMMARY}**")

    ids = set(fdf["show_id"])
    directors = exploded["director"][exploded["director"]["show_id"].isin(ids) &
                                       (exploded["director"]["director_name"] != "Unknown")]
    actors = exploded["cast"][exploded["cast"]["show_id"].isin(ids) &
                                (exploded["cast"]["cast_name"] != "Unknown")]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 15 Directors")
        top_dir = directors["director_name"].value_counts().head(15).reset_index()
        top_dir.columns = ["director", "titles"]
        fig = px.bar(top_dir, x="titles", y="director", orientation="h", template=PLOTLY_TEMPLATE,
                      color="titles", color_continuous_scale="Reds")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.subheader("Top 15 Actors")
        top_act = actors["cast_name"].value_counts().head(15).reset_index()
        top_act.columns = ["actor", "titles"]
        fig = px.bar(top_act, x="titles", y="actor", orientation="h", template=PLOTLY_TEMPLATE,
                      color="titles", color_continuous_scale="Reds")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig, width='stretch')

    st.subheader("Director Detail Lookup")
    director_pick = st.selectbox("Choose a director to drill through:", [""] + top_dir["director"].tolist())
    if director_pick:
        d_ids = directors[directors["director_name"] == director_pick]["show_id"]
        d_titles = df[df["show_id"].isin(d_ids)][["title", "type", "release_year", "listed_in", "rating"]]
        st.dataframe(d_titles.sort_values("release_year", ascending=False), width='stretch', hide_index=True)

# ========================================================================
# PAGE 10 — NETFLIX EXPANSION TIMELINE
# ========================================================================
elif page == "Netflix Expansion Timeline":
    st.title("Netflix Global Expansion Timeline")
    st.caption("First-ever title added per country — a proxy for catalog/market entry timing")

    cd = exploded["country"].merge(df[["show_id", "date_added_parsed", "title"]], on="show_id")
    cd = cd[cd["date_added_parsed"].notna() & (cd["country_name"] != "Unknown")]
    first_entry = cd.sort_values("date_added_parsed").groupby("country_name").first().reset_index()
    first_entry = first_entry.sort_values("date_added_parsed")

    fig = px.scatter(
        first_entry, x="date_added_parsed", y="country_name", template=PLOTLY_TEMPLATE,
        title="First Title Added, by Country (catalog entry proxy)",
        hover_data={"title": True, "date_added_parsed": True}, color_discrete_sequence=[NETFLIX_RED],
        height=max(500, len(first_entry) * 14)
    )
    fig.update_traces(marker=dict(size=8, color=NETFLIX_RED),
                       hovertemplate="<b>%{y}</b><br>%{x}<br>First title: %{customdata[0]}<extra></extra>")
    fig.update_layout(yaxis_title="", xaxis_title="Date")
    st.plotly_chart(fig, width='stretch')

    st.dataframe(first_entry[["country_name", "date_added_parsed", "title"]].rename(
        columns={"country_name": "Country", "date_added_parsed": "First Title Added", "title": "First Title"}
    ), width='stretch', hide_index=True, height=300)

# ========================================================================
# PAGE 11 — EXECUTIVE SUMMARY & RECOMMENDATIONS
# ========================================================================
elif page == "Executive Summary & Recommendations":
    st.title("Executive Summary & Business Recommendations")
    st.caption("Phase 7 deliverable — synthesized from every analysis layer in this project")

    top_country = exploded["country"]["country_name"].value_counts()
    top_genre = exploded["genre"]["genre_name"].value_counts()
    movie_pct = (df["type"] == "Movie").mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Catalog Size", f"{len(df):,} titles")
    with c2: kpi_card("Top Market", top_country.index[0], f"{top_country.iloc[0]:,} titles")
    with c3: kpi_card("Top Genre", top_genre.index[0], f"{top_genre.iloc[0]:,} titles")
    with c4: kpi_card("Movie Share", f"{movie_pct:.0f}%")

    st.markdown("## Emerging Markets")
    st.markdown("""
    Countries with a modest-but-present footprint (5-50 titles) such as several
    Southeast Asian, African and Eastern European markets show low representation
    relative to known regional population/internet-penetration trends. These are
    candidates for localized original content investment ahead of competitors.
    """)

    st.markdown("## Underrepresented Genres")
    st.markdown("""
    Niche genres (Anime, Faith & Spirituality, Classic Movies, Cult Movies, Sports)
    show low absolute title counts but consistent presence across markets — a sign
    of durable, if currently under-served, demand. Selective investment here can
    differentiate the catalog from over-saturated genres like Dramas and Comedies.
    """)

    st.markdown("## High-Growth Countries")
    gy = exploded["country"].merge(df[["show_id", "release_year"]], on="show_id")
    gy = gy[gy["release_year"].between(2015, 2021)]
    gy["period"] = np.where(gy["release_year"] >= 2019, "2019-2021", "2015-2018")
    piv = gy.pivot_table(index="country_name", columns="period", values="show_id", aggfunc="count", fill_value=0)
    piv = piv[piv.get("2015-2018", 0) >= 5]
    piv["growth"] = piv.get("2019-2021", 0) - piv.get("2015-2018", 0)
    top_growth_countries = piv.sort_values("growth", ascending=False).head(5)
    st.dataframe(top_growth_countries, width='stretch')

    st.markdown("## Content Diversification Opportunities")
    st.markdown("""
    - Expand non-English originals in high-growth, under-saturated markets (South
      Korea and India show strong existing momentum and high engagement potential).
    - Balance the Movie-heavy catalog (≈69% movies) with continued TV Show
      investment — TV Shows correlate with longer viewer retention industry-wide.
    - Increase family/kids-rated content share in markets currently skewed toward
      mature ratings, to widen addressable household reach.
    """)

    st.markdown("## Recommendations for Future Investment")
    st.markdown("""
    1. **Double down on India and South Korea** — both already show outsized
       genre diversity and growth momentum; incremental investment compounds.
    2. **Pilot underrepresented genres in saturated markets** (e.g. Anime/Sports
       documentaries in the US) to reduce content overlap with competitors.
    3. **Shift content-drop calendar toward Q4 (Fall)** — current seasonal data
       shows it as the most active addition window; consider whether competitor
       activity in the same window dilutes impact, and test off-cycle drops.
    4. **Formalize a "catalog QA" classifier** (see Phase 8 ML notebook) to catch
       mis-tagged Movie/TV Show metadata before it reaches the consumer-facing
       catalog.
    """)

    st.markdown("---")
    st.markdown("###  Export")
    st.info("Run `python reports/generate_pdf_report.py` from the project root to "
            "generate a polished PDF version of this executive summary with embedded "
            "charts (see reports/Netflix_Executive_Report.pdf).")

st.markdown("---")
st.caption("Netflix Analytics Project · Data Analyst Portfolio Piece · "
           "Built with Python, SQLite, Pandas, Scikit-learn, Streamlit & Plotly")