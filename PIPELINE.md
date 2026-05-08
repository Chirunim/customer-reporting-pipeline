# PIPELINE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Automated pipeline for **First Bill SLA and Onboarding Health Reporting** in an energy retail context. Simulates weekly Kraken data stream arrivals, runs SQL-based analytics via DuckDB, and produces structured reports for Power BI consumption. Orchestrated by Apache Airflow.

## Repository Structure

```
dags/          # Apache Airflow DAG definitions
scripts/       # Python data-processing scripts and SQL queries
data/          # Generated output (excluded from git)
powerbi/       # Power BI report files
```

Key files:
- `dags/good_energy_dag.py` — Airflow DAG, runs every Monday at 06:00; chains all three pipeline tasks
- `scripts/clean_data.py` — generates 250,000 simulated customers, derives all metrics, saves `data/clean_output.csv` and `data/stream_week_0.csv`
- `scripts/simulate_stream.py` — appends 2,000 new customers per run to simulate one week of Kraken stream data; tracks state in `data/stream_state.json`
- `scripts/run_queries.sql` — four DuckDB-compatible SQL queries (SLA breakdown, weekly trend, onboarding scorecard, health check rates)
- `scripts/generate_summary.py` — loads `clean_output.csv`, executes all SQL queries via DuckDB, prints and saves `data/weekly_summary.txt`

## Data Flow

```
clean_data.py  →  simulate_stream.py  →  generate_summary.py
   (base dataset)     (weekly append)        (SQL + report)
```

## Setup

```bash
pip install pandas numpy duckdb apache-airflow
```

No environment variables are required — all paths are resolved relative to the script files.

## Running the Pipeline Manually

```bash
python scripts/clean_data.py        # one-time base dataset generation
python scripts/simulate_stream.py   # once per week to add new customers
python scripts/generate_summary.py  # produces data/weekly_summary.txt
```

## Key Derived Columns

| Column | Logic |
|---|---|
| `days_to_first_bill` | `first_bill_date - supply_start_date` (days) |
| `bill_band` | Bucketed: 0–14, 15–28, 29–42, 43+ |
| `fully_onboarded` | 1 if `first_bill_date` is not null, else 0 |
| `week_cohort` | ISO week of `signup_date`, e.g. `2026-W10` |

## Airflow DAG

- **DAG ID:** `good_energy_weekly_pipeline`
- **Schedule:** `0 6 * * 1` (every Monday at 06:00)
- **Retries:** 1 retry per task, 5-minute delay
- **Failure behaviour:** downstream tasks are skipped automatically if an upstream task fails (`all_success` trigger rule)
