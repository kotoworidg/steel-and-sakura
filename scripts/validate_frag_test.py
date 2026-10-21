"""Verify grenade-only changes and the authorized shared ability relink."""
import hashlib
import json
from pathlib import Path
from validate_free_fire_experiment import entries
ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / "build/fragmentation-test/manifest.json").read_text())
    fallback, test = Path(manifest["fallback"]), Path(manifest["experiment"])
    old, new = entries(fallback), entries(test)
    assert old.keys() <= new.keys()
    assert all(new[k] == v for k, v in old.items()), "An existing combat, UI, artillery or ability payload changed"
    expected = {"db/" + t["table"] + "/steel_sakura_frag_test" for t in manifest["tables"].values()}
    assert new.keys() - old.keys() == expected and len(expected) == 3
    tables = {}
    for name, table in manifest["tables"].items():
        rows = []
        base = json.loads((ROOT / f"build/diagnostic/base_{name}.json").read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
        fields = [f["name"] for f in base["definition"]["fields"]]
        assert fields == table["fields"] and table["version"] == base["definition"]["version"]
        for row, source in zip(table["rows"], table["sources"]):
            original = next(r for r in base["table_data"] if next(iter(r[0].values())) == source["key"])
            assert len(row) == len(original)
            result = dict(zip(fields, (next(iter(c.values())) for c in row)))
            before = dict(zip(fields, (next(iter(c.values())) for c in original)))
            assert result == dict(before, **source["changes"])
            assert all(x.keys() == y.keys() for x, y in zip(row, original))
            rows.append(result)
        tables[name] = rows
    special = tables["unit_special_abilities"]
    assert len(special) == 1 and special[0]["key"] == "blinding_grenade"
    assert special[0]["activated_projectile"] == "steel_sakura_frag_projectile_v1"
    projectiles = {r["key"]: r for r in tables["projectiles"]}
    assert set(projectiles) == {"steel_sakura_frag_projectile_v1", "steel_sakura_frag_fragment_v1"}
    assert projectiles["steel_sakura_frag_projectile_v1"]["explosion_type"] == "steel_sakura_frag_explosion_v1"
    assert projectiles["steel_sakura_frag_projectile_v1"]["base_reload_time"] == 20
    explosion = tables["projectiles_explosions"][0]
    assert explosion["key"] == "steel_sakura_frag_explosion_v1" and explosion["detonation_type"] == "shockwave"
    assert explosion["detonation_damage"] == 8.0 and explosion["detonation_radius"] == 4.0
    assert explosion["particle_type"] in projectiles and explosion["particle_number"] == 3
    assert projectiles[explosion["particle_type"]]["damage"] == 0.5
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest().upper()
    receipt = json.loads((ROOT / "build/fragmentation-test/rpfm-report.json").read_text(encoding="utf-8-sig"))
    assert receipt["pack_sha256"] == sha(test)
    report = {"status": "VERIFIED_OFFLINE_ONLY", "runtime": "PENDING_USER_TEST", "fallback": str(fallback), "test": str(test),
              "fallback_sha256": sha(fallback), "test_sha256": sha(test), "existing_entries_unchanged": len(old), "new_entries": sorted(expected),
              "rifle": "ALL_EXISTING_PAYLOADS_UNCHANGED", "artillery": "ALL_EXISTING_PAYLOADS_UNCHANGED", "button_assignment_and_ui": "UNCHANGED",
              "authorized_shared_effect": "All users of blinding_grenade temporarily use the new fragmentation projectile", "automatic_fire": "NOT_IMPLEMENTED"}
    (ROOT / "build/fragmentation-test/validation-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
