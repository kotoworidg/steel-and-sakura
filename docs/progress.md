# Progress log

## 2026-10-18 — Initial workspace inspection

- Project directory was empty and is not a Git repository.
- Python 3.13.4 is available locally.
- `sqlite3` is available on PATH; `rpfm`, `7z`, `7za`, and `packfilemanager`
  were not found on PATH.
- No game archives, executables, database exports, or existing project files
  were found in the project directory.
- Created an initial project scaffold and a read-only archive inventory script.
- No speculative database entries were written and no game files were changed.

## 2026-10-18 — User supplied installation path

- Installation path supplied: `D:\Games\Total War - SHOGUN 2`.
- Backed up the original scaffold to
  `backups/before-game-inventory-2026-10-18/` before changing the inventory
  script or generating reports.
- Confirmed the installation has a `data` directory and `shogun2.exe`.
- Found these direct `data` archives by filename and size: `boot.pack`,
  `bp_orig.pack`, `data.pack`, `data_fots.pack`, `local_en.pack`,
  `models.pack`, `models2.pack`, `movies.pack`, `movies2.pack`, `movies_fots.pack`,
  `shaders.pack`, `sound.pack`, `terrain.pack`, and
  `!!!!!!!!!!!!!!!!!!!!!run_you_fool_thron.pack`.
- Stopped the first inventory pass before it completed hashing the multi-GB
  archives. Updated the script so hashes are opt-in, then re-ran a fast
  metadata-only inventory. The earlier backup preserves the pre-change script.
- Game version and database schemas are still not verified.

## TODO

- [x] Obtain the exact Shogun 2 installation directory from the user.
- [x] Inventory installed `.pack` archives, sizes, and executable version
      metadata; hashes remain optional and were not computed.
- [ ] Run RPFM with a safe configuration location and verify pack opening and
      automation behavior.
- [x] Inspect locally cached Shogun 2 schema definitions; actual serialized
      table versions and game rows remain to be inspected from packs.
- [ ] Build and validate the automatic-rifle infantry prototype from verified
      schema and asset references.
- [ ] Research vehicle/tank mechanics and document a prototype only if existing
      supported mechanics and assets permit it.
- [ ] Research visible aircraft control, movement, and animation; report tested
      blockers and hypotheses separately.
- [ ] Add a reproducible build and validation command after toolchain discovery.
- [ ] Provide reversible manual-install instructions for any validated output.

## 2026-10-18 — Inventory and editor research

- Completed metadata-only inventory of 16 archives under the installation's
  `data` directory. Report: `build/inventory/game_inventory.json`.
- Inventory includes the base archive `data.pack`, FoTS archives `data_fots.pack`
  and `movies_fots.pack`, and a pre-existing enabled MyMods pack. None was
  opened or changed.
- Read Windows executable metadata and `mod_list.txt`; see
  `docs/technical-findings.md` for the exact values and limits.
- Upstream documentation confirms RPFM v4 had a CLI product for Total War pack
  management. The latest RPFM v5 release has no standalone CLI; it provides a
  WebSocket/MCP server and UI. Installed official RPFM v5.2.0 under
  `tools/rpfm-5.2.0/` after backing up the project. ZIP hash and size are
  recorded in `docs/technical-findings.md`.
- RPFM server startup failed before opening any pack because config-folder
  initialization returned Access Denied. RPFM resolves its default config in
  the user's roaming profile and stores its project-local redirect file there.
  No game files were accessed by RPFM.
- Made `backups/before-findings-update-2026-10-18/` before editing the current
  findings and progress records.
- Next: obtain approval to create or update RPFM's config redirect file in the
  default roaming config folder, pointing RPFM to a configuration directory in
  this project. Then test archive opening before exporting schemas or database
  rows. No game files need modification for that inspection.

## 2026-10-18 — Cached schema inspection

- Read the existing local RPFM Shogun 2 schema file without copying or changing
  it. Added `scripts/inspect_rpfm_schema.py` to report exact field names/types
  from a cached RON schema.
- Confirmed schema definitions for main units, land units, land unit stats,
  missile weapons/projectiles, variants, and articulated vehicle records; exact
  versions and representative fields are recorded in
  `docs/technical-findings.md`.
- This does not verify the serialized table versions or row contents inside
  the installed game packs. No unit database rows or speculative asset values
  have been created.

## 2026-10-18 — Pack decoding and infantry prototype

- Backed up project files to `backups/before-rpfm-server-2026-10-18/`.
- Created RPFM's reversible redirect at
  `%APPDATA%\FrodoWazEre\rpfm\config\config_folder.txt`, pointing into
  `tools/rpfm-config/data`. The existing older config tree was not edited.
- Started official RPFM v5.2.0. Its MCP endpoint opened installed `data.pack`
  and `data_fots.pack` as PFH3 Release packs.
- Decoded actual `unit_stats_land`, `units`, `building_units_allowed`,
  `projectiles`, and military grouping tables.
- Prepared four source rows under `source/infantry/` from installed FoTS Tosa
  Riflemen and Sengoku campaign rows, using only observed fields and values.
- Built `build/steel_sakura_infantry_prototype.pack` as PFH3 Mod. Reopened it
  with RPFM and verified four table rows and `men=40`. Size: 2,858 bytes;
  SHA-256: `2026DDAB3DEA7EEE69E0F7662DEA6558210A3E645572E5F5B82D62FBD3D015D8`.
- Added `scripts/build.ps1` for one-command preparation, packaging, and
  structural validation. No game file was changed or installed.
- Backed up the root `mod_list.txt` under
  `backups/before-prototype-install-2026-10-18/`, copied the prototype pack
  into `data\MyMods`, and appended its mod-list entry. The installed pack's
  SHA-256 matches the build output. Existing archives and saves were not
  changed.
- Inspected 14,322 paths in installed model packs. Found FoTS Armstrong and
  Gatling model and animation files; found no path named for an aircraft,
  A6M, Zero, airplane, or balloon in those model packs. This is an asset-path
  observation, not proof that visible flight is impossible.
- Re-ran `scripts/build.ps1` successfully. It rebuilt and reopened the pack,
  confirming four rows and 40 soldiers. Backed up the previous installed
  prototype before replacing it with this build. Current installed and project
  pack SHA-256: `05B476468698B579CD75D12AC6DEA2C5F2FA6327893BE91D09BA1BFD0E5D078A`.
- Inspected the pre-existing enabled MyMods pack read-only. It contains nine
  unit records and 65 recruitment rows, but none uses this prototype's unit
  key, unique index 1464, or recruitment key 4720. The source preparation
  script now checks for these collisions before writing rows.
- Attempted the computer-use workflow for an in-game check, but its Windows
  helper failed to initialize twice with a missing kernel-assets path. No
  gameplay behavior was observed.

## Current TODO

- [x] Open and decode installed game packs with RPFM.
- [x] Build and structurally validate the infantry prototype.
- [x] Add a one-command build and validation script.
- [ ] Test infantry recruitment and battlefield behavior in the original
      Sengoku campaign; refine from observed results.
- [ ] Investigate tank mechanics using existing artillery and vehicle assets.
- [ ] Investigate actual visible aircraft movement and animation.
- [ ] Package exactly three units only after feature evidence supports them.

## 2026-10-20 — English text and original icon assets

- Backed up the 32 tracked files before editing.
- Decoded installed English unit name/description localization and measured five installed TGA card formats without modifying game archives.
- Added four original English strings and five original TGA UI cards to the infantry pack. RPFM reopened the pack and extracted the card files with matching hashes.
- Passed 79 offline checks and three regression tests. Backed up the previous installed prototype and synced the current build; original game archives and saves remain untouched.
- In-game text/icon display and the other unit behaviors remain untested due to the unavailable GPU.
- Built and reopened an isolated two-row artillery mechanics pack to expose the installed dormant `test_limber_gun`. It is not installed or distributed; movement and recruitment remain untested.
