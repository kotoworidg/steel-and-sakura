# Current prepared release — 27 October 2026

The installable supported fallback is 0.3.0; see
[Type 20 Rifle and Grenade Section](docs/TYPE20_FIELD_RELEASE.md).
Location: dist/type20-field-release/0.3.0/.
It adds the missing Type20 grenade assignment, armour 8 and wider selectable
loose formation, restoring the confirmed two-shot clips. No helper is required.
It is built and offline-validated, NOT installed or in-game verified.
The C89B3F9F candidate remains installed with helper off, as the user chose.
Use the release installer dry-run first; actual installation requires separate
authorization. Its receipt restores the exact previous candidate and configs.
Recovery also includes the original confirmed two-shot archive. The instructions
below describe older releases; do not use an older installer for this package.

<!-- CURRENT-FIVE-ROUND-INSTALL -->
# Type 20 0.2.0 candidate — current installation and recovery

This section supersedes historical installation/rollback instructions below.
The five-round candidate was installed with approval on 25 October 2026. The
runtime attached for an approved 90-second firing test and detached cleanly.
It recorded 659 five-count firing-path groups, but the user reported that gameplay
still looked unchanged. Five distinct damaging projectiles are NOT verified;
this candidate has not met the requested gameplay objective. The helper is off.
No installed EXE/DLL was changed. Three gameplay build iterations are complete.
This launcher revision changes startup/error reporting, not gameplay data.

The core unit is Oda's **JSDF Type 20 - Five-Round Runtime** in a Sengoku custom
battle. A separate x86 helper re-arms the current native primary firing slot
three times inside the paired firing window. Added requests use the existing
validation, ammunition and firing paths; five distinct damaging projectiles have
not been established. The engine retains ownership of action completion.
Without the helper this candidate fires two native shots. Coarse simulation
updates or interrupted actions can shorten a burst; extras are never emitted
as a catch-up volley. Stable movement, damage, exact five-shot counts and crash
absence still require one focused battle verification.

Retained supported improvements: accuracy 45 to 80; projectile speed 200 to 850;
450 range (replacing the diagnostic 900); 210 shared native ammunition; all-rank
fire; wider spacing; guard enabled and skirmishing disabled. Core Rapid Volley
is configured for 60 seconds with 300-second recharge. The optional native
Suppression Fire module is configured for 30 seconds and 120-second recharge,
faster loading and lower accuracy, then native expiry restores its modifiers.
It is **not continuous full-auto**. It changes shared native Suppression Fire
for other units already assigned that ability. Per-soldier magazines and
independent magazine reloads are not implemented. Existing grenade activation
is preserved; grenade damage is not established by that fact.

Extract the ZIP into its own writable directory. Standard-library Python 3.10+
is required. Commands below run from that extracted directory in PowerShell.
The runtime also requires the installed Windows .NET Framework 4.x x86 runtime.
Close SHOGUN 2 before any pack install, rollback, or restoration.

```powershell
python -B .\install_type20.py install --dry-run
python -B .\install_type20.py install
```

`Install-Core.cmd` performs the second command. Packs go directly into
`D:\Games\Total War - SHOGUN 2\data`; the installer manages only its two pack
names and own entries in the two loading lists, with immutable backups first.
It refuses unknown pack edits and unsupported executable/DLL hashes.
`Install-With-Suppression.cmd` adds the optional shared module; it is not
currently installed. Inspect its scope above before choosing it.

The completed tests used 90-second sessions; the first expired while paused.
Do not mistake a successful attach or a firing-path counter for verified bursts.
No further firing experiment is scheduled. If explicitly choosing another test,
launch the game with this pack loaded and the named unit. The battle must run
and the unit must actually fire during the timed window. This installation runs
SHOGUN 2 with elevated privileges: right-click `Test-Five-Round-90s.cmd`, choose
**Run as administrator**, and accept the normal Windows UAC prompt. For a manual
command, use an administrator PowerShell window:

```powershell
python -B .\run_five_round.py start --approved-engine-hook --seconds 90
python -B .\run_five_round.py status
```

Unpause and give normal attack orders. Expected: repeating five separate native
shots where the engine updates sufficiently often, actual enemy damage and
ammunition use, and prompt obedience to halt/move/cease-fire orders. Stop for a
crash, unrelated-unit effect, continued fire after cancellation, unexplained
ammunition changes, or persistent shorter bursts. A log reporting five firing-path
visits with ammunition debits does not establish five damaging projectiles. Hardware breakpoints may slow the game. This run has not
verified the requested visual/damage result, and the launcher never opens or
controls the game. It now waits for an actual attachment log, reports startup
access errors directly, and requests graceful stop if startup times out.

```powershell
python -B .\run_five_round.py stop
python -B .\run_five_round.py report
```

Stop requests graceful cleanup of an unconsumed flag reset, restoration of owned
debug registers, and detach. Report refuses to finalize until detach/end are
logged. Do not force-kill the helper while it is attached; request stop and wait.
Closing the game also removes process memory changes. `Run-Five-Round.cmd` is a
one-hour option for later use; it is not activated by this task. The completed
90-second sessions do not authorize an automatic longer run. No automatic startup or persistence exists.

If the candidate is unsuitable, close the game and install the supported two-shot
0.1.0 fallback, which keeps the projectile, precision, formation and native ability
improvements without the external helper:

```powershell
python -B .\supported\install_type20.py install --dry-run
python -B .\supported\install_type20.py install
```

`Install-Supported-Fallback.cmd` performs the second command. For the original,
user-confirmed two-shot archive instead, use `Restore-Confirmed.cmd` or:

```powershell
python -B .\restore_confirmed.py --dry-run
python -B .\restore_confirmed.py
```

That restores SHA-256
`0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270`,
removes this package's optional module, retains unrelated mods and creates its
own reversible receipt. The source tag is
`steel-sakura/confirmed-two-shot-20261025` at `c4628a6`.

To remove a new installation and restore its exact pre-install state, use the
receipt printed by that installation, including its complete absolute path:

```powershell
python -B .\install_type20.py rollback --receipt "C:\full\path\to\manifest.json" --dry-run
python -B .\install_type20.py rollback --receipt "C:\full\path\to\manifest.json"
```

For the installation already performed in this workspace, the exact rollback is:

```powershell
python -B "C:\Users\Lenovo\Documents\Codex\2026-10-18\you-are-my-lead-developer-for\dist\five_round\0.2.0\install_type20.py" rollback --receipt "C:\Users\Lenovo\Documents\Codex\2026-10-18\you-are-my-lead-developer-for\dist\five_round\0.2.0\backups\type20-20261025T084021.672895Z-46abf51f\manifest.json"
```

This receipt restores the immediately preceding supported 0.1.0 pack
`B0E51ABC7D1FC4FB0D1DE37CA106B72AD55C6DE230B19C309C3BF92AF2EA2280`.
Earlier notes saying the pre-install active pack was the original 0B497 archive
were superseded by the actual installation receipt. Never use an older research
rollback script for this candidate. Keep all receipts and backup originals.

Build commands from the existing repository (requires the preserved build inputs,
installed supported binaries, pefile, .NET 4 x86 csc and bundled RPFM 5.2.0):

```powershell
python -B scripts/five_round_build.py build
python -B scripts/validate_five_round.py
python -B -m unittest discover -s tests -v
python -B scripts/package_five_round.py
```

These commands build/test/package without game attachment. No fourth changed
candidate is permitted in this run. Pack generation and ZIP assembly are checked
for byte reproducibility; legacy csc executable reproducibility is not asserted.
Project-owned native sources and the exact compiled host are included in the ZIP.
Original game binaries remain only in ignored local development backups.
`engine-profile.json` records supported sizes/hashes, live-code checks and each
runtime change/restore operation; unsupported versions are refused.

<!-- END-CURRENT-FIVE-ROUND-INSTALL -->

## 2026-10-22: artillery Nuclear Shell test installed — gameplay pending

[Current artillery report](docs/ARTILLERY_NUCLEAR_TEST.md). Oda artillery/siege:
**FH70 BATTERY - NUCLEAR TEST**, four Armstrong placeholder guns; intended button
**Nuclear Shell (TEST)**. One 15-second activation, private radius-40/damage-100
explosion, existing large explosion visual. No mushroom cloud is implemented.
The user approved the temporary shared Shrapnel Shot relink; other assigned
artillery also receive this test ammunition/label while enabled. Working rifle,
grenade and Suppression Fire data are unchanged. Pack installed directly in data;
backups and installed/build hash verified. No gameplay success is claimed yet.
Rollback: `python scripts/artillery_nuclear.py rollback`.

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
[Native R2 report](docs/TYPE20_NATIVE_SUPPRESSION_FIX.md) gives the exact fix:
real suppression_fire assignment, native button unlock, and private projectile
relink. This uses shared native definitions and awaits explicit shared-scope
approval before installation. Animations and firing statistics are unchanged.
The current installed pack remains the preceding build until approval/install.

## 2026-10-21: single-button Suppressive Fire test installed — runtime pending

Latest report: [TYPE20_SUPPRESSION_TEST.md](docs/TYPE20_SUPPRESSION_TEST.md).
New Oda ranged infantry: **TYPE20 SUPPRESSIVE AUTO TEST**, intended button
**Suppressive Fire**. Tests an unused registered engine identity, private activated
projectile and two-shot 0.10-second timing. Longer individual bursts and continuous
fire remain unconfirmed. The user confirmed the previous unit fires paired shots
without a reload animation; all 60 preceding payloads remain byte-identical.
Artillery, grenades and vanilla Suppression Fire are unchanged.
Build/install: `powershell -File scripts/build_type20_suppression.ps1 -Install`.
Rollback to the preceding confirmed behavior: `python scripts/type20_suppression.py rollback`.

## 2026-10-21: separate automatic-cycle trial installed; runtime pending

See [TYPE20_AUTO_CYCLE.md](docs/TYPE20_AUTO_CYCLE.md) for evidence, exact changes,
validation, installation, rollback and gameplay test. New Oda ranged infantry:
**TYPE20 AUTO CYCLE TEST - continuous trial**. The user-confirmed
**TYPE20 BURST TEST - two timed shots** remains available unchanged alongside it.
The new unit combines a 0.30-second two-event firing clip, short aimed recovery
states, and an experimental zero projectile reload timer. Continuous fire is not
confirmed. All 39 prior payloads are byte-identical. Artillery and grenades unchanged.
Build/install: `powershell -File scripts/build_type20_auto_cycle.ps1 -Install`.
Restore confirmed burst build: `python scripts/type20_auto_cycle.py rollback`.

## 2026-10-21: isolated Type 20 burst test installed — runtime unconfirmed

Current instructions and engine evidence: [TYPE20_BURST_TEST.md](docs/TYPE20_BURST_TEST.md).
Oda ranged infantry: **TYPE20 BURST TEST - two timed shots**. Unique registry,
two timed events 0.15 s apart, repeated source recoil poses, and aimed recovery.
Combat DB statistics and all 20 working fallback payloads are unchanged.
No sustained automatic-fire success is claimed. The previous path control was
inconclusive. Build/validate/install: `powershell -File scripts/build_type20_burst.ps1 -Install`.
Rollback: `python scripts/type20_burst.py rollback`. See the report for exact
installed hash, backup record and short gameplay test. Historical entries follow.

> Current result: the user tested the separate Type 20 unit and reports no automatic fire. The two-event experiment failed its gameplay objective. A one-shot animation-path control is now installed; see [TYPE20_PATH_CONTROL.md](docs/TYPE20_PATH_CONTROL.md). Historical build details below are retained.

# Current Type 20 research status

2026-10-21: the research pass found real numbered human firing events.
See [technical report](docs/TYPE20_RESEARCH.md) and
[test checklist](tests/type20-event-test.md).

Installed: data/steel_sakura_combined_test.pack, with the new separate
Steel & Sakura Type 20 Automatic Fire Test alongside the unchanged riflemen.
This is an unconfirmed two-event experiment, not working automatic fire.
All original rifle, grenade, artillery and recruitment pack payloads are preserved.

Current test is COMBAT_AND_VANILLA_BUTTONS_V1. Expected diagnostic button names
are Blinding Grenades and Shrapnel Shot; original named custom skills are not
implemented by this control test. See docs/COMBAT_DIAGNOSTIC.md.

# Combined test installation — corrected 2026-10-21

Install `steel_sakura_combined_test.pack` directly into:
`D:\Games\Total War - SHOGUN 2\data`.

`data\MyMods` was the wrong installation destination for this setup. Historical
notes describing that folder are superseded. The active user script references
filenames in `data`; the previous loaded infantry pack there was older than the
copy we updated in MyMods. Artillery had never been installed.

## Build and install

Close the game. From the project directory:

```powershell
pwsh -NoProfile -File scripts/build_combat_diagnostic.ps1
python scripts/install_combined.py --dry-run
python scripts/install_combined.py
```

Configuration is in `src/install_config.json`. The installer requires a matching
RPFM/offline validation receipt, backs up the root `mod_list.txt`, the active
`%APPDATA%\The Creative Assembly\Shogun2\scripts\user.script.txt`, and every
existing approved Steel & Sakura pack before writing anything to the game.
It preserves each configuration's encoding and all unrelated mod entries.

Only the combined pack is enabled in both loading lists. Obsolete Steel & Sakura
packs from `data` and `data\MyMods` are moved into the project backup, preserving
their original bytes. Otomo, the intro-skip mod, vanilla packs and saves are not
installation targets. The installer verifies unrelated mod hashes and vanilla file metadata and writes
`build/combined/install-receipt.json` with installed hash and backup location.

## Test and rollback

Use original Sengoku Custom Battle, faction **Oda**. Look under matchlock/gun
infantry for **Modern Infantry Squad (Type 20)** and siege/artillery for
**Modern Artillery Battery (FH70)**. See `docs/COMBINED_TEST.md`.

Rollback using the exact backup named in the install receipt: restore both
loading configurations and the old packs to the relative game paths recorded
under `previous-copies`. Move the combined pack out of `data` if it was absent
before installation. Preserve unrelated files and saves.

This remains a test milestone until the user confirms both units and both
ability buttons appear. Neither automatic rifle fire nor grenade throwing is
claimed working. Tosa and Armstrong graphics remain placeholders.
