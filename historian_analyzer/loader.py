"""
loader.py — load and validate a historian CSV export.

Expected columns: equipment_id, batch_id, tag_name, value, uom, timestamp
timestamp must be ISO 8601 (e.g. 2026-08-20T08:00:00Z).
"""

import pandas as pd

REQUIRED_COLUMNS = ["equipment_id", "batch_id", "tag_name", "value", "uom", "timestamp"]


class HistorianDataError(ValueError):
    pass


def load_csv(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise HistorianDataError(f"Missing required column(s): {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    bad_ts = df["timestamp"].isna().sum()
    if bad_ts:
        raise HistorianDataError(f"{bad_ts} row(s) have an unparseable timestamp")

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    bad_val = df["value"].isna().sum()
    if bad_val:
        raise HistorianDataError(f"{bad_val} row(s) have a non-numeric value")

    return df.sort_values(["equipment_id", "tag_name", "timestamp"]).reset_index(drop=True)
