"""
historian_analyzer
===================
A standalone toolkit for analyzing process historian tag data of the kind
exported from OSIsoft PI or an Emerson DeltaV PCS historian, for
biopharma downstream skids (ultrafiltration, column chromatography) and
their CIP/SIP cycles.

No live PI or DeltaV connection is required or used. The loader reads a
CSV export in the same column shape a PI Web API or SQL query would
return (equipment_id, batch_id, tag_name, value, uom, timestamp), so the
analysis logic here is what you'd point at a live historian client later
— only the data source changes.

All sample data is synthetic.
"""

__version__ = "0.1.0"
