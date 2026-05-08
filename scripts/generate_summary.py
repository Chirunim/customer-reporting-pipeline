import duckdb
import pandas as pd
import logging
from datetime import date
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
CLEAN_OUTPUT = DATA_DIR / "clean_output.csv"
SUMMARY_FILE = DATA_DIR / "weekly_summary.txt"
SQL_FILE = Path(__file__).parent / "run_queries.sql"

GSOP_THRESHOLD = 43  # days — SLA risk band


def load_data() -> pd.DataFrame:
    if not CLEAN_OUTPUT.exists():
        raise FileNotFoundError(f"{CLEAN_OUTPUT} not found — run clean_data.py first.")
    log.info(f"Loading {CLEAN_OUTPUT}...")
    df = pd.read_csv(CLEAN_OUTPUT, low_memory=False)
    log.info(f"Loaded {len(df):,} rows")
    return df


def parse_sql_queries(sql_path: Path) -> list[str]:
    raw = sql_path.read_text()
    queries = []
    for block in raw.split(";"):
        sql_lines = [line for line in block.splitlines() if not line.strip().startswith("--")]
        sql = "\n".join(sql_lines).strip()
        if sql:
            queries.append(sql)
    return queries


def run_queries(df: pd.DataFrame) -> tuple:
    con = duckdb.connect()
    con.register("customers", df)

    queries = parse_sql_queries(SQL_FILE)

    sla_df       = con.execute(queries[0]).df()   # Q1: SLA breakdown by bill_band
    _trend_df    = con.execute(queries[1]).df()   # Q2: weekly trend (available for future use)
    scorecard_df = con.execute(queries[2]).df()   # Q3: onboarding health scorecard
    flags_df     = con.execute(queries[3]).df()   # Q4: health check completion rates

    con.close()
    return sla_df, scorecard_df, flags_df


def build_report(sla_df: pd.DataFrame, scorecard_df: pd.DataFrame, flags_df: pd.DataFrame) -> str:
    week_ending = date.today().strftime("%d %B %Y")

    # SLA bands — index by band label for safe lookup
    bands = sla_df.set_index("bill_band")["pct_of_billed"].to_dict()

    def pct(band: str) -> str:
        val = bands.get(band, 0.0)
        return f"{val:.1f}%"

    pct_14   = float(bands.get("0-14",  0.0))
    pct_4plus = float(bands.get("43+",  0.0))

    sla_14_label  = "good" if pct_14 >= 15 else "flagged"
    gsop_label    = "GSOP risk" if pct_4plus >= 25 else "within target"

    # Overall onboarding %
    total       = scorecard_df["total_customers"].sum()
    onboarded   = scorecard_df["fully_onboarded_count"].sum()
    pct_onboard = onboarded / total * 100 if total else 0

    # Flag completion rates — keyed by health_check name
    flag_map = flags_df.set_index("health_check")["completion_pct"].to_dict()

    def flag_pct(key: str) -> str:
        return f"{flag_map.get(key, 0.0):.1f}%"

    lines = [
        "== GOOD ENERGY WEEKLY REPORT ==",
        f"Week ending: {week_ending}",
        "",
        "FIRST BILL SLA:",
        f"  - % billed within 14 days:      {pct('0-14'):>6}  ({sla_14_label})",
        f"  - % billed within 15-28 days:   {pct('15-28'):>6}",
        f"  - % billed within 29-42 days:   {pct('29-42'):>6}",
        f"  - % billed 43+ days ({gsop_label}): {pct('43+'):>6}",
        "",
        "ONBOARDING HEALTH:",
        f"  % fully onboarded:              {pct_onboard:>5.1f}%",
        f"  - PSR registered:               {flag_pct('psr_flag'):>6}",
        f"  - Direct Debit set up:          {flag_pct('direct_debit'):>6}",
        f"  - Smart Meter installed:        {flag_pct('smart_meter'):>6}",
        f"  - App registered:               {flag_pct('app_registered'):>6}",
    ]

    return "\n".join(lines)


def main():
    df = load_data()

    log.info("Running SQL queries via DuckDB...")
    sla_df, scorecard_df, flags_df = run_queries(df)

    report = build_report(sla_df, scorecard_df, flags_df)

    print("\n" + report + "\n")

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(report)
    log.info(f"Summary saved to {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
