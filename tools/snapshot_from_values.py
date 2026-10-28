"""Write the page's saved copy of the tracker from Google Sheets get_values responses, for when the sheet isn't
link-readable (build.py can then only embed what's on disk).

    python3 tools/snapshot_from_values.py tracker.json synclog.json   # each file: a get_values response {"values": [[...]]}
    python3 build.py --publish
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for src, dst, head in zip(sys.argv[1:3], ("tracker-snapshot.csv", "sync-log-snapshot.csv"), ("Code", "When")):
    values = json.load(open(src)).get("values", [])
    assert values and values[0][0] == head, f"{src}: expected a {head!r} header row"
    width = len(values[0])
    with open(os.path.join(HERE, dst), "w", newline="") as fh:
        csv.writer(fh, quoting=csv.QUOTE_ALL).writerows(r + [""] * (width - len(r)) for r in values)
    print(f"{dst}: {len(values) - 1} rows")
