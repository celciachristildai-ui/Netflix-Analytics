# Deploying the Dashboard Online

The dashboard (`dashboard/app.py`) is a standard Streamlit app — here are the
three easiest ways to get it live on the internet.

## Option A — Streamlit Community Cloud (free, easiest)

1. Push this whole project to a **public or private GitHub repo**.
2. Go to https://share.streamlit.io → "New app".
3. Select your repo, branch `main`, and set the file path to `dashboard/app.py`.
4. Under "Advanced settings," set the Python version to 3.11+ and point
   "Requirements file" at `requirements.txt`.
5. Click Deploy. First boot takes ~2-3 minutes (it runs `src/data_cleaning.py`
   and builds the SQLite DB + TF-IDF recommender on first load via
   `@st.cache_data`/`@st.cache_resource`, so subsequent loads are fast).

**Gotcha:** Streamlit Community Cloud's filesystem is ephemeral and read-only
after deploy — that's fine here because `data_loader.py` rebuilds everything
in-memory from the CSVs on first run rather than expecting a persisted
`netflix.db` file.

## Option B — Hugging Face Spaces (free, good for portfolio links)

1. Create a new Space → SDK: **Streamlit**.
2. Upload the project (or push via `git`), making sure `app.py` is at the repo
   root, or add a one-line `streamlit_app.py` that does
   `import dashboard.app` at the root if you keep the existing folder layout.
3. Add `requirements.txt` at the repo root — Spaces installs it automatically.

## Option C — Self-hosted (Docker / any VM)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t netflix-analytics .
docker run -p 8501:8501 netflix-analytics
```

Then put any reverse proxy (Caddy/Nginx) in front for HTTPS, or deploy the
image directly to Render, Railway, Fly.io, or AWS App Runner — all support
"point at a Dockerfile" deploys with no extra config.

## Local run (no deployment)

```bash
pip install -r requirements.txt
python src/data_cleaning.py     # generates the cleaned CSVs (one-time)
python src/db_utils.py          # builds data/netflix.db (one-time)
streamlit run dashboard/app.py
```
