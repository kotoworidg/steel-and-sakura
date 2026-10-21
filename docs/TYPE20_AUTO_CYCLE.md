# Type 20 automatic-cycle experiment

## Purpose and evidence

The user confirmed the previous unit fires **two bullets then reloads**. That is
our preserved working baseline, not proof of sustained automatic fire.

This experiment asks whether the existing infantry state machine can repeat that
confirmed two-shot behavior with sufficiently short firing and aimed recovery
animations to produce continuous fire. It does not invent an automatic firing
enum, infantry FIRE_LOOP state, FIRE_TIME_3, or a Gatling/human skeleton conversion.
The installed DLL evidence and initial research remain in TYPE20_BURST_TEST.md
and TYPE20_RESEARCH.md. No DLL modification or injection is used.

## Exact changes

A separate unit, `steel_sakura_type20_auto_cycle_test`, is added alongside the
unchanged `steel_sakura_type20_automatic_fire_test` burst unit and original riflemen.
It has independent unit, stats, projectile, equipment and animation keys, cards,
localization, and the same Oda Custom Battle permission as the confirmed unit.
No campaign recruitment, grenades, artillery, model or other unit changes.

- FIRE/KNEEL_FIRE clips: seven same-rig frames at 20 FPS, duration 0.30 seconds;
  source frame sequence `[0,2,4,0,2,4,0]`. This removes the long tail of the
  1.05/1.65-second burst-test clips while retaining two short recoil sequences.
- Exactly two firing markers, at 0.05/0.20 seconds. One projectile per event.
- Four private human clips in total: standing/kneeling fire and ready.
  Ready clips contain two identical source frames (0.05 seconds) and no events.
- The private full musket combat fragment remaps 18 firing/aim/reload states.
  The private full rifle fragment remaps its eight reload states identically.
  Both use aimed poses for recovery, with the observed `blend_in_time = 0.0`
  syntax. This avoids relying on an uncertain precedence between two different
  reload mappings. Locomotion, melee, turning and posture transitions are retained.
- The new projectile's I32 `base_reload_time` changes from 1 to **0**, removing
  the explicit DB reload delay for this trial. All other projectile values,
  including range, damage and projectile count, are unchanged.
- Zero is present in actual vanilla projectile rows such as `blinding_grenade`
  and numerous shell fragments. **Those are not rifle examples.** The schema can
  encode zero; its behavior for a rifle projectile remains a runtime hypothesis.
- `firing_mechanism=none` is unchanged. This trial still uses the infantry firing
  state machine; no new sustained-fire controller has been established.

This combines a confirmed two-event firing path with deliberately shortened
animation states and a removed timer. It is not evidence that reducing reload
alone creates automatic fire. If it repeats in pairs with noticeable gaps, it is
rapid burst fire and must be described that way. There is no magazine-reload
simulation, verified ammo-per-bullet accounting, or proven modern cyclic rate.

## Build and safe installation

Prerequisites: existing project Python and RPFM MCP server on localhost:45127.

```powershell
powershell -File scripts/build_type20_auto_cycle.ps1
# Build, validate, back up and install:
powershell -File scripts/build_type20_auto_cycle.ps1 -Install
# Revalidate existing build:
python scripts/type20_auto_cycle.py validate
# Restore the user-confirmed burst pack:
python scripts/type20_auto_cycle.py rollback
```

Close Shogun 2 before install/rollback. The installer refuses unknown pack hashes,
additional Steel & Sakura pack files, or a running game. It backs up the current
pack, root mod_list.txt and user.script.txt, leaves loading configuration unchanged,
and checks installed/build hash equality. The reused installer reports generic
`mode=control` and uses the historical `type20-path-control-` backup prefix.

Source: `build/steel_sakura_type20_auto_cycle.pack`.
Installed: `D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack`.
SHA256: `56CCB4B44FC1520C379045ED3EC30D3EA13D6B3FB5BCF701A7259CC19EAD1299`.
Exact backup/installation record: `build/type20-auto-cycle/installation.json`.
Preserved confirmed baseline: `build/type20-auto-cycle/confirmed-burst.pack`,
SHA256 `0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270`.

## What is verified offline

RPFM round-trip of all eight new DB tables and localization; PFH3 structure and
metadata cleanup; all 39 prior pack payloads preserved byte-for-byte; unique new
asset paths; registry, fragment and clip references; human rig and exact frame
mapping; finite animation data; positive clip durations; no events in ready clips;
exactly two timed firing events; unchanged ballistics except the new unit's reload
value; Oda permission; actual installed SHA256 and unchanged loading configuration.

None of these checks prove the game dispatches continuous firing, whether the
zero timer is clamped, how ammo is consumed, or whether a minimum pause remains.
No runtime success is claimed for this build yet.

## Short gameplay test at 1–10 FPS

1. Restart the game. Sengoku Custom Battle, Oda, ranged infantry. Bring one
   **TYPE20 AUTO CYCLE TEST - continuous trial** and one unchanged
   **TYPE20 BURST TEST - two timed shots** for separate comparisons.
2. Use a stationary target at the same distance and a short, single-rank
   formation. Start with only the new unit firing; run at normal speed.
3. Watch the new unit for several cycles. Does it keep firing while aimed, or
   still fire twice and stop to reload? Compare the old burst unit separately.
   At low FPS, listen for a continuing series of discharges rather than relying
   on seeing every flash. Sound alone cannot establish an exact bullet count.
4. Toggle fire at will off while it is firing. Does it stop after the current
   short cycle? Order movement and check that it moves normally. Check that the
   ammunition counter decreases. Do not infer per-bullet accounting from this alone.
5. Report the exact unit name, continuous fire versus paired bursts/pause,
   visible reload movement, and whether stop-fire/movement work. An exact RPM
   measurement or 0.15-second timing confirmation is not required at this FPS.

If short ready animations appear but a long pause persists, this would point to
a remaining engine/state-machine gate. Preserve that result; do not increase
damage/projectile count or add fictional event names to disguise the pause.
If the game refuses this variant or becomes unstable, use the rollback command;
the confirmed build and its source remain intact. If the new unit behaves as a
continuous stream, confirm control and ammunition behavior before replacing any
fallback or attempting magazine reloads.
