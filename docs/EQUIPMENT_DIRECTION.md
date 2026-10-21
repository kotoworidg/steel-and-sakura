# Equipment direction: Howa Type 20 and FH70

Current decision, 2026-10-21: two active units only. Chi-Ha is deferred and
preserved for later; aircraft development remains stopped.

## Modern Infantry Squad — Howa Type 20 inspiration

Target: forty soldiers with modern automatic-rifle behavior and the experimental
Throw Grenades ability. The user-selected weapon inspiration is the Japanese
Howa Type 20 5.56 mm assault rifle. No Type 20 geometry, sound, weapon handling,
magazine simulation or accurate ballistic representation has been implemented.
The stable database key remains `SteelSakura_Automatic_Rifle_Squad`.

The installed Tosa foundation uses `boshin_man_rifle_trained`,
`boshin_spencer_bp_1`, `foot_musket`, `firing_mechanism=matchlock` and the
`boshin_repeating_rifle` projectile. That projectile has `base_reload_time=6`
and `projectile_number=1`. These are observed database values; neither their
names nor numeric values establish the final rate of fire in battle.

The installed Gatling projectile has `base_reload_time=18` and also one
projectile. Its unit uses a separate `Boshin_Gatling_Gun` engine type and
`boshin_engine_gatling_gun` animations. This is evidence that projectile reload
values alone are insufficient to infer automatic fire. Copying artillery
engine settings into rifle infantry has no verified compatibility basis.

The inspected land-stat and projectile schemas expose no field named burst.
This limited observation does not prove burst fire is impossible. Keep the
current baseline until a battle establishes firing cadence, animation timing,
reload behavior and grenade switching. Then isolate any rate changes under a
new infantry projectile key to avoid affecting vanilla rifles. Raising
projectile_number is not a demonstrated way to obtain sequential automatic fire.

## Modern Artillery Battery — FH70 inspiration

Target: four conventional towed 155 mm howitzers, deployed and stabilized on
solid ground during firing. The FH70 is equipment inspiration only. Retain the
experimental Nuclear Shell skill as fictional mod gameplay, not a claim about
the real weapon. No FH70 model, stabilizer animation or deployment system is
implemented.

The installed Armstrong foundation has four guns, forty crew,
`gun_train_2_horse`, `does_fire_mounted_by_default=false` and
`can_fire_mounted_whilst_moving=false`. The new validator explicitly preserves
four guns and both firing flags along with the observed towed entity. These
checks protect the prototype configuration; they do not prove ground contact,
stabilization or deployed-only firing. The mounted flags must not be mistaken
for a universal prohibition on firing while moving.

Preserve the Armstrong movement, model and animation references until tested.
Do not invent stabilizer or self-propelled settings. Historical horse towing
is a temporary visual limitation, not a representation of an FH70 towing vehicle.

## Acceptance checks and implementation order

1. Confirm both units render, recruit and enter battle using temporary assets.
2. Infantry: measure rounds fired and reload/animation cycles for one minute;
   check that forty soldiers remain present and grenades visibly leave hands.
3. Artillery: confirm four guns, movement-to-deployment transition, ground
   contact, stationary aiming/firing and behavior when ordered to move.
4. Check Nuclear Shell activation and return to conventional fire, including
   the known 550/600 range interaction with the existing Otomo mod.
5. Tune unit-specific gameplay only after observing these results. Author and
   integrate modern models/animations after the mechanics are established.

## Current evidence

Specifications and displayed prototype descriptions now state the modern
inspiration and historical foundations. Both packs are rebuilt through RPFM;
source validation and pack reopening are required. Runtime acceptance remains
pending. Raw game-derived inputs and packs stay outside Git/source releases.

Sources: locally decoded installed `unit_stats_land`, `projectiles`,
`gun_types`, and `gun_type_to_projectiles` tables in `build/inventory/`.
The weapon identities and intended roles are the user's design specification;
no real-world performance figures are mapped to game values.
