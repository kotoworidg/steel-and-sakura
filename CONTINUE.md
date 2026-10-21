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

## Automatic-fire investigation - 2026-10-21

User confirms faster reload. True automatic fire remains unimplemented. Actual
animation tables show human FIRE/reload states versus a separate Gatling
ENGINE_FIRE_LOOP and skeleton. Preserved the working faster-repeat fallback.
Built an optional one-variable matchlock-to-none scheduling experiment, not
automatic fire; artillery, ability and projectile payloads identical. Experiment
is not installed. See docs/AUTOMATIC_FIRE_FINDINGS.md for opt-in and rollback.

## Active engine diagnostic V1 - 2026-10-21

Both units were visible, but no custom buttons and no modern combat behavior
were observed. The previous custom UI experiment failed. Current diagnostic uses
separate normal combat projectile/gun keys and supported vanilla Blinding Grenades
and Shrapnel Shot buttons with vanilla special ammunition unchanged. One temporary
grenade technology-unlock flag affects vanilla ninjas while enabled. See
[combat diagnostic and low-FPS test](docs/COMBAT_DIAGNOSTIC.md). Rebuild with
scripts/build_combat_diagnostic.ps1. Milestone remains PENDING_USER_CONFIRMATION.

## Combined correction - 2026-10-21

Use scripts/build_combined.ps1 and scripts/install_combined.py. Install directly
into game data; older MyMods notes are superseded. Test Oda gun infantry and
siege/artillery. Both units/buttons require user confirmation. See
docs/COMBINED_TEST.md and INSTALL.md.

## Equipment direction — 2026-10-21

Active priorities: Modern Infantry Squad inspired by the Howa Type 20
(40 soldiers, Throw Grenades) and Modern Artillery Battery inspired by the
FH70 155 mm towed howitzer (four guns, Nuclear Shell). Tosa and Armstrong
assets remain temporary foundations. Tank deferred; aircraft stopped.
See [equipment findings and acceptance checks](docs/EQUIPMENT_DIRECTION.md).
New artillery checks preserve four guns and the observed mounted-firing flags.

## Current priorities — 2026-10-21

Focus on rifle infantry and artillery. Keep Chi-Ha research for later; do not
continue tank experiments now. Aircraft remains removed. Added a provisional
Throw Grenades skill to the rifle build using installed grenade references.
Seven DB rows and seven strings passed RPFM reopening; 119 offline checks and
three existing tests pass. Visible throwing and custom button remain unverified.
The installed infantry pack is still the older version. See `docs/RIFLE_GRENADES.md`.

## Scope decision — 2026-10-21

This decision supersedes earlier aircraft and four-unit plans below. Stop all
Zero/aircraft development. Prioritize the rifle squad and artillery. Investigate
the Chi-Ha only against the acceptance gate in `source/tank/README.md`; exclude
it from the playable release until that gate passes. No evidence currently
proves a tank implementation possible or impossible.

# Continue this project later

Use this prompt in a future Codex session:

> Continue Steel & Sakura from this repository. Read README.md, PROGRESS.md, RESEARCH.md, LIMITATIONS.md, ARCHITECTURE.md, TESTING.md, and docs/technical-findings.md first. The target is the original non-Steam Shogun 2 Sengoku campaign with FoTS installed at `D:\Games\Total War - SHOGUN 2`. Preserve original archives and saves; back up before changes. One 40-man infantry prototype has been built and statically validated with English localization and original UI cards, but no gameplay test has occurred because the GPU was unavailable. The tank and visible flying Zero remain blocked research goals. Do not claim any feature works without in-game evidence or substitute an off-map airstrike for an aircraft. Rebuild with `pwsh -NoProfile -File scripts/build.ps1`, inspect `build/validation/offline-report.json`, and follow TESTING.md when the GPU is available. Resolve the GitHub repository access issue before publishing; do not commit extracted game data, backups, tool binaries, or local packs.

Current local outputs live in `build/` and `dist/`, both ignored by Git. The project-local RPFM binary and configuration are also ignored. Retain the full workspace and backup folders if a future session needs to rebuild without redownloading tools.

An additional **uninstalled** artillery mechanics experiment can be rebuilt with `pwsh -NoProfile -File scripts/build.ps1 -ArtilleryTest`. It enables the game's existing `test_limber_gun` through two rows; it is not a Chi-Ha and is excluded from releases.

Aircraft research found bird fauna meshes and `bird_cycle.anim` in installed archives. This is only an ambient animation lead; no Zero model, flight control, or airborne unit has been demonstrated. See `source/aircraft/README.md`.
# Latest addition

The roster now includes a fourth requested unit, Modern Artillery Battery with
Nuclear Shell. Read `docs/MODERN_ARTILLERY.md`. Its separate optional pack has
passed offline table, localisation and reference validation, but has not been
installed or tested in-game. Ability UI binding remains unverified. Rebuild
using `scripts/build.ps1 -ModernArtillery`.
# Latest UI evidence

Read `docs/ABILITY_UI_FINDINGS.md`. Seven generic ability slots were observed
in the installed battle layout. Custom-key support is still unverified.
The existing Otomo mod changes shared Armstrong range and explosion values;
Nuclear Shell tests should begin below range 550. Reproduce observations with
the `inspect-ability-ui` action and `scripts/inspect_ability_evidence.py`.
