> Current result: the user tested the separate Type 20 unit and reports no automatic fire. The two-event experiment failed its gameplay objective. A one-shot animation-path control is now installed; see [TYPE20_PATH_CONTROL.md](docs/TYPE20_PATH_CONTROL.md). Historical build details below are retained.

# Current Type 20 research status

2026-10-21: the research pass found real numbered human firing events.
See [technical report](docs/TYPE20_RESEARCH.md) and
[test checklist](tests/type20-event-test.md).

Installed: data/steel_sakura_combined_test.pack, with the new separate
Steel & Sakura Type 20 Automatic Fire Test alongside the unchanged riflemen.
This is an unconfirmed two-event experiment, not working automatic fire.
All original rifle, grenade, artillery and recruitment pack payloads are preserved.

Current test is COMBAT_AND_VANILLA_BUTTONS_V1. Expected diagnostic button names
are Blinding Grenades and Shrapnel Shot; original named custom skills are not
implemented by this control test. See docs/COMBAT_DIAGNOSTIC.md.

# Combined test installation — corrected 2026-10-21

Install `steel_sakura_combined_test.pack` directly into:
`D:\Games\Total War - SHOGUN 2\data`.

`data\MyMods` was the wrong installation destination for this setup. Historical
notes describing that folder are superseded. The active user script references
filenames in `data`; the previous loaded infantry pack there was older than the
copy we updated in MyMods. Artillery had never been installed.

## Build and install

Close the game. From the project directory:

```powershell
pwsh -NoProfile -File scripts/build_combat_diagnostic.ps1
python scripts/install_combined.py --dry-run
python scripts/install_combined.py
```

Configuration is in `src/install_config.json`. The installer requires a matching
RPFM/offline validation receipt, backs up the root `mod_list.txt`, the active
`%APPDATA%\The Creative Assembly\Shogun2\scripts\user.script.txt`, and every
existing approved Steel & Sakura pack before writing anything to the game.
It preserves each configuration's encoding and all unrelated mod entries.

Only the combined pack is enabled in both loading lists. Obsolete Steel & Sakura
packs from `data` and `data\MyMods` are moved into the project backup, preserving
their original bytes. Otomo, the intro-skip mod, vanilla packs and saves are not
installation targets. The installer verifies unrelated mod hashes and vanilla file metadata and writes
`build/combined/install-receipt.json` with installed hash and backup location.

## Test and rollback

Use original Sengoku Custom Battle, faction **Oda**. Look under matchlock/gun
infantry for **Modern Infantry Squad (Type 20)** and siege/artillery for
**Modern Artillery Battery (FH70)**. See `docs/COMBINED_TEST.md`.

Rollback using the exact backup named in the install receipt: restore both
loading configurations and the old packs to the relative game paths recorded
under `previous-copies`. Move the combined pack out of `data` if it was absent
before installation. Preserve unrelated files and saves.

This remains a test milestone until the user confirms both units and both
ability buttons appear. Neither automatic rifle fire nor grenade throwing is
claimed working. Tosa and Armstrong graphics remain placeholders.
