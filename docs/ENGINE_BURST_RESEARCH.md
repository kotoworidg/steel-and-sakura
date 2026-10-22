> **22 October update:** The first approved live trace has now run and detached.
> See [ENGINE_BURST_LIVE_TRACE](ENGINE_BURST_LIVE_TRACE.md) for actual evidence,
> the cavalry confound and remaining unit/accounting questions. Setup-only and
> not-executed statements below describe the earlier preparation stage.

# Engine burst investigation — 2026-10-22

## Current conclusion

Five-round bursts and sustained automatic infantry fire remain **unproven in-game**.
A controller extension is plausible, but no functional infantry hook is ready.
The confirmed two-shot builds and current installed artillery/rifle pack are unchanged.

**Correction to the previous investigation:** the two disassembled firing routines
were never positively mapped to the foot-rifle controller. New wrapper/table context
points toward naval firing and grenade-action bindings. That adjacency is a lead,
not definitive class identification. The prior claim that those routines establish
an infantry-wide two-shot hard limit was too strong. The metadata parser's two
named scalar firing-time slots remain verified for the recovered format.

## Evidence added

- Routine A, VA 0x1038b600, has a verified wrapper call at 0x103436bd from
  wrapper entry 0x103436b0. The wrapper loads an object argument, adjusts it by
  -0x1c and calls A. Its callback pointer is at 0x115db218.
- Routine B, VA 0x103d4320, similarly has wrapper entry 0x103b3030 and call
  0x103b303d, with callback pointer at 0x115df97c.
- The A callback table is near naval FIRING_STATE/boarding/ship-state names.
  B's neighborhood includes ENTITY_ACTION_THROW_GRENADE and a source filename
  ending EntityActionThrowGrenade.cpp. Direct source-string references recovered
  so far are debug-variable registration, not proof of the active rifle call chain.
- Both routines still visibly use two firing slots. Their actual live callers,
  unit scope and relationship to our rifle's shots are not established.
- No named C/C++ compiler or debugger was found on PATH or in the inspected
  Visual Studio/Windows SDK debugger directories. No software was installed.

Read-only trace artifacts are under build/engine-burst-research/trace-* and the
wrapper-refs-*, grenade-binding-* and vtable-stores-* files. Empty/heuristic leads
are retained rather than promoted to conclusions.

## Workspace prototypes

scripts/engine_burst_lab.py creates two separate research artifacts:

1. An original reference scheduler contract for five-shot and sustained firing.
   Nine offline scenarios pass: five emissions, movement cancellation, target loss,
   ammo refusal/exhaustion, unit-scope rejection, entity-generation change, ability
   expiry and low-update-rate behavior. It issues at most one intent per update,
   avoiding an instant catch-up volley at 1 FPS. This limits achievable cadence
   when simulation updates are slow. Render FPS and simulation rate are not assumed
   equal. The native emitter must own ammo consumption; no engine ammo fields are
   written by this model. **This is not an engine integration or game test.**
2. A derived DLL copy with a pass-through detour at candidate RVA 0x38b600. Its
   original six-byte `sub esp,0xf0` prologue is moved to a new executable PE section,
   followed by a relative jump back. The entry jumps to it. No scheduler is wired
   in, and the candidate is not verified as the foot-rifle routine. The scaffold
   only demonstrates reversible layout, branch encoding and version checks.

The derived copy was parsed as a PE and its two relative branches checked at three
hypothetical image bases. These are static arithmetic checks, not Windows loader,
ASLR runtime, signature/trust or compatibility tests. The copy was never loaded,
executed, installed or injected into a game process. There is no installer/loader.
It is deliberately named PASSTHROUGH_ONLY_NOT_FOR_INSTALL.

The exact source DLL SHA256 is pinned:
022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5.
Changing the `cmp ...,2` immediate alone remains an invalid design: the recovered
code also maps iterations to index zero/one and tracks two fired flags. A functional
replacement needs its own state, correct caller identity, native emission ABI,
unit filtering, targeting, cancellation, lifecycle and ammunition ownership.

## Preservation, backups and rollback

Every active project file write in this research uses scripts/tracked_files.py.
Before overwriting a file it creates an immutable timestamped original copy and
manifest with absolute original path, SHA256, planned output SHA256 and rollback
command. New creations record original_exists=false / original_sha256=null.
Backup copies/manifests are the immutable audit mechanism and are never overwritten.
Python runs use -B to avoid incidental bytecode-file changes.

Actual rollback checks passed for an updated scratch file, removing a newly created
file, restoring that deletion, and undoing the PE scaffold on an independent copy.
The restored DLL copy matches the original DLL SHA256 exactly. All backups and the
main derived copy remain preserved. Rollback refuses files changed by later work.

General rollback, using the manifest recorded for a specific write:

    python -B scripts/tracked_files.py rollback "<absolute manifest.json>"

Derived-copy restoration, restricted to the research workspace:

    python -B scripts/engine_burst_lab.py restore "<research-dir>/passthrough-plan.json"

The latter backs up the derived copy before restoring original bytes. It cannot
write to the game's directory. Removing a newly created research file is also
reversible: its pre-deletion copy and manifest are retained.

Confirmed fallback archives rechecked:
- Original two-shot burst: build/type20-auto-cycle/confirmed-burst.pack,
  SHA256 0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270.
- No-reload-animation burst: build/type20-suppression/confirmed-no-reload-bursts.pack,
  SHA256 56CCB4B44FC1520C379045ED3EC30D3EA13D6B3FB5BCF701A7259CC19EAD1299.
- Working native Suppression Fire R2: build/type20-five-shot/confirmed-suppression-r2.pack,
  SHA256 1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD.

The currently installed artillery test pack hash remains
2D57C29074E15A3903E6C7900D652770CB27D7023A8A349BDF0C1C5BDDB67AB3.
No original executable/DLL, installed pack, unrelated mod or save was modified.

## Next necessary test

A controlled runtime trace must identify the actual foot-rifle firing callback
before connecting the scheduler. See ENGINE_BURST_RUNTIME_TRACE_PLAN.md. No debugger
was attached. New software installation, any runtime patch/hook or code injection
requires separate approval. A five-shot game test is premature until the mapping,
emitter ABI and unit scope are proven.

## Exact latest lab artifacts

Research directory: `build\engine-burst-research\lab-20261022T062927.417894Z`.

Scheduler evidence: `scheduler-contract.json`; static scaffold: `passthrough-plan.json`;
actual rollback evidence: `rollback-check.json`; unchanged-game hashes: `summary.json`.

Derived-copy SHA256: `0741968D4BFD9CEF3C40373652606A3B9ADCB72B3ED9B2334A87FCEB2160D281`.
