"""Switch the active combined pack between grenade fallback and approved fragmentation test."""
import argparse
import datetime
import hashlib
import json
import os
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("test", "fallback"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    report = json.loads((ROOT / "build/fragmentation-test/validation-report.json").read_text())
    source = Path(report[args.mode])
    expected = report[args.mode + "_sha256"]
    if sha(source) != expected:
        raise ValueError("Source changed since verification")
    config = json.loads((ROOT / "src/install_config.json").read_text())
    game = Path(config["game_root"]).resolve()
    target = game / "data/steel_sakura_combined_test.pack"
    if target.parent != game / "data" or sha(target) not in {report["fallback_sha256"], report["test_sha256"]}:
        raise ValueError("Installed build changed; inspect before switching")
    if args.dry_run:
        print("Verified switch plan:", args.mode, source, "->", target, expected)
        return
    if sha(target) == expected:
        print("Requested version already installed")
        return
    extras = [p for folder in (game / "data", game / "data/MyMods") for p in folder.glob("steel_sakura*.pack") if p != target]
    if extras:
        raise ValueError("Other Steel Sakura packs present; do not duplicate units")
    backup = ROOT / "backups" / ("fragmentation-switch-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True)
    shutil.copy2(target, backup / target.name)
    configs = [game / "mod_list.txt", Path(os.environ["APPDATA"]) / "The Creative Assembly/Shogun2/scripts/user.script.txt"]
    originals = {p: p.read_bytes() for p in configs}
    for p, data in originals.items():
        (backup / p.name).write_bytes(data)
    shutil.copy2(source, target)
    if sha(target) != expected or any(p.read_bytes() != data for p, data in originals.items()):
        raise ValueError("Switch verification failed")
    print("Installed", args.mode, target, expected)
    print("Backup", backup)
    print("Rifle/artillery payloads unchanged; approved shared grenade ability relink is active in test mode")


if __name__ == "__main__":
    main()
