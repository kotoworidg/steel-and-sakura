"""Clone installed schemas/rows into an isolated, nuclear-themed artillery prototype."""
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source" / "modern_artillery"
INV = ROOT / "build" / "inventory"


def load(name):
    return json.loads((INV / f"table_{name}.json").read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]


def values(table, row):
    return dict(zip((f["name"] for f in table["definition"]["fields"]),
                    (next(iter(c.values())) for c in row)))


def emit(name, match, changes, unique):
    table = load(name)
    rows = [r for r in table["table_data"] if all(values(table, r)[k] == v for k, v in match.items())]
    if len(rows) != 1:
        raise ValueError(f"{name}: expected exactly one source row, got {len(rows)}")
    # Check installed base and any inspected existing-mod rows before reserving keys.
    candidates = [table]
    existing = INV / f"existing_mod_{name}.json"
    if existing.exists():
        candidates.append(json.loads(existing.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"])
    for other in candidates:
        for r in other["table_data"]:
            if all(values(other, r)[k] == v for k, v in unique.items()):
                raise ValueError(f"{name}: duplicate {unique}")
    row = deepcopy(rows[0])
    fields = [f["name"] for f in table["definition"]["fields"]]
    for field, new in changes.items():
        cell = row[fields.index(field)]
        kind = next(iter(cell))
        if kind.startswith("I"):
            if int(new) != new:
                raise ValueError(f"{field}: fractional integer")
            new = int(new)
        cell[kind] = new
    document = {"table": name + "_tables", "version": table["definition"]["version"],
                "fields": fields, "row": row, "source_match": match, "changes": changes}
    (OUT / f"{name}.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def main():
    config = json.loads((ROOT / "src" / "modern_artillery.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    unit, ability, projectile, explosion = [config[k] for k in
        ("unit_key", "ability_key", "projectile_key", "explosion_key")]
    base = "Boshin_Art_Armstrong_Guns"
    emit("units", {"key": base}, {"key": unit, "on_screen_name": config["display_name"],
         "unit_description_text": unit, "unique_index": config["unique_index"]}, {"key": unit})
    # Unique numeric index is a separate constraint from the string key.
    for filename in ("table_units.json", "existing_mod_units.json"):
        path = INV / filename
        if path.exists():
            units = json.loads(path.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
            if any(values(units, r)["unique_index"] == config["unique_index"] for r in units["table_data"]):
                raise ValueError("Unit numeric index is already used")
    emit("unit_stats_land", {"key": base}, {"key": unit}, {"key": unit})
    emit("uniforms", {"Uniform_Name": "Default_Boshin_Armstrong_Guns"},
         {"Uniform_Name": "Default_" + unit, "Unit": unit}, {"Unit": unit})
    emit("building_units_allowed", {"key": 1865},
         {"key": config["recruitment_key"], "unit": unit}, {"key": config["recruitment_key"]})
    emit("units_to_groupings_military_permissions", {"unit": "Art_European_Cannons", "military_group": "japan"},
         {"unit": unit}, {"unit": unit, "military_group": "japan"})
    emit("unit_to_unit_abilities_junctions", {"unit_name": base, "ability": "shrapnel_shot"},
         {"unit_name": unit, "ability": ability}, {"unit_name": unit, "ability": ability})
    emit("unit_abilities", {"key": "shrapnel_shot"},
         {"key": ability, "bullet_text": config["ability_name"],
          "info_card_tooltip_text": config["ability_description"],
          "button_tooltip_text": config["ability_name"] + " ||" + config["ability_description"]},
         {"key": ability})
    emit("unit_special_abilities", {"key": "shrapnel_shot"},
         {"key": ability, "active_time": config["ability_active_time"],
          "num_uses": config["ability_uses"], "activated_projectile": projectile}, {"key": ability})
    emit("projectiles", {"key": "boshin_armstrong_gun_shell"},
         {"key": projectile, "explosion_type": explosion}, {"key": projectile})
    emit("projectiles_explosions", {"key": "boshin_armstrong_gun_shell"},
         {"key": explosion, "detonation_radius": config["blast_radius"],
          "detonation_damage": config["blast_damage"],
          "explosion_particle_effect": "Cannon_common_air_explosion_lrg",
          "explosion_particle_effect_on_ground": "Cannon_common_air_explosion_lrg"}, {"key": explosion})
    strings = {
        "units_on_screen_name_" + unit: config["display_name"],
        "unit_description_texts_description_text_" + unit: "Experimental artillery with a nuclear-shell firing ability.",
        "unit_description_texts_long_description_text_" + unit:
            "An experimental battery inspired by the FH70 155 mm towed howitzer. This prototype uses Armstrong guns with forty crew and four cannons. Nuclear Shell enables a brief high-blast firing window once per battle.",
        "unit_description_texts_strengths_and_weaknesses_" + unit:
            "Long-range artillery.||Experimental high-blast shells.||Protect the crew and keep friendly troops clear.",
        "unit_abilities_bullet_text_" + ability: config["ability_name"],
        "unit_abilities_info_card_tooltip_text_" + ability: config["ability_description"],
        "unit_abilities_button_tooltip_text_" + ability:
            config["ability_name"] + " ||" + config["ability_description"],
    }
    (ROOT / "build" / "modern_localisation.json").write_text(
        json.dumps([{"key": k, "text": v, "tooltip": True} for k, v in strings.items()], indent=2) + "\n",
        encoding="utf-8")
    print("Prepared ten namespaced tables and seven strings; ordinary Armstrong ammunition is unchanged.")


if __name__ == "__main__":
    main()
