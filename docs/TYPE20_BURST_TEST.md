## 2026-10-21: user confirms two bullets followed by a reload

User report: "yep confirmed two bullets and a reload" for the latest installed
Type 20 burst experiment. Record this as **user-confirmed two-shot burst behavior**.
Sustained automatic fire, the exact 0.15-second interval, and removal of the reload
animation are not confirmed. The earlier inconclusive control remains historical.
Preserve this working burst build before any further experiments. No combat,
animation, artillery, grenade, or installed pack changes were made for this update.
The detailed report below retains the pre-test expectations as historical context.

# Type 20 burst experiment — 2026-10-21

## Current status

**Installed; runtime unconfirmed.** This is a bounded two-event burst hypothesis,
not a verified automatic weapon. Neither the previous two-event test nor the
four-second path control established that custom firing events were consumed.
The user's direct comparison found similar pauses in both units.

## Engine evidence and limits

Read-only disassembly of the actual installed `empire.retail.dll`:
SHA256 `022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5`.
Reproduce with `python scripts/inspect_type20_engine.py`; requires the user-approved
local Capstone dependency under ignored `tools/python-research/` and pefile.
The DLL was never modified, loaded, injected into, or executed by this script.

- Constructor RVA `0xd3b380` selects the standard registry directory and calls
  the loader at `0xd5c670`; a conditional also selects a custom directory.
- Loader `0xd5c670` calls `0xd5ca50`. Its VFS enumeration uses `*.txt`
  (literal VA `0x116a23f0`) and the directory argument. This supports a distinct
  registry TXT inside `Animations/Animation_Tables/`.
- Standard-directory literal VA `0x1169d0c8` and custom-directory literal
  `0x1169d0e8` resolve to the actual animation-table directories.
- Event-registration instructions near RVA `0xd39e91` register `FIRE_TIME`
  and `FIRE_TIME_2`. The next numbered slot is `IMPACT_TIME`, not FIRE_TIME_3.
  **Registration is not proof that the infantry controller dispatches both shots.**
- Machine-readable bounded disassembly: `build/engine-research/type20-disassembly.json`.

The old shared-registry approach had an uncertain selection path. A shared-file
conflict has **not** been proven to be the cause. A unique registry removes that
shared override and gives us a more isolated experiment. No evidence yet proves
sustained automatic infantry fire or a custom firing mechanism is supported.

## Changes

Only the separate experimental unit is changed:
`steel_sakura_type20_automatic_fire_test`.

- Unique registry: `animations/animation_tables/steel_sakura_type20_burst.txt`.
  No replacement of the shared `animation_tables.txt` is included.
- Full private musket combat fragment replaces only FIRE and KNEEL_FIRE paths.
- Human 48-bone firing clips retain the original skeleton, muzzle positions,
  and frame data. Source frames `[0,2,4,0,2,4,5,...]` repeat an early motion segment
  before completing recovery. This is a rough retiming, not a new Howa animation.
- Standing markers: 0.05/0.20 seconds; kneeling: 0.00/0.15 seconds.
- Private rifle fragment maps its eight reload states to existing standing or
  kneeling aim clips, replacing lever-cycle visuals. The actual reload timer is
  unchanged. This does not implement magazine changes or establish automatic fire.
- Independent projectile/equipment keys from the previous experimental unit
  remain. Reload, range, damage, projectile count, firing mechanism and other DB
  combat values are unchanged. `firing_mechanism` remains the observed `none`.
- Existing Spencer/Tosa weapon and soldier visuals remain placeholders.
- The original 20 working fallback payloads, including grenades/artillery, are
  byte-identical. The earlier failed builds and observations are preserved.

## Build, installation and rollback

Build and validate: `powershell -File scripts/build_type20_burst.ps1`

Build, validate and install: `powershell -File scripts/build_type20_burst.ps1 -Install`

Revalidate existing output: `python scripts/type20_burst.py validate`

Restore the preserved working pack: `python scripts/type20_burst.py rollback`

Close the game before install or rollback. The installer refuses unknown installed
pack hashes, extra Steel & Sakura packs, or a running Shogun process. It backs up
the installed pack, `mod_list.txt` and `user.script.txt` before copying. It preserves
loading configuration and checks the installed hash. Backup folders retain the
historical `type20-path-control-` prefix because the safe installer is reused.

Current generated build: `build/steel_sakura_type20_burst.pack`.
Installed: `D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack`.
SHA256: `0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270`.
Installation record and exact backup: `build/type20-burst/installation.json`.

Offline checks: PFH3 structure; no RPFM metadata; all eight new tables and
localization round-trip through RPFM; complete fragment file references; unit to
registry/equipment/projectile references; unchanged DB combat values; exact source
frame remapping, finite animation data, skeletons, durations and shot times;
20 fallback payloads preserved; installed/build hash equality. These checks do not
prove the registry is selected at runtime or a second projectile is emitted.

## Short test at 1–10 FPS

1. Fully restart the game. Sengoku Custom Battle → Oda → ranged infantry.
   Select **TYPE20 BURST TEST - two timed shots** alongside the unchanged DIAG/EXP
   working riflemen. If the new name is absent, stop: this build is not being seen.
2. Use a stationary enemy in range, a short single-rank frontage and normal speed.
   Toggle fire at will off, select the test unit, then order it to fire.
3. Watch one identifiable soldier over several cycles. Expected hypothesis:
   two discharges about 0.15 seconds apart, then a pause, with aimed recovery
   instead of the repeating-rifle lever motion. Compare the fallback separately.
4. Toggle fire at will off after firing and check that shots stop normally.
5. Report the exact name, whether lever cycling disappeared, and whether there
   were **two actual shots** per soldier/cycle. Sound, smoke and projectiles can
   assist, but duplicated motion or increased kills alone are insufficient proof.
   At 1 FPS the 0.15-second separation may be unobservable; report it as uncertain.

If aimed recovery changes but there is only one projectile, private animation
selection is stronger evidence but the second-shot dispatch hypothesis has failed.
Preserve that outcome; do not compensate by lowering reload or increasing damage.
If neither animation nor firing changes, investigate registry loading/selection
before further event tuning. Sustained automatic fire remains an open engine
question until a reproducible runtime mechanism is established.
