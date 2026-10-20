# Technical findings

## Verified locally

- The project directory was empty at the start of work and has no Git metadata.
- Python 3.13.4 is callable. `sqlite3.exe` is present on PATH.
- `rpfm`, `7z`, `7za`, and `packfilemanager` were not found via PowerShell's
  `Get-Command` lookup. This only verifies they are not exposed under those
  command names on PATH; it does not rule out GUI installs or other locations.
- The supplied installation path is `D:\Games\Total War - SHOGUN 2`; it has a
  `data` directory and `shogun2.exe`.
- The executable's Windows version metadata reports file version `1.1.0.0`,
  product version `3.1.0.0`, product name `Total War: SHOGUN 2`, and company
  `The Creative Assembly Ltd`. This is executable metadata, not confirmation of
  the runtime build or DLC entitlement.
- The data directory contains 14 direct `.pack` files, plus two under
  `data\MyMods`, for 16 files inventoried in total. This includes
  `data_fots.pack` and `movies_fots.pack`, consistent with FoTS data being
  present. A pre-existing `data\MyMods\mods_modern_units_otomo.pack` is listed
  in `mod_list.txt`; both it and the game archives were left unchanged.
- The `mod_list.txt` file is UTF-16 and lists
  `mods_modern_units_otomo.pack` as enabled.
- The inventory report is `build/inventory/game_inventory.json`. It lists
  relative paths and sizes; archive hashing is optional because several
  archives are multi-gigabyte. The first attempt to hash all archives was
  stopped before completion and no partial hash report was written.
- Two project backups were made before subsequent project changes:
  `backups/before-game-inventory-2026-10-18/` and
  `backups/before-findings-update-2026-10-18/`. No game files were changed.

## Pack editor research

- Downloaded the official latest Windows release, RPFM v5.2.0, from the
  maintainer's GitHub release. The ZIP is 293,948,083 bytes with local
  SHA-256
  `5880FA393EF8CBF961751B0229ACA40795747F4AA0042584A334673692AEDB61`.
  Its ZIP structure opened successfully. The copy in `tools/rpfm-5.2.0/`
  contains 263 extracted non-PDB files (360,814,725 bytes), including
  `rpfm_ui.exe` and `rpfm_server.exe`.
- The v5 release bundle has no `rpfm_cli.exe`. Upstream release history says
  the CLI was removed in v5.0. RPFM v5 instead exposes the headless backend by
  WebSocket and MCP. Its server documentation lists pack open/inspect commands
  and its localhost endpoints. This is scriptable, but it is not a traditional
  one-shot CLI.
- The v5.2.0 release notes say it adds initial support for Shogun 2: Complete
  Edition. The user's target is the original 2011 Windows game; compatibility
  with that exact installation remains unverified.
- The first server attempt failed to initialize its default config path with
  `Access is denied`. RPFM's actual redirect location is
  `%APPDATA%\FrodoWazEre\rpfm\config\config_folder.txt`. A small reversible
  redirect now points to `tools/rpfm-config/data`; the older config tree was
  not edited. The server then started successfully on localhost port 45127.
- Sources: [RPFM v5.2.0 release](https://github.com/Frodo45127/rpfm/releases/tag/v5.2.0),
  [RPFM server overview](https://frodo45127.github.io/rpfm/manual/server/overview.html),
  [RPFM settings implementation](https://github.com/Frodo45127/rpfm/blob/master/rpfm_server/src/settings.rs),
  [RPFM changelog](https://github.com/Frodo45127/rpfm/blob/master/CHANGELOG.md).

## Not yet verified

- Runtime game version and exact installed campaign/DLC state.
- Actual in-game rendering, recruitment, movement, and firing behavior of the
  infantry prototype.
- Whether Shogun 2 supports a custom tank as a battlefield-controlled unit.
- Whether a 3D aircraft can be independently controlled or animated in battle.

Installed pack contents and tool behavior have now been examined. Structural
pack validation alone does not establish gameplay behavior.

## Shogun 2 schema definitions found in the local RPFM cache

Read-only inspection found
`%APPDATA%\FrodoWazEre\rpfm\config\schemas\schema_sho2.ron` (6,772,328 bytes,
schema format version 5). It was not copied or modified. A project script,
`scripts/inspect_rpfm_schema.py`, extracts named definitions without changing
that source file.

The cached schema defines these relevant tables and latest definitions:

- `main_units_tables`, schema definition version 35 (49 fields): includes
  `unit`, `land_unit`, and `num_men`.
- `land_units_tables`, version 43 (59 fields): includes `key`, `man_entity`,
  `man_animation`, `primary_missile_weapon`, `reload`, and `primary_ammo`.
- `unit_stats_land_tables`, version 16 (113 fields): includes `men`, `guns`,
  `soldier_model`, `man_entity`, `man_animations_table`,
  `primary_missile_weapon`, `primary_missile_attack`, `firing_mechanism`, and
  `ammo`.
- `missile_weapons_tables` version 11 and
  `missile_weapons_to_projectiles_tables` version 0 define weapon/projectile
  links; `projectiles_tables` version 44 defines projectile properties.
- `unit_variants_tables` version 5 links a unit/variant to a unit card.
- `land_unit_articulated_vehicles_tables` version 4 contains articulated
  entity and ammo-caisson fields. These fields alone do not establish a generic
  vehicle movement system.

These were initially schema-definition versions only. The following section
records versions confirmed by decoding the installed pack.

## Installed pack and infantry findings

- RPFM v5.2.0 MCP opened installed `data.pack` and `data_fots.pack` as PFH3
  Release packs. RPFM loaded the Shogun 2 schema from the project-local config.
- In installed `data.pack`, RPFM decoded `unit_stats_land_tables` version 16
  (340 rows), `units_tables` version 13 (432 rows),
  `building_units_allowed_tables` version 2 (644 rows), `projectiles_tables`
  version 5 (114 rows), and
  `units_to_groupings_military_permissions_tables` version 0 (383 rows).
- `Boshin_Inf_Light_Tosa_Riflemen` has 120 men and references the installed
  `boshin_repeating_rifle` missile type, `boshin_man_rifle_trained` animation,
  and `boshin_spencer_bp_1` equipment theme. It is a real rapid-fire firearm
  prototype but not evidence of a fully automatic rifle mechanic.
- The first source row changes this unit's key and `men` to 40. A companion
  `units_tables` row is based on Sengoku Matchlock Ashigaru, with a new key,
  display name, description key, and unique index. Recruitment clones its
  observed `SHO_Castle_1_Fort` entry. Military grouping uses observed `japan`.
- The project output is a PFH3 Mod pack containing four DB files. RPFM reopened
  it and verified exactly one row in each file, expected table versions, and
  `men=40`. This is a structural validation, not an in-game result.
- The pack was installed into `data\MyMods` after backing up the root
  `mod_list.txt`; the original enabled mod entry remains. The installed copy's
  SHA-256 matches the project output. The next check is recruitment and battle
  behavior in the original Sengoku campaign.
- The other enabled MyMods pack was decoded read-only. Its nine unit rows and
  65 recruitment rows do not use this prototype's unit key, unique index
  1464, or recruitment key 4720. This checks direct key collisions in the
  observed pack; it does not establish full compatibility between mods.
- `scripts/build.ps1` completed preparation, packaging, reopen validation,
  offline checks, and regression tests in one command. After the 2026-10-20
  backup and sync, the current output and installed copy share SHA-256
  `EB2485BDAFEB2D52EFB41DCBFEB87D460BA7325034A99E528062DC0847B1161B`.
- The Windows computer-use helper failed to initialize twice, so an in-game
  test could not be performed in this turn. No gameplay success is claimed.

## Tank and aircraft observations

- Installed FoTS Armstrong and Gatling artillery rows use four guns and
  `gun_train_2_horse` as the articulated entity. Corresponding Armstrong and
  Gatling rigid model and animation paths exist in the installed model packs.
  This establishes an artillery prototype route for a tank experiment, but
  does not establish independent armored vehicle movement or a Chi-Ha model.
- A path scan of 14,322 entries from `models.pack` and `models2.pack` found no
  names matching aircraft, A6M, Zero, airplane, aeroplane, biplane, or balloon.
  It is not proof of an engine limitation. There is no visible flying-aircraft
  prototype yet, and no off-map strike is being substituted.
