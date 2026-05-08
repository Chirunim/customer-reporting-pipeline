import numpy as np
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

N = 250_000
SEED = 42
DATA_DIR = Path(__file__).parent.parent / "data"


def generate_customers(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    today = pd.Timestamp.today().normalize()

    signup_dates = today - pd.Timedelta(days=730) + pd.to_timedelta(
        rng.integers(0, 730, size=n), unit="D"
    )
    supply_start_dates = signup_dates + pd.to_timedelta(
        rng.integers(1, 8, size=n), unit="D"
    )

    has_bill = rng.random(n) < 0.85
    bill_offsets = pd.to_timedelta(rng.integers(5, 61, size=n), unit="D")
    first_bill_dates = (supply_start_dates + bill_offsets).where(has_bill, other=pd.NaT)

    return pd.DataFrame({
        "customer_id":       [f"A-{i+1:06d}" for i in range(n)],
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


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["days_to_first_bill"] = (df["first_bill_date"] - df["supply_start_date"]).dt.days

    df["bill_band"] = pd.cut(
        df["days_to_first_bill"],
        bins=[-1, 14, 28, 42, float("inf")],
        labels=["0-14", "15-28", "29-42", "43+"],
    )

    df["fully_onboarded"] = df["first_bill_date"].notna().astype(int)
    df["week_cohort"] = df["signup_date"].dt.strftime("%Y-W%V")
    return df


def save_outputs(df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    full_path = DATA_DIR / "clean_output.csv"
    df.to_csv(full_path, index=False)
    log.info(f"Saved {len(df):,} rows to {full_path}")

    stream_path = DATA_DIR / "stream_week_0.csv"
    df.nlargest(2000, "signup_date").to_csv(stream_path, index=False)
    log.info(f"Saved 2,000 latest rows to {stream_path}")


def print_summary(df: pd.DataFrame) -> None:
    n = len(df)
    billed = int(df["fully_onboarded"].sum())

    print("\n" + "=" * 52)
    print("  CUSTOMER DATA SUMMARY")
    print("=" * 52)
    print(f"  Total customers       {n:>10,}")
    print(f"  With first bill       {billed:>10,}   ({billed/n:.1%})")
    print(f"  Without first bill    {n - billed:>10,}   ({(n - billed)/n:.1%})")

    print("\n  Bill Band")
    for band in ["0-14", "15-28", "29-42", "43+"]:
        count = int((df["bill_band"] == band).sum())
        print(f"    {band:<8}  {count:>10,}   ({count/n:.1%})")

    print("\n  Region")
    for region, count in df["region"].value_counts().items():
        print(f"    {region:<10}  {count:>10,}   ({count/n:.1%})")

    print("\n  Tariff Type")
    for tariff, count in df["tariff_type"].value_counts().items():
        print(f"    {tariff:<10}  {count:>10,}   ({count/n:.1%})")

    print("\n  Flags")
    for flag in ["psr_flag", "direct_debit", "smart_meter", "app_registered"]:
        count = int(df[flag].sum())
        print(f"    {flag:<20}  {count:>10,}   ({count/n:.1%})")

    print("=" * 52 + "\n")


def main():
    log.info("Generating 250,000 customer records...")
    df = generate_customers(N, SEED)

    log.info("Adding derived columns...")
    df = add_derived_columns(df)

    log.info("Saving outputs...")
    save_outputs(df)

    print_summary(df)


if __name__ == "__main__":
    main()
