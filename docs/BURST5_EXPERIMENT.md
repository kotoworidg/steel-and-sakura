# Burst5 integrated experiment â€” prepared, not activated

Build: `python -B scripts/burst5_build.py build`
Release: `dist/burst5/Burst5Experiment.exe` plus `engine-profile.json`.
Fallback: `CONFIRMED_TWO_SHOT_FALLBACK_DO_NOT_AUTO_INSTALL.pack` is byte-identical
to the confirmed two-shot archive. Existing installed packs are not replaced.

## What the experiment attempts

An external x86 debug controller observes the native B firing callback. It leaves
the original two shots alone, then attempts three paced additional dispatches
through the original routine, one per eligible engine callback, at least 100 ms
apart in the recovered 0.1-second native clock. It retains the current action for at most six simulation seconds. It does
not inject a DLL, copy a stale projectile request, call an emitter manually, patch
code bytes, modify game executables, or lower reload speed. Runtime action flags,
AL at the callback return, and hardware debug registers ARE modified when enabled;
that is an experimental engine hook and requires separate explicit approval.

There is no sustained-auto mode: ability lifetime and order semantics do not yet
justify enabling it. Native models, animations, grenades and artillery are unchanged.

## Fail-closed admission and cancellation

- Exact engine/installed-pack hashes and relocated controller-code checks must pass.
- Both the custom unit key and its ordinary private projectile key must match in
  bounded record/string-wrapper checks. No global memory scan authorizes an actor.
- Two native emissions must demonstrate a finite, delta-one accounting candidate.
  Additional shots continue using the game's own accounting path; no ammo is set.
- Actor/target pointers, vtables, unit record, battle context, animation selector
  and variant must remain consistent. Clock resets, unreadable data, a nonzero conservative target-reference
  predicate, changed animation/target, and displaced shot origin cancel.
- No timer thread emits shots. Loss of native dispatch means no additional shots.
- A stop request drains callbacks, restores debug registers at a paused debug event,
  and detaches. An idle process can require an OS debugger break for cleanup.
- Guard/no-access pages, image writes and executable-heap writes are rejected.
- Five-shot cap, six-second burst deadline, 90-second host limit and event budget.

## Unverified engine semantics

`unit+0xB9C` as a direct unit-record root, the bounded string wrapper discovery,
and `unit+0xF78` as ammunition are candidates supported by native data accesses,
not verified gameplay mappings. The first live release wrongly required shooter+0x1B4 to be zero. R3 follows helper RVA 0x3A6630: ECX=action+0x2C, [ECX+0x0C]=target. Shooter state is recorded only, never treated as a death flag. Target state remains a conservative restriction, not proven health semantics. Key lookup/accounting failure preserves native
firing and logs a refusal. The pre-debit gate runs only after native request validation and rechecks the
current projectile and origin before charging ammo or spawning. Native
animation/dispatch/validity/origin checks are
conservative movement/death/cease-fire safeguards; exact order/death fields remain
unmapped. A shot already accepted by the native pipeline cannot be retracted.
Action retention may fail when the animation ends. Windows debugger transport was
validated on a synthetic process; the first adapter ran and safely refused all candidates; the corrected R3 adapter has not been run. Bounded passive native pre/post evidence now records keys, target state and ammo candidates even if admission fails, without authorizing extension.
A successful offline result is not evidence of five live bullets or correct damage.

## Single battle, only after explicit engine-hook approval

1. Use Oda's existing **TYPE20 SUPPRESSION FIX R2**, protected by yari infantry,
   facing slow melee infantry. Leave every special ability off.
2. Pause before firing. The approved launch command is:
   `python -B scripts/burst5_build.py launch --approved-engine-hook --pid <PID>`
   Accept UAC. The approval flag is not a substitute for obtaining human approval.
3. Unpause: observe stationary firing, issue Stop, resume firing, then move away.
   Capture whether five distinct shots occur and watch the ammunition indicator.
4. The host stops after 90 seconds; earlier stop/rollback:
   `python -B scripts/burst5_rollback.py`
5. Aggregate the entire battle, including gate refusals:
   `python -B scripts/burst5_build.py report`.
   Logs live in `build/burst5/runtime/<timestamp>/`. Do not enable another build.

## Rollback and backups

Every source/config/output write uses timestamped originals and SHA256 records in
`backups/tracked-*`; compiler outputs additionally use `backups/external-burst5-*`.
The rollback script gracefully deactivates the controller, confirms detach, and
verifies game/fallback hashes. No original game files need restoring because none
are installed/changed. Do not force-close the host during an active debug session.
Optional full project-file restoration: `python -B scripts/burst5_rollback.py --project-files`.
This preflights all latest hashes and refuses to discard later work. Evidence and
backup archives remain preserved. Its ledger is `build/burst5/rollback-ledger.json`.

Offline evidence is packaged as `offline-tests.json`, `transport-tests.json`,
`rollback-tests.json` and `binary-validation.json`. No installation or game-hook
execution is performed by the build or test commands.

## R3 offline correction

Native helper/caller/validator instructions and the 703 captured shooter values are checked by `python -B scripts/burst5_validity_research.py`. The first live-tested release is preserved under `build/burst5/preserved/first-live-refused-*`. R3 has no runtime approval inherited from the earlier one-battle activation; do not launch it without explicit approval. No immediate battle is requested. Five-shot and death/order semantics remain unverified.
