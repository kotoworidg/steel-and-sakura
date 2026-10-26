# Steel & Sakura — final attempt, 23 October 2026

**Stopped five-shot development. The confirmed two-shot pack is restored; recovery stability remains untested.**

- Installed `D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack`: SHA256 `0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270`. This is the original confirmed two-shot WITH reload build, not the later automatic-cycle/Suppression Fire additions. Its entry was appended to `mod_list.txt` and `scripts/user.script.txt`; existing unrelated entries and archives were preserved.
- Evidence copies: `build/final-attempt/20261023T093032.281929Z/`. Inventory records original absolute paths, UTC file times and SHA256; preserves all available Shogun dumps, filtered Windows event XML, logs, configs, installed R2 pack, working fallbacks, controller sessions and source.
- New crash signature: 22 October 22:22/22:25, `Empire.Retail.dll + 0xC0C624`, `0xC0000005`, read `0xC`. Fault instruction reads `[eax+0xC]` with EAX=0. Its code emits a missing-key diagnostic naming `UNIT_EXPERIENCE_THRESHOLD_RECORD` before the failure. This establishes a failed experience-table lookup, not the missing key or responsible mod. These dumps do not prove the reported firing freeze has that same cause. Older `+0xECFB0` null-string crashes are a separate signature.
- No persistent Steel & Sakura hook found. The original EXE/DLL hashes match the recorded baseline. Last controller session detached at 20:14 on 22 October, with no additional-shot attempts. The game and controller were not launched during this attempt. Earlier graphics diagnostics showed disabled GPU/software-renderer selection; that is a performance risk, not proof of this database failure.

## Research and stopping reason

[Eight-player patcher source](https://github.com/TasmanModding/Shogun2-8Player-Coop/blob/main/lib/Patcher.cs) pins the exact same original engine SHA256 as ours. It checks original instructions, constructs a separate patched copy, uses relative detours/new PE code sections and preserves existing calls. Those are reusable engineering techniques, not an infantry firing implementation. Source and MIT license snapshots are preserved locally; nothing was compiled or installed. [Author notes](https://github.com/TasmanModding/Shogun2-8Player-Coop/blob/main/NOTES.md) describe version-specific state/calling-convention research. The [third-person author's post](https://www.reddit.com/r/shogun2/comments/1xbckn2/third_person_mod_control_any_unit_as_single_entity/) identifies Complete Edition; no source/package was accessible in the inspected post, so its internal mechanism and legacy compatibility were not inferred from video.

The recovered metadata has scalar `FIRE_TIME`/`FIRE_TIME_2` slots; duplicating them does not create five independent events. This is not a universal two-shot engine limit. R3 captured 64 private-projectile matches and 64 candidate ammo decrements of one, but zero verified unit-key matches. Death, cease-fire and movement cancellation remain unmapped. Offline scheduler tests assume these meanings; they cannot establish them. Keeping an action alive for extra shots without those guarantees is not a credible safe implementation. No new five-shot build or hook was created.

## Rollback and one recovery check

`python -B scripts/final_recovery.py rollback`

Restores the pre-recovery pack and both loading lists, after fresh timestamped/SHA256 backups; refuses later edits. Evidence/backups remain. Immutable transaction: `backups/final-recovery-20261023T093038.026552Z-94e27fb6/manifest.json`.

Offline recovery checks: 12 encoding/preservation/idempotence cases, 39 pack entries, two valid 48-bone/two-marker clips; original backups and current rollback hashes verified. Game stability is not claimed.

Recovery-only test when ready: launch normally with no controller/debugger, Oda's **TYPE20 BURST TEST - two timed shots**, one protected rifle unit versus slow melee infantry, abilities off. Observe one burst, then Stop and Move. Stop at any freeze; do not launch an automatic-fire test. No five-shot test is ready.
