"""Validate combined Oda selection, ability chains, and exact release contents."""
import hashlib
import json
import struct
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def check():
    manifest = json.loads((ROOT / "build/combined/manifest.json").read_text())
    if manifest.get("diagnostic_mode"):
        from validate_combat_diagnostic import check_diagnostic
        return check_diagnostic(manifest)
    tables = manifest["tables"]
    data = {name: [dict(zip(t["fields"], (next(iter(c.values())) for c in row))) for row in t["rows"]] for name, t in tables.items()}
    inf, art = "SteelSakura_Automatic_Rifle_Squad", "SteelSakura_Modern_Artillery"
    units = {r["key"]: r for r in data["units"]}
    assert set(units) == {inf, art}, "Exactly two units required"
    for key, unit in units.items():
        assert all(unit[field] for field in ("mp_available_early", "mp_available_middle", "mp_available_late"))
        assert not any(unit[field] for field in ("religion_requirement", "resource_requirement", "additional_building_level_requirement"))
        assert any(r == {"key": key, "faction": "oda", "allowed": True} for r in data["units_to_exclusive_faction_permissions"])
        assert any(r["unit"] == key and r["military_group"] == "japan" for r in data["units_to_groupings_military_permissions"])
        assert any(r["Unit"] == key for r in data["uniforms"])
    assert units[art]["multiplayer_category"] == "mp_siege_and_stealth"
    assert units[inf]["multiplayer_category"] == "mp_gun"
    stats = {r["key"]: r for r in data["unit_stats_land"]}
    assert stats[inf]["men"] == 40
    assert stats[art]["guns"] == 4 and stats[art]["men"] == 40
    assert stats[art]["articulated_entity"] == "gun_train_2_horse"
    assert stats[art]["can_fire_mounted_whilst_moving"] is False
    abilities = {r["key"]: r for r in data["unit_abilities"]}
    special = {r["key"]: r for r in data["unit_special_abilities"]}
    for unit, ability in ((inf, "steel_sakura_throw_grenades"), (art, "steel_sakura_nuclear_shell")):
        assert any(r["unit_name"] == unit and r["ability"] == ability for r in data["unit_to_unit_abilities_junctions"])
        assert ability in abilities and ability in special and abilities[ability]["requires_effect_enabling"] is False
        assert any(r["key"] == ability for r in data["unit_info_card_abilities_strings"])
        assert sum(ability in a["destination"] for a in manifest["assets"]) == 8
    assert special["steel_sakura_throw_grenades"]["activated_projectile"] == "grenade"
    nuclear = special["steel_sakura_nuclear_shell"]["activated_projectile"]
    projectile = next(r for r in data["projectiles"] if r["key"] == nuclear)
    assert any(r["key"] == projectile["explosion_type"] for r in data["projectiles_explosions"])
    # Reject accidentally overriding any vanilla ability, unit, projectile or explosion key.
    for name in ("units", "unit_stats_land", "unit_abilities", "unit_special_abilities", "projectiles", "projectiles_explosions"):
        base = json.loads((ROOT / f"build/inventory/table_{name}.json").read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
        keys = {next(iter(row[0].values())) for row in base["table_data"]}
        assert all(row["key"] not in keys for row in data[name]), f"Vanilla override in {name}"
    pack = ROOT / "build/steel_sakura_combined_test.pack"
    raw = pack.read_bytes()
    assert raw[:4] == b"PFH3"
    count, size = struct.unpack_from("<II", raw, 16)
    pos, offset, packed = 32, 32 + size, {}
    for _ in range(count):
        length = struct.unpack_from("<I", raw, pos)[0]
        end = raw.index(b"\0", pos + 4)
        name = raw[pos + 4:end].decode().replace("\\", "/")
        assert name not in packed and not name.endswith(".rpfm_reserved")
        packed[name] = raw[offset:offset + length]
        pos, offset = end + 1, offset + length
    assert pos == 32 + size and offset == len(raw)
    expected = {"db/" + table["table"] + "/steel_sakura_combined" for table in tables.values()}
    expected |= {"text/db/steel_sakura_combined.loc"} | {a["destination"] for a in manifest["assets"]}
    assert set(packed) == expected
    for asset in manifest["assets"]:
        assert packed[asset["destination"]] == Path(asset["source"]).read_bytes()
    sha = hashlib.sha256(raw).hexdigest().upper()
    report = json.loads((ROOT / "build/combined/rpfm-report.json").read_text(encoding="utf-8-sig"))
    assert report["pack_sha256"] == sha
    report["references_and_release_contents"] = "VERIFIED"
    report["manifest_sha256"] = hashlib.sha256((ROOT / "build/combined/manifest.json").read_bytes()).hexdigest().upper()
    (ROOT / "build/combined/validation-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"VERIFIED offline: two Oda units, ability/reference/UI chains, {count} release entries, SHA256 {sha}")
    print("Runtime milestone remains PENDING_USER_CONFIRMATION")


if __name__ == "__main__":
    check()
