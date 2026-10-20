# Technical research and evidence

## VERIFIED: installed game and toolchain

- Read-only inventory found 16 `.pack` archives, including `data_fots.pack`, at `D:\Games\Total War - SHOGUN 2`. The executable's Windows metadata says file version 1.1.0.0 and product version 3.1.0.0. This metadata does not establish the loaded game's runtime version. Evidence: `build/inventory/game_inventory.json` and `docs/technical-findings.md`. Confidence: high for files and metadata, low for runtime version.
- Official RPFM v5.2.0 opened installed `data.pack` and `data_fots.pack` as PFH3 Release packs; its MCP server decoded installed Shogun 2 DB tables. The four infantry table versions are 16 (`unit_stats_land`), 13 (`units`), 2 (`building_units_allowed`), and 0 (`units_to_groupings_military_permissions`). Evidence: generated `build/inventory/table_*.json` and [RPFM v5.2.0 release](https://github.com/Frodo45127/rpfm/releases/tag/v5.2.0). Confidence: high for local decode.
- RPFM v5 has a local server with an MCP interface, used by `scripts/rpfm_mcp.ps1`; the v5 Windows bundle has no `rpfm_cli.exe`. [Official server documentation](https://frodo45127.github.io/rpfm/manual/server/overview.html). Confidence: high for the installed v5.2.0 bundle.
- Installed FoTS `Boshin_Inf_Light_Tosa_Riflemen` uses a repeating-rifle missile type, a FoTS rifle animation, and a FoTS equipment theme. Existing Sengoku `Inf_Missile_Matchlock_Ashigaru` supplies the companion unit and Japanese military-group prototype. Evidence: decoded local rows. Confidence: high for references, no confidence yet for their combined in-game behavior.
- Installed FoTS Armstrong and Gatling artillery use an articulated horse-drawn gun entity. Model-pack filenames include their rigid models and animations. This is an artillery experiment basis only. Evidence: local DB and 14,322 model-pack path scan. Confidence: high for path and row observations.
- Installed base rows also contain `test_limber_gun`: 40 crew, four Parrott guns, `gun_train_2_horse`, and no observed Fort recruitment or `japan` permission. A separate two-row research pack enables those permissions and reopens in RPFM. It is not installed or distributed and proves no in-game movement. Confidence: high for decoded rows and pack structure, low for runtime behavior.
- Installed English `text/db/units.loc` has `units_on_screen_name_<unit key>` entries. `text/db/unit_description_texts.loc` has description, long description, and strengths/weaknesses keys for both Matchlock Ashigaru and Tosa Riflemen. The prototype uses these observed key patterns with original English copy. Evidence: locally decoded `build/inventory/loc_*.json`. Confidence: high for format and local key pattern; in-game lookup untested.
- Installed Matchlock Ashigaru UI assets are uncompressed 32-bit TGA at 64×118 (`icons`), 46×46 (`icons_square`), 128×236 (`info`), 75×75 (`recruitment_large`), and 64×64 (`recruitment_small`). The project draws original cards at these measured sizes. Evidence: local RPFM extraction into ignored `build/inventory/sample-icon/` and TGA header inspection. Confidence: high for file format/dimensions, low for lookup of newly named assets.
- The same model-pack filename scan found no aircraft/A6M/Zero/airplane/aeroplane/biplane/balloon name. A filename scan cannot prove an engine feature is impossible. Confidence: high for the scan, low for any engine inference.
- A broader model-pack scan found bird fauna meshes and textures, while `data.pack` contains `animations/shogun_animation/battle/animals/birds/bird_cycle.anim`. Decoded `battle_entities_tables` v0 has 42 rows and movement/radius/height fields, but no aircraft-named row or altitude field in that table. This points to an ambient bird animation research path, not a unit flight/control system. Evidence: local archive path scans and `build/inventory/table_battle_entities.json`. Confidence: high for observed files/fields, low for feasibility of adaptation.

## Model import constraints

- RPFM's [Rigid Model editor manual](https://frodo45127.github.io/rpfm/manual/editors/rigidmodel.html) says its editor reads/writes supported rigid-model versions, but does not edit geometry, bones, or attachment points; external authoring/export tooling is needed. Confidence: high for RPFM's documented editor limits.
- RPFM's [glTF extension documentation](https://frodo45127.github.io/rpfm/api/rpfm_extensions/gltf/index.html) marks `rigid_from_gltf` as not yet implemented and notes animation export limitations. This blocks assuming a built-in glTF-to-game path in this RPFM toolchain, not all possible community import paths. Confidence: high for this documented API state.

## PROVISIONAL conclusions

- The built infantry pack reopens in RPFM and passes source/schema/collision checks. Its English strings and five TGA files round-trip through RPFM. This does not verify recruitment, custom battle inclusion, visible appearance, text/icon lookup, automatic fire, or game stability.
- A horse-drawn artillery unit might be a useful movement and cannon test for a tank, but it does not make a Chi-Ha.
- No route to a visible flying aircraft has been verified. No off-map strike is counted as a Zero.

See `docs/technical-findings.md` for detailed local observations. Generated decoded tables stay local and are excluded from source distribution.
