import pandas as pd
import os

REQUIRED_COLUMNS = [
    "symbol", "strike", "expiry", "option_type",
    "bid", "ask", "underlying_price", "timestamp", "volume"
]

def load_from_csv(filepath: str) -> pd.DataFrame:
    """Load options data from a CSV file and validate schema."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    df = pd.read_csv(filepath)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["expiry"] = pd.to_datetime(df["expiry"])
    df = df.drop_duplicates()
    print(f"[Ingester] Loaded {len(df)} records from {filepath}")
    return df


def load_from_dict(records: list) -> pd.DataFrame:
    """Load options data from a list of dicts (e.g. API response)."""
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["expiry"] = pd.to_datetime(df["expiry"])
    return df