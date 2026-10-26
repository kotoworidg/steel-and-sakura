# Type 20 five-round runtime — 0.2.0 candidate

This adds a real native-action adapter, not another observer or a five-projectile
shotgun setting. Its intended sequence is one native first shot, three scheduled
primary-slot re-arms, then the native second slot as round five. The re-arms occur
inside the currently selected native firing action, at least 100 ms apart in the
recovered simulation clock. Each accepted shot uses the original request validator,
ammunition debit, projectile spawn, hit/effect path and native action completion.

The paired pack moves only the existing second shot marker to 0.50 seconds. It
preserves motion frames, skeletons, projectile count 1, damage, 450 range, velocity
850, 210 ammunition and the v0.1.0 fire-control settings. The exact unit is **JSDF
Type 20 - Five-Round Runtime**, Oda ranged infantry in Sengoku Custom Battle.
Without the running adapter this pack still uses two native shots; a pack alone
cannot execute the added native scheduling logic.

The adapter resolves the actor through `actor+0x214 -> unit+0x28 -> exact terminated
UTF-16 unit key`, the route observed in the preserved capture. It validates the
selected animation, private projectile, current action, target/battle continuity,
clock and native pre/post ammunition accounting. It does not reinterpret unknown
fields as health or orders. Native action continuity handles interruption;
Stop/Move/death behavior still needs actual gameplay verification.

Only one Boolean byte in an admitted current action (`action+0x6C`) is changed.
There are no ammunition/health writes, AL return overrides, held completed actions,
manual emitter calls, DLL injection, or installed game EXE/DLL modifications.
An unconsumed reset is restored during orderly stop. Already accepted native
projectiles can finish normally. This is an experimental memory hook and needs
separate human approval before activation under the repository's AGENTS.md.
The earlier approval for a read-only trace does not authorize this runtime.

## Install and use

Extract the package into a writable folder and retain it for rollback/runtime logs.
With the game closed, run `Install-Core.cmd`. This uses the hash-checked installer
and preserves the current combined pack, both loading lists and unrelated mods.
The optional `Install-With-Suppression.cmd` retains the v0.1.0 native timed
Suppression Fire module. Its shared ability changes affect other existing native
Suppression Fire users too. It is not true full-auto.

After runtime-hook approval, start the game and prepare one paused custom battle
with the exact unit above against slow melee infantry. Keep abilities off for the
first verification. Run `Test-Five-Round-90s.cmd`, then unpause and observe a burst.
Disable Fire at Will, issue Stop and Move, then resume firing to check interruption
and repeated bursts. This is a single acceptance test of the integrated adapter.

`Run-Five-Round.cmd` enables a normal session of up to one hour. Both scripts
require the matching pack and exact supported EXE/DLL hashes, and refuse another
active Steel & Sakura controller. `Stop-Five-Round.cmd` requests orderly detach.
Wait for `Report-Five-Round.cmd` to show `detached: true` before closing/removing
the helper. It exits automatically at the configured duration or game exit.
The external debugger transport may reduce performance; test a small battle first.

Equivalent commands from the extracted package:

```powershell
python -B run_five_round.py start --approved-engine-hook --seconds 90
python -B run_five_round.py status
python -B run_five_round.py stop
python -B run_five_round.py report
```

The approval flag is an execution guard, not a substitute for actual permission.
Logs and pre-activation disk hashes are under `build/five_round/runtime/` in this
package. Reports distinguish native debit/spawn-path observations from visual
projectile damage. A coarse simulation update, cancelled native action, rejected
request or ammunition shortage produces a shorter burst; no simultaneous catch-up
volley is manufactured to claim five shots.

The installer prints an exact receipt and rollback command. Stop the adapter,
confirm detach, close the game, then use:

```powershell
python -B install_type20.py rollback --receipt "<backup-folder>\manifest.json" --dry-run
python -B install_type20.py rollback --receipt "<backup-folder>\manifest.json"
```

## Validation and current status

The shared live adapter passes 22 offline scenarios and 839 assertions, including
five debited emissions, repeated cycles, foreign-unit rejection, cancellation
proxies, clock rewind, request rejection, finite ammo, coarse updates and pending
flag restoration. Four-site synthetic debugger transport restores registers and
detaches. All 205 preserved instructions of the relevant native routine match the
installed engine. The paired clips preserve their entire motion data. RPFM reopens
the changed unit/localization, and the remaining v0.1.0 gameplay payloads remain
unchanged. This consumes gameplay build iteration 3; stable v0.1.0 is preserved.

**No real-game activation or five-projectile gameplay verification has occurred.**
The runtime is implemented and compiled; the next necessary step is the approved
integrated game test. Until then this is a candidate, not a verified five-round
release. Full-auto, per-soldier magazine management and custom Type 20 visuals
remain outside this candidate.
