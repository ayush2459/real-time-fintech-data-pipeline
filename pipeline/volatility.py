import numpy as np
import pandas as pd


def detect_iv_anomalies(df: pd.DataFrame, iv_col: str = "implied_volatility") -> list:
    """
    Detect anomalies in the implied volatility surface.
    Flags records where IV deviates more than 3 std devs from the mean.
    """
    if iv_col not in df.columns:
        return []

    anomalies = []
    mean_iv = df[iv_col].mean()
    std_iv = df[iv_col].std()

    for idx, row in df.iterrows():
        z_score = abs(row[iv_col] - mean_iv) / std_iv if std_iv > 0 else 0
        if z_score > 3:
            anomalies.append({
                "index": idx,
                "symbol": row.get("symbol"),
                "implied_volatility": row[iv_col],
                "z_score": round(z_score, 2),
                "severity": "WARNING",
                "rule": "IV_SURFACE_ANOMALY",
            })

    return anomalies


def check_term_structure(df: pd.DataFrame) -> list:
    """
    Detect inverted volatility term structures.
    Near-term IV should generally be <= longer-term IV in normal markets.
    """
    if "implied_volatility" not in df.columns or "expiry" not in df.columns:
        return []

    alerts = []
    for symbol, group in df.groupby("symbol"):
        sorted_group = group.sort_values("expiry")
        ivs = sorted_group["implied_volatility"].values
        expiries = sorted_group["expiry"].values

        for i in range(len(ivs) - 1):
            if ivs[i] > ivs[i + 1] * 1.15:  # 15% inversion threshold
                alerts.append({
                    "symbol": symbol,
                    "rule": "INVERTED_TERM_STRUCTURE",
                    "severity": "WARNING",
                    "near_expiry": str(expiries[i]),
                    "far_expiry": str(expiries[i + 1]),
                    "near_iv": round(ivs[i], 4),
                    "far_iv": round(ivs[i + 1], 4),
                })

    return alerts