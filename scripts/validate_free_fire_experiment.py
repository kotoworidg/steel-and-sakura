"""Assert the optional mechanism experiment leaves every unrelated payload unchanged."""
import hashlib
import json
import struct
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def entries(path):
    raw = path.read_bytes()
    if raw[:4] != b"PFH3":
        raise ValueError("Expected PFH3")
    flags, deps, depsize, count, size = struct.unpack_from("<5I", raw, 4)
    if flags != 3 or deps or depsize:
        raise ValueError("Unexpected pack flags/dependencies")
    pos, offset, output = 32, 32 + size, {}
    for _ in range(count):
        length = struct.unpack_from("<I", raw, pos)[0]
        end = raw.index(b"\0", pos + 4)
        name = raw[pos + 4:end].decode().replace("\\", "/")
        if name in output or name.endswith(".rpfm_reserved"):
            raise ValueError("Duplicate entry/editor metadata")
        output[name] = raw[offset:offset + length]
        pos, offset = end + 1, offset + length
    if pos != 32 + size or offset != len(raw):
        raise ValueError("Invalid pack index")
    return output


def main():
    evidence = json.loads((ROOT / "build/automatic-research/experiment-rpfm-evidence.json").read_text(encoding="utf-8-sig"))
    fallback, experiment = Path(evidence["fallback"]), Path(evidence["experiment"])
    before, after = entries(fallback), entries(experiment)
    assert before.keys() == after.keys()
    changed = [k for k in before if before[k] != after[k]]
    assert set(changed) == {"db/unit_stats_land_tables/steel_sakura_combined", "text/db/steel_sakura_combined.loc"}
    a = evidence["before_stats"]["DBRFileInfo"][0]["table"]
    b = evidence["after_stats"]["DBRFileInfo"][0]["table"]
    assert a["definition"] == b["definition"]
    fields = [f["name"] for f in a["definition"]["fields"]]
    diffs = []
    for old, new in zip(a["table_data"], b["table_data"]):
        key = next(iter(old[fields.index("key")].values()))
        for field, x, y in zip(fields, old, new):
            if x != y:
                diffs.append((key, field, x, y))
    assert diffs == [("SteelSakura_Automatic_Rifle_Squad", "firing_mechanism", {"StringU16": "matchlock"}, {"StringU16": "none"})]
    oldloc = evidence["before_loc"]["LocRFileInfo"][0]["table"]["table_data"]
    newloc = evidence["after_loc"]["LocRFileInfo"][0]["table"]["table_data"]
    assert len(oldloc) == len(newloc)
    ld = [(x[0], x[1], y[1]) for x, y in zip(oldloc, newloc) if x != y]
    assert len(ld) == 1 and ld[0][0] == {"StringU16": "units_on_screen_name_SteelSakura_Automatic_Rifle_Squad"}
    report = {"status": "VERIFIED_OFFLINE_ONLY", "runtime_status": "UNTESTED", "implemented": "Firing-scheduler experiment, not automatic fire", "fallback": str(fallback), "experiment": str(experiment),
              "fallback_sha256": hashlib.sha256(fallback.read_bytes()).hexdigest().upper(), "experiment_sha256": hashlib.sha256(experiment.read_bytes()).hexdigest().upper(),
              "changed_pack_entries": changed, "combat_change": "Only infantry firing_mechanism matchlock -> none", "unchanged": "All projectiles, reload values, damage, animations, artillery, abilities, control units and UI assets"}
    (ROOT / "build/automatic-research/free-fire-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
