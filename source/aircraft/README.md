# Visible A6M Zero research state

## Verified in installed data

- A filename scan of 14,322 entries in the installed `models.pack` and
  `models2.pack` found no names containing aircraft, A6M, Zero, airplane,
  aeroplane, biplane, or balloon.
- A broader scan found bird fauna meshes and textures, and `data.pack`
  contains `animations/shogun_animation/battle/animals/birds/bird_cycle.anim`.
  This is a potential lead for visible ambient airborne animation, not evidence
  of a controllable aircraft unit.
- The installed `battle_entities_tables` version 0 has 42 rows with fields
  such as `walk_speed`, `run_speed`, `radius`, and `height`; it has no
  aircraft-named row or altitude/movement-axis field in this table. Other
  script or scene systems have not been ruled out.
- No aircraft DB row, model, flight animation, or battlefield control path has
  been verified.

## Requirements still to establish

- An original or properly licensed A6M-shaped 3D model compatible with the
  game's asset format.
- A verified way to render it in battle, animate continuous flight, move it
  through 3D space, and associate it with a unit without replacing it with an
  off-map strike.
- In-game video or other direct evidence of all of the above.

## Next offline hypothesis

Trace how the game spawns and animates its ambient birds and whether that
system can accept a separately authored, licensed aircraft mesh. Even if it
can, an ambient effect would still need demonstrated meaningful movement and
battle participation before it could count as the requested Zero unit.

The project contains no aircraft unit entry or airstrike substitute yet.
