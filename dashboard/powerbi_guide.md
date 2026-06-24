# Power BI Rebuild Guide

This project's interactive dashboard is delivered as a **working Streamlit app**
(`dashboard/app.py`) because Power BI Desktop is a Windows/Mac GUI application
that can't run in the Linux build environment this project was assembled in.

If you have Power BI Desktop, this guide gets you to an equivalent (or better)
dashboard in under an hour, using the exact same cleaned data.

## 1. Load the data

Power BI → **Get Data → Text/CSV** → import:
- `data/netflix_titles_clean.csv` (main fact table)
- `data/bridge_country.csv`, `data/bridge_genre.csv`, `data/bridge_cast.csv`, `data/bridge_director.csv`

Or, **Get Data → ODBC/SQLite connector** → point at `data/netflix.db` to pull
`titles` + the 4 `bridge_*` tables + the 7 pre-built SQL views directly.

## 2. Build relationships

In Model view, create **one-to-many** relationships from `titles[show_id]` to
each bridge table's `show_id` column. This mirrors the SQL schema in
`sql/01_schema.sql` exactly — a title can have many countries/genres/cast/directors.

## 3. Core DAX measures

```dax
Total Titles = COUNTROWS(titles)

Total Movies = CALCULATE([Total Titles], titles[type] = "Movie")

Total TV Shows = CALCULATE([Total Titles], titles[type] = "TV Show")

Movie Pct = DIVIDE([Total Movies], [Total Titles])

Countries Represented = DISTINCTCOUNT(bridge_country[country_name])

Genres Represented = DISTINCTCOUNT(bridge_genre[genre_name])

Avg Movie Duration =
CALCULATE(
    AVERAGE(titles[duration_minutes]),
    titles[type] = "Movie"
)

YoY Title Growth % =
VAR CurrentYear = SUM(titles[release_year_count])  -- use a release-year-grouped table
VAR PriorYear =
    CALCULATE(
        [Total Titles],
        titles[release_year] = MAX(titles[release_year]) - 1
    )
RETURN DIVIDE([Total Titles] - PriorYear, PriorYear)

Top Genre =
CALCULATE(
    SELECTEDVALUE(bridge_genre[genre_name]),
    TOPN(1, VALUES(bridge_genre[genre_name]),
        CALCULATE(COUNTROWS(bridge_genre)), DESC)
)
```

## 4. Page-by-page build (matches dashboard/app.py 1:1)

| Page | Visuals | Source |
|---|---|---|
| Executive Overview | 5 KPI cards, stacked area (release_year × type), donut (type split), 2 bar charts (top countries/genres) | `titles`, bridge tables |
| Global Content Map | Filled Map visual (`country_name` → titles count) | `bridge_country` |
| Genre Analysis | Treemap (genre count), 2 bar charts (growth, underrepresented) | `bridge_genre`, `titles` |
| Country Performance | Bar chart with **drill-through** page configured (right-click → Drill through) | `bridge_country` |
| Release Trend Dashboard | Line chart (monthly date_added), YoY bar, seasonal donut, day-of-week bar | `titles` |
| Ratings Dashboard | KPI cards, bar (rating counts), donut (maturity), matrix/heatmap (country × rating %) | `titles`, `bridge_country` |
| Movie vs TV Dashboard | KPI cards, 2 histograms, line chart by type | `titles` |
| Title Search & Detail | Table visual + slicer search box; "Filters → Drill through" to a detail page | `titles` |
| Director/Actor Rankings | 2 bar charts + drill-through detail page | `bridge_director`, `bridge_cast` |
| Expansion Timeline | Scatter/line chart (first date_added per country) | `bridge_country`, `titles` |
| Executive Summary | KPI cards + Smart Narrative visual + text boxes for recommendations | All tables |

## 5. Filters / slicers

Add slicers bound to `titles[release_year]` (range slider), `bridge_country[country_name]`,
`bridge_genre[genre_name]`, and `titles[rating]` — set them to **sync across all
pages** (View → Sync Slicers) to match the Streamlit sidebar's global-filter behavior.

## 6. Drill-through

Power BI's native drill-through (right-click a data point → Drill through) is a
closer analog than Streamlit's session-state approach used in this project.
Create a "Country Detail" page, add the relevant fields to the **Drill-through
filters** well, and it will work automatically from any bar/map visual that has
`country_name` in scope.

## 7. Tooltips & dynamic titles

- **Tooltips**: Format pane → Tooltip → add a tooltip page or report-page tooltip
  showing extra fields (already native in Power BI, no extra work needed beyond
  what's described above).
- **Dynamic titles**: bind a text box to a DAX measure like
  `"Showing " & [Total Titles] & " titles (" & MIN(titles[release_year]) & "–" & MAX(titles[release_year]) & ")"`.

## 8. Publish

File → Publish → Power BI Service, or export to Power BI Report Server if your
organization self-hosts.
