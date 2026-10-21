"""Replace the combined manifest with an explicit, reversible combat/ability diagnostic."""
import hashlib
import json
from copy import deepcopy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/combined"
INF = "SteelSakura_Automatic_Rifle_Squad"
ART = "SteelSakura_Modern_Artillery"


def base(name):
    t = json.loads((ROOT / f"build/diagnostic/base_{name}.json").read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
    return t, [f["name"] for f in t["definition"]["fields"]]


def vals(fields, row):
    return dict(zip(fields, (next(iter(c.values())) for c in row)))


def main():
    manifest = json.loads((OUT / "manifest.json").read_text())
    tables = manifest["tables"]
    def change(name, key, modifications):
        entry = tables[name]
        field = "unit_name" if name == "unit_to_unit_abilities_junctions" else "key"
        rows = [r for r in entry["rows"] if vals(entry["fields"], r)[field] == key]
        if len(rows) != 1:
            raise ValueError(f"Expected one {name} row {key}")
        for name, value in modifications.items():
            cell = rows[0][entry["fields"].index(name)]
            cell[next(iter(cell))] = value
    def clone(name, match, modifications):
        t, fields = base(name)
        rows = [r for r in t["table_data"] if all(vals(fields, r)[k] == v for k, v in match.items())]
        if len(rows) != 1:
            raise ValueError(f"Ambiguous vanilla source {name} {match}")
        row = deepcopy(rows[0])
        for k, v in modifications.items():
            cell = row[fields.index(k)]
            cell[next(iter(cell))] = v
        entry = tables.setdefault(name, {"table": name + "_tables", "version": t["definition"]["version"], "fields": fields, "rows": []})
        entry["rows"].append(row)
    # Remove inactive special-ammunition and custom-key UI experiments from this diagnostic.
    for name in ["unit_abilities", "unit_special_abilities", "projectiles", "projectiles_explosions", "unit_info_card_abilities_strings"]:
        tables.pop(name, None)
    tables["unit_to_unit_abilities_junctions"]["rows"] = []
    clone("unit_to_unit_abilities_junctions", {"unit_name": "Boshin_Inf_Special_Kisho_Ninjas", "ability": "blinding_grenade"}, {"unit_name": INF})
    clone("unit_to_unit_abilities_junctions", {"unit_name": "Boshin_Art_Armstrong_Guns", "ability": "shrapnel_shot"}, {"unit_name": ART})
    # One temporary, declared vanilla override: remove the ninja technology gate.
    # Keep vanilla ability text, projectile, duration, recharge and UI untouched.
    clone("unit_abilities", {"key": "blinding_grenade"}, {"requires_effect_enabling": False})
    change("unit_stats_land", INF, {"default_missile_type": "steel_sakura_diag_rifle", "core_loading_skill": 100, "ammo": 200})
    change("unit_stats_land", ART, {"gun_type": "steel_sakura_diag_armstrong", "core_loading_skill": 100, "ammo": 100})
    clone("projectiles", {"key": "boshin_repeating_rifle"}, {"key": "steel_sakura_diag_rifle", "base_reload_time": 1, "effective_range": 900, "damage": 3.0})
    clone("projectiles", {"key": "boshin_armstrong_gun_shell"}, {"key": "steel_sakura_diag_shell", "base_reload_time": 5, "effective_range": 900})
    clone("gun_types", {"gun_type": "boshin_armstrong_cannon"}, {"gun_type": "steel_sakura_diag_armstrong"})
    clone("gun_type_to_projectiles", {"gun_type": "boshin_armstrong_cannon"}, {"gun_type": "steel_sakura_diag_armstrong", "shot_type": "steel_sakura_diag_shell"})
    # Expose the real vanilla units as controls, changing ONLY frontend selection fields.
    for key, category, caste, name in [
        ("Boshin_Inf_Light_Tosa_Riflemen", "mp_gun", "ashigaru", "CONTROL - Tosa (120 men; shared Otomo projectile)"),
        ("Boshin_Art_Armstrong_Guns", "mp_siege_and_stealth", "special", "CONTROL - Armstrong (shared Otomo projectile)")]:
        clone("units", {"key": key}, {"multiplayer_category": category, "unit_caste": caste})
        # Military permission schema uses the separately inspected inventory.
        t = json.loads((ROOT / "build/inventory/table_units_to_groupings_military_permissions.json").read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
        fields = [f["name"] for f in t["definition"]["fields"]]
        if not any(vals(fields, r)["unit"] == key and vals(fields, r)["military_group"] == "japan" for r in t["table_data"]):
            row = deepcopy(next(r for r in t["table_data"] if vals(fields, r)["unit"] == "Art_European_Cannons" and vals(fields, r)["military_group"] == "japan"))
            cell = row[fields.index("unit")];cell[next(iter(cell))] = key
            tables["units_to_groupings_military_permissions"]["rows"].append(row)
        permissions = tables["units_to_exclusive_faction_permissions"]
        row = deepcopy(permissions["rows"][0]);cell = row[permissions["fields"].index("key")];cell[next(iter(cell))] = key;permissions["rows"].append(row)
        manifest["localisation"].append({"key": "units_on_screen_name_" + key, "text": name, "tooltip": True})
    labels = {INF: "DIAG RIFLE - reload 1 / range 900", ART: "DIAG GUNS - reload 5 / range 900"}
    for entry in manifest["localisation"]:
        for key, label in labels.items():
            if entry["key"] == "units_on_screen_name_" + key:
                entry["text"] = label
            elif entry["key"].startswith("unit_description_texts_") and entry["key"].endswith(key):
                entry["text"] = "TEMPORARY ENGINE DIAGNOSTIC. Reduced reload is not automatic fire. Vanilla ability controls only."
    manifest["localisation"] = [r for r in manifest["localisation"] if not r["key"].startswith("unit_abilities_")]
    manifest["assets"] = [a for a in manifest["assets"] if a["destination"].startswith("ui/units/")]
    manifest["diagnostic_mode"] = "COMBAT_AND_VANILLA_BUTTONS_V1"
    manifest["temporary_overrides"] = ["blinding_grenade: requires_effect_enabling=false (also unlocks vanilla ninja button while this pack is enabled)", "Vanilla Tosa/Armstrong frontend category/caste/name and Oda permissions only; no control combat stats changed"]
    manifest["ui_binding"] = "Use unmodified vanilla button names Blinding Grenades and Shrapnel Shot; do not represent these as final custom skills"
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Diagnostic applied: unique normal projectiles/gun; vanilla ability projectiles unchanged; four selection entries including two controls")


if __name__ == "__main__":
    main()
