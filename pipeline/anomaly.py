def classify_severity(errors: list) -> str:
    """Return the highest severity level from a list of errors."""
    levels = {"CRITICAL": 3, "WARNING": 2, "INFO": 1}
    if not errors:
        return "CLEAN"
    return max(errors, key=lambda e: levels.get(e["severity"], 0))["severity"]


def build_report(validation_result: dict, parity_violations: list, iv_anomalies: list) -> dict:
    """Aggregate all anomalies into a single pipeline report."""
    total = validation_result["total"]
    clean = validation_result["clean"]
    anomalies = validation_result["anomaly_records"]

    breakdown = {
        "inverted_market": 0,
        "stale_timestamps": 0,
        "wide_spread": 0,
        "zero_volume": 0,
        "parity_violations": len(parity_violations),
        "iv_surface_anomalies": len(iv_anomalies),
    }

    rule_map = {
        "INVERTED_MARKET": "inverted_market",
        "STALE_DATA": "stale_timestamps",
        "WIDE_SPREAD": "wide_spread",
        "ZERO_VOLUME": "zero_volume",
    }

    for record in anomalies:
        for error in record["errors"]:
            key = rule_map.get(error["rule"])
            if key:
                breakdown[key] += 1

    return {
        "summary": {
            "total_records": total,
            "clean": clean,
            "clean_pct": round(clean / total * 100, 1) if total else 0,
            "warnings": sum(1 for r in anomalies for e in r["errors"] if e["severity"] == "WARNING"),
            "critical": sum(1 for r in anomalies for e in r["errors"] if e["severity"] == "CRITICAL"),
        },
        "breakdown": breakdown,
        "parity_violations": parity_violations,
        "iv_anomalies": iv_anomalies,
    }