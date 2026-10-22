> **22 October update:** The first approved live trace has now run and detached.
> See [ENGINE_BURST_LIVE_TRACE](ENGINE_BURST_LIVE_TRACE.md) for actual evidence,
> the cavalry confound and remaining unit/accounting questions. Setup-only and
> not-executed statements below describe the earlier preparation stage.

# Debugger setup and trace status — 2026-10-22

## Installed and checked

Official portable release: [x64dbg 2026.05.27](https://github.com/x64dbg/x64dbg/releases/tag/2026.05.27).
Archive: `snapshot_2026-05-27_12-11.zip`, 31,526,833 bytes.
Published SHA256 and downloaded bytes agree:
`D41966DFC5B435A372798245300CA0AB7BB8E48BDBF48512C6FB20FCCA427697`.

Local x86 debugger:
`tools/x64dbg/2026.05.27/release/x32/x32dbg.exe`.
Its Windows Authenticode signature is Valid; file/product version is 0.0.2.5.
Packaged source commit: `9c8ca1cae0b6d56cc44f31fddcb10e3b02ffbb87`.
All 220 extracted file hashes were rechecked. No .dp32/.dp64 plugins are included.
Binaries/downloads are excluded from Git. No debugger executable was launched.

## Approval and next trace

The user approved project-local setup, then explicitly approved using the debugger.
The controlled attach/pause trace is authorized. Installing/loading a game patch,
manual native function calls, injected payloads and gameplay memory edits remain
outside this approval. No game process was present during the latest inventory.
The user was asked to launch normally and prepare a paused small Custom Battle:
working two-shot Type 20 rifle versus melee infantry, without artillery/grenades.

See [runtime trace plan](ENGINE_BURST_RUNTIME_TRACE_PLAN.md). Five-round and
sustained automatic fire remain unimplemented and unproven. The next result must
identify the actual infantry callback; neither existing candidate is proven to
control it. The two-shot fallback, installed pack and original DLL are unchanged.

## Automation review

Official source at the packaged commit was read without executing the tool:

- `src/headless/headless.cpp`: supports a stdin command loop and `state`; output
  can be captured without using the debugger's log-to-file command.
- `src/bridge/startupargs.h`: `-userdir` selects an explicit settings directory.
- `src/bridge/bridgemain.cpp`: settings are saved at shutdown.
- `src/dbg/x64dbg.cpp`: global notes and database/symbol directories use userdir;
  `attach`/`detach` and hardware-breakpoint commands are registered.
- `src/dbg/database.cpp`: detach can save .dd32, .cmdline and .bak; database
  compression can cause additional writes. SaveDatabaseInProgramDirectory
  defaults false and must stay false.

These are source-supported capabilities, not locally exercised debugger behavior.
Before launching, cover settings/cache/database writes with timestamped backups;
use isolated workspace state, disable unintended symbol downloads/patching and
retain a reliable detach route. Do not run `exit` while attached as a substitute
for explicit detach. Do not launch the research pass-through DLL.

## Backups and rollback

Every downloaded/extracted file was recorded before creation/overwrite using
`scripts/tracked_files.py`. Original paths, original hashes (or original absent),
new hashes and rollback commands are in immutable `backups/tracked-*` manifests.
Intermediate setup checkpoints preserve progress even if extraction is interrupted.

Full setup receipt:
`build/tool-downloads/x64dbg/setup-20261022T064414.938388Z.json`.
Verification receipt: `build/tool-downloads/x64dbg/verification-20261022.json`.

To undo files written by setup, from the project directory:

```powershell
python -B scripts/setup_x32dbg.py rollback --receipt "build/tool-downloads/x64dbg/setup-20261022T064414.938388Z.json"
```

Rollback preflights hashes and refuses to discard later edits. It backs up each
file before reverting it. Receipts, original backups and source scripts are kept.
Empty directories may remain. Individual project/document edits can be reverted
using the corresponding tracked-file manifest command.
