## 2026-10-21: native Suppression Fire R2 installed with user approval

The user approved the temporary shared native-ability override. Installed hash:
`1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD`.
Oda ranged infantry: **TYPE20 SUPPRESSION FIX R2**; expected native button:
**Suppression Fire**, configured for 30 seconds active / 120 seconds recharge.
Backups and installed/build hash checks completed; loading files unchanged.
Button visibility, activation and firing behavior await gameplay confirmation.
Animations and firing statistics were not changed in R2. Other native Suppression
Fire users receive the approved shared projectile/unlock behavior while enabled.
Rollback: `python scripts/type20_native_suppression.py rollback`.
Exact installation/backup record: `build/type20-native-suppression/installation.json`.
Earlier prepared/not-installed statements below are historical.

## 2026-10-21: dummy ability failed; native-key R2 built, not installed

User reports no Suppressive Fire button and only the existing paired firing.
Do not count the preceding build as a working ability or continuous fire.
[Native R2 report](TYPE20_NATIVE_SUPPRESSION_FIX.md) gives the exact fix:
real suppression_fire assignment, native button unlock, and private projectile
relink. This uses shared native definitions and awaits explicit shared-scope
approval before installation. Animations and firing statistics are unchanged.
The current installed pack remains the preceding build until approval/install.

## 2026-10-21: single-button Suppressive Fire test installed — runtime pending

Latest report: [TYPE20_SUPPRESSION_TEST.md](TYPE20_SUPPRESSION_TEST.md).
New Oda ranged infantry: **TYPE20 SUPPRESSIVE AUTO TEST**, intended button
**Suppressive Fire**. Tests an unused registered engine identity, private activated
projectile and two-shot 0.10-second timing. Longer individual bursts and continuous
fire remain unconfirmed. The user confirmed the previous unit fires paired shots
without a reload animation; all 60 preceding payloads remain byte-identical.
Artillery, grenades and vanilla Suppression Fire are unchanged.
Build/install: `powershell -File scripts/build_type20_suppression.ps1 -Install`.
Rollback to the preceding confirmed behavior: `python scripts/type20_suppression.py rollback`.

## 2026-10-21: separate automatic-cycle trial installed; runtime pending

See [TYPE20_AUTO_CYCLE.md](TYPE20_AUTO_CYCLE.md) for evidence, exact changes,
validation, installation, rollback and gameplay test. New Oda ranged infantry:
**TYPE20 AUTO CYCLE TEST - continuous trial**. The user-confirmed
**TYPE20 BURST TEST - two timed shots** remains available unchanged alongside it.
The new unit combines a 0.30-second two-event firing clip, short aimed recovery
states, and an experimental zero projectile reload timer. Continuous fire is not
confirmed. All 39 prior payloads are byte-identical. Artillery and grenades unchanged.
Build/install: `powershell -File scripts/build_type20_auto_cycle.ps1 -Install`.
Restore confirmed burst build: `python scripts/type20_auto_cycle.py rollback`.

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
