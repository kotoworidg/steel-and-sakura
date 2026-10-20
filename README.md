# Steel & Sakura

**Offline handoff status (2026-10-20):** One structurally validated, gameplay-untested infantry prototype exists. The physical Chi-Ha and visible flying A6M Zero remain blocked research goals. The user currently cannot launch the game because there is no working GPU. See [PROGRESS.md](PROGRESS.md), [LIMITATIONS.md](LIMITATIONS.md), and [TESTING.md](TESTING.md).

Research and development workspace for a manual-install Shogun 2 mod targeting
the original Sengoku campaign with Fall of the Samurai content installed.

## Current status

The first infantry prototype is in
`build/steel_sakura_infantry_prototype.pack`. RPFM reopened it and verified
four DB rows, including a 40-soldier land unit. It has **not** been tested in
the game. Its weapon is based on the installed FoTS Tosa repeating rifle;
automatic fire remains unverified. The tank and visible aircraft are research
tasks, with no unit entries authored yet.

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
the four DB rows. RPFM's configuration redirect must point to
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
