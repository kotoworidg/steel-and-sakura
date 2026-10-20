# Manual installation and removal

The installed pack is an **untested infantry prototype** containing one new unit. The planned roster now has four units. A separate, uninstalled modern artillery prototype and its manual instructions are documented in [MODERN_ARTILLERY.md](docs/MODERN_ARTILLERY.md). Original game archives and saves are not overwritten.

## Existing installation

The project copied `build/steel_sakura_infantry_prototype.pack` to `D:\Games\Total War - SHOGUN 2\data\MyMods\steel_sakura_infantry_prototype.pack` and appended `steel_sakura_infantry_prototype.pack` to the root `mod_list.txt`. On 2026-10-20 the updated localization/icon pack was synced to that installed path after backing up the older copy under `backups/before-localisation-icon-sync-2026-10-20/`. The current installed and project pack SHA-256 is `A428212117948BE5776E4B56A7C45A9D367892374C782047FF0D101A35AB1D86`. The original mod list and earlier pack copies are in project `backups/`. The pre-existing `mods_modern_units_otomo.pack` entry was preserved. A future build in `build/` will not automatically replace the installed copy.

## Rebuild and install later

1. Keep a copy of `mod_list.txt` and any existing prototype pack before changing them.
2. From the project directory, run `pwsh -NoProfile -File scripts/build.ps1`; require a passing RPFM reopen and offline report.
3. Copy `build/steel_sakura_infantry_prototype.pack` to the game's `data\MyMods` directory. Check `mod_list.txt` for exactly one entry named `steel_sakura_infantry_prototype.pack`; append it only if absent, preserving the file's current encoding and all other entries. Do not rename or overwrite base archives.
4. When a GPU is available, launch the original Sengoku campaign and follow `TESTING.md`. Keep the prototype disabled for normal play until recruitment and battle behavior are observed.

The source ZIP cannot build a pack alone: it requires this Shogun 2/FoTS installation, the official RPFM v5.2.0 toolchain, and decoded local inputs. `scripts/rpfm_mcp.ps1 -Action probe` and `scripts/prepare_infantry_source.py` are the local extraction path; see `ARCHITECTURE.md`.

## Remove prototype

Remove only the prototype's line from `mod_list.txt`, preserving every other line and the encoding. The prototype `.pack` may then be moved out of `data\MyMods` after verifying its exact filename. Do not touch saves or original game archives. The project backups can restore the previous mod list if needed.
