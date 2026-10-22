## 2026-10-22: engine research resumed; earlier controller scope corrected

Current evidence: [ENGINE_BURST_RESEARCH](ENGINE_BURST_RESEARCH.md).
The earlier two-shot routines are not proven to be the foot-rifle controller;
new wrapper context points toward naval/grenade actions. Two metadata fire-time
slots remain verified, but a universal infantry hard limit is not established.
An offline five-shot scheduler contract and reversible pass-through DLL-copy
scaffold were validated only in the workspace. No game DLL/EXE, installed pack
or running process was changed. All file writes now use timestamped hash-backed
transactions via scripts/tracked_files.py. Next gate: approved runtime mapping
of the actual rifle callback, not another reload or speculative .pack experiment.

# Five-shot burst feasibility — 2026-10-22

## Gameplay result and preserved baseline

User confirms native **Suppression Fire works**, but the unit still fires only
two shots per burst and does not sustain continuous fire. Requested next burst
size: five actual sequential bullets.

The working pack remains installed and unchanged:
`D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack`.
SHA256 `1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD`.
Additional preserved copy: `build/type20-five-shot/confirmed-suppression-r2.pack`.
No new test pack was installed. No ability, projectile, model or game executable
was changed in this investigation. The previously approved shared native ability
relink remains as it was in the working R2 build.

## Result: an actual controller limit, not just missing marker names

A genuine five-shot burst has **not** been implemented. The recovered animation
firing path cannot express five timed shots through the settings currently used.
Read-only disassembly adds substantially stronger evidence than earlier guesses.

Exact installed `empire.retail.dll` SHA256:
`022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5`.

### 1. Metadata is scalar storage, not an arbitrary shot-event queue

The recovered parser function begins at VA `0x10d398f0`. Its scalar-name table
registers exactly these firing-time names: `FIRE_TIME` and `FIRE_TIME_2`.
The next entry is **IMPACT_TIME**, not a third firing time. The remaining time
entries concern distance, pulling, blood and dismemberment.

The scalar parse/store loop begins at `0x10d3a189`, uses an eight-byte slot stride,
stores one floating-point value (`fstp dword ptr [eax]` at `0x10d3a20d`), and scans
13 named scalar properties (`cmp esi,0xd` at `0x10d3a243`). The outer source-entry
loop returns through `0x10d39df0`; it resets the matching flag at `0x10d39e11`.
Adding repeated entries for the same firing-time name writes the same scalar slot;
it does not supply additional independent shot times. A small storage model in
the audit demonstrates the consequence, but is explicitly not an engine runtime test.

### 2. The consumer reads those same slots

Function VA `0x103d2ef0` obtains the selected animation data. At `0x103d2f06` it
checks the slot-present byte at `[eax+ecx*8+0x94]`, then at `0x103d2f10` returns the
float at `[eax+ecx*8+0x90]`. Thus the recovered consumer uses the scalar slot layout.

### 3. Two recovered dispatchers process two shots and track two fired flags

| Routine entry | Loop bound | Shot flags | Completion flag |
| --- | --- | --- | --- |
| 0x1038b600 | `cmp ebp,2` at 0x1038b8fc | object+0x74 / +0x75 | object+0x76 |
| 0x103d4320 | `cmp ebp,2` at 0x103d45c3 | object+0x6c / +0x6d | object+0x6e |

Both routines call the recovered time getter. They derive an index using
`test ebp,ebp` followed by `setne dl`, giving index zero or one. They set the
corresponding already-fired byte and later check the two completion bytes.

Changing a loop immediate from two to five would **not** create five firing slots:
iterations after the first still select index one, and shot flags/object layouts
are sized around the current behavior. This is a specific reason not to apply a
blind binary patch. No executable patch was attempted.

This structure is consistent with the user's observed two-shot ceiling despite
shorter clips, zero projectile reload and an activated native ability.

## What the evidence does and does not prove

Verified: the exact instruction ranges, time names, scalar getter, two loop bounds,
boolean index construction and shot-flag offsets in the installed executable.
The native ability's activation and two-shot behavior are user-confirmed.

Not proven: source class names, every use of these routines, or an instrumented
runtime trace identifying the active routine for this particular unit. This is not
a universal proof that all Shogun 2 weapon controllers are limited to two shots:
Gatling guns already use a different engine path. No verified alternative
**foot-infantry** controller or cross-state five-shot chain has been established.
The existing seven-bone Gatling clip/controller is not a drop-in replacement for
the human 48-bone rig and rifle unit structure.

## Reproduce the audit

```powershell
python scripts/audit_five_shot_limit.py
```

Uses the previously approved project-local Capstone package and existing pefile.
No additional software installation is needed. Reads only the exact DLL and
installed pack, verifies their hashes, disassembles bounded instruction ranges,
asserts the cited instructions and writes ignored local research output.

Evidence: `build/type20-five-shot/limit-audit.json` includes instruction bytes,
addresses, names, assertions' inputs and the explicitly labelled scalar-storage
model. Earlier `*-leads.json` files are heuristic leads only; they are not evidence
of verified instruction boundaries. `limit-audit.json` uses bounded confirmed
instruction starts without data skipping.

## Next technical gate

Five sequential shots require a different controller path or a controlled engine
extension that owns five time slots and five fired flags, schedules them, and
preserves cancellation, ammo accounting, targeting and ability expiry. None is
implemented or verified. A full solution must first map the exact runtime caller,
object lifetime/layout and reset logic; inspect an actual repeat-fire controller;
then produce a separate reversible proof before changing gameplay code.

Within the verified `.pack`-only route, the honest supported result is currently
**two-shot bursts plus working Suppression Fire**. There is no supported
`burst_size=5` setting in the inspected schemas. No invented FIRE_TIME_3/4/5 names,
simultaneous projectile multiplication, extra damage, or further reload edits were
introduced as substitutes for five timed bullets.
