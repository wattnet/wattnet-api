"""Verify that the wattnet-api wheel bundles the required data files."""

import pathlib
import sys
import zipfile

whl = next(pathlib.Path(sys.argv[1]).glob("*.whl"))
names = zipfile.ZipFile(whl).namelist()

required = [
    "data/geojson/",
    "data/zones/entsoe_selected_zones_2026.yaml",
    "data/zones/entsoe_selected_crossborders_2026.yaml",
]
missing = [r for r in required if not any(r in n for n in names)]

if missing:
    print(f"FAIL {whl.name}: missing {missing}")
    sys.exit(1)

print(f"OK {whl.name}: all data files present")
