# Changelog

## 2026-10-25 — Type 20 playable upgrade and five-round candidate

- Live firing test attached and detached cleanly, but the user reported no visible
  change. Native firing-path/ammo counters do not verify five damaging projectiles.
  Correct launcher startup acknowledgement and visible access-error reporting;
  leave the requested candidate installed with the helper disabled. 36 tests pass.
- Preserve the confirmed two-shot source tag and archive; include the improved
  supported-mechanics two-shot build and guarded one-command restoration.
- Improve rifle precision, velocity, usable range, formation spacing, guard
  behavior and finite native ammunition; configure native timed rifle abilities.
- Add a paired pack and removable, version-locked x86 runtime which re-arms the
  current native primary firing slot three times while preserving engine shot
  validation, projectile creation, ammo debit and action lifetime. No EXE/DLL edit.
- Ship compiled helper, project-owned source, deterministic pack/ZIP generation,
  transactional installer, stop/report controls, both fallbacks and checksums.
- Pass 31 Python tests, 22 native-adapter cases / 839 assertions, synthetic debug
  transport cleanup, independent pack reopening and actual recovery dry-runs.
- Candidate installed with approval; runtime not attached and five-round combat
  remains unverified. Full-auto suppression and individual magazines are absent.

## 2026-10-20

- Added observed English unit localization keys and four authored strings.
- Added five original TGA cards at dimensions measured from installed game assets; packaged and round-trip checked them in RPFM.
- Expanded offline validation to localization and icon checks (79 passing checks, three regression tests), backed up the prior installed prototype, and synced the new pack.
- Built a separate, uninstalled artillery mechanics research pack from the installed dormant `test_limber_gun` using only observed recruitment and permission table schemas.
- Expanded aircraft research to installed bird fauna meshes, `bird_cycle.anim`, and the decoded `battle_entities` table; no aircraft unit was authored.
- Backed up the current project before offline handoff work.
- Added source intent/specifications, offline row/schema/key checks, a corruption regression test, and packaging/checksum automation.
- Added full research, architecture, limits, progress, install, test, and asset handoff documents.
- Backed up the earlier installed prototype and synced the latest statically validated pack.

## 2026-10-18

- Inventoried the installed Shogun 2 game and FoTS content.
- Automated RPFM v5.2.0 MCP operations; decoded installed DB schemas and rows.
- Built and reopened the first PFH3 infantry prototype from observed game rows.
- Installed the prototype into `data\MyMods` after backing up `mod_list.txt` and the prior output.
- Recorded artillery and model-pack observations. No in-game test was possible.
## 2026-10-20 — Modern artillery prototype

- Added a fourth requested unit with an experimental Nuclear Shell skill.
- Added installed-data preparation, isolated pack build, localisation,
  RPFM round-trip checks, reference validation and optional local ZIP.
- Preserved ordinary artillery keys; generated rows and packs remain ignored.
- Kept gameplay, custom ability UI and nuclear visuals explicitly unverified.
