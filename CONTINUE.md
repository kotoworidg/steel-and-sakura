# Continue this project later

Use this prompt in a future Codex session:

> Continue Steel & Sakura from this repository. Read README.md, PROGRESS.md, RESEARCH.md, LIMITATIONS.md, ARCHITECTURE.md, TESTING.md, and docs/technical-findings.md first. The target is the original non-Steam Shogun 2 Sengoku campaign with FoTS installed at `D:\Games\Total War - SHOGUN 2`. Preserve original archives and saves; back up before changes. One 40-man infantry prototype has been built and statically validated with English localization and original UI cards, but no gameplay test has occurred because the GPU was unavailable. The tank and visible flying Zero remain blocked research goals. Do not claim any feature works without in-game evidence or substitute an off-map airstrike for an aircraft. Rebuild with `pwsh -NoProfile -File scripts/build.ps1`, inspect `build/validation/offline-report.json`, and follow TESTING.md when the GPU is available. Resolve the GitHub repository access issue before publishing; do not commit extracted game data, backups, tool binaries, or local packs.

Current local outputs live in `build/` and `dist/`, both ignored by Git. The project-local RPFM binary and configuration are also ignored. Retain the full workspace and backup folders if a future session needs to rebuild without redownloading tools.

An additional **uninstalled** artillery mechanics experiment can be rebuilt with `pwsh -NoProfile -File scripts/build.ps1 -ArtilleryTest`. It enables the game's existing `test_limber_gun` through two rows; it is not a Chi-Ha and is excluded from releases.

Aircraft research found bird fauna meshes and `bird_cycle.anim` in installed archives. This is only an ambient animation lead; no Zero model, flight control, or airborne unit has been demonstrated. See `source/aircraft/README.md`.
