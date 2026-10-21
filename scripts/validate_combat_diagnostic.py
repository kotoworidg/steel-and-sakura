"""Verify diagnostic values, controls, and unmodified vanilla special ammunition."""
import hashlib
import json
import struct
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def decoded(prefix, name):
    path = ROOT / f"build/diagnostic/{prefix}_{name}.json"
    table = json.loads(path.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
    fields = [f["name"] for f in table["definition"]["fields"]]
    return [dict(zip(fields, (next(iter(c.values())) for c in row))) for row in table["table_data"]]


def check_diagnostic(manifest):
    tables = manifest["tables"]
    data = {n: [dict(zip(t["fields"], (next(iter(c.values())) for c in row))) for row in t["rows"]] for n, t in tables.items()}
    inf, art = "SteelSakura_Automatic_Rifle_Squad", "SteelSakura_Modern_Artillery"
    controls = {"Boshin_Inf_Light_Tosa_Riflemen", "Boshin_Art_Armstrong_Guns"}
    stats = {r["key"]: r for r in data["unit_stats_land"]}
    assert set(stats) == {inf, art}, "Control combat stats must never be overridden"
    assert stats[inf]["men"] == 40 and stats[inf]["ammo"] == 200 and stats[inf]["core_loading_skill"] == 100
    assert stats[art]["guns"] == 4 and stats[art]["ammo"] == 100
    assert stats[inf]["default_missile_type"] == "steel_sakura_diag_rifle"
    assert stats[art]["gun_type"] == "steel_sakura_diag_armstrong"
    p = {r["key"]: r for r in data["projectiles"]}
    assert set(p) == {"steel_sakura_diag_rifle", "steel_sakura_diag_shell"}
    assert (p["steel_sakura_diag_rifle"]["base_reload_time"], p["steel_sakura_diag_rifle"]["effective_range"], p["steel_sakura_diag_rifle"]["damage"]) == (1, 900, 3.0)
    assert (p["steel_sakura_diag_shell"]["base_reload_time"], p["steel_sakura_diag_shell"]["effective_range"]) == (5, 900)
    assert p["steel_sakura_diag_rifle"]["projectile_number"] == p["steel_sakura_diag_shell"]["projectile_number"] == 1
    gun = data["gun_types"][0]
    original = next(r for r in decoded("base", "gun_types") if r["gun_type"] == "boshin_armstrong_cannon")
    assert gun == dict(original, gun_type="steel_sakura_diag_armstrong")
    assert data["gun_type_to_projectiles"][0]["shot_type"] == "steel_sakura_diag_shell"
    assert data["gun_type_to_projectiles"][0]["gun_type"] == stats[art]["gun_type"]
    links = {(r["unit_name"], r["ability"]) for r in data["unit_to_unit_abilities_junctions"]}
    assert links == {(inf, "blinding_grenade"), (art, "shrapnel_shot")}
    # No special ammunition/ability timing overridden. Only the enabling gate changes.
    assert "unit_special_abilities" not in tables and "projectiles_explosions" not in tables
    vanilla_grenade = next(r for r in decoded("base", "unit_abilities") if r["key"] == "blinding_grenade")
    assert data["unit_abilities"] == [dict(vanilla_grenade, requires_effect_enabling=False)]
    units = {r["key"]: r for r in data["units"]}
    assert set(units) == {inf, art} | controls
    for key in units:
        assert any(r["key"] == key and r["faction"] == "oda" and r["allowed"] for r in data["units_to_exclusive_faction_permissions"])
        assert any(r["unit"] == key and r["military_group"] == "japan" for r in data["units_to_groupings_military_permissions"])
    for key in controls:
        before = next(r for r in decoded("base", "units") if r["key"] == key)
        assert {k for k, v in units[key].items() if v != before[k]} <= {"multiplayer_category", "unit_caste"}
    # Check projectile clones have no undeclared changes.
    for key, base_key, expected in [
        ("steel_sakura_diag_rifle", "boshin_repeating_rifle", {"key": "steel_sakura_diag_rifle", "base_reload_time": 1, "effective_range": 900, "damage": 3.0}),
        ("steel_sakura_diag_shell", "boshin_armstrong_gun_shell", {"key": "steel_sakura_diag_shell", "base_reload_time": 5, "effective_range": 900})]:
        before = next(r for r in decoded("base", "projectiles") if r["key"] == base_key)
        assert p[key] == dict(before, **expected)
    raw = (ROOT / "build/steel_sakura_combined_test.pack").read_bytes()
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
    expected = {"db/" + t["table"] + "/steel_sakura_combined" for t in tables.values()} | {"text/db/steel_sakura_combined.loc"} | {a["destination"] for a in manifest["assets"]}
    assert set(packed) == expected
    for asset in manifest["assets"]:
        assert packed[asset["destination"]] == Path(asset["source"]).read_bytes()
    sha = hashlib.sha256(raw).hexdigest().upper()
    report = json.loads((ROOT / "build/combined/rpfm-report.json").read_text(encoding="utf-8-sig"))
    assert report["pack_sha256"] == sha
    report.update(references_and_release_contents="VERIFIED", diagnostic_mode=manifest["diagnostic_mode"],
                  manifest_sha256=hashlib.sha256((ROOT / "build/combined/manifest.json").read_bytes()).hexdigest().upper(),
                  runtime_status="PENDING_USER_CONFIRMATION", special_ammunition="VANILLA_UNCHANGED")
    (ROOT / "build/combined/validation-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("VERIFIED OFFLINE: unique faster normal weapons, unchanged control combat rows, vanilla ability projectiles untouched")
    print("PENDING: observed cadence and visible Blinding Grenades / Shrapnel Shot buttons")


if __name__ == "__main__":
    manifest = json.loads((ROOT / "build/combined/manifest.json").read_text())
    check_diagnostic(manifest)
