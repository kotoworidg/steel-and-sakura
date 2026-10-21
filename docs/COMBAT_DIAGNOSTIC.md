# Combat and vanilla-button diagnostic V1

Milestone PENDING_USER_CONFIRMATION. This diagnostic replaces the previous
combined pack under the same filename. Exactly two custom combat-stat rows
remain; real vanilla Tosa/Armstrong units are exposed only as selection controls.

## 1. What was wrong

RPFM decoded the exact installed data/steel_sakura_combined_test.pack before
replacement. Relative to vanilla Tosa, its infantry land-stat differences were
ONLY key and men (120 -> 40). Equipment, loading skill 65, ammunition 40,
matchlock firing mechanism, trained-rifle animation and foot_musket skeleton
were identical. default_missile_type still pointed to boshin_repeating_rifle:
reload 6, damage 0.9, projectile_number 1, musket_breech bullet, original range
150. primary_missile_weapon=rifle is an existing engine identifier, not a new
weapon object. This schema directly links the projectile via default_missile_type;
no additional infantry weapon-to-projectile table was observed.

Relative to Armstrong, the artillery land stats differed ONLY in key. Its
normal weapon chain remained boshin_armstrong_cannon -> gun_types (Armstrong
engine/model/animations) -> gun_type_to_projectiles -> boshin_armstrong_gun_shell.
Normal reload was 25, range 550, damage 1, calibration area 35 and loading skill
50 with ammunition 20. Only its unusable custom ability referenced nuclear
ammunition. Its ordinary combat had not been modernized.

The active Otomo projectile rows override repeating-rifle range 150 -> 600 and
velocity 200 -> 600; normal Armstrong range 550 -> 600. Shared projectile
references made both old custom units inherit those changes. No custom-key
collisions were found against decoded data.pack and active Otomo tables.
The loading lists now select one combined pack directly in data, and both units
are observed visible in-game. No evidence now suggests the pack is unloaded.
This is not a live process-memory trace or complete reverse engineering of the
engine's DB priority resolver. Read-only pack-index inspection found the relevant
combat tables in data.pack, Otomo and our pack; some unrelated pack index formats
were not parsed and are not claimed exhaustively conflict-free.

The user confirmed both custom buttons absent even after adding custom textures.
Assignment rows, keys, enabling flags, localisation and files round-trip offline,
but custom key/UI acceptance has failed in this setup. Missing textures alone
was not the cause. Unsupported custom-key dispatch is a hypothesis, not yet a
proven universal engine limit. Animation compatibility cannot be diagnosed from
an absent button. Raw audit data: build/diagnostic/combat-audit.json, with exact
installed/base/Otomo decoded rows alongside it.

## 2. What changed in this test

| Normal combat parameter | Prior vanilla value | Diagnostic value |
| --- | --- | --- |
| Rifle projectile base_reload_time | 6 | 1 |
| Rifle effective_range | 150 (600 with Otomo) | 900 |
| Rifle damage | 0.9 | 3 |
| Rifle loading skill / ammo | 65 / 40 | 100 / 200 |
| Cannon shell base_reload_time | 25 | 5 |
| Cannon effective_range | 550 (600 with Otomo) | 900 |
| Cannon loading skill / ammo | 50 / 20 | 100 / 100 |

The rifle points to steel_sakura_diag_rifle. The artillery points to
steel_sakura_diag_armstrong -> steel_sakura_diag_shell. Gun type, mapping and
normal projectiles are separate keys; engine type, models and animations remain
unchanged. One projectile per shot is retained. Normal shell explosion, accuracy
and model references are preserved. This is deliberately exaggerated combat
loading evidence, not balance or proof of automatic fire. Engine animation
floors may prevent the requested cadence; the battle test must measure it.

Custom ability assignments are removed from THIS diagnostic. Infantry instead
links to vanilla blinding_grenade and artillery to vanilla shrapnel_shot.
No unit_special_abilities or explosion override is included, and no vanilla
projectile is replaced. Only requires_effect_enabling=false on blinding_grenade
is temporarily overridden, removing the technology gate. This also unlocks that
ability for vanilla ninjas while this pack is enabled. Disable/replace the test
pack to undo it; no vanilla archives are modified. Vanilla ability names/icons
remain Blinding Grenades and Shrapnel Shot. These do not implement explosive
Throw Grenades or Nuclear Shell and must not be presented as those final skills.

Vanilla Tosa and Armstrong controls retain original combat stats. Only their
frontend category/caste, Oda permissions and displayed control labels are changed.
Their shared projectile overrides from Otomo still apply; the control therefore
is not a clean unmodded reference. Tosa has 120 database men, custom has 40: compare
volley cadence or ammo consumption per soldier, not total unit casualties.

## 3. Offline verification and installation

RPFM reopened every actual packed DB row, localisation row and card file.
Diagnostic validation checks unique normal projectile/gun chains, exact clone
changes, preserved 40-men/four-gun targets, unchanged control stats and vanilla
special-ammunition behavior, and exact release entries. Installer backs up both
loading lists and prior pack, then verifies the installed hash. Only one Steel &
Sakura pack is active; Otomo and unrelated packs are preserved.

Rebuild locally: pwsh -NoProfile -File scripts/build_combat_diagnostic.ps1
Install: python scripts/install_combined.py
Target: D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack
Pre-diagnostic audit inputs in build/diagnostic must be retained. Do not overwrite
those snapshots when investigating a later version. The ordinary build_combined
command restores the prior custom-key experiment; it is not the diagnostic command.

## 4. Short low-FPS game test

1. Restart the game. Original Sengoku Custom Battle, Oda. Pick DIAG RIFLE and
   CONTROL - Tosa from gun infantry, DIAG GUNS and CONTROL - Armstrong from siege/
   artillery. Control selection is attempted via vanilla units; if filtered out,
   report that separately rather than substituting different combat stats.
2. Enter battle and pause. Confirm DIAG names/range 900. Individually select the
   rifle: look for Blinding Grenades. Select artillery: look for Shrapnel Shot.
   Do not activate either yet. Record absent versus greyed-out buttons.
3. Use identical stationary targets at about 100-150 range for both rifle units.
   Unpause for 20 seconds on the IN-GAME battle timer, then pause. Count volleys
   or compare ammo consumed, not kills. At 1-10 FPS, wall-clock time is misleading.
   Keep the target alive; stop/restart the measurement if one target is destroyed.
4. Compare both four-gun batteries against separate equivalent targets at roughly
   300 range for 30 in-game seconds. Count firing cycles/ammo consumed. A visible
   range-900 overlay provides a separate check even if reload animation limits
   erase the intended speed difference. Targets at >600 and <900 offer another
   range check if the map and aiming allow it.
5. Report: DIAG names/range correct? rifle faster/same? cannon faster/same?
   Blinding Grenades button present/absent/grey? Shrapnel Shot present/absent/grey?
   Activation and special ammunition are a later test after buttons are confirmed.

## 5. Engine limits still under investigation

The Gatling reference uses Boshin_Gatling_Gun engine type and its own gun rig/
animations; its projectile reload value is 18 despite its rapid-fire behavior.
Tosa uses a man-rifle animation, no gun engine and matchlock firing mechanism.
Changing a projectile alone cannot establish a working infantry automatic-weapon
animation or burst scheduler. Moving the artillery engine onto a soldier has no
verified compatible skeleton, attachment or control chain. No such substitution
is included. True automatic fire and grenade throwing may require animation or
engine support not exposed by the inspected tables. Impossibility is not proven.

This milestone is incomplete until the user confirms faster rifle/cannon behavior
and both vanilla diagnostic buttons. Final named custom skills remain unresolved.
