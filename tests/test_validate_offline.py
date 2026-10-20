"""Offline regression checks, including a deliberately corrupted source row."""

import json
import tempfile
import unittest
from pathlib import Path
from shutil import copy2
from sys import path

ROOT = Path(__file__).resolve().parents[1]
path.insert(0, str(ROOT / "scripts"))
from validate_offline import check  # noqa: E402


class OfflineValidationTests(unittest.TestCase):
    def test_current_project(self):
        result = check(ROOT)
        self.assertEqual(result["errors"], [], result["errors"])

    def test_rejects_wrong_soldier_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source" / "infantry").mkdir(parents=True)
            (root / "src").mkdir(parents=True)
            (root / "build" / "inventory").mkdir(parents=True)
            for source in (ROOT / "assets" / "infantry").rglob("*.tga"):
                target = root / "assets" / "infantry" / source.parent.name / source.name
                target.parent.mkdir(parents=True, exist_ok=True)
                copy2(source, target)
            copy2(ROOT / "src" / "infantry_localisation.json", root / "src" / "infantry_localisation.json")
            for source in (ROOT / "source" / "infantry").glob("*.json"):
                copy2(source, root / "source" / "infantry" / source.name)
            for source in (ROOT / "build" / "inventory").glob("*.json"):
                if source.name.startswith(("table_", "existing_mod_", "loc_")):
                    copy2(source, root / "build" / "inventory" / source.name)
            copy2(ROOT / "build" / "steel_sakura_infantry_prototype.pack", root / "build" / "steel_sakura_infantry_prototype.pack")
            file = root / "source" / "infantry" / "unit_stats_land.json"
            data = json.loads(file.read_text(encoding="utf-8"))
            data["row"][data["fields"].index("men")]["I32"] = 41
            file.write_text(json.dumps(data), encoding="utf-8")
            result = check(root)
            self.assertEqual(result["status"], "FAILED")
            self.assertTrue(any("40 soldiers" in x for x in result["errors"]))

    def test_rejects_missing_localisation_key(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source" / "infantry").mkdir(parents=True)
            (root / "src").mkdir(parents=True)
            (root / "build" / "inventory").mkdir(parents=True)
            for source in (ROOT / "assets" / "infantry").rglob("*.tga"):
                target = root / "assets" / "infantry" / source.parent.name / source.name
                target.parent.mkdir(parents=True, exist_ok=True)
                copy2(source, target)
            for source in (ROOT / "source" / "infantry").glob("*.json"):
                copy2(source, root / "source" / "infantry" / source.name)
            for source in (ROOT / "build" / "inventory").glob("*.json"):
                if source.name.startswith(("table_", "existing_mod_", "loc_")):
                    copy2(source, root / "build" / "inventory" / source.name)
            copy2(ROOT / "build" / "steel_sakura_infantry_prototype.pack", root / "build" / "steel_sakura_infantry_prototype.pack")
            file = root / "src" / "infantry_localisation.json"
            data = json.loads((ROOT / "src" / "infantry_localisation.json").read_text(encoding="utf-8"))
            data["entries"][0]["key"] = "wrong_key"
            file.write_text(json.dumps(data), encoding="utf-8")
            result = check(root)
            self.assertEqual(result["status"], "FAILED")
            self.assertTrue(any("observed key patterns" in x for x in result["errors"]))


if __name__ == "__main__":
    unittest.main()
