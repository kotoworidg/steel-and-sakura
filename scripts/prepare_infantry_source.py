"""Clone installed DB rows into a reversible, evidence-based infantry prototype."""

import json
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "source" / "infantry"
DEST.mkdir(parents=True, exist_ok=True)
KEY = "SteelSakura_Automatic_Rifle_Squad"


def assert_unused(name, column, candidate):
    for prefix in ("table", "existing_mod"):
        path = ROOT / "build" / "inventory" / f"{prefix}_{name}.json"
        if not path.exists():
            continue
        db = json.loads(path.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
        index = [field["name"] for field in db["definition"]["fields"]].index(column)
        if any(value(row[index]) == candidate for row in db["table_data"]):
            raise ValueError(f"{column}={candidate!r} already exists in {path}")


def table(name):
    source = ROOT / "build" / "inventory" / f"table_{name}.json"
    db = json.loads(source.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
    fields = [field["name"] for field in db["definition"]["fields"]]
    return db, fields, source


def value(cell):
    return next(iter(cell.values()))


def find_row(db, fields, column, wanted):
    index = fields.index(column)
    return deepcopy(next(row for row in db["table_data"] if value(row[index]) == wanted))


def set_value(row, fields, column, new_value):
    cell = row[fields.index(column)]
    cell[next(iter(cell))] = new_value


def emit(name, source_key, changes):
    db, fields, source_path = table(name)
    row = find_row(db, fields, "key" if name != "units_to_groupings_military_permissions" else "unit", source_key)
    for field, new_value in changes.items():
        set_value(row, fields, field, new_value)
    document = {
        "table": f"{name}_tables",
        "version": db["definition"]["version"],
        "source_file": str(source_path.relative_to(ROOT)).replace("\\", "/"),
        "source_row": source_key,
        "fields": fields,
        "row": row,
        "changes": changes,
    }
    (DEST / f"{name}.json").write_text(json.dumps(document, indent=2), encoding="utf-8")


for table_name, column, candidate in (
    ("units", "key", KEY),
    ("units", "unique_index", 1464),
    ("unit_stats_land", "key", KEY),
    ("building_units_allowed", "key", 4720),
    ("units_to_groupings_military_permissions", "unit", KEY),
):
    assert_unused(table_name, column, candidate)

emit("unit_stats_land", "Boshin_Inf_Light_Tosa_Riflemen", {"key": KEY, "men": 40})
emit("units", "Inf_Missile_Matchlock_Ashigaru", {
    "key": KEY,
    "on_screen_name": "Automatic Rifle Squad",
    "unit_description_text": KEY,
    "unique_index": 1464,
})
emit("building_units_allowed", 1865, {
    "key": 4720,
    "unit": KEY,
})
emit("units_to_groupings_military_permissions", "Inf_Missile_Matchlock_Ashigaru", {
    "unit": KEY,
    "military_group": "japan",
})
print(f"Prepared {KEY} in {DEST}")
