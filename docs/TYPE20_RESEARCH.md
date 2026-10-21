> Current result: the user tested the separate Type 20 unit and reports no automatic fire. The two-event experiment failed its gameplay objective. A one-shot animation-path control is now installed; see [TYPE20_PATH_CONTROL.md](TYPE20_PATH_CONTROL.md). Historical build details below are retained.

# Type 20 infantry: firing-system research and bounded experiment

Date: 2026-10-21. Status: OFFLINE INVESTIGATION AND EXPERIMENT; AUTOMATIC FIRE UNCONFIRMED.

## 1. Findings and limits

The previous build genuinely changes reload statistics, as the user confirmed in battle.
It still uses the rifle controller and human musket firing clip. That explains why a
faster reload alone did not establish automatic fire.

New evidence opens a more specific route: installed human dual-pistol clips contain
FIRE_TIME and FIRE_TIME_2, with corresponding muzzle positions. A mounted clip gives
these different times. The human rifle clips have only the first pair. We can edit
the event block without changing the skeleton or motion data. This justifies testing
a second timed event on a separate rifle unit. It DOES NOT prove the rifle controller
dispatches that event, nor establish unrestricted burst counts or continuous fire.

No inspected mod supplies a proven modern automatic-infantry implementation.
Expanded Japan and Radious were inspected as actual local packs. Other named mods
were investigated through author/distribution pages, with explicit access gaps below.

The model-format barrier is smaller than previously understood: actual installed
equipment libraries successfully round-trip through an open-source VMPF reader/writer.
An original coarse rifle blockout was exported and round-tripped separately. Rendering,
attachment registration and convincing Type 20 grip/recoil remain unproven.

## 2. Mod research: what was actually inspected

| Candidate | Access/evidence | What was learned |
| --- | --- | --- |
| Expanded Japan | User-supplied new_regions.pack, 13,217,227 bytes; 408 packed files inspected in RPFM | Nine campaign tables, map/border/road/startpos content. No unit combat tables, battle animation files, or battle models. This supplied pack has no automatic-fire solution. This finding does not cover every mod called Expanded Japan. |
| Radious Sengoku | User-supplied radious_total_war_mod.pack, 79,432,810 bytes; 1,074 packed files and relevant DB tables inspected | Real custom unit keys, equipment themes, projectiles, uniforms, recruitment and vanilla ability junctions. 246 land-stat rows across seven files use only matchlock/none; 58 row keys are absent from this installed vanilla land-stat catalog. No animations/ payloads; 48 unit-part meshes. Detailed example below. |
| DarthMod Shogun II | Author's ModDB overview, file list, v5 package page and normal browser download dialog read | Author documents battle/AI/formation/synchronization work and optional visual mods. Automated download returned HTTP 403; browser transfer timed out. Package contents NOT inspected; no firing-controller conclusion drawn from advertising. |
| Morning Sun | Author uanime5's Workshop collection read | Useful campaign and custom-roster reference candidate. Package not obtained; no claim about its exact weapon, mesh or animation implementation. |
| Tosa Isekai | Author Workshop search results, Nexus file list and author's download announcement found | Nexus lists arg.pack and argex.pack for ordinary/Expanded Japan variants. Descriptions concern bringing Tosa into Sengoku; they do not establish automatic fire. Signed-in/download access gap; package not inspected. |
| Ultimate Expanded Field Command | Author Workshop description and credits read | Combines Sengoku/FoTS content and several unit/map/artillery contributions; explicitly distinguishes the original game. Package not obtained. No proven automatic-infantry scheduler learned. |
| FoTS Artillery Tweaks v3, The_Yogi | Author Workshop description read | Documented changes concern range, elevation, accuracy/reload and train properties. No source-level evidence of a new firing controller. No artillery changes made here. |
| S2TW Vanilla Plus, Edgy190 | Public author's GitHub pack downloaded ONLY for research, RPFM inventory and land rows decoded | 345 land rows use matchlock/none and familiar vanilla animation tables; pack has no custom animation assets. Does not establish modern automatic fire. |
| Forgotten Total Wars, Rebrond | Public repository tree and Shogun2 source filenames inspected | Visible Shogun2 work concerns borderless/window/UI behavior. No inspected firing patch. No DLL installed or executed. |
| RAW Equipment / Havie animation guide | Author resource listing / community tutorial index located | Leads for follow-up, NOT completed tutorial/workflow verification: direct pages were inaccessible. No assets borrowed. |

### Direct Radious implementation example

Inside db/unit_stats_land_tables/aum_unit_stats_land:
aum_Inf_Missile_Arquebusiers_Samurai selects shogun_man_musket,
firing_mechanism=matchlock, equipment_theme=aum_shogun_arquebusier,
default_missile_type=aum_shogun_arquebusier.

Its equipment theme in aum_warscape_equipment_themes selects the existing
shogun_oversized_teppo item. Its independent projectile in aum_projectiles has
projectile_number=1, range=170, damage=2, reload=35. This is a genuinely distinct
DB unit/projectile/loadout using an existing firing system.

The uniforms row points to samurai_inf_missile_arquebusiers_samurai_aum.
Its ability junctions use rank_fire, rapid_volley, kneel_fire_ability and bamboo_wall.
Recruitment rows reference SHO_Siege_3_Gunsmith and SHO_Siege_4_Arsenal.
The special-ability table contains 43 keys, all present in our vanilla catalog.
It does not supply a demonstrated new ability dispatch type.

The 48 mesh entries are unit parts such as heads, helmets, torsos and limbs.
There is no animations/ content and no inspected automatic firearm controller.
The only Lua files are export_experience.lua and campaigns/jap_shogun/scripting.lua; static review finds experience/campaign logic and no per-shot battle scheduler. Neither was executed.
Mesh presence proves packaged custom appearance content; it does not prove original
authorship of each mesh or runtime compatibility with our installation. None was reused.

### Sources and provenance

- [Radious author Workshop page](https://steamcommunity.com/sharedfiles/filedetails/?id=99424636)
- [Radious historical unit pack listing](https://www.moddb.com/games/shogun-2-total-war/downloads/radious-units-mod-9-0-special)
- [DarthMod author page](https://www.moddb.com/mods/darthmod-shogun-2)
- [DarthMod v5 author upload](https://www.moddb.com/mods/darthmod-shogun-2/downloads/darthmod-shogun-ii-v5)
- [Expanded Japan listing matching supplied folder ID](https://steamcommunity.com/sharedfiles/filedetails/?id=3439306253)
- [Morning Sun author collection](https://steamcommunity.com/workshop/filedetails/?id=294977787)
- [Tosa Isekai author's Nexus file list](https://www.nexusmods.com/totalwarshogun2/mods/13?tab=files)
- [UEFC author page](https://steamcommunity.com/sharedfiles/filedetails/?id=3461206466)
- [The_Yogi artillery tweaks](https://steamcommunity.com/sharedfiles/filedetails/?id=105216586)
- [Vanilla Plus repository](https://github.com/Edgy190/mod_S2TW_Vanilla_Plus)
- [Forgotten Total Wars repository](https://github.com/Rebrond/Forgotten-Total-Wars-)
- [RAW equipment author resource lead](https://www.totalrtsmods.com/post/raw-equipment-carbines-revolvers-muskets-models-for-modders-12409893)
- [TWC tutorial index, including Havie animation guide lead](https://wiki.twcenter.net/index.php?title=Total_War%3A_Shogun_2_-_Modding_Index)

Radious local SHA256: 6AFDBA13FD82D6313F5EDD70878F391EA3D0936CF7A832747BB21610C61A4B5E.
Expanded Japan SHA256: 942AC02792EEAEACD450BBAA2CDD9B55362F86E11B400145DC6A6EF47DE2951A.
Vanilla Plus SHA256: B83DAD0F2F4A41AC58DFCD0D6506C5F79E7585730055E224C35C2204C0F3CAC4.

The Radious mirror was supplied by the user. Its ZIP endpoint had an expired TLS
certificate; validation was not bypassed. Inspection used the user's already
downloaded local pack. Its identity against an author-published checksum remains
unverified. The raw research findings apply to those exact bytes.

The local executable version resources do not expose a usable patch/build number.
Compatibility claims here are limited to the inspected local pack schemas and asset formats;
there is no claim of verified gameplay compatibility with an untested game patch.

## 3. Installed firing dependency chain

Evidence: RPFM-decoded data.pack tables under build/diagnostic/base_*.json;
fresh installed snapshots under build/type20-research/installed_*.json;
equipment tables under build/type20-research/base_warscape_equipment_*.json.

Units v13 supplies identity, category, cost, unit card and roster flags.
Unit_stats_land v16 supplies the same unit key, men, controller selectors, ammo,
animation table, equipment theme, firing mechanism and default projectile.
Projectiles v5 supplies ballistic behavior and base_reload_time.

There is no separately observed infantry missile_weapons table here. The existing
primary_missile_weapon selector remains rifle; an independent loadout is registered
through warscape_equipment_themes/items, plus an independent projectile. A new
equipment key is not a new engine controller.

| Property | Matchlock Ashigaru | Tosa | Gatling |
| --- | --- | --- | --- |
| Land key | Inf_Missile_Matchlock_Ashigaru | Boshin_Inf_Light_Tosa_Riflemen | Boshin_Art_Gatling_Guns |
| firing_mechanism | matchlock | matchlock | none |
| Human animations | shogun_man_musket | boshin_man_rifle_trained | shogun_man_katana crew |
| Missile skeleton | foot_musket | foot_musket | cannon_crew |
| Unit weapon selector | musket | rifle | empty, gun_type used |
| Projectile | shogun_matchlock | boshin_repeating_rifle | boshin_gatling_gun_bullet via gun junction |
| Projectile count | 1 | 1 | 1 |
| Base reload field | 22 | 6 | 18 |
| Base range | 100 | 150 | 250 |
| Base damage | 2 | 0.9 | 1 |

These are base data.pack rows, not claims about every modded effective value.
The existing Otomo pack overrides shared projectile values, including Tosa range.
Our diagnostic projectile is namespaced and has reload=1, range=900, damage=3;
the new event test copies these exactly, preserving the comparison.

Gatling has a separate gun_types row:
boshin_gatling_gun -> battle entity boshin_gatling_gun, model gatling_gun,
animation table boshin_engine_gatling_gun, engine_type Boshin_Gatling_Gun.
gun_type_to_projectiles maps it to boshin_gatling_gun_bullet and puckle_muzzle_flash;
concentrated_fire_maximum_frequency=1.0. That field's precise controller meaning
was not measured. It is not an infantry burst interval.

### Animation selection

animations/animation_tables/animation_tables.txt:
boshin_man_rifle_trained uses skeleton_type man_shogun, inherits musket FIRE and
KNEEL_FIRE, then overrides reload states through boshin_man_rifle_combat_fragment.
The musket combat fragment selects:
- animations/shogun_animation/battle/men/musket/musket_poise/mus_fire.anim
- animations/shogun_animation/battle/men/musket/musket_kneel/mus_kneel_fire.anim

Gatling's table uses skeleton_type gatling_gun. Its fragment binds ENGINE_FIRE
and ENGINE_FIRE_LOOP to the same engine clip. Human operator/loader clips have
48 bones and no shot events; the gun clip has 7 bones. Swapping this gun clip onto
a human rifle skeleton is not a supported conversion.

### Parsed binary events: new direct evidence

Our reader consumes complete v1 clips and reconstructs their event blocks byte
for byte. Eleven real clips were checked, not just searched for text strings.

| Clip | Duration / frames / bones | Shot event values |
| --- | --- | --- |
| mus_fire.anim | 1.0 s / 21 / 48 | FIRE_TIME 0.05; one FIRE_POSITION |
| mus_kneel_fire.anim | 1.6 s / 33 / 48 | FIRE_TIME 0.00; one FIRE_POSITION |
| pistol_fire.anim | 1.8 s / 37 / 48 | FIRE_TIME 0.02 |
| dual_pistol_fire.anim | 1.6 s / 33 / 48 | FIRE_TIME 0.12; FIRE_TIME_2 0.12; two positions |
| rider_dual_pistol_b_fire.anim | 3.6 s / 73 / 48 | FIRE_TIME 1.65; FIRE_TIME_2 1.30; two positions |
| rider dual-pistol front/left/right | 48-bone clips | Both numbered markers, with equal or slightly different times |
| gatling_fire.anim | 0.7 s / 15 / 7 | FIRE_TIME 0.50; one position |
| gat_op_fire.anim / gat_loader_fire.anim | 48-bone clips | Empty event blocks |

The mounted back-firing clip establishes that CA authored two distinct shot times
in one human clip. Runtime use of both by foot rifle infantry remains a hypothesis.
Marker positions can also be tied to weapon/controller-specific code; their
presence alone does not prove general dispatch.

The only inspected base projectile with projectile_number>1 is shogun_donderbuss,
with six. Its schema has no temporal burst spacing field. This is evidence for a
projectile count, not evidence for six successive automatic shots.

## 4. Supported, uncertain, and possibly hardcoded

| Question | Evidence-based answer |
| --- | --- |
| New units, equipment themes/items, projectiles and cards? | Structurally supported; existing custom roster and reload changes already confirmed in game. |
| More than one projectile configured per firing event? | Count field and vanilla count-six example exist. Temporal distribution unverified. |
| More than one shot time in a human animation? | Demonstrated in actual dual-pistol files. |
| Does the rifle controller honor FIRE_TIME_2? | Unknown. This is the specific installed experiment. |
| Arbitrary three-/ten-shot event lists? | Not established; no invented FIRE_TIME_3 or burst enum added. |
| Sustained automatic foot-infantry fire? | No verified route yet. Gatling engine looping does not establish a human loop. |
| New firing_mechanism names? | Only matchlock/none observed in inspected rows. Schema points at an enum not found as a packed table. No auto enum invented. |
| Are all limitations hardcoded? | Not proven. Engine source/disassembly was not obtained; controller behavior beyond data/animation dispatch remains uncertain. |
| New or adapted human motion files? | File layout/editing and matching rig preservation verified offline; runtime acceptance of our custom table and clips remains untested. |

Database values request cadence, ballistics, counts and controller/asset choices.
Animation fragments choose states/clips; binary clips contain motion and shot markers.
The engine schedules states and dispatches events. The last statement is an
architectural inference from those dependencies; it is not a recovered engine
implementation or a claim that a DLL patch has been made.

## 5. Model and animation authoring workflow

CA's [official Assembly Kit overview](https://wiki.totalwar.com/w/Official_CA_modding_tips_and_tutorials)
documents Max export scripts, example models, Unit Editor and BoB processing.
No Assembly Kit, Max or Blender installation was performed.

The reviewed GPL-3.0 [Blender format tool source](https://github.com/robert-d-schultz/rmv2_anim_blender_import_export/tree/28c2f47ba12cf3e5d02df75cf65579a1111b3deb)
provides Shogun 2 v1 animation and VMPF import/export. Its documented workflow is
reference skeleton first for skinned parts, then mesh; preserve bone indices and
export the game's format/version. Events are preserved separately from sampled
motion. A modern RMV2/animation version must not be exported blindly for Shogun 2.

Local validation: twelve equipment VMPF files, including mesh1/mesh2 libraries,
were read and re-saved byte-identically. These installed files are VMPF v3,
rigid named-part format 2, skeleton man_shogun. Spencer's part is attached at bone
index 1 and has four LOD entries. This validates the format code against this
installation; it does not validate the whole Blender UI/export/render pipeline.

Original blockout:
- Source: assets/type20/type20_blockout.obj, created from six original cuboids.
- Generator: scripts/create_type20_blockout.py.
- Native research output: build/type20-research/original-model/type20_blockout.variant_part_mesh.
- Four LOD parts; 144 vertices / 72 triangles per LOD; native re-read/write identical.
- No game mesh geometry or another mod's assets copied into this original model.
- Coarse rifle silhouette only; not dimensionally accurate Howa equipment.
- NOT installed in the firing pack. Material appearance, equipment lookup, grip,
  muzzle alignment and render behavior still need a separate controlled test.

A 3D replacement would follow equipment_theme -> equipment_key -> equipment_item
and the variant/equipment library registration, retaining Weapon1 attachment and
matching human rig. The complete new-name equipment-library lookup has not yet
been validated. We intentionally retain the Spencer visual while testing events.

## 6. Minimal experimental implementation

Display name: Steel & Sakura - Type 20 Automatic Fire Test
(the installed localization uses an em dash after Sakura).
Unit key: steel_sakura_type20_automatic_fire_test.

New independent rows:
- units, unit_stats_land, uniforms;
- Oda exclusive permission and japan military grouping;
- warscape_equipment_themes with an independent primary_weapon key;
- warscape_equipment_items with that key, pointing to the existing spencer item;
- projectiles with key steel_sakura_type20_automatic_fire_test_bullet.

It shares the human rig and temporary uniform/model. The projectile's ballistic
values, reload, count and damage match the working rifle. No new controller enum
or invented DB field was introduced.

Its private fragment overrides only FIRE/KNEEL_FIRE. New animation files preserve
every header, bone and frame byte; they add FIRE_TIME_2 at 0.35 standing / 0.30
kneeling, with FIRE_POSITION_2 equal to the existing muzzle position.
The existing first markers remain 0.05 / 0.00. Interval: 0.30 seconds.

Rationale: transplant only a marker pair observed in real human dual-pistol clips.
Risks: the rifle path may ignore it, use only one event, require a pistol-specific
controller, or emit effects without an extra damaging projectile. No second recoil
motion has been authored yet. This is a scheduler diagnostic, not completed Howa
animation or sustained automatic fire.

The shared animation registry path is included with its original bytes intact and
one uniquely named table appended. This is a real shared-file override footprint,
not a claim of a magically isolated asset loader. Inspected boot, bp_orig,
data_fots, Otomo and intro-skip packs contain no competing animation registry.
Future animation mods can conflict and require registry merging.

Existing rifle, grenades, artillery, ability tables and recruitment payloads remain
byte-for-byte unchanged. No grenade ability is added to the experimental unit,
so rifle timing can be observed in isolation. Campaign recruitment is deliberately
not added during this combat investigation. Its required building/permission
relationships were researched through existing and Radious rows, not declared tested.

## 7. Build, validation, install and rollback

Build output: build/steel_sakura_type20_event_test.pack.
Installed AS THE SINGLE COMBINED PACK:
D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack

Installed/build SHA256:
8574F88C37FE2E6D8058785FC24CC25741C5573E2A6929C4B57C202E77B4420F

Preserved pre-investigation fallback SHA256:
0A5CC547E5515CB813FB5341335E2A4D24E3596C7C9D7D3F32F39362FBB122F8

Offline checks:
- RPFM creates/reopens eight new DB files at installed schema versions.
- Every new row and localization round-trips.
- Unique composite DB keys and unit index checked against available base/installed/Otomo catalogs.
- Unit -> theme -> item and unit -> projectile relationships checked.
- Oda/category/uniform/roster flags checked against working fallback.
- Every generated animation parses with matching rig, unchanged frame bytes and ordered markers.
- All 20 pre-existing pack payloads unchanged; 18 new payloads; 38 total.
- PFH3 Mod format; no editor metadata, duplicate packed paths or new vanilla-key overrides.
- New assets match packed bytes; full installed hash matches built hash.
- One Steel Sakura pack active, directly in data; no Steel Sakura pack in MyMods.
- mod_list.txt and active user.script.txt backed up and unchanged.
- Original archives and unrelated mods untouched; saved games never accessed.
- Seven unit tests passed: four synthetic animation-parser checks and three existing offline-validator regressions.
- This is offline integrity, not proof of gameplay.

Latest install backup: backups/type20-events-20261021-211645-104045.
The initial backup also preserves the exact pre-investigation installed pack and
both loading lists: backups/type20-events-20261021-205044-678795.
Rebuilds can vary binary GUIDs/hash; the current validation/installation reports
record the exact resulting bytes.

From project root, game closed:

~~~powershell
powershell -NoProfile -File scripts/build_type20_event_test.ps1 -Install
~~~

Rollback, retaining the working original roster/grenades/artillery:

~~~powershell
python scripts/select_type20_event_test.py fallback
~~~

Do not enable the separately named output pack alongside the combined installed
pack: the output contains the existing units too. Use the new selector; older
grenade/rifle selectors deliberately reject unfamiliar installed hashes.

Local evidence:
- build/type20-research/animation-events.json
- build/type20-research/model-format-roundtrip.json
- build/type20-research/original-model/report.json
- build/type20-research/animation-registry-conflicts.json
- build/type20-research/event-test-manifest.json
- build/type20-research/event-test-rpfm.json
- build/type20-research/event-test-validation.json
- build/type20-research/installation-report.json
- build/type20-research/external-mods/expanded-japan-paths.json
- build/type20-research/external-mods/radious/paths.json and decoded-research-rows.json

Game-derived data, downloaded packs and GPL reference copies stay in ignored build/.
The original model source, scripts and this report are project files. No other
mod's assets were added to our build or repository.

## 8. In-game test at 1-10 FPS

1. Fully exit/relaunch. Use original Sengoku Custom Battle, Oda, gun/matchlock infantry.
   Add the new exact-name Type 20 test and the unchanged working DIAG/EXP riflemen.
   If the new unit is absent, report that first: it is a roster/load test failure,
   not evidence that two-event firing is impossible.
2. Use a small battle on flat open ground. Form shallow lines, facing a stationary
   enemy at roughly 100-150 range; prevent overlap. Turn fire-at-will off initially.
3. Fire with ONLY the fallback for 10 simulation seconds, then cease fire. Repeat
   with ONLY the Type 20 test at a comparable fresh target. Pause frequently and
   observe one front-rank soldier, keeping the other squad silent.
4. Look for TWO temporally separate projectile launches/impacts from ONE soldier
   during ONE firing cycle, about 0.30 simulation seconds apart. Existing rifle
   motion, uniform, smoke style, reload value and range are intentionally similar.
   A different name, more kills or a denser squad volley is not sufficient proof.
5. Record: exact unit name, fires/does not fire, one or two identifiable shots,
   ammo behavior, stop-fire response, animation/origin errors. A short recording
   helps, but at 1 FPS the interval may be below visual resolution: report
   INCONCLUSIVE rather than judging success from flashes or kill count.
   If available, use the game's slower simulation speed or replay for observation.
6. Do not activate grenades or field artillery during this test. They are unchanged.

## 9. Decision tree and remaining work

- If two damaging timed shots are confirmed: preserve this pack and recording,
  establish ammo accounting, then author matching second recoil and test reliable
  repeated bursts. Do not assume a third numbered marker or an infinite loop.
- If the unit moves/fires but no second shot is observed: preserve the result.
  First prove the private animation/event path is consumed with a positive timing
  control. Then isolate pistol-controller requirements; no further reload tweaks.
- If effects repeat but damage/ammo do not: classify it as an effects-only outcome,
  not automatic fire.
- If the new unit freezes/crashes or is absent: rollback; investigate table loading,
  fragment selection and asset resolution before any firing-system conclusion.
- If the human controller ultimately accepts only one shot: retain honest rapid
  single fire unless a compatible new controller or rigorously verified engine
  extension is found. A modern weapon model alone will not fix it.
- Complete actual DarthMod inspection when a local author-distributed package is
  available. Morning Sun, Tosa Isekai and UEFC package inspections remain gaps.

No automatic-fire milestone is complete. The next decision requires actual gameplay
evidence from the new separate unit, with the unchanged rifle present as control.
