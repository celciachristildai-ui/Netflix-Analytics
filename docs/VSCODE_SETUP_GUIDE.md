# Netflix Analytics Project — VS Code Setup & Run Manual

This is a complete, start-to-finish walkthrough for opening, running, and
exploring this project entirely inside Visual Studio Code. Follow it top to
bottom the first time; afterward you'll only need the "Day-to-day" section.

---

## 0. Prerequisites (install once)

| Tool | Why | Check you have it |
|---|---|---|
| **VS Code** | the editor | `code --version` |
| **Python 3.10+** | runs everything | `python --version` or `python3 --version` |
| **Git** (optional, needed for Streamlit Cloud deploy) | version control | `git --version` |

VS Code extensions to install (Extensions panel → search → Install):
- **Python** (Microsoft) — IntelliSense, run/debug
- **Jupyter** (Microsoft) — lets you open/run `.ipynb` files inside VS Code
- **SQLite Viewer** or **SQLTools** (optional) — lets you browse `data/netflix.db`
  visually instead of via the command line

---

## 1. Unzip and open the project

1. Unzip `Netflix-Analytics.zip` anywhere on your machine.
2. Open VS Code → **File → Open Folder...** → select the unzipped
   `Netflix-Analytics` folder.
3. Open the integrated terminal: **Terminal → New Terminal** (or `` Ctrl+` ``).
   Make sure the terminal's working directory is the project root (it should
   say `Netflix-Analytics` in the prompt).

---

## 2. Create a virtual environment (recommended)

Doing this keeps the project's packages separate from the rest of your system.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activating, your terminal prompt should show `(.venv)` at the start.

In VS Code, also point the editor at this interpreter so IntelliSense and
the Jupyter extension use the right packages:
**Ctrl/Cmd+Shift+P → "Python: Select Interpreter" → choose the one inside
`.venv`.**

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

> If you're on a system Python that refuses installs with an "externally
> managed environment" error (common on Ubuntu/Debian), use a venv (Step 2)
> — that avoids the issue entirely. If you must skip the venv, add
> `--break-system-packages` to the command above.

This installs pandas, numpy, matplotlib, seaborn, plotly, scikit-learn,
streamlit, jupyter tooling, reportlab, and python-pptx — everything every
layer of this project needs.

---

## 4. Run the data pipeline (Phases 1-2: Collection & Cleaning)

The raw CSV is already included at `data/netflix_titles_raw.csv`, so you
don't need to download anything. Build the cleaned dataset and the SQL
database from scratch:

```bash
python src/data_cleaning.py
python src/db_utils.py
```

What each does:
- `src/data_cleaning.py` → reads the raw CSV, cleans it, and writes
  `data/netflix_titles_clean.csv` plus four `data/bridge_*.csv` files
  (the exploded country/genre/cast/director tables).
- `src/db_utils.py` → loads all of those into `data/netflix.db` (SQLite),
  creates indexes, and builds the SQL views from `sql/03_views.sql`.

You should see console output ending in something like:
```
[db] Loaded 7786 titles, 9066 country rows, ...
```

---

## 5. Explore the SQL layer (Phase 4)

- Open `sql/01_schema.sql` to see the relational schema (table + bridge
  tables for multi-valued fields).
- Open `sql/02_queries.sql` — 50 queries covering joins, CTEs, window
  functions, ranking, CASE, subqueries, date functions, and views.
- To run all 50 and regenerate the results file:
  ```bash
  python src/run_all_queries.py
  ```
  Results land in `reports/query_results.md` — open it in VS Code's Markdown
  preview (`Ctrl/Cmd+Shift+V`) to read every query's output.
- To poke at the database directly in VS Code, install the **SQLite Viewer**
  extension, then right-click `data/netflix.db` in the Explorer → "Open
  Database", or run ad-hoc queries from the terminal:
  ```bash
  python -c "from src.db_utils import run_query; print(run_query('SELECT * FROM vw_country_summary LIMIT 5'))"
  ```

---

## 6. Run the notebooks (Phases 3, 5, 8)

The notebooks are already executed with saved output (charts included), so
you can just open and read them — but you can also re-run them live:

1. In VS Code's Explorer, click `notebooks/02_eda_analysis.ipynb`.
2. The Jupyter extension opens it as a notebook UI directly inside VS Code.
3. Click the ⏩ "Run All" button at the top, or run cells one at a time with
   `Shift+Enter`.
4. VS Code will prompt you to pick a kernel the first time — choose the
   `.venv` Python environment from Step 2.

Notebook order:
| Notebook | Phase | Content |
|---|---|---|
| `01_data_cleaning.ipynb` | 1-2 | Before/after cleaning walkthrough |
| `02_eda_analysis.ipynb` | 3 | All 10 EDA questions, charts saved to `images/` |
| `03_python_advanced_analysis.ipynb` | 5 | Stats, correlation, outliers, time series |
| `04_machine_learning.ipynb` | 8 | Movie/TV classifier + genre recommender |

> Each notebook's `.py` twin (e.g. `02_eda_analysis.py`) is the same content
> in plain-script form (via `jupytext`) — easier to diff/review in a normal
> editor view if you don't want the notebook UI.

---

## 7. Run the interactive dashboard (Phase 6 + bonus features)

```bash
streamlit run dashboard/app.py
```

VS Code will show the terminal output; it includes a **Local URL** like
`http://localhost:8501`. Either:
- `Ctrl/Cmd`-click the link in the VS Code terminal, or
- Open it manually in your browser.

The app has 11 pages (sidebar navigation) and global filters (Year, Country,
Genre, Rating) that apply across pages — including the Executive Overview,
Global Content Map, Genre Analysis, Country Performance (with click-to-
drill-through), Release Trends, Ratings, Movie vs TV, full-catalog Title
Search with recommendations, Director/Actor Rankings, the Expansion
Timeline, and the Executive Summary.

To stop the server: click in the terminal and press `Ctrl+C`.

**Optional — headless self-test:** before/after editing the dashboard, you
can verify every page still renders without errors, with no browser needed:
```bash
python dashboard/test_dashboard.py
```

---

## 8. Generate the PDF executive report and PowerPoint deck (Phase 9)

```bash
python reports/generate_pdf_report.py
```
Regenerates `reports/Netflix_Executive_Report.pdf` from the latest data and
charts in `images/`.

The slide deck `presentation.pptx` (12 slides) is already built and included
at the project root — open it directly in PowerPoint/Keynote/Google Slides,
or in VS Code with the **vscode-pptx** extension if you want a quick
in-editor preview.

---

## 9. Project map — what's where

```
Netflix-Analytics/
├── data/              raw + cleaned CSVs, bridge tables, netflix.db
├── sql/                schema, 50 queries, views
├── notebooks/          4 executed Jupyter notebooks (+ .py source twins)
├── src/                reusable Python modules (cleaning, DB load, query runner)
├── dashboard/           Streamlit app, data loader, headless test, deploy guide, Power BI guide
├── images/             17 chart PNGs generated by the notebooks
├── reports/            SQL query results, PDF executive report, generator script
├── docs/               this manual + the Streamlit deployment guide
├── presentation.pptx   12-slide executive deck
├── README.md           full project documentation
└── requirements.txt    pinned dependencies
```

---

## 10. Day-to-day (after first-time setup)

```bash
source .venv/bin/activate        # or .venv\Scripts\Activate.ps1 on Windows
streamlit run dashboard/app.py    # just want the dashboard
# — or —
code .                            # reopen the whole project in VS Code
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` for any package | Re-run `pip install -r requirements.txt` inside the activated venv |
| Jupyter cell can't find `src` module | Notebooks add the project root to `sys.path` automatically — make sure you're running them from inside the `notebooks/` folder context (VS Code does this by default) |
| Streamlit page blank/error | Run `python dashboard/test_dashboard.py` to see which page and exact error |
| Port 8501 already in use | `streamlit run dashboard/app.py --server.port 8502` |
| `pip install` fails with "externally-managed-environment" | You skipped the venv (Step 2) — create and activate it, then retry |
