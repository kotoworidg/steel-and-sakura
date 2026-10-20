"""Validate the local infantry prototype against decoded installed game data.

This checks data consistency and pack structure, not in-game behavior.
"""

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = "SteelSakura_Automatic_Rifle_Squad"
TABLES = ("unit_stats_land", "units", "building_units_allowed", "units_to_groupings_military_permissions", "unit_abilities", "unit_special_abilities", "unit_to_unit_abilities_junctions")


def scalar(cell):
    if not isinstance(cell, dict) or len(cell) != 1:
        raise ValueError(f"Invalid DB cell: {cell!r}")
    return next(iter(cell.values()))


def read_table(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]


def check(root=ROOT):
    errors, checks, details = [], [], {}

    def require(condition, label):
        (checks if condition else errors).append(label)

    inventory = root / "build" / "inventory"
    source_dir = root / "source" / "infantry"
    sources = {}
    for name in TABLES:
        path = source_dir / f"{name}.json"
        base_path = inventory / f"table_{name}.json"
        if not path.is_file() or not base_path.is_file():
            errors.append(f"Missing {path if not path.is_file() else base_path}")
            continue
        src = json.loads(path.read_text(encoding="utf-8"))
        base = read_table(base_path)
        fields = [f["name"] for f in base["definition"]["fields"]]
        require(src["table"] == f"{name}_tables", f"{name}: table name")
        require(src["version"] == base["definition"]["version"], f"{name}: installed schema version")
        require(src["fields"] == fields, f"{name}: installed field order")
        require(len(src["row"]) == len(fields), f"{name}: cell count")
        if len(src["row"]) != len(fields) or src["fields"] != fields:
            continue
        key_field = {"units_to_groupings_military_permissions": "unit", "unit_to_unit_abilities_junctions": "unit_name"}.get(name, "key")
        source_idx = fields.index(key_field)
        originals = [row for row in base["table_data"] if scalar(row[source_idx]) == src["source_row"]]
        if name == "units_to_groupings_military_permissions":
            originals = [row for row in originals if scalar(row[fields.index("military_group")]) == "japan"]
        if name == "unit_to_unit_abilities_junctions":
            originals = [r for r in originals if scalar(r[fields.index("ability")]) == "blinding_grenade"]
        require(len(originals) == 1, f"{name}: unique installed source row")
        if len(originals) == 1:
            expected = json.loads(json.dumps(originals[0]))
            for field, new_value in src["changes"].items():
                require(field in fields, f"{name}: changed field {field} exists")
                if field in fields:
                    cell = expected[fields.index(field)]
                    cell[next(iter(cell))] = new_value
            require(src["row"] == expected, f"{name}: only declared changes from installed row")
            require(all(set(a) == set(b) for a, b in zip(src["row"], originals[0])), f"{name}: cell types preserved")
        sources[name] = {field: scalar(src["row"][i]) for i, field in enumerate(fields)}

    if len(sources) == len(TABLES):
        for name, column in (("unit_stats_land", "key"), ("units", "key"),
                             ("building_units_allowed", "unit"),
                             ("units_to_groupings_military_permissions", "unit")):
            require(sources[name][column] == KEY, f"{name}: shared unit key")
        require(sources["unit_stats_land"]["men"] == 40, "infantry: 40 soldiers")
        ability = "steel_sakura_throw_grenades"
        require(sources["unit_to_unit_abilities_junctions"]["unit_name"] == KEY, "grenades: unit link")
        require(sources["unit_to_unit_abilities_junctions"]["ability"] == sources["unit_abilities"]["key"] == sources["unit_special_abilities"]["key"] == ability, "grenades: ability links")
        require(sources["unit_special_abilities"]["activated_projectile"] == "grenade", "grenades: explosive projectile")
        require(sources["unit_abilities"]["requires_effect_enabling"] is False, "grenades: no borrowed ninja unlock required")
        require(sources["unit_special_abilities"]["num_uses"] == 2, "grenades: two activations")
        projectile_path = inventory / "table_projectiles.json"
        if projectile_path.is_file():
            projectiles = read_table(projectile_path)
            projectile_fields = [f["name"] for f in projectiles["definition"]["fields"]]
            projectile_index = projectile_fields.index("key")
            missile = sources["unit_stats_land"]["default_missile_type"]
            require(any(scalar(row[projectile_index]) == "grenade" for row in projectiles["table_data"]), "grenades: installed projectile exists")
            require(any(scalar(row[projectile_index]) == missile for row in projectiles["table_data"]),
                    f"infantry: projectile {missile!r} exists in installed table")
        else:
            errors.append(f"Missing projectile reference input: {projectile_path}")
        require(sources["building_units_allowed"]["building"] == "SHO_Castle_1_Fort", "infantry: observed Fort recruitment building")
        require(sources["units_to_groupings_military_permissions"]["military_group"] == "japan", "infantry: observed military group")
        for name, column, candidate in (
            ("units", "key", KEY), ("units", "unique_index", sources["units"]["unique_index"]),
            ("unit_stats_land", "key", KEY),
            ("building_units_allowed", "key", sources["building_units_allowed"]["key"]),
            ("units_to_groupings_military_permissions", "unit", KEY),
        ):
            for prefix in ("table", "existing_mod"):
                path = inventory / f"{prefix}_{name}.json"
                if not path.exists():
                    if prefix == "existing_mod" and name == "units_to_groupings_military_permissions":
                        continue
                    errors.append(f"Missing collision input: {path}")
                    continue
                table = read_table(path)
                names = [f["name"] for f in table["definition"]["fields"]]
                idx = names.index(column)
                require(not any(scalar(row[idx]) == candidate for row in table["table_data"]),
                        f"{name}: {column}={candidate!r} unused in {prefix}")

    loc_path = root / "src" / "infantry_localisation.json"
    if loc_path.is_file():
        loc = json.loads(loc_path.read_text(encoding="utf-8"))
        entries = loc.get("entries", [])
        require(loc.get("unit_key") == KEY, "localisation: intended unit key")
        require(len(entries) == 7, "localisation: seven authored strings")
        keys = [entry.get("key") for entry in entries]
        require(len(set(keys)) == len(keys), "localisation: unique keys")
        required_prefixes = ("units_on_screen_name_", "unit_description_texts_description_text_",
                             "unit_description_texts_long_description_text_",
                             "unit_description_texts_strengths_and_weaknesses_")
        ability_keys = {"unit_abilities_" + field + "_steel_sakura_throw_grenades" for field in ("bullet_text", "info_card_tooltip_text", "button_tooltip_text")}
        require(set(keys) == {prefix + KEY for prefix in required_prefixes} | ability_keys, "localisation: observed key patterns")
        require(all(isinstance(entry.get("text"), str) and entry["text"].strip() and
                    isinstance(entry.get("tooltip"), bool) for entry in entries),
                "localisation: nonempty text and Boolean tooltip")
        existing = set()
        for name in ("units", "unit_description_texts", "unit_abilities"):
            path = inventory / f"loc_{name}.json"
            if path.is_file():
                table = json.loads(path.read_text(encoding="utf-8-sig"))["LocRFileInfo"][0]["table"]
                fields = [field["name"] for field in table["definition"]["fields"]]
                require(fields == ["key", "text", "tooltip"], f"localisation: installed {name} schema")
                existing.update(scalar(row[0]) for row in table["table_data"])
            else:
                errors.append(f"Missing localisation collision input: {path}")
        require(not any(key in existing for key in keys), "localisation: keys unused in installed English files")
    else:
        errors.append(f"Missing {loc_path}")

    icon_name = "steel_sakura_automatic_rifle_squad.tga"
    icon_sizes = {"icons": (64, 118), "icons_square": (46, 46), "info": (128, 236),
                  "recruitment_large": (75, 75), "recruitment_small": (64, 64)}
    for folder, size in icon_sizes.items():
        icon_path = root / "assets" / "infantry" / folder / icon_name
        if not icon_path.is_file():
            errors.append(f"Missing original icon: {icon_path}")
            continue
        image = icon_path.read_bytes()
        require(len(image) >= 18, f"icon {folder}: TGA header")
        if len(image) >= 18:
            require(image[2] == 2 and image[16] == 32, f"icon {folder}: uncompressed 32-bit TGA")
            require(struct.unpack_from("<HH", image, 12) == size, f"icon {folder}: observed dimensions")

    pack = root / "build" / "steel_sakura_infantry_prototype.pack"
    if pack.is_file():
        data = pack.read_bytes()
        require(data.startswith(b"PFH3"), "pack: PFH3 signature")
        details["pack_bytes"] = len(data)
        details["pack_sha256"] = hashlib.sha256(data).hexdigest().upper()
    else:
        errors.append(f"Missing {pack}; run scripts/build.ps1")
    details["note"] = "Static checks cannot prove recruitment, localisation display, icon lookup, firing, movement, or campaign behavior."
    return {"status": "VERIFIED" if not errors else "FAILED", "checks_passed": len(checks),
            "checks": checks, "errors": errors, "details": details}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = check(args.root)
    report = args.report or args.root / "build" / "validation" / "offline-report.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {result['checks_passed']} checks; {len(result['errors'])} errors. Report: {report}")
    for error in result["errors"]:
        print(f"ERROR: {error}", file=sys.stderr)
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
