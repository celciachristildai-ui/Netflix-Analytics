# Deploying to Streamlit Community Cloud — Step by Step

This walks through the free, easiest deployment path in full detail. Total
time: ~10 minutes.

## Step 1 — Push the project to GitHub

If you don't already have the project in a Git repo:

```bash
cd Netflix-Analytics
git init
git add .
git commit -m "Initial commit — Netflix Analytics project"
```

Create a new repository on GitHub (via the website: **+ → New repository**,
either public or private), then connect and push:

```bash
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git branch -M main
git push -u origin main
```

> **Repo size note:** `data/netflix.db` and the CSVs together are a few MB —
> fine for a normal GitHub repo. If you ever add much larger files, use
> [Git LFS](https://git-lfs.com/) instead of committing them directly.

## Step 2 — Create the Streamlit Cloud app

1. Go to **https://share.streamlit.io** and sign in with your GitHub account.
2. Click **"New app"**.
3. Choose **"Deploy a public app from GitHub"** (or the private-repo option
   if applicable).
4. Fill in the deploy form:
   - **Repository:** `<your-username>/<your-repo-name>`
   - **Branch:** `main`
   - **Main file path:** `dashboard/app.py`
5. Click **"Advanced settings"** before deploying:
   - **Python version:** 3.11 (or 3.10+)
   - Leave "Secrets" empty — this project doesn't need any API keys or
     credentials.
6. Click **Deploy**.

## Step 3 — Wait for the first build

Streamlit Cloud will:
1. Clone your repo.
2. Install everything in `requirements.txt`.
3. Run `dashboard/app.py`, which on first load calls `load_data()` (runs the
   full cleaning pipeline from `src/data_cleaning.py` in-memory) and
   `build_recommender()` (fits the TF-IDF matrix). Both are wrapped in
   `@st.cache_data` / `@st.cache_resource`, so this happens once and is
   instant on every subsequent viewer/session.

First boot typically takes **2-4 minutes**. You'll see a build log in the
browser; once it says "Your app is live!" you have a public URL like:

```
https://<your-app-name>.streamlit.app
```

## Step 4 — Share it

That URL is now your live, public dashboard — share it directly in a
portfolio, resume, or LinkedIn post. Every page (Executive Overview, Global
Map, Genre Analysis, Country Performance with drill-through, Release
Trends, Ratings, Movie vs TV, Title Search, Rankings, Expansion Timeline,
and Executive Summary) and all filters work exactly as they do locally.

## Step 5 — Updating the live app later

Any time you push new commits to `main`, Streamlit Cloud auto-redeploys:

```bash
git add .
git commit -m "Update dashboard"
git push
```

The app rebuilds automatically within a minute or two — no redeploy button
needed.

## Common issues

| Symptom | Cause / Fix |
|---|---|
| "ModuleNotFoundError" in the cloud logs | A package is missing from `requirements.txt` — add it and push again |
| App works locally but errors on Cloud | Usually a hardcoded local file path — this project uses relative paths from `dashboard/data_loader.py`'s `ROOT = Path(__file__).resolve().parent.parent`, which works identically in the cloud |
| App is slow on first load only | Expected — that's the one-time cache build (Step 3); it's instant afterward |
| Want to restart/reboot the app | Streamlit Cloud dashboard (share.streamlit.io) → your app → "⋮" menu → **Reboot app** |
| Want a custom subdomain | Streamlit Cloud → app settings → "General" → edit the app URL slug |

## Alternative hosts

If you'd rather not use Streamlit Community Cloud, `dashboard/DEPLOYMENT.md`
in this repo also covers **Hugging Face Spaces** and **self-hosted Docker**
as drop-in alternatives — same `dashboard/app.py`, no code changes needed.
