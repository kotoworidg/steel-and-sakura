> Current result: the user tested the separate Type 20 unit and reports no automatic fire. The two-event experiment failed its gameplay objective. A one-shot animation-path control is now installed; see [TYPE20_PATH_CONTROL.md](docs/TYPE20_PATH_CONTROL.md). Historical build details below are retained.

# Current Type 20 research status

2026-10-21: the research pass found real numbered human firing events.
See [technical report](docs/TYPE20_RESEARCH.md) and
[test checklist](tests/type20-event-test.md).

Installed: data/steel_sakura_combined_test.pack, with the new separate
Steel & Sakura Type 20 Automatic Fire Test alongside the unchanged riflemen.
This is an unconfirmed two-event experiment, not working automatic fire.
All original rifle, grenade, artillery and recruitment pack payloads are preserved.

## Active engine diagnostic V1 - 2026-10-21

Both units were visible, but no custom buttons and no modern combat behavior
were observed. The previous custom UI experiment failed. Current diagnostic uses
separate normal combat projectile/gun keys and supported vanilla Blinding Grenades
and Shrapnel Shot buttons with vanilla special ammunition unchanged. One temporary
grenade technology-unlock flag affects vanilla ninjas while enabled. See
[combat diagnostic and low-FPS test](docs/COMBAT_DIAGNOSTIC.md). Rebuild with
scripts/build_combat_diagnostic.ps1. Milestone remains PENDING_USER_CONFIRMATION.

## Combined correction - 2026-10-21

Use scripts/build_combined.ps1 and scripts/install_combined.py. Install directly
into game data; older MyMods notes are superseded. Test Oda gun infantry and
siege/artillery. Both units/buttons require user confirmation. See
docs/COMBINED_TEST.md and INSTALL.md.

# Test plan when a GPU is available

## Offline verification now

Run `pwsh -NoProfile -File scripts/build.ps1`. It prepares local rows, builds and reopens the pack with RPFM, runs `scripts/validate_offline.py`, and executes Python regression tests. The generated report is `build/validation/offline-report.json`. Static checks do not prove gameplay.

## In-game infantry acceptance

Use a disposable new Sengoku campaign and keep existing saves untouched. Record game executable/runtime version, selected unit-size setting, enabled mod list, screenshots or video, and any crash logs.

1. Confirm the campaign loads and existing factions/buildings appear normally.
2. Check a Japanese faction's Fort recruitment panel for Automatic Rifle Squad. Record cost, availability, text, icon, and whether recruitment completes.
3. Deploy it in battle and count soldiers at the selected unit-size setting; the DB target is 40, but unit-size scaling may affect observed count.
4. Observe model/equipment, movement, ranged attack, reload timing, ammunition, accuracy, morale, sound, and crash/stall behavior. Compare to a FoTS repeating rifle unit; do not call the fire mode automatic without observed evidence.
5. Check custom-battle selection separately. Record absence as a defect rather than assuming campaign permission covers it.
6. Test with the existing Otomo mod enabled and disabled to isolate conflicts. Preserve both mod-list configurations.

## Tank and aircraft gates

For tank research, `pwsh -NoProfile -File scripts/build.ps1 -ArtilleryTest` creates a separate pack in `build/`. Back up `mod_list.txt` before any temporary installation. Test whether the dormant limbered gun recruits from a Sengoku Fort and capture actual movement, collision, aim/firing, and crew behavior. Remove the research pack after testing. A horse-drawn gun does not pass the Chi-Ha acceptance gate. For aircraft, require on-screen 3D geometry continuously above the battlefield, verified movement/animation and meaningful game control or scripted behavior. An off-map strike or projectile does not pass.
