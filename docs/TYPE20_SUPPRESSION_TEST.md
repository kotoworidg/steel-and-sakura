# Type 20 — single-button Suppressive Fire experiment

## Current status, 2026-10-21

Installed, offline validated, **ability and continuous fire unconfirmed in-game**.
The user confirmed the preceding unit fires two-shot bursts without the reload
animation. This is not confirmation of uninterrupted automatic fire.

User's selected design: **one Suppressive Fire button also enables the proposed
Full Auto mode**. The user additionally requested increased, realistic burst fire.
This build tests the button and higher cadence. It still has only two established
timed shots per animation cycle. Longer individual bursts are not implemented.

## Engine finding: use an existing unused identity

The actual DLL contains fixed name/number pairs:

| Entry VA | String VA | Name | Number |
| --- | --- | --- | --- |
| 0x115b3d80 | 0x115b9cdc | suppression_fire | 61 |
| 0x115b3d98 | 0x115b9d1c | tower_suppression_fire | 64 |
| 0x115b3db0 | 0x115b9d5c | dummy_suppression_fire | 67 |

Read-only reproduction: `python scripts/inspect_suppression_engine.py`.
Evidence: `build/type20-suppression/engine-key-evidence.json`.
Exact DLL SHA256:
`022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5`.
No DLL modification or execution was performed.

`dummy_suppression_fire` has no rows/assignments in the inspected vanilla and
Otomo ability tables. This gives an isolated built-in identity to investigate.
It is **not proof** that this identity supports a player-visible button, active
projectile switching or the complete normal suppression behavior. It may serve
an internal purpose. A fixed identity improves the evidence for recognition over
an invented ability key; actual behavior requires gameplay testing.

The normal `suppression_fire` definition, its projectiles and its users are not
modified. No shared grenade/artillery/ability rows from the working pack change.

## New unit and assignment chain

Separate unit: `steel_sakura_type20_suppressive_test`.
Display: **TYPE20 SUPPRESSIVE AUTO TEST**, Oda ranged infantry, 40 men.

- `unit_to_unit_abilities_junctions`: new unit → `dummy_suppression_fire`.
- `unit_abilities`: that key clones vanilla Suppression Fire text fields, sets
  `requires_effect_enabling=false`, and displays **Suppressive Fire**. No separate
  Full Auto button. Disabling the effect gate avoids a campaign research unlock.
- `unit_special_abilities`: same key, 10-second active time, 30-second recharge,
  unlimited reuses, no autotrigger; activated projectile is private to this test.
- 19 native suppression button/icon assets copied under the built-in dummy key's
  corresponding names, in both normal and Boshin UI paths as present in data.pack.
  Localization uses the actual observed unit_abilities field-key conventions.
- Independent equipment, projectile and animation keys. No new campaign rows or
  grenade assignments. Existing visual weapon remains a Spencer/Tosa placeholder.

## Firing mechanics and limits

Both normal and activated modes use a new short human firing clip: five frames
at 20 FPS, duration 0.20 seconds, FIRE_TIME=0.00 and FIRE_TIME_2=0.10. The source
frames come from the previous working seven-frame clip, indices `[0,2,3,5,6]`.
Aimed recovery clips remain two identical frames (0.05 seconds) with no events.
Only observed state names and existing `blend_in_time` syntax are used.

A 0.10-second separation corresponds arithmetically to a 600-round/minute cadence
**within the two-shot pair**. This does not establish the average cyclic rate,
continuous fire, or accurate Howa Type 20 simulation. No FIRE_TIME_3 is invented.
No simultaneous projectile multiplication is used: each event has one projectile.

Normal private projectile: existing diagnostic ballistics and base_reload_time=1.
Activated private projectile: base_reload_time=0, shot_type=`suppression_shot`,
calibration_area=2.0 instead of 1.0. The shot type is taken from actual vanilla
`boshin_rifle_suppressive`; damage and range stay at their diagnostic values.
A wider calibration area is intended to reduce precision; effect size is untested.

This ability switches projectiles if the engine honors the generic assignment;
it does not switch animation tables. Shorter clips apply in both modes. The zero
timer removes a DB gate but the infantry state machine may impose other pauses.
Changing the timer is not proof of automatic fire. The previous zero-timer test
was reported as paired bursts, not sustained automatic fire.

Vanilla effect values were inspected without changes:
`special_ability_bonus_suppression_fire_reload=20`, accuracy penalty `-20`, morale
penalty `-4`, movement-speed multiplier `0.5`. This unused identity has not been
shown to inherit those effects. `suppression_shot` hit behavior, morale/slowdown,
expiry, ammunition accounting and stop-fire behavior all remain unverified.
No magazine reload simulation or longer-than-two-shot event sequence is claimed.

## Build, validation, install and rollback

```powershell
powershell -File scripts/build_type20_suppression.ps1
powershell -File scripts/build_type20_suppression.ps1 -Install
python scripts/type20_suppression.py validate
# Restore the exact no-reload-animation burst build:
python scripts/type20_suppression.py rollback
```

Uses the installed RPFM MCP server on localhost:45127, Python and the existing
local vanilla/source exports. The 19 UI source assets were read with RPFM from
owned data.pack into ignored build/type20-suppression/vanilla. No copyrighted
assets are added to source control. Fresh-machine source extraction still needs
the owned game data; this is a repeatable build in the current research workspace.

Installed directly into:
`D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack`.
Generated: `build/steel_sakura_type20_suppression.pack`.
SHA256: `11B6BF8D14B868C31327495AD8E29CA35513DFFD3EA805DCF288D7E81B90BBD1`.
Exact backup: see `build/type20-suppression/installation.json`.
The reused safe installer reports generic mode `control` and its historical
`type20-path-control-` backup prefix. It refused installation while the game was
running, then installed after the user confirmed normal exit.

Verified offline: RPFM schema/row/localization round-trip for 11 new tables;
PFH3 and metadata cleanup; all **60 preceding payloads byte-identical**; new unit
and asset references; ability/projectile assignment chain; finite animation data,
rigs, exact source frame mapping and positive durations; two valid timed markers;
event-free ready clips; Oda permission; build/installed hash equality and unchanged
loading files. The new button and combat behavior are not offline-verifiable.

## Short gameplay test

1. Restart. Sengoku Custom Battle → Oda → ranged infantry →
   **TYPE20 SUPPRESSIVE AUTO TEST**. The previous test units remain unchanged.
2. Select this unit in battle. Report whether **Suppressive Fire** is visible and
   usable. If absent or disabled, report that before drawing conclusions about
   firing behavior. A registered dummy identity may still be unsuitable for UI.
3. Fire normally at stationary dense infantry, then activate the button. Compare
   whether firing continues in a stream or still occurs as pairs separated by a
   pause. Compare animation and sound; damage alone does not prove extra shots.
4. Use the battle clock rather than wall-clock timing on the 1–10 FPS PC. After
   the configured activation period, check that normal cadence returns and the
   button recharges. Check that ammo decreases; this does not establish accounting
   per individual bullet.
5. Toggle fire at will off, then move. Check that firing stops after the current
   short cycle and movement works. Do not activate other skills during this test.

If the button is absent, preserve the result: recognition in the built-in mapping
alone was insufficient. If it appears but no change occurs, separate activation,
projectile-switch and state-machine questions. If shots remain paired with a pause,
report rapid burst fire; the continuous-fire target remains unmet. Do not treat
extra damage, wider spread or a morale effect as proof of a longer firing sequence.
