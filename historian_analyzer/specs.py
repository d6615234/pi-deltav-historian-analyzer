"""
specs.py — tag specification limits and CIP/SIP hold-time requirements.

In a real deployment these would come from the approved recipe/MBR, not
be hard-coded — they're defined here as a plain dict so the whole
toolkit is runnable standalone. Swapping this for a lookup against a
recipe database is a one-function change (see `load_specs_from_json`).
"""

import json

TAG_SPECS = {
    "TMP":            {"low": 5.0,   "high": 30.0,  "uom": "psi",   "equipment": "UF_SKID"},
    "PERMEATE_FLUX":  {"low": 20.0,  "high": 80.0,  "uom": "LMH",   "equipment": "UF_SKID"},
    "COND":           {"low": 0.0,   "high": 5.0,   "uom": "mS/cm", "equipment": "ANY"},
    "UV280":          {"low": 0.0,   "high": 2.5,   "uom": "AU",    "equipment": "CHROM_SKID"},
    "CIP_TEMP":       {"low": 60.0,  "high": 85.0,  "uom": "C",     "equipment": "ANY"},
    "SIP_TEMP":       {"low": 121.0, "high": 134.0, "uom": "C",     "equipment": "ANY"},
}

# Minimum continuous minutes a CIP/SIP tag must stay at-or-above its low
# limit for the cycle to be considered a verified hold, not just a
# momentary spike through the setpoint.
CIP_SIP_MIN_HOLD_MINUTES = {
    "CIP_TEMP": 20,
    "SIP_TEMP": 15,
}


def load_specs_from_json(path):
    """Load an alternate spec table from JSON, same shape as TAG_SPECS.
    Lets you point the analyzer at a different recipe's limits without
    touching code."""
    with open(path) as f:
        return json.load(f)
