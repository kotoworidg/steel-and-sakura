"""Install only the validated combined test pack directly in the game's data folder."""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def edit_list(raw, filename):
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        encoding = "utf-16"
    elif raw.startswith(b"\xef\xbb\xbf"):
        encoding = "utf-8-sig"
    else:
        encoding = "utf-8"
    text = raw.decode(encoding)
    pattern = r'(?im)^[ \t]*mod[ \t]+"(?:MyMods[\\/])?steel_sakura_[^"\r\n]+\.pack"[ \t]*;[ \t]*'
    other_before = re.sub(pattern, "", text)
    ending = "\r\r\n" if "\r\r\n" in text else ("\r\n" if "\r\n" in text else "\n")
    result = other_before
    if result and not result.endswith(("\r", "\n")):
        result += ending
    result += f'mod "{filename}";' + ending
    if re.sub(pattern, "", result).rstrip("\r\n") != other_before.rstrip("\r\n"):
        raise ValueError("Unrelated configuration changed")
    return result.encode(encoding)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = json.loads((ROOT / "src/install_config.json").read_text())
    game = Path(config["game_root"]).resolve()
    data = (game / config["install_subdirectory"]).resolve()
    if data != game / "data":
        raise ValueError("Installation must be directly in data")
    name = config["pack_filename"]
    if name != "steel_sakura_combined_test.pack":
        raise ValueError("Unexpected destination filename")
    source = ROOT / "build" / name
    report = json.loads((ROOT / "build/combined/validation-report.json").read_text())
    if report.get("references_and_release_contents") != "VERIFIED" or report.get("pack_sha256") != sha(source):
        raise ValueError("Build does not match combined validation report")
    manifest = ROOT / "build/combined/manifest.json"
    if report.get("manifest_sha256") != sha(manifest):
        raise ValueError("Manifest changed after validation")
    scripts = Path(os.environ["APPDATA"]) / "The Creative Assembly/Shogun2/scripts"
    configs = [game / "mod_list.txt", scripts / "user.script.txt"]
    allowed_names = set(config["retired_pack_filenames"]) | {name}
    folders = [data, game / config["legacy_subdirectory"]]
    packs = []
    for folder in folders:
        for pack in folder.glob("steel_sakura*.pack"):
            if pack.name not in allowed_names or pack.resolve().parent != folder.resolve():
                raise ValueError(f"Unexpected Steel Sakura pack; inspect manually: {pack}")
            packs.append(pack)
    for cfg in configs:
        if not cfg.is_file():
            raise ValueError(f"Expected loading configuration missing: {cfg}")
    edits = {cfg: edit_list(cfg.read_bytes(), name) for cfg in configs}
    # Preserve hashes of all unrelated .pack files at both locations.
    all_unrelated = [p for folder in folders for p in folder.glob("*.pack") if p.name not in allowed_names]
    unrelated = {str(p): sha(p) for p in all_unrelated if p.stat().st_size < 20_000_000}
    vanilla_metadata = {str(p): (p.stat().st_size, p.stat().st_mtime_ns) for p in all_unrelated if p.stat().st_size >= 20_000_000}
    print("DESTINATION", data / name)
    print("RETIRED COPIES", [str(p) for p in packs])
    if args.dry_run:
        print("DRY RUN: no changes")
        return
    backup = ROOT / "backups" / ("combined-install-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True)
    # Back up every configuration and old pack before any game/configuration write.
    for cfg in configs:
        dest = backup / ("mod_list.txt" if cfg == configs[0] else "user.script.txt")
        shutil.copy2(cfg, dest)
        if sha(cfg) != sha(dest):
            raise ValueError("Configuration backup verification failed")
    for pack in packs:
        dest = backup / "previous-copies" / pack.relative_to(game)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pack, dest)
        if sha(pack) != sha(dest):
            raise ValueError("Pack backup verification failed")
    target = data / name
    shutil.copy2(source, target)
    if sha(target) != sha(source):
        raise ValueError("Installed pack mismatch")
    for cfg, content in edits.items():
        cfg.write_bytes(content)
        if cfg.read_bytes() != content:
            raise ValueError("Configuration write mismatch")
    for pack in packs:
        if pack == target:
            continue
        # Move exact approved obsolete packs outside both game directories.
        dest = backup / "retired-installed" / pack.relative_to(game)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pack), str(dest))
    for folder in folders:
        remaining = list(folder.glob("steel_sakura*.pack"))
        expected = [target] if folder == data else []
        if sorted(remaining) != sorted(expected):
            raise ValueError("Unexpected remaining Steel Sakura pack")
    for file, expected_metadata in vanilla_metadata.items():
        if (Path(file).stat().st_size, Path(file).stat().st_mtime_ns) != expected_metadata:
            raise ValueError("Vanilla file metadata changed")
    for file, expected_hash in unrelated.items():
        if sha(Path(file)) != expected_hash:
            raise ValueError("Unrelated pack changed")
    receipt = {"installed": str(target), "pack_sha256": sha(target), "backup": str(backup),
               "configs": {str(p): sha(p) for p in configs}, "unrelated_pack_hashes": unrelated, "vanilla_metadata": vanilla_metadata,
               "retired": [str(p) for p in packs if p != target], "runtime_status": "PENDING_USER_CONFIRMATION"}
    (ROOT / "build/combined/install-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("INSTALLED", json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
