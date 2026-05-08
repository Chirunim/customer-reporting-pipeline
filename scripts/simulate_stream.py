import numpy as np
import pandas as pd
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BATCH_SIZE = 2000
DATA_DIR = Path(__file__).parent.parent / "data"
STATE_FILE = DATA_DIR / "stream_state.json"
CLEAN_OUTPUT = DATA_DIR / "clean_output.csv"
STREAM_LATEST = DATA_DIR / "stream_latest.csv"

# Initial dataset size produced by clean_data.py
INITIAL_CUSTOMERS = 250_000


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"week": 1, "next_customer_num": INITIAL_CUSTOMERS + 1, "total": INITIAL_CUSTOMERS}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def generate_batch(n: int, start_id: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    today = pd.Timestamp.today().normalize()

    # Signup dates spread across the past 7 days (this week's cohort)
    signup_dates = today - pd.Timedelta(days=6) + pd.to_timedelta(
        rng.integers(0, 7, size=n), unit="D"
    )
    supply_start_dates = signup_dates + pd.to_timedelta(rng.integers(1, 8, size=n), unit="D")

    has_bill = rng.random(n) < 0.85
    bill_offsets = pd.to_timedelta(rng.integers(5, 61, size=n), unit="D")
    first_bill_dates = (supply_start_dates + bill_offsets).where(has_bill, other=pd.NaT)

    df = pd.DataFrame({
        "customer_id":       [f"A-{start_id + i:06d}" for i in range(n)],
        "signup_date":       signup_dates,
        "supply_start_date": supply_start_dates,
        "first_bill_date":   first_bill_dates,
        "psr_flag":          rng.choice([0, 1], size=n, p=[0.90, 0.10]),
        "direct_debit":      rng.choice([0, 1], size=n, p=[0.30, 0.70]),
        "smart_meter":       rng.choice([0, 1], size=n, p=[0.40, 0.60]),
        "app_registered":    rng.choice([0, 1], size=n, p=[0.45, 0.55]),
        "region":            rng.choice(["North", "South", "East", "West", "Midlands"], size=n),
        "tariff_type":       rng.choice(["Fixed", "Variable", "Green"], size=n, p=[0.50, 0.30, 0.20]),
    })

    df["days_to_first_bill"] = (df["first_bill_date"] - df["supply_start_date"]).dt.days
    df["bill_band"] = pd.cut(
        df["days_to_first_bill"],
        bins=[-1, 14, 28, 42, float("inf")],
        labels=["0-14", "15-28", "29-42", "43+"],
    )
    df["fully_onboarded"] = df["first_bill_date"].notna().astype(int)
    df["week_cohort"] = df["signup_date"].dt.strftime("%Y-W%V")

    return df


def append_to_output(df: pd.DataFrame) -> None:
    if not CLEAN_OUTPUT.exists():
        raise FileNotFoundError(
            f"{CLEAN_OUTPUT} not found — run clean_data.py first to generate the base dataset."
        )
    df.to_csv(CLEAN_OUTPUT, mode="a", header=False, index=False)


def print_summary(df: pd.DataFrame, week: int, total: int) -> None:
    n = len(df)
    billed_14 = int((df["bill_band"] == "0-14").sum())
    fully_onboarded = int(df["fully_onboarded"].sum())

    print("\n" + "=" * 52)
    print(f"  STREAM SUMMARY — Week {week}")
    print("=" * 52)
    print(f"  New customers added       {n:>8,}")
    print(f"  Billed within 14 days     {billed_14:>8,}   ({billed_14 / n:.1%})")
    print(f"  Fully onboarded           {fully_onboarded:>8,}   ({fully_onboarded / n:.1%})")
    print(f"  Running total             {total:>8,}")
    print("=" * 52 + "\n")


def main():
    state = load_state()
    week = state["week"]
    start_id = state["next_customer_num"]
    seed = 1000 + week  # unique reproducible seed per week

    log.info(f"Simulating week {week} — generating {BATCH_SIZE:,} customers (from A-{start_id:06d})...")
    df = generate_batch(BATCH_SIZE, start_id, seed)

    log.info("Appending to clean_output.csv...")
    append_to_output(df)

    log.info("Saving stream_latest.csv...")
    df.to_csv(STREAM_LATEST, index=False)

    new_total = state["total"] + BATCH_SIZE
    print_summary(df, week, new_total)

    save_state({"week": week + 1, "next_customer_num": start_id + BATCH_SIZE, "total": new_total})


if __name__ == "__main__":
    main()
