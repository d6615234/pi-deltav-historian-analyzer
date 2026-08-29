import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from historian_analyzer.excursions import flag_excursions, excursion_summary, verify_cip_sip_hold


def make_df(rows):
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def test_flag_excursions_detects_high_and_low():
    df = make_df([
        {"batch_id": "B1", "equipment_id": "EQ1", "tag_name": "TMP", "value": 2.0, "uom": "psi", "timestamp": "2026-01-01T00:00:00Z"},
        {"batch_id": "B1", "equipment_id": "EQ1", "tag_name": "TMP", "value": 40.0, "uom": "psi", "timestamp": "2026-01-01T00:05:00Z"},
        {"batch_id": "B1", "equipment_id": "EQ1", "tag_name": "TMP", "value": 18.0, "uom": "psi", "timestamp": "2026-01-01T00:10:00Z"},
    ])
    flagged = flag_excursions(df)
    assert flagged["in_spec"].tolist() == [False, False, True]


def test_excursion_summary_counts():
    df = make_df([
        {"batch_id": "B1", "equipment_id": "EQ1", "tag_name": "TMP", "value": 2.0, "uom": "psi", "timestamp": "2026-01-01T00:00:00Z"},
        {"batch_id": "B1", "equipment_id": "EQ1", "tag_name": "TMP", "value": 18.0, "uom": "psi", "timestamp": "2026-01-01T00:05:00Z"},
    ])
    flagged = flag_excursions(df)
    summary = excursion_summary(flagged)
    row = summary.iloc[0]
    assert row["readings"] == 2
    assert row["excursions"] == 1


def test_cip_hold_passes_when_long_enough():
    # all readings stay at/above the 60C low limit for a continuous 25 minutes
    rows = [
        {"batch_id": "B1", "equipment_id": "EQ1", "tag_name": "CIP_TEMP", "value": v,
         "uom": "C", "timestamp": f"2026-01-01T00:{m:02d}:00Z"}
        for m, v in zip(range(0, 30, 5), [65, 68, 70, 72, 71, 66])
    ]
    df = make_df(rows)
    result = verify_cip_sip_hold(df, "CIP_TEMP")
    assert result.iloc[0]["passed"]
    assert result.iloc[0]["longest_hold_minutes"] == 25.0


def test_cip_hold_fails_when_too_short():
    rows = [
        {"batch_id": "B1", "equipment_id": "EQ1", "tag_name": "CIP_TEMP", "value": v,
         "uom": "C", "timestamp": f"2026-01-01T00:{m:02d}:00Z"}
        for m, v in zip(range(0, 15, 5), [61, 63, 50])
    ]
    df = make_df(rows)
    result = verify_cip_sip_hold(df, "CIP_TEMP")
    assert not result.iloc[0]["passed"]
