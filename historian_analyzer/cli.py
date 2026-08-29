"""
cli.py — command-line entry point.

Usage:
    python -m historian_analyzer.cli --input data/sample_historian_export.csv --output-dir output
"""

import argparse
from pathlib import Path

from .loader import load_csv
from .excursions import flag_excursions, excursion_summary, verify_cip_sip_hold
from .trends import batch_tag_summary, rolling_drift
from .plotting import plot_tag_trend, plot_batch_drift
from .specs import CIP_SIP_MIN_HOLD_MINUTES


def main():
    parser = argparse.ArgumentParser(description="PI / DeltaV historian analyzer")
    parser.add_argument("--input", required=True, help="Path to historian CSV export")
    parser.add_argument("--output-dir", default="output", help="Directory for reports and charts")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_csv(args.input)
    print(f"Loaded {len(df)} readings across "
          f"{df['batch_id'].nunique()} batch(es) and {df['equipment_id'].nunique()} equipment unit(s)")

    flagged = flag_excursions(df)
    summary = excursion_summary(flagged)
    summary_path = out_dir / "excursion_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"\nExcursion summary written to {summary_path}")
    print(summary.to_string(index=False))

    print("\nCIP/SIP hold-time verification:")
    for tag in CIP_SIP_MIN_HOLD_MINUTES:
        if tag in df["tag_name"].unique():
            hold = verify_cip_sip_hold(df, tag)
            hold_path = out_dir / f"{tag.lower()}_hold_verification.csv"
            hold.to_csv(hold_path, index=False)
            print(hold.to_string(index=False))

    batch_summary = batch_tag_summary(df)
    batch_summary.to_csv(out_dir / "batch_tag_summary.csv", index=False)

    # Plot every tag/equipment combination present in the data
    charts_dir = out_dir / "charts"
    for (equipment_id, tag_name), _ in df.groupby(["equipment_id", "tag_name"]):
        chart_path = charts_dir / f"{equipment_id}_{tag_name}.png"
        plot_tag_trend(df, equipment_id, tag_name, chart_path)

        drift = rolling_drift(df, equipment_id, tag_name)
        if len(drift) > 1:
            plot_batch_drift(drift, equipment_id, tag_name,
                              charts_dir / f"{equipment_id}_{tag_name}_drift.png")

    print(f"\nCharts written to {charts_dir}")


if __name__ == "__main__":
    main()
