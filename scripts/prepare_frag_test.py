"""Prepare new fragmentation assets and a reversible vanilla-ability relink."""
import hashlib
import json
from copy import deepcopy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/fragmentation-test"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    installed = Path(r"D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack")
    fallback = OUT / "working-infantry-grenade-fallback.pack"
    if fallback.exists() and fallback.read_bytes() != installed.read_bytes():
        raise ValueError("Installed version changed; restore the preserved fallback before rebuilding")
    if not fallback.exists():
        fallback.write_bytes(installed.read_bytes())
    tables = {}
    def clone(name, key, changes):
        t = json.loads((ROOT / f"build/diagnostic/base_{name}.json").read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
        fields = [f["name"] for f in t["definition"]["fields"]]
        rows = [r for r in t["table_data"] if next(iter(r[fields.index("key")].values())) == key]
        if len(rows) != 1:
            raise ValueError("Ambiguous vanilla source")
        row = deepcopy(rows[0])
        for field, value in changes.items():
            cell = row[fields.index(field)]
            cell[next(iter(cell))] = value
        if changes.get("key", key).startswith("steel_sakura_"):
            for prefix in ("base", "otomo"):
                path = ROOT / f"build/diagnostic/{prefix}_{name}.json"
                if not path.exists():
                    continue
                other = json.loads(path.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
                assert not any(next(iter(r[0].values())) == changes["key"] for r in other["table_data"]), "Key collision"
        entry = tables.setdefault(name, {"table": name + "_tables", "version": t["definition"]["version"], "fields": fields, "rows": [], "sources": []})
        entry["rows"].append(row)
        entry["sources"].append({"key": key, "changes": changes})
    clone("projectiles", "blinding_grenade", {"key": "steel_sakura_frag_projectile_v1", "explosion_type": "steel_sakura_frag_explosion_v1", "base_reload_time": 20})
    clone("projectiles", "grenade_fragment", {"key": "steel_sakura_frag_fragment_v1", "damage": 0.5})
    clone("projectiles_explosions", "grenade_blinding", {"key": "steel_sakura_frag_explosion_v1", "detonation_type": "shockwave", "detonation_radius": 4.0, "detonation_damage": 8.0, "particle_type": "steel_sakura_frag_fragment_v1", "particle_number": 3, "explosion_particle_effect": "explode_grenade", "explosion_particle_effect_on_ground": "explode_grenade"})
    clone("unit_special_abilities", "blinding_grenade", {"activated_projectile": "steel_sakura_frag_projectile_v1"})
    manifest = {"tables": tables, "fallback": str(fallback), "experiment": str(ROOT / "build/steel_sakura_frag_test.pack"), "fallback_sha256": hashlib.sha256(fallback.read_bytes()).hexdigest().upper(), "scope": "Authorized temporary shared ability relink; all users of blinding_grenade affected while enabled", "runtime": "UNTESTED", "rifle": "NO_COMBAT_OR_ANIMATION_CHANGES"}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Prepared unique fragmentation assets; original ability key, assignment, UI and timing retained")


if __name__ == "__main__":
    main()
