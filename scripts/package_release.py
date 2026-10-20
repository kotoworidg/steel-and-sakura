"""Package safe project source and a separate local provisional pack."""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
PACK = ROOT / "build" / "steel_sakura_infantry_prototype.pack"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    if not PACK.is_file() or PACK.read_bytes()[:4] != b"PFH3":
        raise SystemExit("Missing valid-looking PFH3 prototype; run scripts/build.ps1 first")
    report = ROOT / "build" / "validation" / "offline-report.json"
    if not report.is_file():
        raise SystemExit("Missing passing offline report; run scripts/build.ps1 first")
    validation = json.loads(report.read_text(encoding="utf-8"))
    if validation["status"] != "VERIFIED" or validation["details"].get("pack_sha256") != sha(PACK):
        raise SystemExit("Offline report does not verify this pack; run scripts/build.ps1 first")
    OUT.mkdir(exist_ok=True)
    documents = sorted(ROOT.glob("*.md"))
    sources = documents + sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "scripts").glob("*.ps1"))
    sources += sorted((ROOT / "docs").glob("*.md"))
    sources += sorted((ROOT / "tests").glob("*.py")) + sorted((ROOT / "tests").glob("*.md"))
    sources += sorted((ROOT / "src").glob("*")) + sorted((ROOT / "assets").glob("*.md"))
    sources += sorted((ROOT / "assets" / "infantry").rglob("*.tga"))
    sources += sorted((ROOT / "assets" / "infantry").glob("*.md"))
    sources += sorted((ROOT / "source" / "tank").glob("*.md")) + sorted((ROOT / "source" / "aircraft").glob("*.md"))
    sources += [ROOT / ".gitignore"]
    source_zip = OUT / "steel-and-sakura-source.zip"
    with zipfile.ZipFile(source_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sources:
            if file.is_file():
                archive.write(file, file.relative_to(ROOT).as_posix())
    prototype_zip = OUT / "steel-and-sakura-infantry-prototype-local.zip"
    with zipfile.ZipFile(prototype_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(PACK, PACK.name)
        for name in ("INSTALL.md", "TESTING.md", "LIMITATIONS.md"):
            archive.write(ROOT / name, name)
        archive.write(report, "offline-report.json")
        archive.write(ROOT / "docs" / "RIFLE_GRENADES.md", "RIFLE_GRENADES.md")
    manifest = {file.name: {"bytes": file.stat().st_size, "sha256": sha(file)}
                for file in (source_zip, prototype_zip, PACK)}
    modern = ROOT / "build" / "steel_sakura_modern_artillery_prototype.pack"
    if modern.exists():
        modern_report = ROOT / "build" / "validation" / "modern-artillery-report.json"
        receipt = json.loads(modern_report.read_text(encoding="utf-8-sig"))
        if (receipt.get("status") != "VERIFIED_OFFLINE_ONLY" or
                receipt.get("source_provenance_and_reference_chain") != "VERIFIED" or
                receipt.get("pack_sha256") != sha(modern)):
            raise SystemExit("Modern artillery pack needs a matching offline validation report")
        modern_zip = OUT / "steel-and-sakura-modern-artillery-prototype-local.zip"
        with zipfile.ZipFile(modern_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(modern, modern.name)
            archive.write(ROOT / "INSTALL.md", "INSTALL.md")
            archive.write(ROOT / "docs" / "MODERN_ARTILLERY.md", "MODERN_ARTILLERY.md")
            archive.write(ROOT / "docs" / "ABILITY_UI_FINDINGS.md", "ABILITY_UI_FINDINGS.md")
            archive.write(modern_report, "modern-artillery-report.json")
        for file in (modern, modern_zip):
            manifest[file.name] = {"bytes": file.stat().st_size, "sha256": sha(file)}
    (OUT / "SHA256SUMS.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for name, info in manifest.items():
        print(f"{name}: {info['bytes']} bytes SHA256 {info['sha256']}")


if __name__ == "__main__":
    main()
