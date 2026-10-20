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
