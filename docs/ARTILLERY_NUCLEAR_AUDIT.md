# Artillery and nuclear-style shell audit — 2026-10-22

The user asks whether the artillery nuclear shell can become a working in-game
feature, and notes the last test only had infantry. Do not assume the artillery
or its skill was present/activated in that test.

## Actual installed build

SHA256 `1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD`.
Copied unchanged into a unique project research path, then decoded with RPFM to
avoid mistaking a cached earlier pack for the installed one. Evidence:
`build/artillery-nuclear-audit/inspection.json`, `decoded.json`, `findings.json`.

The pack contains `SteelSakura_Modern_Artillery`, 40 crew, four guns, Armstrong
model/controller, gun type `steel_sakura_diag_armstrong`, a gun/projectile junction,
Japan grouping, explicit Oda permission and Sengoku siege/stealth frontend category.
Its actual roster visibility remains unconfirmed. Presence of rows is not proof
that it can be selected. A missing category/card or runtime filter has not been
diagnosed; no cause is asserted yet.

It assigns native `shrapnel_shot`. It contains **no**
`steel_sakura_nuclear_projectile` or `steel_sakura_nuclear_explosion` rows.
The old source config still describes a nuclear prototype, but that is not the
installed implementation. The native special ability remains the vanilla
Shrapnel Shot assignment, not a verified Nuclear Shell activation.

## What is technically promising

Actual `projectiles_explosions` fields include detonation radius, duration, speed,
damage, fragment projectile/count and separate air/ground particle references.
The inspected Armstrong shell has radius 4 and damage 16. Native `ship_magazine`
has radius 70 and damage 100; a native naval torpedo has radius 25 and damage 100.
These establish that the schema/data support large damaging explosions; they do
not prove those settings work unchanged on land or perform acceptably at low FPS.

A private artillery projectile linked to a private explosion, using verified
existing land-capable particle assets, is a plausible first proof of concept.
It can be nuclear-themed through a large blast and heavy damage. Genuine nuclear
physics, fallout, persistent radiation, a mushroom cloud, visual scaling and an
expanding visible shockwave are not established features of this implementation.
Blast radius does not automatically enlarge its particle effect. Those require
separate evidence/custom visual work and must not be claimed from DB values.

## Next implementation gates

1. Establish the four-gun battery is selectable in Oda Sengoku Custom Battle with
   a recognizable name/card, keeping the Armstrong placeholder explicit.
2. Confirm the native artillery ability is visible and activates.
3. Build an isolated high-blast projectile/explosion and validate every reference.
   Choose a bounded initial effect and avoid unnecessary fragment multiplication
   on the user's 1–10 FPS machine. No arbitrary fields or speculative asset paths.
4. Verify actual shell launch, land detonation, casualties, friendly effects and
   ammunition behavior in-game before naming it a functioning Nuclear Shell.
5. Investigate custom nuclear-style visuals only after the blast mechanics work.

Native Shrapnel Shot uses a shared ability key, so changing its activated
projectile would affect other assigned artillery while enabled. The prior user
approval concerned grenade and Suppression Fire relinks; it is not approval of a
new shared artillery relink. Prepare a concrete reviewable build before seeking
that approval if a shared override is necessary. An isolated impact-only test
can avoid the shared change but must clearly state that it is not yet a special
ability implementation.

No game files or packs were changed by this audit. The working rifle and native
Suppression Fire build remains installed.
