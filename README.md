# Energy Retail Customer Reporting Pipeline

This project is an end-to-end automated data pipeline built to solve a critical problem in energy retail operations: too much data and too few resources to process it manually. The pipeline ingests customer data from a source system, cleans and transforms it using Python, queries it using SQL via DuckDB, orchestrates the full workflow using Apache Airflow, and delivers two production-ready reports in Power BI. The data used in this project is simulated to mirror the structure and behaviour of a real energy retail customer management system export. All distributions, percentages, and customer behaviours reflect realistic energy retail patterns.

---

## Pipeline Architecture

```
Source System Export
        |
        v
Python Cleaning & Transformation
        |
        v
SQL Queries (DuckDB)
        |
        v
Airflow Orchestration
        |
        v
Power BI Dashboard
        |
        v
Excel Export on Demand
```

---

## Reports Produced

### Report 1: First Bill SLA Tracker

Tracks how long each customer takes to receive their first bill, broken into bands of 0–14 days, 15–28 days, 29–42 days, and 43 or more days. Surfaces the percentage of customers meeting the Ofgem SLA window, flags cohorts at GSOP risk, and shows week-on-week trends.

### Report 2: Onboarding Health Scorecard

Tracks whether customers were onboarded with all health checks complete, including PSR registration, Direct Debit setup, Smart Meter installation, and app or online account registration. Shows the percentage fully onboarded, which checks are most commonly missed, and which weekly intake cohorts had poor onboarding scores.

---

## Insights

### First Bill SLA Insights

- **74.59% of customers** receive their first bill within 14 days — just below the 80% Ofgem target, flagging an **AT RISK** status.
- The **43+ day band accounts for 3%** of billed customers — a small but critical cohort that could trigger GSOP financial penalties if left unaddressed.
- The weekly trend line enables the team to identify whether SLA performance is improving or deteriorating over time, supporting proactive intervention rather than reactive firefighting.

### Onboarding Health Insights

- **Smart Meter installation** is consistently the lowest-completed health check, suggesting a supply chain or scheduling bottleneck that requires operational attention.
- Weekly cohort analysis reveals which intake weeks had poor onboarding scores, helping the team trace problems back to specific campaigns or processes.
- **Customers without Direct Debit set up** represent both a credit risk and a potential churn indicator for the business.

---

## Recommendations

### Operational Recommendations

1. Prioritise customers in the **43+ day band** for immediate billing investigation before GSOP penalties are triggered.
2. Investigate the **Smart Meter installation bottleneck** through a targeted operational review to lift the fully onboarded percentage across all cohorts.
3. Set **weekly SLA improvement targets** using the trend line rather than relying on the overall figure alone, enabling earlier identification of deteriorating performance.
4. Automate **early warnings using Power BI threshold alerts** so the team is notified before a breach occurs rather than after it has already happened.

### Training Recommendations

5. Deliver targeted training to Energy Specialists on the importance and process of **PSR registration, Smart Meter installation, and Direct Debit setup** so they can have more informed and confident conversations with customers at the point of onboarding.

### Marketing Recommendations

6. Launch **targeted marketing campaigns** encouraging customers to sign up for Direct Debits, clearly highlighting the discounts available to customers who choose to pay by Direct Debit.
7. Run **Smart Meter awareness campaigns** that directly address the following common myths and misconceptions:
   - Smart meters do not emit radiation.
   - Smart meters do not listen to or record customer conversations.
   - Smart meters do not add unnecessary readings to the meter.
   - Smart meters are only used to transmit readings automatically, removing the need for manual meter submissions entirely.
8. Develop **customer communications** that connect each onboarding health check to a tangible personal benefit, making it clear to customers why completing each step improves their overall experience.

---

## Tech Stack

| Tool | Role |
|---|---|
| **Python** | Data generation, cleaning, transformation, and summary output |
| **SQL via DuckDB** | Business logic queries and report table production |
| **Apache Airflow** | Pipeline orchestration and scheduling every Monday at 6am |
| **Power BI** | Interactive dashboards, KPI cards, RAG status indicators, and threshold alerts |
| **Excel** | On-demand export from Power BI for stakeholder sharing |

---

## How to Run

**Step 1** — Place the source system export in the `data/` folder as `kraken_export.csv`.

**Step 2** — Generate and clean the dataset:
```bash
python scripts/clean_data.py
```

**Step 3** — Add the latest weekly batch of customers:
```bash
python scripts/simulate_stream.py
```

**Step 4** — Produce the plain English summary report:
```bash
python scripts/generate_summary.py
```

**Step 5** — Open Power BI and click **Refresh** to update the dashboard.

**Step 6** — Trigger the full pipeline automatically by activating the Airflow DAG named `good_energy_weekly_pipeline`, which runs every Monday at 6am.

---

## Project Structure

```
customer-reporting-pipeline/
├── dags/
│   └── good_energy_dag.py          # Airflow DAG orchestrating the full pipeline
├── scripts/
│   ├── clean_data.py               # Data generation and cleaning
│   ├── simulate_stream.py          # Weekly stream simulation (2,000 new customers per run)
│   ├── run_queries.sql             # Business logic SQL queries
│   └── generate_summary.py        # Runs queries via DuckDB, produces plain English report
├── data/                           # Generated CSV files (excluded from version control)
├── powerbi/
│   └── energy_reporting_dashboard.pbix   # Power BI dashboard file
└── PIPELINE.md                     # Developer reference
```

---

## Data Note

All data in this project is synthetically generated to mirror the structure and statistical behaviour of a real energy retail customer management system. No real customer data is used at any point. The simulated dataset reflects realistic energy retail distributions across billing timelines, regional spread, tariff types, and onboarding health metrics.
