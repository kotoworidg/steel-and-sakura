"""Summarize exact installed pre-diagnostic rows and the vanilla/Otomo chain."""
import json
from pathlib import Path
from validate_combat_diagnostic import decoded, ROOT


def main():
    report = {"source": "RPFM decode of exact data/steel_sakura_combined_test.pack before diagnostic replacement",
              "infantry": {}, "artillery": {}, "collisions": {}}
    for label, custom, vanilla in [("infantry", "SteelSakura_Automatic_Rifle_Squad", "Boshin_Inf_Light_Tosa_Riflemen"),
                                   ("artillery", "SteelSakura_Modern_Artillery", "Boshin_Art_Armstrong_Guns")]:
        own = next(r for r in decoded("installed", "unit_stats_land") if r["key"] == custom)
        base = next(r for r in decoded("base", "unit_stats_land") if r["key"] == vanilla)
        report[label] = {"installed_stats": own, "vanilla_stats": base,
                         "actual_differences": {k: {"installed": v, "vanilla": base[k]} for k, v in own.items() if v != base[k]}}
    for name in ("units", "unit_stats_land", "projectiles", "unit_abilities", "unit_special_abilities"):
        own = [r["key"] for r in decoded("installed", name)]
        base = {r["key"] for r in decoded("base", name)}
        other = {r["key"] for r in decoded("otomo", name)}
        report["collisions"][name] = [k for k in own if k in base | other]
    for label, key in [("infantry", "boshin_repeating_rifle"), ("artillery", "boshin_armstrong_gun_shell")]:
        report[label]["base_projectile"] = next(r for r in decoded("base", "projectiles") if r["key"] == key)
        report[label]["otomo_projectile"] = [r for r in decoded("otomo", "projectiles") if r["key"] == key]
    report["ability_links"] = decoded("installed", "unit_to_unit_abilities_junctions")
    report["custom_abilities"] = decoded("installed", "unit_abilities")
    report["custom_special"] = decoded("installed", "unit_special_abilities")
    report["rapid_fire_reference"] = {
        "gatling_stats": next(r for r in decoded("base", "unit_stats_land") if r["key"] == "Boshin_Art_Gatling_Guns"),
        "gatling_gun": next(r for r in decoded("base", "gun_types") if r["gun_type"] == "boshin_gatling_gun"),
        "gatling_projectile": next(r for r in decoded("base", "projectiles") if r["key"] == "boshin_gatling_gun_bullet")}
    report["limits"] = ["No runtime memory inspection or engine instrumentation", "Known custom-key collisions checked against data.pack and active Otomo; not an exhaustive decoder for all pack formats", "Rifle primary_missile_weapon is an existing engine identifier, default_missile_type directly selects the projectile in this schema", "Artillery resolves gun_type through gun_types and gun_type_to_projectiles; no separate infantry weapon-to-projectile table observed"]
    target = ROOT / "build/diagnostic/combat-audit.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(target)
    for label in ("infantry", "artillery"):
        print(label, report[label]["actual_differences"])


if __name__ == "__main__":
    main()
