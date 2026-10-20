"""Safely extract a release ZIP inside a destination folder, omitting PDBs."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    archive = args.archive.resolve(strict=True)
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve(strict=True)

    total_written = 0
    count_written = 0
    with zipfile.ZipFile(archive) as bundle:
        for item in bundle.infolist():
            relative = Path(item.filename.replace("\\", "/"))
            if relative.is_absolute() or any(part in ("..", "") for part in relative.parts):
                raise ValueError(f"unsafe archive path: {item.filename!r}")
            target = (root / relative).resolve()
            if not target.is_relative_to(root):
                raise ValueError(f"archive path escapes destination: {item.filename!r}")
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if target.suffix.lower() == ".pdb":
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(item, "r") as source, target.open("wb") as output:
                while chunk := source.read(1024 * 1024):
                    output.write(chunk)
                    total_written += len(chunk)
            count_written += 1

    print(f"Extracted {count_written} files ({total_written:,} bytes) into {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
