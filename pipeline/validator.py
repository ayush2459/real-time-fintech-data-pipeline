import pandas as pd
from datetime import datetime, timezone
from pipeline.parity import check_put_call_parity
import os

PARITY_THRESHOLD = float(os.getenv("PARITY_THRESHOLD", 0.02))
STALE_MINUTES = 5
MAX_SPREAD_PCT = 0.10  # 10% of mid price


def validate(df: pd.DataFrame) -> dict:
    """
    Run all validation rules on the dataframe.
    Returns a summary with clean records and anomalies.
    """
    anomalies = []
    clean_indices = []
    now = datetime.now(timezone.utc)

    for idx, row in df.iterrows():
        record_errors = []

        # 1. Timestamp validation
        ts = row["timestamp"]
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        staleness = (now - ts).total_seconds() / 60
        if staleness > STALE_MINUTES:
            record_errors.append({
                "rule": "STALE_DATA",
                "severity": "WARNING",
                "detail": f"Data is {staleness:.1f} min old"
            })

        # 2. Bid-ask spread check
        bid, ask = row["bid"], row["ask"]
        if bid > ask:
            record_errors.append({
                "rule": "INVERTED_MARKET",
                "severity": "CRITICAL",
                "detail": f"Bid {bid} > Ask {ask}"
            })
        elif ask > 0:
            spread_pct = (ask - bid) / ((ask + bid) / 2)
            if spread_pct > MAX_SPREAD_PCT:
                record_errors.append({
                    "rule": "WIDE_SPREAD",
                    "severity": "WARNING",
                    "detail": f"Spread {spread_pct:.1%} exceeds threshold"
                })

        # 3. Volume sanity check
        if row["volume"] == 0:
            record_errors.append({
                "rule": "ZERO_VOLUME",
                "severity": "INFO",
                "detail": "Zero volume record"
            })

        # 4. Put-call parity (requires paired records - checked separately)
        # Flagged in check_parity_pairs()

        if record_errors:
            anomalies.append({"index": idx, "record": row.to_dict(), "errors": record_errors})
        else:
            clean_indices.append(idx)

    clean_df = df.loc[clean_indices]
    return {
        "total": len(df),
        "clean": len(clean_df),
        "anomalies": len(anomalies),
        "clean_df": clean_df,
        "anomaly_records": anomalies,
    }


def check_parity_pairs(df: pd.DataFrame) -> list:
    """
    Find call-put pairs for the same symbol/strike/expiry
    and check put-call parity for each pair.
    """
    violations = []
    calls = df[df["option_type"] == "call"]
    puts = df[df["option_type"] == "put"]

    merged = pd.merge(
        calls, puts,
        on=["symbol", "strike", "expiry", "underlying_price"],
        suffixes=("_call", "_put")
    )

    for _, row in merged.iterrows():
        expiry_days = (row["expiry"] - pd.Timestamp.now()).days
        mid_call = (row["bid_call"] + row["ask_call"]) / 2
        mid_put = (row["bid_put"] + row["ask_put"]) / 2

        result = check_put_call_parity(
            call_price=mid_call,
            put_price=mid_put,
            spot=row["underlying_price"],
            strike=row["strike"],
            expiry_days=expiry_days,
            threshold=PARITY_THRESHOLD,
        )

        if result["violation"]:
            violations.append({
                "symbol": row["symbol"],
                "strike": row["strike"],
                "expiry": str(row["expiry"].date()),
                **result,
            })

    return violations