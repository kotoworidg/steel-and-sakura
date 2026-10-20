"""Summarize decoded, locally installed Shogun 2 DB tables for mod research."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
for name in (
    "unit_stats_land",
    "units",
    "building_units_allowed",
    "projectiles",
    "gun_type_to_projectiles",
    "units_to_groupings_military_permissions",
):
    path = ROOT / "build" / "inventory" / f"table_{name}.json"
    table = json.loads(path.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
    fields = [field["name"] for field in table["definition"]["fields"]]
    print(f"TABLE {name} version={table['definition']['version']} rows={len(table['table_data'])}")
    print("FIELDS", ", ".join(fields))
    for row in table["table_data"]:
        values = [next(iter(cell.values())) for cell in row]
        if any("tosa_riflemen" in str(value).lower() for value in values):
            print("TOSA", json.dumps(dict(zip(fields, values)), ensure_ascii=False))
