## 2026-10-21: user confirms two bullets followed by a reload

User report: "yep confirmed two bullets and a reload" for the latest installed
Type 20 burst experiment. Record this as **user-confirmed two-shot burst behavior**.
Sustained automatic fire, the exact 0.15-second interval, and removal of the reload
animation are not confirmed. The earlier inconclusive control remains historical.
Preserve this working burst build before any further experiments. No combat,
animation, artillery, grenade, or installed pack changes were made for this update.
The detailed report below retains the pre-test expectations as historical context.

## 2026-10-21: isolated Type 20 burst test installed — runtime unconfirmed

Current instructions and engine evidence: [TYPE20_BURST_TEST.md](TYPE20_BURST_TEST.md).
Oda ranged infantry: **TYPE20 BURST TEST - two timed shots**. Unique registry,
two timed events 0.15 s apart, repeated source recoil poses, and aimed recovery.
Combat DB statistics and all 20 working fallback payloads are unchanged.
No sustained automatic-fire success is claimed. The previous path control was
inconclusive. Build/validate/install: `powershell -File scripts/build_type20_burst.ps1 -Install`.
Rollback: `python scripts/type20_burst.py rollback`. See the report for exact
installed hash, backup record and short gameplay test. Historical entries follow.

# Type 20 investigation TODO

- [x] Inspect installed rifle/matchlock/Gatling projectile and controller selections.
- [x] Parse eleven real animation event blocks, preserve exact motion bytes.
- [x] Inspect actual Expanded Japan and Radious packs supplied by user.
- [x] Record other named mods as author-page research with package access gaps.
- [x] Verify installed equipment VMPF formats; create original coarse model separately.
- [x] Build independent two-event experimental unit alongside unchanged fallback.
- [x] RPFM round trip eight new tables; check references, collision keys and payload preservation.
- [x] Safely install one combined pack directly in data with hashes and backups.
- [x] Run seven offline unit tests. Gameplay is not covered by these tests.
- [x] User confirms selecting the intended Type 20 test unit.
- [x] User reports the intended test still does not achieve automatic fire; exact per-cycle shot count remains unresolved.
- [ ] If one shot only, prove custom clip/event consumption using a positive timing control.
- [ ] Resolve pistol-specific dispatch requirements without inventing new enums.
- [ ] Inspect DarthMod/Tosa/Morning Sun/UEFC actual packages if supplied/access permits.
- [ ] Only after firing proof, adapt recoil, test repeated bursts/ammo, integrate model.
- [ ] Keep campaign recruitment work deferred until the combat prototype is proven.

Do not resume grenade damage changes, artillery, tanks, aircraft or cosmetic polishing.
Do not label an event-only effect, projectile-count increase or reload reduction automatic fire.

## Current gate

- [x] Preserve failed two-event pack and build/install the one-shot path control.
- [x] User comparison obtained: both squads pause similarly; control is INCONCLUSIVE.
- [ ] Prove clip selection/event timing before interpreting a second-marker failure.

- [ ] Trace engine registry selection/event dispatch using the saved PE reference inventory before another firing build.
