# Weather Data Pipeline

## What it does

Extracts hourly temperature forecasts from the free [Open-Meteo API](https://open-meteo.com/) and saves the raw response as a daily JSON file.

This is the first stage of a batch ELT pipeline on Google Cloud Platform that I'm building step by step: raw data lands in Cloud Storage, is loaded into BigQuery, transformed and tested with dbt, visualized in Looker Studio, and orchestrated with Airflow. It's a learning project and portfolio piece while I study for the Google Cloud Professional Data Engineer certification.

## Architecture

```
Open-Meteo API
      │  extract.py (Python, requests)
      ▼
Raw JSON  ── local data/ folder ✅  →  Google Cloud Storage 🚧
      │
      ▼
BigQuery (raw tables) 🚧
      │  dbt: staging → marts, with tests
      ▼
BigQuery (marts) 🚧
      │
      ▼
Looker Studio dashboard 🚧

Orchestration: Airflow in Docker 🚧
```

✅ built  🚧 planned

## How to run

**Requirements:** Python 3.15 (tested on Windows, PowerShell). No API key needed.

```powershell
# 1. Clone the repo
git clone https://github.com/hamzachouaibi9/weather_data.git
cd weather_data

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it (your prompt should now start with "(.venv)")
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the extract
python extract.py
```

**Output:** the raw API response is saved to `data/weather_YYYY-MM-DD.json` (date in UTC). Progress and errors are logged to the terminal.

**Exit codes:** `0` on success, `1` on any failure, so the script can be run by a scheduler.

> **Windows note:** if step 3 fails with *"running scripts is disabled on this system"*, allow local scripts for your user once, then retry:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
>
> **macOS/Linux:** use `source .venv/bin/activate` in step 3.

## Design decisions

### Raw JSON is saved unchanged
The API response is written to disk exactly as received, before any transformation.
**Why:** raw data is the source of truth. If a transformation bug is discovered later, or requirements change, the data can be reprocessed from the original files instead of re-calling the API (which may no longer return the same forecasts). It also gives an audit trail of what the source actually sent.

### One file per day, overwritten on re-run
Files are named `weather_YYYY-MM-DD.json`; running twice on the same day replaces that day's file.
**Why:** this makes the extract **idempotent**: re-running a day (after a failure or a fix) leaves the same end state, with no duplicates for downstream loads to clean up.
**Trade-off:** only the latest run of each day is kept, so an earlier same-day snapshot is lost. That's acceptable because the data is a forecast snapshot; if every run mattered, files would be timestamped instead.

### Dates are in UTC
The file date comes from `datetime.now(UTC)`, not local time.
**Why:** a pipeline should give the same result no matter where it runs. A laptop, a Docker container and a cloud scheduler can sit in different time zones; UTC keeps file names consistent and avoids gaps or duplicates around midnight and daylight-saving changes.

### The run date is decided by the caller, not by `save_raw`
`main` computes the date and passes it into `save_raw(data, date_str)`.
**Why:** this enables **backfills**. If the pipeline was down for several days, those dates can be re-run by passing them in explicitly. An orchestrator like Airflow supplies the logical run date the same way. If `save_raw` read the clock itself, it could only ever write "today". It also makes the function easy to test with a fixed date.

### Requests time out after 10 seconds
`requests.get(..., timeout=10)`.
**Why:** by default, `requests` waits forever. In a scheduled job, a hung request means a run that never finishes and never reports failure. 10 seconds is long enough for a healthy but slow response, and short enough to fail fast.

### Errors are logged once and fail the run
Functions log context (for example, the API's error reason) and re-raise; the entry point logs the full traceback once and exits with code `1`.
**Why:** a scheduler only knows a run failed from a non-zero exit code. Logging in one place avoids duplicate tracebacks, and keeping `sys.exit` out of the functions lets other code (like an Airflow task) import and call them safely.

## Roadmap

- [x] Extract hourly temperature from Open-Meteo
- [x] Save raw JSON, one file per day (UTC)
- [x] Functions, entry point, and exit codes
- [x] Request timeout
- [x] Logging and top-level error handling
- [x] README
- [ ] Retries for transient errors (timeouts, connection errors, 5xx)
- [ ] Move locations to a config file instead of hardcoding
- [ ] Upload raw files to Google Cloud Storage
- [ ] Load into BigQuery
- [ ] dbt models (staging → marts) with tests
- [ ] Looker Studio dashboard
- [ ] Airflow DAG (local, in Docker)
- [ ] Terraform for GCP resources
- [ ] CI/CD with GitHub Actions
