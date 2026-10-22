## 2026-10-22: artillery Nuclear Shell test installed — gameplay pending

[Current artillery report](docs/ARTILLERY_NUCLEAR_TEST.md). Oda artillery/siege:
**FH70 BATTERY - NUCLEAR TEST**, four Armstrong placeholder guns; intended button
**Nuclear Shell (TEST)**. One 15-second activation, private radius-40/damage-100
explosion, existing large explosion visual. No mushroom cloud is implemented.
The user approved the temporary shared Shrapnel Shot relink; other assigned
artillery also receive this test ammunition/label while enabled. Working rifle,
grenade and Suppression Fire data are unchanged. Pack installed directly in data;
backups and installed/build hash verified. No gameplay success is claimed yet.
Rollback: `python scripts/artillery_nuclear.py rollback`.

## 2026-10-21: native Suppression Fire R2 installed with user approval

The user approved the temporary shared native-ability override. Installed hash:
`1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD`.
Oda ranged infantry: **TYPE20 SUPPRESSION FIX R2**; expected native button:
**Suppression Fire**, configured for 30 seconds active / 120 seconds recharge.
Backups and installed/build hash checks completed; loading files unchanged.
Button visibility, activation and firing behavior await gameplay confirmation.
Animations and firing statistics were not changed in R2. Other native Suppression
Fire users receive the approved shared projectile/unlock behavior while enabled.
Rollback: `python scripts/type20_native_suppression.py rollback`.
Exact installation/backup record: `build/type20-native-suppression/installation.json`.
Earlier prepared/not-installed statements below are historical.

## 2026-10-21: dummy ability failed; native-key R2 built, not installed

User reports no Suppressive Fire button and only the existing paired firing.
Do not count the preceding build as a working ability or continuous fire.
[Native R2 report](docs/TYPE20_NATIVE_SUPPRESSION_FIX.md) gives the exact fix:
real suppression_fire assignment, native button unlock, and private projectile
relink. This uses shared native definitions and awaits explicit shared-scope
approval before installation. Animations and firing statistics are unchanged.
The current installed pack remains the preceding build until approval/install.

## 2026-10-21: single-button Suppressive Fire test installed — runtime pending

Latest report: [TYPE20_SUPPRESSION_TEST.md](docs/TYPE20_SUPPRESSION_TEST.md).
New Oda ranged infantry: **TYPE20 SUPPRESSIVE AUTO TEST**, intended button
**Suppressive Fire**. Tests an unused registered engine identity, private activated
projectile and two-shot 0.10-second timing. Longer individual bursts and continuous
fire remain unconfirmed. The user confirmed the previous unit fires paired shots
without a reload animation; all 60 preceding payloads remain byte-identical.
Artillery, grenades and vanilla Suppression Fire are unchanged.
Build/install: `powershell -File scripts/build_type20_suppression.ps1 -Install`.
Rollback to the preceding confirmed behavior: `python scripts/type20_suppression.py rollback`.

## 2026-10-21: separate automatic-cycle trial installed; runtime pending

See [TYPE20_AUTO_CYCLE.md](docs/TYPE20_AUTO_CYCLE.md) for evidence, exact changes,
validation, installation, rollback and gameplay test. New Oda ranged infantry:
**TYPE20 AUTO CYCLE TEST - continuous trial**. The user-confirmed
**TYPE20 BURST TEST - two timed shots** remains available unchanged alongside it.
The new unit combines a 0.30-second two-event firing clip, short aimed recovery
states, and an experimental zero projectile reload timer. Continuous fire is not
confirmed. All 39 prior payloads are byte-identical. Artillery and grenades unchanged.
Build/install: `powershell -File scripts/build_type20_auto_cycle.ps1 -Install`.
Restore confirmed burst build: `python scripts/type20_auto_cycle.py rollback`.

## 2026-10-21: isolated Type 20 burst test installed — runtime unconfirmed

Current instructions and engine evidence: [TYPE20_BURST_TEST.md](docs/TYPE20_BURST_TEST.md).
Oda ranged infantry: **TYPE20 BURST TEST - two timed shots**. Unique registry,
two timed events 0.15 s apart, repeated source recoil poses, and aimed recovery.
Combat DB statistics and all 20 working fallback payloads are unchanged.
No sustained automatic-fire success is claimed. The previous path control was
inconclusive. Build/validate/install: `powershell -File scripts/build_type20_burst.ps1 -Install`.
Rollback: `python scripts/type20_burst.py rollback`. See the report for exact
installed hash, backup record and short gameplay test. Historical entries follow.

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
