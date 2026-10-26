# Read-only capture — 24 October 2026

User confirms the restored two-shot build does not crash. Approved read-only observer detached automatically after 180 seconds. No game-memory writes, extra-shot controller, game binary/pack/config changes, or runtime exceptions were reported. Disk preservation hashes match.

New evidence: actor+0x214 points to the unit; unit+0x28 points directly to the exact terminated UTF-16 key `steel_sakura_type20_automatic_fire_test`. All 12 observed custom unit objects match. Four captured actor blocks independently verify the actor-to-unit link. The earlier unit+0xB9C assumption was not the correct route to this key.

400 native pre/post pairs each consumed exactly one ammunition unit. This confirms accounting for those native emissions, not for an unimplemented extra-shot path. Two actors were polled 1,103 times. Their snapshots are nonatomic; twelve custom units were present, and user Stop/Move timing/selection has not yet been confirmed. Do not label raw state changes as movement, cease-fire, or death. No death test was conducted. Five-shot firing remains unproven.

Evidence: build/read-trace/20261024T050235.371701Z/report.json and identity-analysis.json. The earlier launch had malformed quoted paths and exited without a trace log; its attachment outcome is unknown and recorded separately. The corrected run logged attach, orderly drain, detach and end. Both executable revisions passed synthetic transport tests; these are not gameplay tests.

Re-run offline analysis: `python -B scripts/analyze_read_trace.py`.
One-command rollback: `python -B scripts/read_trace_rollback.py`. Restores existing edited files and archives observer sources/executables; preserves trace/crash evidence and all backups. Timestamp/hash receipts are under backups/tracked-* and backups/banzai-compiler-*.

Next: obtain the user's description of which units received Stop/Move. No additional battle or five-shot activation requested yet.
