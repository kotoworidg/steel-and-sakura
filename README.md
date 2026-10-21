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
