# Steel & Sakura project rules

The user's latest instructions require a timestamped backup BEFORE every file
modification. Use scripts/tracked_files.py for workspace writes and deletions.
Each transaction records absolute original path, SHA256, preserved original,
planned new hash, and rollback command. Record a missing original for new files.
Never overwrite/delete backup copies or immutable backup manifests. Use Python -B
for research scripts to avoid untracked bytecode writes. Existing legacy build
scripts are not automatically compliant: wrap/upgrade their writes before use.
External tools may also write config/cache files; prepare their backup coverage
before launching them. Do not assume that an old installer meets the new rule.

Preserve confirmed burst archives and all previous experiments. Current confirmed
hashes are listed in docs/ENGINE_BURST_RESEARCH.md. Never substitute a model or
static check for in-game evidence. Current infantry rifle-controller mapping is
unresolved; do not repeat the earlier unsupported universal two-shot-limit claim.

Engine research and experimental patches/copies are authorized INSIDE the project.
Original game EXEs/DLLs must not be changed without explicit user approval.
Do not inject code, install/load an experimental game patch/hook, or attach/pause
with a debugger without approval for that action. The current workspace scaffold
is pass-through-only, NOT_FOR_INSTALL, and is not a functional five-shot patch.
New software installation still requires approval. No engine-patch installer is
provided. Use official sources for any proposed debugger/tool downloads.

Experimental .pack installs belong directly in the game's data directory, never
MyMods; back up the previous pack and loading configuration first, record original
path/hash, provide rollback, preserve unrelated mods/saves, and verify installed
hash. No new pack installation is required for the current engine investigation.
Keep replies concise: evidence, modifications, backups, and the next needed test.
