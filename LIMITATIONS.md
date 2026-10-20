# Limits and blockers

## Automatic Rifle Squad — PROVISIONAL

The local pack is structurally valid and sets `men=40`. It reuses the installed FoTS Tosa repeating-rifle row; true automatic fire is unverified. Four authored English text entries and five original TGA cards are packed and reopen correctly, but their in-game display is unverified. There is no custom soldier model or custom-battle evidence. Without a working GPU, campaign recruitment, battlefield behavior, animation, and stability cannot be tested. The current installed copy is an experiment, not a gameplay-certified release.

## Type 97 Chi-Ha — BLOCKED

Installed horse-drawn artillery provides an observed cannon/articulated-entity basis. A separate, uninstalled research pack enables the base game's dormant `test_limber_gun` via two recruitment/permission rows and reopens in RPFM. It does not establish that the unit recruits or moves in-game, nor self-propelled tracks, turret rotation, armor behavior, or tank pathfinding. There is no licensed Chi-Ha model and no in-game evidence. The research pack is excluded from release ZIPs and must not be shipped as the tank unit.

## A6M Zero — BLOCKED

No visible 3D aircraft model or aircraft-named path was found in the model-pack scan. Bird fauna meshes and a `bird_cycle.anim` exist, but no verified way to adapt their ambient animation into an aircraft unit or control its flight has been identified. The decoded `battle_entities` table has no altitude field or aircraft-named row; other systems may exist. The RPFM glTF importer needed for an easy model pipeline is documented as unimplemented. This does **not** prove that all physical aircraft implementations are unsupported. An off-map strike, projectile, or ground unit would not satisfy the requested aircraft.

## Project-wide

The executable version metadata is not a runtime build number. FoTS files are present, but exact DLC entitlement cannot be confirmed without launch. Direct key collisions were checked against decoded vanilla tables and one installed mod; other possible mod interactions remain untested. No gameplay status is marked VERIFIED.
