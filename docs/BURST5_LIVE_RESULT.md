# Burst5 live result — 2026-10-22

Approved controller session: uild/burst5/runtime/20261022T101927.563542Z. User reported sample done.

- Attached to Shogun2 PID 10072; reached the native B firing callback.
- 713 rejected entries: 703 native entity-validity predicate refusals, 10 animation/action mismatches. Logged actor +0x1B4 was 1 in the sampled refusals; the guard requires zero for both actor and target. Target value was not logged separately, so do not assign all refusals solely to the actor.
- No actor was admitted, no identity/ammo accounting was verified, and no additional-shot attempt occurred. No evidence of five-shot or sustained fire.
- Detached cleanly; host exited; game remained running. One-command rollback ran and verified the DLL, installed pack and preserved fallback hashes. EXE SHA256 independently unchanged.
- This identifies an admission blocker, not an engine burst limit. Native dispatch occurring with a nonzero sampled actor field means our interpretation/placement of this conservative guard needs offline review. Do not invert or remove it without evidence. Later identity/accounting gates remain untested.

Next work: follow the exact native validity helper callers and actor/target pointer types offline; improve evidence coverage before another integrated test. No immediate repeat battle or new parameter trial requested.

Rollback: python -B scripts/burst5_rollback.py. All logs and edits have immutable manifests under ackups/tracked-*. Original game EXEs/DLLs and packs were not modified.

## Offline follow-up: R3

The byte-verified caller at RVA 3D44B4 supplies action+2C to helper 3A6630. The helper dereferences +0C, resolving action+38 (target); it never reads the shooter there. Its boolean is stored in request metadata at 3D44BE, and a different validator (420D00) is checked before the pre-debit hook. The first controller therefore imposed an unsupported shooter-field gate. R3 removes that shooter requirement, retains the conservative target-only filter, and adds independent native identity/ammo observations. This is a verified scope correction, not proof of health-field semantics or five live shots.

R3 offline results: 51 scenarios, 1,000 randomized schedules, 11 instruction assertions, nine compatibility masks, and synthetic transport/detach passed. R3 was not activated.
