"""
trends.py — batch-to-batch trending statistics.

Useful for spotting slow drift (e.g. a UF membrane's permeate flux
declining batch over batch, signaling it needs cleaning or replacement)
that a single-batch spec check would never catch.
"""

import pandas as pd


def batch_tag_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Mean/min/max per (batch_id, equipment_id, tag_name), ordered by
    the first timestamp seen for that batch — i.e. batch sequence order."""
    grp = df.groupby(["batch_id", "equipment_id", "tag_name"])
    summary = grp.agg(
        first_seen=("timestamp", "min"),
        mean_value=("value", "mean"),
        min_value=("value", "min"),
        max_value=("value", "max"),
        n=("value", "count"),
    ).reset_index()
    return summary.sort_values(["equipment_id", "tag_name", "first_seen"])


def rolling_drift(df: pd.DataFrame, equipment_id: str, tag_name: str, window: int = 3) -> pd.DataFrame:
    """Rolling mean of a tag's per-batch average, to visualize drift over
    a window of consecutive batches on one piece of equipment."""
    summary = batch_tag_summary(df)
    subset = summary[(summary["equipment_id"] == equipment_id) & (summary["tag_name"] == tag_name)].copy()
    subset = subset.sort_values("first_seen")
    subset["rolling_mean"] = subset["mean_value"].rolling(window, min_periods=1).mean()
    return subset
