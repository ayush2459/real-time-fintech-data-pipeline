import argparse
import json
from pipeline.ingester import load_from_csv
from pipeline.validator import validate, check_parity_pairs
from pipeline.volatility import detect_iv_anomalies, check_term_structure
from pipeline.anomaly import build_report


def run(filepath: str):
    print(f"\n{'='*55}")
    print(f"  Real-Time Fintech Data Pipeline")
    print(f"{'='*55}\n")

    # Load
    df = load_from_csv(filepath)

    # Validate
    result = validate(df)
    parity_violations = check_parity_pairs(df)
    iv_anomalies = detect_iv_anomalies(df)
    iv_anomalies += check_term_structure(df)

    # Report
    report = build_report(result, parity_violations, iv_anomalies)

    s = report["summary"]
    b = report["breakdown"]

    print(f"Processed : {s['total_records']} records")
    print(f"Clean     : {s['clean']} ({s['clean_pct']}%)")
    print(f"Warnings  : {s['warnings']}")
    print(f"Critical  : {s['critical']}")
    print(f"\nAnomaly Breakdown:")
    for k, v in b.items():
        print(f"  - {k.replace('_', ' ').title()}: {v}")

    print(f"\nFull report saved to report.json")
    with open("report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fintech Data Pipeline")
    parser.add_argument("--file", default="data/sample_options.csv", help="Path to input CSV")
    args = parser.parse_args()
    run(args.file)