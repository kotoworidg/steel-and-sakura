> **22 October update:** The first approved live trace has now run and detached.
> See [ENGINE_BURST_LIVE_TRACE](ENGINE_BURST_LIVE_TRACE.md) for actual evidence,
> the cavalry confound and remaining unit/accounting questions. Setup-only and
> not-executed statements below describe the earlier preparation stage.

# Proposed infantry controller runtime trace â€” NOT EXECUTED

## Approval and tooling

The official portable x64dbg package is installed and verified locally; see
[DEBUGGER_SETUP](DEBUGGER_SETUP.md). Its 32-bit x32dbg matches this x86 game.
The user approved setup and then the controlled debugger trace. No debugger has
been launched/attached, and no game process was found. Waiting for a prepared
Custom Battle. No experimental engine patch is ready for installation, and no
prototype DLL should be loaded. Runtime patch installation remains unapproved.

Official sources:
- https://x64dbg.com/
- https://help.x64dbg.com/en/latest/commands/breakpoint-control/SetHardwareBreakpoint.html
- https://help.x64dbg.com/en/latest/commands/debug-control/AttachDebugger.html

The official hardware breakpoint command uses debug registers. Attaching reaches
an OS system breakpoint and pauses the game; this is not a timing-neutral action.
No software breakpoint patches or experimental payload injections are proposed.
Debugger configuration/default actions must be reviewed before attaching.

## Reviewable test procedure

1. Use the current original game binaries and preserved working two-shot unit.
   Create one small Custom Battle with the test rifle and a melee-only target.
   Do not use artillery or grenades during the initial firing observation.
2. Verify the on-disk DLL hash against the pinned research hash. Obtain its actual
   loaded module base from the debugger's module view; do not assume 0x10000000.
3. With explicit attach/pause approval, set one-byte hardware execution breakpoints
   at loaded-base + these RVAs (three separate debug-register slots):

   | RVA | Purpose |
   | --- | --- |
   | 0x38b600 | Previously recovered dispatch candidate A |
   | 0x3d4320 | Previously recovered dispatch candidate B |
   | 0x3d2ef0 | Scalar firing-time getter |

   In official command syntax, substitute each computed absolute address into
   `bph ADDRESS,x,1`. These are proposed commands, not commands executed here.
4. Order the rifle to fire. On the first hit, record the actual instruction address,
   thread, return address/call stack and ECX object pointer. At the getter also
   record its two stack arguments (selected-animation index and time-slot index).
   Resume only after clearing/disabling frequent breakpoints to avoid an unusable
   pause on every entity/update.
5. Compare observed hits with several actual rifle shots. A hit alone does not prove
   the routine emits those shots. Identify the relevant object and follow its
   native emission call; read its target/arguments and ammo ownership without
   invoking it manually or modifying registers/memory.
6. If neither candidate belongs to rifle firing, reject them as hook targets. Use
   the actual getter caller or projectile-emission call path as the next lead.
   A later separate grenade control may help classify candidate B, but do not infer
   a class from neighboring strings alone.
7. Verify the genuine rifle callback's unit identity and normal stop-fire/movement
   transitions. Map lifetime/reset, ability activation/expiry and ammo consumption.
   A native emitter returning success must not be assumed to consume ammo once
   per projectile until observed. Only then design the scheduler adapter.
8. Clear hardware breakpoints and detach through the debugger. Verify original
   DLL/EXE and installed pack hashes still match. Store captures in the project
   through the tracked-file helper, with timestamped backups before overwrites.

## Success criteria for this trace

A recorded call path from the known test rifle's firing action to the actual
projectile emission, with validated unit scope, calling convention, target data,
reset/cancellation and ammo semantics. This is a tracing test, not proof of five
shots or sustained fire. Any subsequent hook integration/test needs a concrete
reviewable design and separate user approval before game installation/injection.

## Automation capability to verify after approved tool setup

The official 2026.04.20/2026.05.27 release notes document command-file startup
(`-cf`), process attachment (`-p`) and a headless testing mode. These capabilities
could make a bounded trace reproducible without a custom injection plugin. They
have been checked against packaged release notes and official source; the debugger
is downloaded but has not been run, so local runtime behavior remains unverified.
Source: https://github.com/x64dbg/x64dbg/releases . The May notes also fix absolute
command-file paths. Confirm the actual downloaded binary/version/options before
using them; do not infer that a script is safe or fully automated from the notes.
