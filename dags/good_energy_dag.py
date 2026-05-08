# =============================================================================
# Good Energy Weekly Reporting Pipeline — Airflow DAG
#
# This is a simulation of a Kraken (Octopus Energy tech platform) data pipeline.
# It generates synthetic customer data, appends the latest weekly batch to
# simulate a live Kraken data stream, then runs SQL queries via DuckDB to
# produce a First Bill SLA and Onboarding Health report.
#
# Schedule: every Monday at 06:00
# Pipeline: clean_data.py → simulate_stream.py → generate_summary.py
# =============================================================================

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "depends_on_past": False,
}

with DAG(
    dag_id="good_energy_weekly_pipeline",
    default_args=default_args,
    description="Weekly First Bill SLA and Onboarding Health report for Good Energy",
    schedule_interval="0 6 * * 1",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["good_energy", "reporting", "kraken"],
) as dag:

    generate_data = BashOperator(
        task_id="generate_and_clean_data",
        bash_command=f"python {SCRIPTS_DIR}/clean_data.py",
    )

    simulate_stream = BashOperator(
        task_id="simulate_weekly_stream",
        bash_command=f"python {SCRIPTS_DIR}/simulate_stream.py",
    )

    generate_summary = BashOperator(
        task_id="generate_weekly_summary",
        bash_command=f"python {SCRIPTS_DIR}/generate_summary.py",
    )

    generate_data >> simulate_stream >> generate_summary
