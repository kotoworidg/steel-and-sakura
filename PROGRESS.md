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
