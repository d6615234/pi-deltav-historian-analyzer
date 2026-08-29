"""
plotting.py — matplotlib trend charts, saved as PNG files (no GUI needed).
"""

import matplotlib
matplotlib.use("Agg")  # headless-safe backend, no display required
import matplotlib.pyplot as plt
from pathlib import Path


def plot_tag_trend(df, equipment_id, tag_name, out_path):
    """Plot every raw reading for one equipment/tag over time, with spec
    limits overlaid as horizontal reference lines."""
    from .specs import TAG_SPECS

    subset = df[(df["equipment_id"] == equipment_id) & (df["tag_name"] == tag_name)].sort_values("timestamp")
    if subset.empty:
        raise ValueError(f"No data for {equipment_id} / {tag_name}")

    spec = TAG_SPECS.get(tag_name)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(subset["timestamp"], subset["value"], marker="o", linewidth=1)
    if spec:
        ax.axhline(spec["low"], color="orange", linestyle="--", linewidth=1, label=f"low ({spec['low']})")
        ax.axhline(spec["high"], color="red", linestyle="--", linewidth=1, label=f"high ({spec['high']})")
        ax.legend(fontsize=8)

    ax.set_title(f"{equipment_id} — {tag_name}")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel(spec["uom"] if spec else "value")
    fig.autofmt_xdate()
    fig.tight_layout()

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


def plot_batch_drift(drift_df, equipment_id, tag_name, out_path):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(drift_df["first_seen"], drift_df["mean_value"], marker="o", label="per-batch mean")
    ax.plot(drift_df["first_seen"], drift_df["rolling_mean"], linestyle="--", label="rolling mean")
    ax.set_title(f"Batch-to-batch drift — {equipment_id} / {tag_name}")
    ax.set_xlabel("Batch start")
    ax.set_ylabel("value")
    ax.legend(fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)
