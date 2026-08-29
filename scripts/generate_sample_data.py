"""
generate_sample_data.py — build a synthetic multi-batch historian export
for demoing the analyzer, including a deliberate UF flux drift trend and
one CIP hold-time failure, so the tool has something real to find.

Run with: python scripts/generate_sample_data.py
"""

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(42)

OUT = Path(__file__).resolve().parent.parent / "data" / "sample_historian_export.csv"

rows = []
base_time = datetime(2026, 8, 1, 6, 0, tzinfo=timezone.utc)


def add(batch_id, equipment_id, tag, value, ts, uom):
    rows.append({
        "batch_id": batch_id, "equipment_id": equipment_id, "tag_name": tag,
        "value": round(value, 2), "uom": uom, "timestamp": ts.isoformat(),
    })


# 6 sequential batches on UF-SKID-01: permeate flux drifts down over time
# (simulates a membrane fouling trend worth catching before it fails a batch)
for i in range(6):
    batch_id = f"BATCH-{2000 + i}"
    start = base_time + timedelta(days=i)
    flux_baseline = 62 - i * 4.2  # drifting down batch over batch
    for m in range(0, 30, 5):
        ts = start + timedelta(minutes=m)
        add(batch_id, "UF-SKID-01", "TMP", 18 + random.uniform(-1, 1), ts, "psi")
        add(batch_id, "UF-SKID-01", "PERMEATE_FLUX", flux_baseline + random.uniform(-2, 2), ts, "LMH")
        add(batch_id, "UF-SKID-01", "COND", 2.0 + random.uniform(-0.2, 0.2), ts, "mS/cm")

    # CIP cycle after each batch — one of them (batch 3) fails to hold temp long enough
    cip_start = start + timedelta(hours=2)
    if i == 3:
        # only holds >=60C for ~10 minutes, below the 20-minute requirement
        temps = [58, 61, 63, 62, 55, 50, 48]
    else:
        temps = [58, 63, 70, 74, 76, 75, 73, 71, 68, 60]
    for j, t in enumerate(temps):
        add(batch_id, "UF-SKID-01", "CIP_TEMP", t, cip_start + timedelta(minutes=j * 3), "C")

# CHROM-SKID-02: 4 batches, mostly in spec, one clear UV280 excursion (leak/loading issue)
for i in range(4):
    batch_id = f"BATCH-{3000 + i}"
    start = base_time + timedelta(days=i, hours=5)
    for m in range(0, 25, 5):
        ts = start + timedelta(minutes=m)
        uv = 1.3 + random.uniform(-0.2, 0.2)
        if i == 2 and m == 15:
            uv = 3.1  # deliberate excursion above the 2.5 AU high limit
        add(batch_id, "CHROM-SKID-02", "UV280", uv, ts, "AU")
        add(batch_id, "CHROM-SKID-02", "COND", 3.5 + random.uniform(-0.3, 0.3), ts, "mS/cm")

    sip_start = start + timedelta(hours=1)
    for j, t in enumerate([122, 126, 129, 130, 128, 125, 122]):
        add(batch_id, "CHROM-SKID-02", "SIP_TEMP", t, sip_start + timedelta(minutes=j * 3), "C")

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["batch_id", "equipment_id", "tag_name", "value", "uom", "timestamp"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {OUT}")
