"""Create a combined Oda diagnostic build from the preserved unit prototypes."""
import json
from copy import deepcopy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "build/inventory"
OUT = ROOT / "build/combined"
INF = "SteelSakura_Automatic_Rifle_Squad"
ART = "SteelSakura_Modern_Artillery"


def table(name):
    return json.loads((INV / f"table_{name}.json").read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]


def row_values(fields, row):
    return dict(zip(fields, (next(iter(c.values())) for c in row)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tables = {}
    for folder in ("infantry", "modern_artillery"):
        for path in sorted((ROOT / "source" / folder).glob("*.json")):
            doc = json.loads(path.read_text())
            name = doc["table"].removesuffix("_tables")
            entry = tables.setdefault(name, {"table": doc["table"], "version": doc["version"], "fields": doc["fields"], "rows": []})
            if entry["version"] != doc["version"] or entry["fields"] != doc["fields"]:
                raise ValueError("Incompatible source definitions")
            entry["rows"].append(deepcopy(doc["row"]))
    # Give both units explicit observed Oda permissions. Do not override other units.
    def clone(name, match, changes):
        base = table(name)
        fields = [f["name"] for f in base["definition"]["fields"]]
        matches = [r for r in base["table_data"] if all(row_values(fields, r)[k] == v for k, v in match.items())]
        if len(matches) != 1:
            raise ValueError(f"Ambiguous reference: {name} {match}")
        row = deepcopy(matches[0])
        for key, value in changes.items():
            cell = row[fields.index(key)]
            cell[next(iter(cell))] = value
        entry = tables.setdefault(name, {"table": name + "_tables", "version": base["definition"]["version"], "fields": fields, "rows": []})
        entry["rows"].append(row)
    for unit in (INF, ART):
        clone("units_to_exclusive_faction_permissions", {"key": "Inf_Missile_Matchlock_Ashigaru_Oda", "faction": "oda"}, {"key": unit, "allowed": True})
    clone("uniforms", {"Unit": "Boshin_Inf_Light_Tosa_Riflemen", "Faction": ""}, {"Uniform_Name": "Default_" + INF, "Unit": INF})
    # Keep the mobile artillery class, while using the observed Sengoku frontend category/caste/icon.
    entry = tables["units"]
    for row in entry["rows"]:
        v = row_values(entry["fields"], row)
        changes = {"mp_available_early": True, "mp_available_middle": True, "mp_available_late": True,
                   "religion_requirement": "", "resource_requirement": "", "additional_building_level_requirement": ""}
        if v["key"] == ART:
            changes.update(multiplayer_category="mp_siege_and_stealth", unit_caste="special", unit_type_icon="siege")
        for key, value in changes.items():
            cell = row[entry["fields"].index(key)]
            cell[next(iter(cell))] = value
    loc = json.loads((ROOT / "src/infantry_localisation.json").read_text())["entries"]
    loc += json.loads((ROOT / "build/modern_localisation.json").read_text())
    names = {INF: "Modern Infantry Squad (Type 20)", ART: "Modern Artillery Battery (FH70)"}
    for entry in loc:
        for key, name in names.items():
            if entry["key"] == "units_on_screen_name_" + key:
                entry["text"] = name
    ability_sources = [("blinding_grenade", "steel_sakura_throw_grenades", "Throw Grenades"),
                       ("shrapnel_shot", "steel_sakura_nuclear_shell", "Nuclear Shell")]
    assets = []
    paths = json.loads((INV / "all_data_local_paths.json").read_text(encoding="utf-8-sig"))
    for vanilla, custom, label in ability_sources:
        clone("unit_info_card_abilities_strings", {"key": vanilla},
              {"key": custom, "bullet_text": label, "tooltip_text": "Experimental " + label + ". Gameplay behavior requires testing."})
        # All source paths were observed in data.pack. Only namespace-derived destinations are hypotheses.
        observed = [p for p in paths if p.startswith("ui/") and
                    ("/button_" + vanilla + "_" in p or p.endswith("/" + vanilla + "_icon.tga"))]
        if len(observed) != 8:
            raise ValueError(f"Expected seven states and an icon for {vanilla}: {len(observed)}")
        for source in observed:
            disk = OUT / "vanilla-ui" / source
            if not disk.is_file():
                raise ValueError(f"Missing extracted UI reference {source}")
            assets.append({"source": str(disk.resolve()), "destination": source.replace(vanilla, custom)})
    for path in sorted((ROOT / "assets/infantry").rglob("*.tga")):
        assets.append({"source": str(path.resolve()), "destination": "ui/units/" + path.relative_to(ROOT / "assets/infantry").as_posix()})
    document = {"tables": tables, "localisation": loc, "assets": assets,
                "runtime_status": "PENDING_USER_CONFIRMATION", "ui_binding": "Custom-key texture lookup hypothesis; engine acceptance unverified"}
    (OUT / "manifest.json").write_text(json.dumps(document, indent=2) + "\n")
    print(f"Prepared {len(tables)} tables, {sum(len(x['rows']) for x in tables.values())} rows, {len(assets)} assets")


if __name__ == "__main__":
    main()
