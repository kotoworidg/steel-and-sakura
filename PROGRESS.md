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

Installed combined test directly into game data on 2026-10-21. SHA256 C60B0D87B9D3D0015333C3C3328B323156A19228E170BDD76D5B8EC14067B6E9. Both loading lists now enable only this Steel & Sakura pack; old copies archived under C:\Users\Lenovo\Documents\Codex\2026-10-18\you-are-my-lead-developer-for\backups\combined-install-20261021-185244-282860. Otomo hashes preserved. Milestone remains PENDING_USER_CONFIRMATION.

## Combined correction - 2026-10-21

Use scripts/build_combined.ps1 and scripts/install_combined.py. Install directly
into game data; older MyMods notes are superseded. Test Oda gun infantry and
siege/artillery. Both units/buttons require user confirmation. See
docs/COMBINED_TEST.md and INSTALL.md.

## User battle failure — 2026-10-21

User reports repeating-rifle behavior and failed grenades. The modern automatic
rifle target has not been achieved. Treat the grenade experiment as failed, not
working. User clarified that the grenade button is missing. Identical empty editor metadata
conflicts with the intro-skip pack; release cleanup now removes editor entries
while preserving every game payload. This does not repair grenade mechanics.

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

- Removed the Zero from active unit specifications at the user's request.
- Priorities: rifle squad, modern artillery, then conditional Chi-Ha feasibility.
- Tank is excluded from the playable release until movement, model, cannon and
  damage behavior are demonstrated together in-game.
- Existing artillery data establishes a test basis, not tank support.
- Preserved historical aircraft research and backed up changed project files.

# Progress and next work

## Completed offline

- [x] Backed up project states and the game's original mod list before changes. Latest project backup: `backups/before-offline-handoff-2026-10-20/`.
- [x] Inventoried local game packs and executable metadata without editing original archives.
- [x] Installed official RPFM v5.2.0 locally and automated its MCP pack operations.
- [x] Decoded installed schema/table rows, authored one 40-soldier infantry prototype from those rows, and built a PFH3 Mod pack.
- [x] Reopened the pack in RPFM and passed offline consistency/collision checks and regression tests.
- [x] Offline validator checks the referenced projectile, English localization keys, and original TGA headers; currently 79 checks and three regression tests pass.
- [x] Added four English unit strings and five original UI cards to the prototype pack; RPFM reopened the localization and extracted icon bytes match their sources.
- [x] Backed up the previously installed prototype under `backups/before-localisation-icon-sync-2026-10-20/` and synced the new build; project and installed hashes match.
- [x] Copied the prototype into `data\MyMods` and appended its name to `mod_list.txt` after backups; existing mod remains enabled.
- [x] Backed up the older installed prototype under `backups/before-offline-sync-2026-10-20/` and synced the latest validated pack; installed and project SHA-256 hashes match.
- [x] Recorded verified FoTS artillery and model-path observations; scanned model packs for aircraft names.
- [x] Built and reopened a separate, uninstalled two-row artillery mechanics pack that exposes the base game's dormant `test_limber_gun` for future testing.
- [x] Identified installed bird fauna meshes and an ambient bird animation as an aircraft research lead; decoded `battle_entities` without finding an aircraft/altitude route there.

## Pending

- [ ] Test original Sengoku campaign recruitment, battlefield spawn, rifle fire and reload, visual attachments, text/icon, and custom battle when a GPU is available.
- [ ] Fix any observed infantry runtime problems; add legitimate art/localization and revalidate.
- [ ] In-game test the separate artillery mechanics experiment for recruitment, movement, firing, and collision, then decide whether a physical Chi-Ha is feasible. A licensed model and compatible import path are missing.
- [ ] Identify and test a real visible airborne entity path for the A6M Zero; obtain an original/licensed model and animation pipeline.
- [ ] Package exactly three real units only after each can be demonstrated. Current pack intentionally contains only the infantry experiment.
- [ ] Publish to the user-provided GitHub repository once it is accessible; never push extracted game rows, packs, backups, or editor binaries without separate review.

See `docs/progress.md` for the detailed dated history and `docs/github.md` for repository access state.
# Modern artillery addition â€” 2026-10-20

- Backed up the 41 previously tracked project files to `backups/before-modern-artillery-2026-10-20`.
- User extended the roster to four units with modern artillery and a nuclear-shell skill.
- Inspected installed ability, projectile, explosion, uniform and localisation data.
- Built an optional PFH3 Mod pack with ten new DB rows and seven strings.
- RPFM reopened and compared all rows/strings; clone provenance and reference checks passed.
- Uses Armstrong graphics, a one-use 30-second firing ability, and larger blast values.
- TODO: verify custom ability button, projectile switching, firing-window round count,
  explosion behavior, recruitment and interactions with the existing Otomo mod in-game.
- No modern model or nuclear-specific visual effect exists yet. Pack remains uninstalled.
- Details: `docs/MODERN_ARTILLERY.md`; rebuild: `scripts/build.ps1 -ModernArtillery`.
# Ability UI research â€” 2026-10-20

- Backed up tracked sources under `backups/before-ability-ui-20261020-233734`.
- Extracted four installed UI files read-only; found seven generic ability slots.
- Added repeatable UI extraction and a hash/byte-offset evidence report.
- Compared shared Armstrong keys with the existing Otomo mod: range 550â†’600,
  explosion radius 4â†’5 and speed 10â†’15 are potential runtime interactions.
- Documented the range mismatch with Nuclear Shell and adjusted its manual test plan.
- TODO: establish custom button binding in-game; then decide whether to isolate
  ordinary ammunition from other mods. No runtime claims or UI binary edits.
- See `docs/ABILITY_UI_FINDINGS.md`.

Installed metadata-only conflict fix on 2026-10-21. All 13 game payloads are
byte-identical to the previous installed pack. The intro-skip pack was preserved.
This fixes shared editor-entry paths only; rifle and grenade mechanics remain failed.
