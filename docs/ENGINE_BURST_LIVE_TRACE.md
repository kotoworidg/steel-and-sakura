# First live firing-controller trace — 22 October 2026

## Result

The approved debugger trace was executed against the user's prepared battle.
It recorded the two timing-slot lookups and downstream native firing calls during
the firing samples. **Five-round/sustained fire is still not implemented.**
No engine patch, scheduler injection, reload change or new pack was installed.

The previous uncertainty about nearby naval/grenade strings remains relevant:
those strings do not establish controller identity. We now have runtime evidence
of candidate B during the firing exercise, but have not resolved its captured
actors to the custom unit's database key. It is premature to label this a complete
Type 20-specific hook target or a universal engine limit.

## Session and observations

- Game PID: 7196; original DLL loaded base: `0x70D20000`.
- The user confirmed both firing samples, with abilities off as requested.
- In the second sample the user reports the riflemen were overrun by cavalry.
  Other actors/controller types may therefore contribute. No exact shot cadence,
  ammunition delta, projectile damage, or unit identity was measured.
- The OS denied non-administrator process-memory access. The user accepted UAC;
  the isolated headless x32dbg host then attached successfully.

| Checkpoint | DLL RVA | Evidence |
| --- | --- | --- |
| Candidate B entry | `0x3D4320` | 32 bounded samples, wrapper return RVA `0x3B3042` |
| Timing getter | `0x3D2EF0` | 32 samples, all return to B at RVA `0x3D43FA` |
| B firing call site | `0x3D4558` | 90 samples; both loop-slot values observed |
| Shared native callee | `0x427400` | 83 calls returning to B; 13 returning to A |
| B callback completion checkpoint | `0x3D45B7` | 90 samples after the downstream calls returned |

The getter observed animation selector `0x82` and slot zero 12 times / slot one
20 times. These are numeric selector values, not verified animation names.
B firing-site samples include slot zero 46 times and slot one 44 times. There are
17 distinct action pointers, 16 seen with both slots. Pointers may be reused across
cycles; these are not counts of soldiers or unique action lifetimes.

The shared callee returned to B at runtime `0x710F455D` (83 samples) and A at
`0x710AB88B` (13 samples). A had zero entry samples in the first bounded pass;
that does not mean it was inactive for the entire battle. The B-layout act/ent
labels in those 13 A samples are not interpreted as actor addresses.
Each checkpoint has an independent cap; the shared callee exhausted its 96-sample
cap first. Do not describe these totals as matched bullets or five-shot bursts.

## Native code evidence and remaining mapping

The original DLL's B routine queries the timing getter, tests time, and marks
fired bytes at action+0x6C / +0x6D. It then builds a request and calls native
functions including RVAs `0x427400` and `0x41C760`. Live B post checkpoints confirm
that the latter portion returned, but `0x41C760` was not independently breakpointed.
Its static body loops over a request-record count and calls an object constructor
at RVA `0x40E2F0`, which initializes positions/directions and simulation-state fields.
These structures are evidence of a projectile creation route; their complete
semantics, damage outcomes and ownership still require verification.

The B path calls RVA `0x1A9290` before the shared firing callee when the actor+0x214
pointer is non-null. Static code in that function subtracts a float constant from
object+0xF78 under a threshold check. That is an ammunition-accounting candidate,
not a verified ammo field: no before/after values or ammo-UI correlation were
captured. Do not bypass or manually invoke it in a game patch.

For this observed route, changing a loop bound to five remains insufficient:
index selection is boolean and only two fired flags exist. A separate timed
scheduler/controller extension is a plausible research direction, not a proven
implementation. It must rebuild valid current requests, identify the custom unit,
follow native accounting, and stop on movement/target loss/action destruction.
Do not replay pointers to stack-built requests after their lifetime ends.

## Safe execution, backups and rollback

Only hardware breakpoints and read/log/resume/pause/detach commands were sent.
No software breakpoint was requested, no native function was called manually,
and no experimental payload was loaded. DLL and installed-pack hashes match the
pre-trace values; all four fallback archive hashes and all 220 debugger-package
file hashes were rechecked unchanged.

The host uses a separate workspace settings directory. Before launch, seed files
were written via tracked_files; the original directory ACL was recorded, then a
scoped deny-write ACL blocked tool configuration/database/cache writes. Two blocked
write checks passed before launch. Each command and stdout batch was recorded in
a new hash-tracked file, with a timestamped pre-write transaction.
The native settings save intentionally failed on exit because writes were denied.
This was after explicit `Detached!` confirmation, not a game crash.
The debugger exited, the original state ACL was restored exactly, and every seed
file hash remained unchanged. The game process remained running.

Session: `build/engine-burst-research/runtime-20261022T065501.372693Z`.
Evidence: `events/`, `trace-rows.json`, `trace-summary.json`,
`static-emission-candidates.json`, `static-ammo-spawn-candidates.json`,
`post-trace-tool-audit.json`.

Project-file rollback uses each manifest in `backups/tracked-*`:

```powershell
python -B scripts/tracked_files.py rollback "<absolute manifest.json>"
```

The isolated directory-permission rollback is preserved as
`restore-state-acl.ps1` in the session; it has already run successfully. It only
restores the debugger-state directory, never the game directory. Do not delete
session/backup evidence or run the pass-through research DLL.

## Next necessary experiment

One controlled Custom Battle with the working custom rifle unit shooting a slow
melee infantry target. Keep cavalry out of the sampled combat, and exclude artillery
and other shooters. If a general/cavalry unit must be present, protect the riflemen
behind friendly yari infantry and sample the opening long-range volleys. Capture
raw unit/record identity and verify it equals the custom unit key, then capture
native accounting before/after paired shots and action cancellation on stop-fire.
No further firing-stat changes are indicated. Only after those semantics are
mapped can we prepare a reviewable scoped five-shot adapter. Installing/injecting
that adapter would require separate explicit approval.
