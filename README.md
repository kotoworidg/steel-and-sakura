## Type 20 playable release — 25 October 2026

**JSDF Type 20 Rifle Section 0.1.0** is built and offline-validated. It upgrades
projectile speed/precision, all-rank firing, spacing, finite ammunition and native
fire-control abilities while retaining the confirmed two-shot clips. Optional
native Suppression Fire has explicit shared scope. Five-round/full-auto fire and
per-soldier magazines remain unimplemented. No new gameplay success is claimed.

See [changes, installation and verification](docs/TYPE20_PLAYABLE.md).
Builds: `build/type20-playable/iteration-01/`; installable ZIP:
`dist/type20-playable/steel-and-sakura-type20-0.1.0.zip`.
The installed game remains on the preserved two-shot baseline. No game binaries
or unrelated Otomo files were changed. Historical development entries follow.

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

## Active infantry-only fragmentation test - 2026-10-21

Grenade activation and faster rifle reload are user-confirmed. True automatic
fire remains unimplemented; inspected data provides no verified human fire-loop
route. This pass preserves rifle, artillery, recruitment and UI payloads exactly.
Adds unique fragmentation assets and the user-approved temporary shared vanilla
grenade-ability relink. Both grenade baseline and rifle fallbacks are preserved.
See [fragmentation changes, test and rollback](docs/FRAGMENTATION_TEST.md).
Use scripts/build_frag_test.ps1 and scripts/select_frag_test.py test/fallback;
older combined-build commands restore earlier experiments. Gameplay confirmation
of grenade lethality and return to rifle fire remains pending.

## Active engine diagnostic V1 - 2026-10-21

Both units were visible, but no custom buttons and no modern combat behavior
were observed. The previous custom UI experiment failed. Current diagnostic uses
separate normal combat projectile/gun keys and supported vanilla Blinding Grenades
and Shrapnel Shot buttons with vanilla special ammunition unchanged. One temporary
grenade technology-unlock flag affects vanilla ninjas while enabled. See
[combat diagnostic and low-FPS test](docs/COMBAT_DIAGNOSTIC.md). Rebuild with
scripts/build_combat_diagnostic.ps1. Milestone remains PENDING_USER_CONFIRMATION.

# Steel & Sakura

Original non-Steam Shogun 2 Sengoku test mod, with FoTS assets installed.
Two active units: forty-soldier Type 20-inspired infantry with Throw Grenades,
and four-gun FH70-inspired towed artillery with Nuclear Shell. Tosa/Armstrong
assets remain placeholders. Tank deferred; aircraft stopped.

## Current milestone

PENDING_USER_CONFIRMATION: the first battle showed repeating-rifle behavior
and no grenade button. Artillery had never been installed. The combined test
addresses the data-folder destination, Oda permissions, Sengoku artillery
category, and missing custom ability UI textures. Custom key recognition and
both selectable buttons still require the user's game test.

Build: `pwsh -NoProfile -File scripts/build_combined.ps1`.
Install: `python scripts/install_combined.py` (supports `--dry-run`).
Target: `D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack`.
MyMods is a legacy inspection location, not an installation destination.

See [installation](INSTALL.md), [combined diagnosis/test](docs/COMBINED_TEST.md),
[equipment direction](docs/EQUIPMENT_DIRECTION.md) and [progress](PROGRESS.md).
Legacy unit builds remain for development; enable only the combined test pack.
