"""Enable an installed dormant limbered-gun test unit in an isolated research pack."""

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "build" / "inventory"
OUT = ROOT / "source" / "tank"
OUT.mkdir(parents=True, exist_ok=True)
UNIT = "test_limber_gun"


def value(cell):
    return next(iter(cell.values()))


def table(name):
    path = INVENTORY / f"table_{name}.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
    fields = [field["name"] for field in data["definition"]["fields"]]
    return data, fields


def ensure_unused(name, field, candidate):
    for prefix in ("table", "existing_mod"):
        path = INVENTORY / f"{prefix}_{name}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
        fields = [item["name"] for item in data["definition"]["fields"]]
        if any(value(row[fields.index(field)]) == candidate for row in data["table_data"]):
            raise ValueError(f"{field}={candidate!r} already exists in {path}")


def emit(name, predicate, changes):
    data, fields = table(name)
    originals = [row for row in data["table_data"] if predicate(row, fields)]
    if len(originals) != 1:
        raise ValueError(f"Expected one observed source row in {name}, found {len(originals)}")
    row = deepcopy(originals[0])
    for field, new_value in changes.items():
        cell = row[fields.index(field)]
        cell[next(iter(cell))] = new_value
    document = {"table": f"{name}_tables", "version": data["definition"]["version"],
                "fields": fields, "row": row, "changes": changes}
    (OUT / f"{name}.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def main():
    stats, sf = table("unit_stats_land")
    units, uf = table("units")
    if not any(value(row[sf.index("key")]) == UNIT for row in stats["table_data"]):
        raise ValueError("Installed limbered-gun stats row is missing")
    if not any(value(row[uf.index("key")]) == UNIT for row in units["table_data"]):
        raise ValueError("Installed limbered-gun unit row is missing")
    ensure_unused("building_units_allowed", "key", 4721)
    ensure_unused("building_units_allowed", "unit", UNIT)
    ensure_unused("units_to_groupings_military_permissions", "unit", UNIT)
    emit("building_units_allowed", lambda row, fields: value(row[fields.index("key")]) == 1865,
         {"key": 4721, "unit": UNIT})
    emit("units_to_groupings_military_permissions",
         lambda row, fields: value(row[fields.index("unit")]) == "Art_European_Cannons" and
         value(row[fields.index("military_group")]) == "japan", {"unit": UNIT})
    print("Prepared isolated recruitment/permission research rows for installed test_limber_gun")


if __name__ == "__main__":
    main()
