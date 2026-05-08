# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Automated data pipeline for **First Bill SLA and Onboarding Health Reporting**. The pipeline uses Apache Airflow (DAGs), Python scripts, and SQL queries, with output intended for Power BI dashboards.

## Repository Structure

```
dags/          # Apache Airflow DAG definitions
scripts/       # Python data-processing scripts and SQL queries
data/          # Data artifacts (local, not committed)
powerbi/       # Power BI report files
```

Key files:
- `dags/good_energy_dag.py` — main Airflow DAG orchestrating the pipeline
- `scripts/run_queries.sql` — SQL queries that extract/transform source data
- `scripts/clean_data.py` — cleans/normalizes query results
- `scripts/generate_summary.py` — produces the final summary for reporting

## Setup

No `requirements.txt` or environment config exists yet. As dependencies are added, document the install command here (e.g., `pip install -r requirements.txt`) and any environment variables required (database connections, Airflow config, etc.).

## Development Notes

- The project is in early scaffolding stage — all source files are currently empty placeholders.
- Airflow DAG development: add tasks to `dags/good_energy_dag.py` following the standard `DAG` + `Operator` pattern.
- SQL queries in `scripts/run_queries.sql` feed into `scripts/clean_data.py`, which feeds `scripts/generate_summary.py`.
