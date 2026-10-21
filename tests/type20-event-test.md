> Previous two-event build: user reports no automatic fire. The current installed diagnostic is the [one-shot animation-path control](../docs/TYPE20_PATH_CONTROL.md). Use its test and rollback commands.

# Type 20 event test: user checklist

Status: awaiting in-game confirmation. Details: [research report](../docs/TYPE20_RESEARCH.md).

1. Fully restart Shogun 2. Original Sengoku Custom Battle -> Oda -> gun/matchlock infantry.
2. Add **Steel & Sakura - Type 20 Automatic Fire Test** (the roster uses an em dash)
   and the existing DIAG/EXP riflemen. Both must be available together.
3. Small flat battle, stationary enemy about 100-150 range away. Spread both squads
   into shallow lines; keep fire-at-will off until ready.
4. Fire only the old squad for ten simulation seconds, stop, then fire only the new
   squad at a comparable fresh target. Pause often. Observe one front-rank soldier.
5. Record whether that soldier launches TWO separate shots in ONE cycle, approximately
   0.30 simulation seconds apart. Uniform, gun, recoil motion and ballistic statistics
   intentionally remain placeholders/controls. Faster reload or more casualties
   alone is not a passing result.
6. Note ammo changes, stop-fire response, projectile origin and any freezing/crashes.
   At 1 FPS, two flashes may be unresolvable: mark **INCONCLUSIVE**. A recording or
   slower simulation/replay, if available, can help; skipped frames cannot prove timing.
7. Do not use grenades/artillery in this comparison.

Report:

- Exact new unit name visible:
- Old riflemen also selectable:
- New unit moves and fires:
- One / two shots per soldier per cycle / impossible to distinguish:
- Ammo and cease-fire behavior:
- Any animation errors or crash:

The experiment adds a second timed event observed in vanilla dual-pistol data.
It may be ignored by the rifle controller. No sustained automatic-fire success
is claimed, and the existing grenade/artillery systems have not been altered.

Rollback with game closed, from project root:

~~~powershell
python scripts/select_type20_event_test.py fallback
~~~

Rebuild and safely install:

~~~powershell
powershell -NoProfile -File scripts/build_type20_event_test.ps1 -Install
~~~
