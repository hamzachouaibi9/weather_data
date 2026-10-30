# <project name>
## What it does
## Architecture
## How to run
## Design decisions
## Design decisions

### Raw JSON is saved unchanged
The API response is written to disk exactly as received, before any transformation.
**Why:** raw data is the source of truth. If a transformation bug is discovered
later, or requirements change, the data can be reprocessed from the original
files instead of re-calling the API (which may no longer return historical
forecasts). It also gives an audit trail of what the source actually sent.

### One file per day, overwritten on re-run
Files are named `weather_YYYY-MM-DD.json`; running twice on the same day replaces the file.
**Why:** this makes the extract **idempotent**: re-running a day (after a failure
or a fix) gives the same end state, with no duplicates for downstream loads to clean up.
**Trade-off:** only the latest run of each day is kept, so earlier same-day
responses are lost. Acceptable here because the data is a forecast snapshot;
if every run mattered, files would be timestamped instead.

### Dates are in UTC
The file date comes from `datetime.now(UTC)`, not local time.
**Why:** a pipeline should give the same result no matter where it runs. A
laptop, a Docker container and a cloud scheduler can sit in different time zones;
UTC keeps file names consistent and avoids gaps or duplicates around midnight
and daylight-saving changes.

### The run date is decided by the caller, not by `save_raw`
`main` computes the date and passes it into `save_raw(data, date_str)`.
**Why:** this enables **backfills**. If the pipeline was down for several days,
those dates can be re-run by passing them in explicitly. An orchestrator like
Airflow supplies the logical run date the same way. If `save_raw` read the
clock itself, it could only ever write "today".

### Requests time out after 10 seconds
`requests.get(..., timeout=10)`.
**Why:** by default, `requests` waits forever. In a scheduled job, a hung request
means a run that never finishes and never reports failure. 10 seconds is long
enough for a healthy but slow response, and short enough to fail fast.

### Errors are logged once and fail the run
Functions log context (for example, the API's error reason) and re-raise; the entry
point logs the full traceback once and exits with code `1`.
**Why:** a scheduler only knows a run failed from a non-zero exit code. Logging
in one place avoids duplicate tracebacks, and keeping `sys.exit` out of the
functions lets other code (like an Airflow task) import and call them safely.

## Roadmap
