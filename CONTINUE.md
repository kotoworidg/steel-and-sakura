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

## 2026-10-21: user confirms two bullets followed by a reload

User report: "yep confirmed two bullets and a reload" for the latest installed
Type 20 burst experiment. Record this as **user-confirmed two-shot burst behavior**.
Sustained automatic fire, the exact 0.15-second interval, and removal of the reload
animation are not confirmed. The earlier inconclusive control remains historical.
Preserve this working burst build before any further experiments. No combat,
animation, artillery, grenade, or installed pack changes were made for this update.
The detailed report below retains the pre-test expectations as historical context.

## 2026-10-21: isolated Type 20 burst test installed — runtime unconfirmed

Current instructions and engine evidence: [TYPE20_BURST_TEST.md](docs/TYPE20_BURST_TEST.md).
Oda ranged infantry: **TYPE20 BURST TEST - two timed shots**. Unique registry,
two timed events 0.15 s apart, repeated source recoil poses, and aimed recovery.
Combat DB statistics and all 20 working fallback payloads are unchanged.
No sustained automatic-fire success is claimed. The previous path control was
inconclusive. Build/validate/install: `powershell -File scripts/build_type20_burst.ps1 -Install`.
Rollback: `python scripts/type20_burst.py rollback`. See the report for exact
installed hash, backup record and short gameplay test. Historical entries follow.

## 2026-10-21: path-control gameplay result is inconclusive

The user initially reported: "yeah i think it work shot then wait 4 secs then shoots".
On direct comparison, the user then clarified: "Both units pause about the same".

Do not treat this as a successful positive control. It does not demonstrate a
control-specific delay or confirm that the private clip/event path is consumed.
The initial report describes a pause AFTER a shot; it does not measure latency
between entering FIRE and the first projectile. Automatic fire remains unimplemented.
No new pack was built or installed in response to this comparison.

Read-only follow-up:
- The existing data.pack path inventory lists 4,097 .anim files and 291 animation
  .txt files, including both standard and custom animation registries.
- No obvious separate compiled animation container was found in that inventory.
  This is not proof that no other pack/cache can affect selection.
- The actual empire.retail.dll contains standard/custom animation-table directory
  names, the battleconfiguration directory, FIRE_TIME and FIRE_TIME_2.
- A static PE audit records literal addresses and .text references for those strings:
  build/type20-path-control/engine-loader-evidence.json.
- Engine SHA256:
  022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5.
- Loader string references: standard registry RVA 0x59fe1; custom registry RVA
  0x59fc1 and 0xfd712b. FIRE_TIME reference RVA 0xd39e98; FIRE_TIME_2 RVA 0xd39eae.
  These are investigation leads, not recovered function semantics.
- RPFM's man_animations_table schema points to battle_animations_table/key, but
  that referenced table was not found in the inventoried packed DB paths.
  Do not invent a row/schema to fill the gap.
- No executable was modified, run, patched or injected. No software was installed.

Next gate: trace registry/table selection and event dispatch; seek a distinctive
animation-selection observation before any further burst experiment.
Keep the current installed pack unchanged until a supported next step is established.

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
