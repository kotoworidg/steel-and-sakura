# Type 20 native projectile checkpoint — 27 October 2026

Five-round firing and full-auto remain unfinished. The last gameplay test was
unsuccessful ("Still looked unchanged"). This checkpoint supersedes older claims
that an ammunition debit or returning from the firing path proves a projectile.
The supported fallback release is frozen while burst/full-auto are the priority.

## What the existing evidence establishes

The old helper counted 3,306 path/ammo pairs, 1,983 additional pairs and 659
five-count groups. It captured no projectile objects, trajectories or linked
damage. The first unsupported inference is `AfterFire` calling those pairs shots.
No observed first divergence yet justifies a firing-mechanism change.

All addresses below are RVAs in DLL SHA256
`022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5`.

| Native stage | Static evidence |
| --- | --- |
| Fresh request | `40E9D0`; definition+4, origin+8, shooter+18, damage multiplier+34. Both ordinary and added paths rebuild this. |
| Debit / direction | `1A9290` debits before construction; `427400` prepares direction/dispersion. |
| Creation / registration | `41C760`, constructor `40E2F0`, append `41C868`. Manager+10 count,+14 vector,+4C serial. Definition+4C=0 skips construction; this is a possible false-positive gate, not the established failure. |
| Object identity | +4 serial,+8 definition,+0C origin,+1C shooter,+38 damage scale,+80 position,+8C velocity. Object+0 is context, not a vtable. |
| Movement / collision | `483D40` iterates the manager vector and calls `481010`; previous/current position+74/+80, velocity+8C. Query `158970`, resolver `4740A0`, actor-hit `38F340`. Bounds and tiny-displacement gates can skip collision, but no live failure is established. |
| Component damage | `38F340` -> `4255C0` -> `424D20`. Calculators use definition+78 times object+38. `424F4F` stores clamped subtraction at component+44; `424F52` is immediately after the store. This is component integrity, not proven whole-soldier HP. |
| Existing post checkpoint | `3D45B7` follows reload bookkeeping via actor vtable+EC -> `3EA970`; it is not an impact checkpoint. |

Captured older ordinary definitions all had count1. They used older range900 /
speed200 data; this does not establish current C89 runtime values. Fresh static
review rules out velocity decaying to zero with extra-shot animation time:
`3E1560` computes approximately speed * sqrt((range + time) / range).

Native ability selection `14AD40` runs per emission. Override activation is
`14ACC0`; `1B54F0`/`1082C0` update native duration, `167A20`/`1AD1F0` restore the
base definition on expiry. The adapter's fixed `s.Record` guard would reject this
transition; it does not explain the abilities-off failed test. Do not claim a
full-auto fix from identifying this guard. The stable clock is battle+50 *0.1,
used by `3D42D0`, `3D33F0` and projectile birth; Stop/Move/death authority is still
unverified. Existing older controllers also re-arm flags, not direct emitters.

## Prepared correction to the missing evidence check

The existing runtime now has a bounded evidence mode. It matches actual appended
objects by manager, serial, definition, shooter and origin, requires finite
nonzero launch velocity and positive native damage input, then tracks the same
identity through movement and the before/after component counter store. An ammo
debit without confirmed registration cancels further additions. Pointer reuse,
changed component owner, ambiguous registration and unmatched nested calls cannot
be credited. A missing hit can be an ordinary miss; it does not identify a failure.

Scope: one actor selected by an ordinary registered shot, at most32 registered
objects/64 requests, maximum90 seconds including impact observation. The existing
three primary re-arms reproduce the unresolved path; this is NOT a new firing
architecture, a combat fix, a new pack, or a gameplay build iteration. It stops
early when an ordinary and an added projectile both move and decrease a component
counter. That comparison still does not prove five damaging projectiles per burst.

Prepare: `python -B scripts/prepare_projectile_evidence.py prepare`.
Prepared artifact: `build/five_round/projectile-evidence-20261027T073916.442694Z/`.
No game was launched, attached or changed. Old approval flags are rejected by the
changed host. Activation requires separate approval via the packaged launcher's
`start --approved-projectile-evidence --seconds 90`; `stop` requests restoration
and detach, and `status` confirms it. Do not activate merely by reading this note.

Offline:55 Python tests,22 adapter fixtures,37 native-layout evidence cases pass;
a synthetic child test exercises four hardware slots/six multiplexed sites and
confirms restoration/detach. These are not combat verification. The initial new
fixture correctly caught missing component-owner revalidation before it was fixed.
Every source/artifact write has a timestamped SHA-backed manifest in backups/.
No installed EXE/DLL bytes are patched; no proprietary binaries are committed.

Next: obtain narrowly scoped approval for this materially different comparison,
then capture an ordinary versus added object. Use the first observed divergence
to choose a combat correction; do not repeat the old visual-only test or spend a
remaining gameplay iteration speculatively. Full-auto and magazines stay unfinished.
