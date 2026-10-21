"""Check clone provenance and the experimental ability reference chain offline."""
import hashlib
import json
from pathlib import Path
from prepare_modern_artillery import load, values

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    config = json.loads((ROOT / "src" / "modern_artillery.json").read_text())
    rows = {}
    files = sorted((ROOT / "source" / "modern_artillery").glob("*.json"))
    require(len(files) == 10, "Expected exactly ten source tables")
    for path in files:
        source = json.loads(path.read_text())
        original = load(path.stem)
        require(source["version"] == original["definition"]["version"], "Schema version changed")
        require(source["fields"] == [f["name"] for f in original["definition"]["fields"]], "Fields changed")
        matches = [r for r in original["table_data"]
                   if all(values(original, r)[k] == v for k, v in source["source_match"].items())]
        require(len(matches) == 1, "Ambiguous source row")
        require(len(source["row"]) == len(matches[0]), "Column count changed")
        result = values(original, source["row"])
        before = values(original, matches[0])
        for field, old_cell, new_cell in zip(source["fields"], matches[0], source["row"]):
            require(old_cell.keys() == new_cell.keys(), f"{field}: cell type changed")
            require(result[field] == source["changes"].get(field, before[field]), f"{field}: unexpected change")
        rows[path.stem] = result
    unit, ability, projectile, explosion = [config[k] for k in
        ("unit_key", "ability_key", "projectile_key", "explosion_key")]
    require(rows["units"]["key"] == rows["unit_stats_land"]["key"] == unit, "Unit mismatch")
    require(rows["uniforms"]["Unit"] == rows["building_units_allowed"]["unit"] ==
            rows["units_to_groupings_military_permissions"]["unit"] == unit, "Recruitment/uniform mismatch")
    require(rows["unit_to_unit_abilities_junctions"]["unit_name"] == unit, "Ability owner mismatch")
    require(rows["unit_to_unit_abilities_junctions"]["ability"] == rows["unit_abilities"]["key"] ==
            rows["unit_special_abilities"]["key"] == ability, "Ability reference mismatch")
    require(rows["unit_special_abilities"]["activated_projectile"] == rows["projectiles"]["key"] ==
            projectile, "Projectile reference mismatch")
    require(rows["projectiles"]["explosion_type"] == rows["projectiles_explosions"]["key"] ==
            explosion, "Explosion reference mismatch")
    require(rows["unit_special_abilities"]["num_uses"] == 1, "Expected one activation")
    require(rows["unit_stats_land"]["gun_type"] == "boshin_armstrong_cannon", "Ordinary gun type changed")
    require(rows["unit_stats_land"]["men"] == 40, "Expected forty crew")
    require(rows["unit_stats_land"]["guns"] == config["target_guns"] == 4, "Expected four guns")
    require(rows["unit_stats_land"]["articulated_entity"] == "gun_train_2_horse", "Preserve observed towed prototype entity")
    require(rows["unit_stats_land"]["can_fire_mounted_whilst_moving"] is False, "Prototype must not enable mounted firing while moving")
    require(rows["unit_stats_land"]["does_fire_mounted_by_default"] is False, "Preserve dismounted firing default")
    pack = ROOT / "build" / "steel_sakura_modern_artillery_prototype.pack"
    report_path = ROOT / "build" / "validation" / "modern-artillery-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    require(report["pack_sha256"] == hashlib.sha256(pack.read_bytes()).hexdigest().upper(),
            "RPFM report does not match pack")
    report["source_provenance_and_reference_chain"] = "VERIFIED"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Verified ten source clones, cell types, ability references, and pack-bound RPFM receipt.")


if __name__ == "__main__":
    main()
