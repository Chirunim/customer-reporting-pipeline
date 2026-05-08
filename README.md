# Energy Retail Customer Reporting Pipeline

This pipeline automates the generation, processing, and reporting of customer onboarding data for an energy retail business. It simulates a weekly data extract from a Kraken-style customer management system, applies data quality checks and derived metrics, runs analytical SQL queries via DuckDB, and produces a structured report covering First Bill SLA performance and overall onboarding health. The pipeline is designed to run on a schedule via Apache Airflow and feed into Power BI for business-facing dashboards.

---

## Pipeline Architecture

```
Simulated Kraken Stream
        |
        v
  Python (data generation + cleaning)
        |
        v
  SQL queries (DuckDB)
        |
        v
  Apache Airflow (orchestration)
        |
        v
  Power BI (dashboards)
```

---

## Reports Produced

| Report | Description |
|---|---|
| **First Bill SLA Breakdown** | Customer counts and percentages by bill band (0–14, 15–28, 29–42, 43+ days), with GSOP risk flagging |
| **Onboarding Health Scorecard** | % fully onboarded by region and tariff type, plus individual completion rates for PSR, Direct Debit, Smart Meter and App registration |

---

## Tech Stack

| Tool | Role |
|---|---|
| **Python** | Data generation, cleaning, derived metrics |
| **NumPy / Pandas** | Vectorised data simulation and transformation |
| **SQL** | Analytical queries (SLA trends, health checks) |
| **DuckDB** | In-process SQL engine — queries Pandas DataFrames directly |
| **Apache Airflow** | Pipeline orchestration and scheduling |
| **Power BI** | Business dashboards (connected to pipeline output) |

---

## How to Run

### 1. Install dependencies

```bash
pip install pandas numpy duckdb apache-airflow
```

### 2. Generate the base dataset

Generates 250,000 simulated customers with realistic onboarding data and saves to `data/clean_output.csv`:

```bash
python scripts/clean_data.py
```

### 3. Simulate a weekly data stream

Each run adds 2,000 new customers to the dataset, simulating one week of new Kraken data arriving:

```bash
python scripts/simulate_stream.py
```

Run this repeatedly to simulate multiple weeks. The week counter increments automatically.

### 4. Generate the weekly report

Runs all SQL queries via DuckDB and prints + saves the Good Energy Weekly Report:

```bash
python scripts/generate_summary.py
```

The report is saved to `data/weekly_summary.txt`.

### 5. Run via Airflow (scheduled)

The DAG `good_energy_weekly_pipeline` runs automatically every Monday at 06:00 and executes steps 2–4 in sequence. To load it into Airflow, copy or symlink the `dags/` folder to your Airflow DAGs directory.

---

## Project Structure

```
customer-reporting-pipeline/
├── dags/
│   └── good_energy_dag.py       # Airflow DAG — runs every Monday at 06:00
├── scripts/
│   ├── clean_data.py            # Generates 250k customers, derives metrics, saves CSV
│   ├── simulate_stream.py       # Adds 2,000 new customers per run (weekly stream)
│   ├── run_queries.sql          # Four analytical SQL queries
│   └── generate_summary.py     # Runs queries via DuckDB, prints and saves report
├── data/                        # Generated output files (not committed)
├── powerbi/                     # Power BI report files
└── PIPELINE.md                  # Developer reference
```

---

## Data Note

All customer data in this pipeline is fully simulated using NumPy and Pandas. The data is generated to reflect the structure and characteristics of a real energy retail customer management system export from a Kraken-based platform — including onboarding dates, first bill timelines, tariff types, regional distribution, and onboarding flag completion rates. No real customer data is used at any point.
