"""Read extracted UI bytes and installed table exports; never patch game UI."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "build" / "inventory"


def matching_rows(prefix, name, key):
    path = INV / f"{prefix}_{name}.json"
    if not path.exists():
        return None
    table = json.loads(path.read_text(encoding="utf-8-sig"))["DBRFileInfo"][0]["table"]
    fields = [field["name"] for field in table["definition"]["fields"]]
    rows = [dict(zip(fields, [next(iter(cell.values())) for cell in row]))
            for row in table["table_data"]]
    return [row for row in rows if row[fields[0]] == key]


def main():
    files = {}
    for relative in ("ui/battle ui/layout", "ui/common ui/unit_ability_entry",
                     "ui/templates/template.unit_ability_entry.luac", "ui/battle ui/root.luac"):
        path = INV / "ability-ui" / relative
        data = path.read_bytes()
        # These are byte-string observations, not a parser or decompilation.
        tokens = (b"BattleSpecialAbilityPanel", b"BattleSpecialAbilityButton",
                  b"generic_abilities", b"InitialiseBattleUIUnitAbilityEntry",
                  b"shrapnel_shot", b"steel_sakura_nuclear_shell")
        observations = {token.decode(): [m.start() for m in re.finditer(re.escape(token), data)]
                        for token in tokens}
        slots = sorted(set(m.group().decode() for m in
                           re.finditer(rb"button_ability[0-9]+_DY", data)))
        files[relative] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                           "token_offsets": observations, "slot_names": slots}
    comparisons = []
    for name, key in (("gun_types", "boshin_armstrong_cannon"),
                      ("gun_type_to_projectiles", "boshin_armstrong_cannon"),
                      ("projectiles", "boshin_armstrong_gun_shell"),
                      ("projectiles_explosions", "boshin_armstrong_gun_shell")):
        base = matching_rows("table", name, key)
        mod = matching_rows("existing_mod", name, key)
        item = {"table": name, "key": key, "base_matches": len(base or []),
                "existing_mod_matches": None if mod is None else len(mod)}
        if base and mod and len(base) == len(mod) == 1:
            item["differences"] = {field: {"base": value, "existing_mod": mod[0].get(field)}
                                   for field, value in base[0].items() if mod[0].get(field) != value}
        comparisons.append(item)
    report = {
        "status": "OBSERVED_OFFLINE_ONLY",
        "method": "Exact byte-token search, SHA-256 hashes and decoded table comparison",
        "runtime_tested": False,
        "ui_files": files,
        "shared_artillery_comparisons": comparisons,
        "limitations": [
            "Generic slots do not establish custom ability-key support or texture lookup rules.",
            "Lua byte strings are not a decompiled control-flow analysis.",
            "Table comparisons use the cached installed-mod exports, not a complete load-order resolver.",
            "A shared-key difference is a potential interaction; actual runtime precedence is untested."
        ]
    }
    target = INV / "ability-evidence-report.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {target}")
    print("Generic button slots:", ", ".join(files["ui/battle ui/layout"]["slot_names"]))
    for item in comparisons:
        for field, difference in item.get("differences", {}).items():
            print(f"{item['table']}.{field}: base={difference['base']} existing_mod={difference['existing_mod']}")


if __name__ == "__main__":
    main()
