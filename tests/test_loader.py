import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from historian_analyzer.loader import load_csv, HistorianDataError


def test_load_valid_csv(tmp_path):
    p = tmp_path / "d.csv"
    p.write_text(
        "equipment_id,batch_id,tag_name,value,uom,timestamp\n"
        "EQ-1,B-1,TMP,18.2,psi,2026-08-20T08:00:00Z\n"
    )
    df = load_csv(p)
    assert len(df) == 1
    assert df.iloc[0]["value"] == 18.2


def test_missing_column_raises(tmp_path):
    p = tmp_path / "d.csv"
    p.write_text("equipment_id,batch_id,tag_name,value,timestamp\nEQ-1,B-1,TMP,18.2,2026-08-20T08:00:00Z\n")
    with pytest.raises(HistorianDataError):
        load_csv(p)


def test_bad_timestamp_raises(tmp_path):
    p = tmp_path / "d.csv"
    p.write_text(
        "equipment_id,batch_id,tag_name,value,uom,timestamp\n"
        "EQ-1,B-1,TMP,18.2,psi,not-a-date\n"
    )
    with pytest.raises(HistorianDataError):
        load_csv(p)
