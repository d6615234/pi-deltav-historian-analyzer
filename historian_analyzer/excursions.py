"""
excursions.py — spec-limit excursion detection and CIP/SIP hold-time
verification.
"""

import pandas as pd
from .specs import TAG_SPECS, CIP_SIP_MIN_HOLD_MINUTES

MAX_GAP_MINUTES = 10  # a gap in readings longer than this breaks a "hold"


def flag_excursions(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with an added `in_spec` column and an
    `excursion_reason` column (None when in spec)."""
    out = df.copy()
    out["in_spec"] = True
    out["excursion_reason"] = None

    for tag, spec in TAG_SPECS.items():
        mask = out["tag_name"] == tag
        below = mask & (out["value"] < spec["low"])
        above = mask & (out["value"] > spec["high"])
        out.loc[below, "in_spec"] = False
        out.loc[below, "excursion_reason"] = (
            f"{tag} below low limit {spec['low']}{spec['uom']}")
        out.loc[above, "in_spec"] = False
        out.loc[above, "excursion_reason"] = (
            f"{tag} above high limit {spec['high']}{spec['uom']}")

    return out


def excursion_summary(flagged_df: pd.DataFrame) -> pd.DataFrame:
    """One row per (batch_id, equipment_id, tag_name) with excursion counts."""
    grp = flagged_df.groupby(["batch_id", "equipment_id", "tag_name"])
    summary = grp.agg(
        readings=("value", "count"),
        excursions=("in_spec", lambda s: (~s).sum()),
        min_value=("value", "min"),
        max_value=("value", "max"),
    ).reset_index()
    summary["excursion_pct"] = (summary["excursions"] / summary["readings"] * 100).round(1)
    return summary.sort_values("excursions", ascending=False)


def verify_cip_sip_hold(df: pd.DataFrame, tag_name: str) -> pd.DataFrame:
    """For each (batch_id, equipment_id), find the longest continuous run
    of readings at-or-above the tag's low limit (with no gap longer than
    MAX_GAP_MINUTES), and check it meets the minimum hold time.

    Returns one row per (batch_id, equipment_id) with pass/fail.
    """
    if tag_name not in CIP_SIP_MIN_HOLD_MINUTES:
        raise ValueError(f"No minimum hold time configured for {tag_name}")

    spec = TAG_SPECS[tag_name]
    min_hold = CIP_SIP_MIN_HOLD_MINUTES[tag_name]
    subset = df[df["tag_name"] == tag_name].sort_values("timestamp")

    results = []
    for (batch_id, equipment_id), g in subset.groupby(["batch_id", "equipment_id"]):
        g = g.sort_values("timestamp").reset_index(drop=True)
        best_minutes = 0.0
        run_start = None
        prev_ts = None

        for _, row in g.iterrows():
            in_hold = row["value"] >= spec["low"]
            gap_ok = prev_ts is None or (row["timestamp"] - prev_ts).total_seconds() / 60 <= MAX_GAP_MINUTES

            if in_hold and gap_ok and run_start is not None:
                pass  # continue current run
            elif in_hold:
                run_start = row["timestamp"]

            if in_hold and run_start is not None:
                minutes = (row["timestamp"] - run_start).total_seconds() / 60
                best_minutes = max(best_minutes, minutes)
            else:
                run_start = None

            prev_ts = row["timestamp"]

        results.append({
            "batch_id": batch_id,
            "equipment_id": equipment_id,
            "tag_name": tag_name,
            "longest_hold_minutes": round(best_minutes, 1),
            "min_required_minutes": min_hold,
            "passed": best_minutes >= min_hold,
        })

    return pd.DataFrame(results)
