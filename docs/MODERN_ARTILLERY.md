# Modern Artillery Battery — provisional fourth unit

Added at the user's request on 2026-10-20, extending the original three-unit scope.

## Implemented locally

Separate optional pack: `build/steel_sakura_modern_artillery_prototype.pack`.
Ten new namespaced database rows and seven English localisation strings.
The prototype clones installed FoTS Armstrong guns: forty crew, four guns,
existing uniforms, model, animations, movement and ordinary ammunition.
Sengoku Fort recruitment and the `japan` military permission follow inspected
existing rows. Recruitment and custom battle availability are untested.

Nuclear Shell clones the installed `shrapnel_shot` ability structure:
unit → ability junction → special ability → activated projectile → explosion.
The custom ability requests one 30-second activation, using an Armstrong-type
impact shell with blast radius 70 and damage 100 in database units. These
magnitudes also occur in the installed `ship_magazine` explosion. They are
gameplay parameters, not physical nuclear simulation.

The visual uses the observed `Cannon_common_air_explosion_lrg` effect. There
is no modern howitzer mesh, mushroom cloud, fallout, radiation, or terrain
destruction implementation. The default Armstrong gun and its ammunition
are referenced, not overridden by this pack.

## Evidence and limits

- VERIFIED OFFLINE: actual installed schemas, row provenance and reference
  chain; PFH3 Mod encoding; RPFM reopened and compared every database cell
  and all seven localisation strings.
- PROVISIONAL: engine acceptance of a new ability key, selectable ability
  button, projectile switching, blast damage, friendly fire and visuals.
- The installed UI has shrapnel-specific button textures. No evidence yet
  proves it automatically creates a button for a custom key. This may need
  UI layout work and original button art after inspecting the UI definitions.
- A duration-based ability is **not guaranteed to fire exactly one shell**.
  Four guns may fire several nuclear-themed rounds, or fail to fire during
  the window because of reload timing. One activation is the current target.
- Existing `mods_modern_units_otomo.pack` contains gun/projectile tables.
  This prototype does not override those shared keys, so that mod may change
  ordinary artillery behavior. Test the prototype in isolation first.
- No game launch or battle test has been performed.

## Rebuild and tune

From the project directory:

```powershell
pwsh -NoProfile -File scripts/build.ps1 -ModernArtillery
python scripts/package_release.py
```

Uses the project's existing RPFM 5.2.0 setup, installed game and cached base
inventory from the initial inspection. `inspect-modern` refreshes ability,
uniform and explosion data. No game archives are written by these commands.
Edit authored values in `src/modern_artillery.json`. Generated game-derived
rows stay in ignored `source/modern_artillery/`, outside the source release.
The local prototype ZIP is for this licensed installation.

## Optional manual installation

This prototype has not been installed automatically. Back up the existing
game-root `mod_list.txt` and any previous copy of this optional pack first.
Copy the pack into `D:\Games\Total War - SHOGUN 2\data\MyMods`.
Following the installation's existing mod-list convention, append:

```text
steel_sakura_modern_artillery_prototype.pack
```

Preserve the mod list's existing encoding and entries. See `INSTALL.md` for
the installation's launcher caveats. To remove it, restore the backed-up
mod list and move only this optional pack out of `MyMods`. Do not touch saves.

## Next in-game checks

1. Use a disposable campaign/custom battle; confirm model and forty crew.
2. Confirm Fort recruitment and availability, then check normal shell fire.
3. Check that Nuclear Shell is selectable and has the correct text.
4. Activate while guns are loaded; record rounds fired, blast and visuals.
5. Confirm one activation limit, expiry and return to ordinary shells.
6. Measure friendly fire, performance, and behavior with the existing mod.

If the ability button does not appear, preserve the failed build and log;
investigate UI binding before claiming the ability works.
