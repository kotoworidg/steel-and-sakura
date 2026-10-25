# Type 20 playable upgrade 0.1.0

A supported-mechanics release built from the preserved, user-confirmed two-shot
pack `0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270`.
Select **JSDF Type 20 Rifle Section** under Oda ranged infantry in Sengoku Custom
Battle. The unit remains 40 soldiers at its authored size. Existing riflemen and
artillery remain in the combined pack.

| Setting | Two-shot baseline | This release |
| --- | ---: | ---: |
| Marksmanship | 45 | 80 |
| Rifle projectile velocity field | 200 | 850 |
| Effective range | 900 diagnostic value | 450 |
| Calibration distance / area | 100 / 1 | 200 / 0.75 |
| Native ammunition setting | 200 | 210 |
| Formation rank depth | 3 | 2 |
| Close spacing horizontal / vertical | 0.8 / 1.75 | 1.4 / 2.4 |
| All-rank firing | false | true |
| Skirmish capability | true | false |
| Guard capability | false | true |
| Loading skill | 100 | 80, with native ability headroom |
| Base projectile reload timer | 1 | 1, preserved |
| Custom-battle cost | 400 | 1200 |

Normal bullets retain positive damage 3 and armour-piercing `ap` behavior, one
projectile per native event, and native impact handling. Fort-wall penetration
is disabled. The normal projectile has no explosion or simultaneous multi-shot
trick. These are game tuning values, not a calibrated simulation of the real
Type 20. The existing two-marker clips, animation registry, reload mappings,
rig, equipment references and native controller selector are byte-identical.

The core pack adds the existing **Rapid Volley** ability. It retains native
60-second active time, 300-second recharge and 60-second initial recharge. The
native effect requests +15 loading skill; ordinary firing returns automatically
when it expires. Wait for the initial recharge before expecting the button to
be usable. The default projectile does not switch for this core ability.

The optional **Suppression Fire** module uses the previously activated native
ability identity, 30-second duration, 120-second recharge, and manual activation.
It switches to a private damaging suppression projectile (damage 2, velocity
850, range 450, one projectile/event, reload timer 1, calibration area 1.5).
Existing native suppression effects are retained: +20 loading, -20 accuracy,
and hit-target movement/morale penalties. Actual application and return to rifle
ammunition still need gameplay verification on this build.

The optional module changes the shared `suppression_fire` definition: it unlocks
the native button and relinks its ammunition. **Every other unit already assigned
native Suppression Fire also receives this unlock and projectile during use.**
The core-only installation adds no new shared ability overrides. Existing shared
grenade definitions inherited from the baseline remain unchanged. Modern Otomo
files are never installation or build targets.

Five-round bursts, true full-auto and per-soldier 30-round magazine reloads remain
unimplemented. The fallback is repeating native two-shot cycles with a finite
native ammunition reserve and ordinary engine reload handling. No controller,
debugger, injector, game binary patch or external simulation is used. Tosa/Spencer
visuals remain placeholders. No campaign recruitment or JSDF faction is added.

## Build and validate

From the existing checkout:

```powershell
python -B scripts/type20_playable.py build --iteration 1
python -B scripts/type20_playable.py validate
python -B scripts/validate_type20_rpfm.py run
python -B -m unittest discover -s tests -p 'test_*.py' -v
python -B scripts/package_type20_playable.py
```

The build script limits this version to three meaningful iterations. Iteration
1 passed; no additional gameplay rebuild was needed. Revalidating or packaging
does not create another gameplay iteration. Build output is under
`build/type20-playable/iteration-01/`. The ZIP is under
`dist/type20-playable/steel-and-sakura-type20-0.1.0.zip`.

The builder requires the preserved baseline/R2 packs and existing RPFM-decoded
schema evidence already present in this checkout. The package installer uses
only standard-library Python. The installed RPFM 5.2.0 server is used headlessly
for independent table/localization reopening, with pre-launch state backups.

## Install and rollback

Extract the release ZIP to a writable folder. From that folder:

```powershell
python -B install_type20.py install --dry-run
python -B install_type20.py install
```

To opt into the shared native suppression module:

```powershell
python -B install_type20.py install --with-suppression --dry-run
python -B install_type20.py install --with-suppression
```

The installer defaults to `D:\Games\Total War - SHOGUN 2`; override with
`--game-root <path>` for an identical supported installation. Packs go directly
into `data`. Close the game first. It verifies EXE/DLL hashes without modifying
binaries, checks package hashes, and refuses unknown installed Steel & Sakura
packs or conflicting extra copies. Both loading lists retain unrelated entries
and their encodings. Choosing core-only removes the optional module if this
installer previously installed it; the change is backed up and reversible.

Every affected existing pack/configuration is copied with an SHA256 check before
any write. Missing originals are recorded. Immutable intent manifests include
absolute paths, original hashes, staged output hashes and exact rollback commands.
Backups stay in the extracted package's `backups/type20-<timestamp>-<id>/` folder.
The install output prints the exact receipt and rollback command, for example:

```powershell
python -B install_type20.py rollback --receipt "<backup-folder>\manifest.json" --dry-run
python -B install_type20.py rollback --receipt "<backup-folder>\manifest.json"
```

Rollback takes fresh backups and refuses later user edits or corrupted originals.
Retain the extracted package and its backups while the upgrade is installed.
The current installed game was left on its preserved baseline during development.

## Verification and first gameplay checks

Offline: both packs pass structural/reference/damage/ammunition checks. RPFM
independently reopens all eight changed/added tables and localization payloads,
matching every scalar and schema version. All 35 unrelated baseline payloads
remain identical, including both confirmed firing clips. Regression tests cover
corrupt packs, changed animations, zero-damage and fake multi-projectile edits,
invalid ammo, unrelated artillery, install/rollback, encoding preservation,
failed-install recovery, and refusal to discard later edits.

This release has not been played in-game. Verify the exact unit name, 40-man
size scaling, accuracy/casualties, fast projectile impacts, all-rank firing,
formation spacing, absence of skirmish retreat, Stop/Move response, finite ammo
and reload behavior. Then check Rapid Volley after its initial recharge. If the
optional module is selected, separately check its button, damage/debuffs,
30-second expiry, 120-second recharge and return to normal ammunition. Stability
and compatibility with the active Otomo setup require actual gameplay evidence.
