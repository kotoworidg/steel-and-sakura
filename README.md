## Equipment direction — 2026-10-21

Active priorities: Modern Infantry Squad inspired by the Howa Type 20
(40 soldiers, Throw Grenades) and Modern Artillery Battery inspired by the
FH70 155 mm towed howitzer (four guns, Nuclear Shell). Tosa and Armstrong
assets remain temporary foundations. Tank deferred; aircraft stopped.
See [equipment findings and acceptance checks](docs/EQUIPMENT_DIRECTION.md).
New artillery checks preserve four guns and the observed mounted-firing flags.

# Steel & Sakura

**Current scope (2026-10-21):** Develop the rifle squad and modern artillery. Defer the Chi-Ha for later. Aircraft development has stopped. The two built prototypes have passed structural checks; neither has gameplay evidence. The user currently cannot launch the game because there is no working GPU. See [PROGRESS.md](PROGRESS.md), [LIMITATIONS.md](LIMITATIONS.md), and [TESTING.md](TESTING.md).

Research and development workspace for a manual-install Shogun 2 mod targeting
the original Sengoku campaign with Fall of the Samurai content installed.

## Current status

The rifle squad now includes an experimental Throw Grenades ability: two
20-second activations with a 90-second recharge. See
[grenade findings and battle checks](docs/RIFLE_GRENADES.md). Visible throwing
and rifle animation compatibility are unverified; this build is not installed.

The active roster targets rifle infantry, modern artillery with a nuclear-shell
skill, and a Chi-Ha only if its required behavior can be demonstrated. Build this optional prototype with
`pwsh -NoProfile -File scripts/build.ps1 -ModernArtillery`.
It uses Armstrong gun graphics and a namespaced projectile-switching ability,
with one 30-second activation and increased blast parameters. It is not
installed. The ability button and actual firing behavior remain unverified;
see [modern artillery findings and instructions](docs/MODERN_ARTILLERY.md).

The first infantry prototype is in
`build/steel_sakura_infantry_prototype.pack`. RPFM reopened it and verified
seven DB rows, seven English localization strings, and five original TGA cards,
including a 40-soldier land unit. It has **not** been tested in
the game. Its weapon is based on the installed FoTS Tosa repeating rifle;
automatic fire remains unverified. The tank is deferred for later, with no custom unit entry.
The Zero is removed from active scope; previous aircraft findings are retained
only as historical documentation.

A separate, uninstalled artillery mechanics test pack can be built with
`pwsh -NoProfile -File scripts/build.ps1 -ArtilleryTest`. It exposes the
installed game's dormant limbered gun for future movement testing; it is not
a Chi-Ha and is excluded from release archives.

The prototype was copied to `data\MyMods` and added to the root
`mod_list.txt`. That file was backed up first; original archives and saves
remain unchanged. Project and mod-list backups are under `backups/`.

## Build and validation

On this Windows workspace, run:

```powershell
pwsh -NoProfile -File scripts/build.ps1
```

The script prepares source rows from decoded installed tables, starts the
project-local RPFM backend if needed, builds the pack, reopens it, and checks
the DB, localization, and icon files. RPFM's configuration redirect must point to
`tools/rpfm-config/data`. The tool bundle is in `tools/rpfm-5.2.0/`.

The command also runs offline data checks and Python regression tests.
Run `python scripts/package_release.py` to create a safe source ZIP, local
provisional pack ZIP, and SHA-256 manifest in `dist/`. Generated game data and
tool binaries are excluded from the shareable source ZIP.

Source rows and their provenance are under `source/infantry/`; decoded game
tables used for research are under `build/inventory/`. See
[technical findings](docs/technical-findings.md) and [progress](docs/progress.md).

## Read-only inventory

Once the game installation directory is known, run:

```powershell
python scripts/inventory_game.py "C:\path\to\Shogun 2"
```

The script only reads files. It inventories `.pack` archives and records sizes;
it does not unpack, edit, or copy game files. Use `--hash` to request SHA-256
hashes (this is slow for multi-gigabyte archives). Its report is written under
`build/inventory/` in this project.

RPFM v5.2.0 is stored under `tools/rpfm-5.2.0/`. Its backend uses a reversible
redirect at `%APPDATA%\FrodoWazEre\rpfm\config\config_folder.txt`, so all
generated RPFM settings remain in the project. The game installation remains
read-only. See [what is needed](docs/needed-from-user.md) for in-game checks.
