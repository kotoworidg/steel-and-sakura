"""Read-only inventory of Shogun 2 .pack files and likely game executables."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("install_dir", type=Path, help="Shogun 2 installation folder")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/inventory/game_inventory.json"),
        help="Report path, relative to the current directory by default",
    )
    parser.add_argument(
        "--hash",
        action="store_true",
        help="Compute SHA-256 for each archive (slow for multi-gigabyte game packs)",
    )
    args = parser.parse_args()

    root = args.install_dir.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"installation directory does not exist or is not a directory: {root}")

    archives = []
    executables = []
    # Game archives normally live in data/. Avoid unrelated browser caches,
    # logs, and redistributables elsewhere under the installation directory.
    scan_root = root / "data" if (root / "data").is_dir() else root
    for dirpath, dirnames, filenames in os.walk(scan_root):
        # Avoid traversing junctions/symlinks outside the requested tree.
        dirnames[:] = [name for name in dirnames if not (Path(dirpath) / name).is_symlink()]
        for filename in filenames:
            path = Path(dirpath) / filename
            suffix = path.suffix.lower()
            if suffix == ".pack":
                stat = path.stat()
                item = {"path": str(path.relative_to(root)), "size_bytes": stat.st_size}
                if args.hash:
                    item["sha256"] = sha256_file(path)
                archives.append(item)

    for path in root.iterdir():
        if path.is_file() and path.suffix.lower() == ".exe" and (
            "shogun" in path.name.lower() or "totalwar" in path.name.lower()
        ):
            executables.append({"path": path.name, "size_bytes": path.stat().st_size})

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "install_dir": str(root),
        "read_only": True,
        "pack_archives": sorted(archives, key=lambda item: item["path"].lower()),
        "likely_game_executables": sorted(executables, key=lambda item: item["path"].lower()),
        "archive_scan_root": str(scan_root),
        "hashes_computed": args.hash,
        "notes": [
            "Archive contents and database schemas are not parsed by this inventory script.",
            "Hashes are optional because game archives may be several gigabytes each.",
        ],
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Inventoried {len(archives)} .pack files; report: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
