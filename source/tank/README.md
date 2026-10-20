# Chi-Ha research state

## Verified in installed data

- FoTS Armstrong and Gatling artillery units have 40 crew, four guns, and the
  `gun_train_2_horse` articulated entity in the installed
  `unit_stats_land_tables` version 16.
- The model packs contain Armstrong and Gatling rigid models and animations.
- The installed `unit_stats_land_tables` has `articulated_entity`,
  `artillery_model`, `gun_type`, and `bulletproof` fields. This verifies the
  fields exist, not that they can form a self-propelled tank.
- The installed base tables also contain a dormant `test_limber_gun` unit and
  land-stat row. It uses 40 crew, four Parrott guns, the `parrott_gun` model,
  and `gun_train_2_horse`. It has no observed Fort recruitment or `japan`
  military permission row in the decoded base tables.

## Isolated mechanics experiment

Run `pwsh -NoProfile -File scripts/build.ps1 -ArtilleryTest` to generate
`build/steel_sakura_artillery_mechanics_test.pack`. It contains only two new
database rows: a Fort recruitment entry and a `japan` permission entry for
the **existing** `test_limber_gun`. RPFM reopened and verified both rows. The
pack is Git-ignored, excluded from release ZIPs, and has not been installed.
This is a data-access experiment, not a Chi-Ha unit or proof that a limbered
gun moves correctly in the original Sengoku campaign.

## Unverified hypothesis

An artillery-based proof of concept might move a single cannon around the
battlefield. A Chi-Ha would also require a permitted original 3D tank model,
vehicle animation/rigging, and evidence that the engine can control it as an
armored mobile unit. No tank entry is in the installed prototype pack.

## Next experiment

When a GPU is available, back up the mod list and install this experiment
separately from the infantry prototype, then observe recruitment, movement,
aiming, firing, collision, and crew behavior in battle. Remove it afterward.
Keep it labeled as an artillery test until a real tank model and vehicle
behavior are demonstrated.
