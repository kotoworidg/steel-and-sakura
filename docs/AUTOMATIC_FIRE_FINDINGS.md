# Current Type 20 research status

2026-10-21: the research pass found real numbered human firing events.
See [technical report](TYPE20_RESEARCH.md) and
[test checklist](../tests/type20-event-test.md).

Installed: data/steel_sakura_combined_test.pack, with the new separate
Steel & Sakura Type 20 Automatic Fire Test alongside the unchanged riflemen.
This is an unconfirmed two-event experiment, not working automatic fire.
All original rifle, grenade, artillery and recruitment pack payloads are preserved.

> Latest result: user confirms faster reload and working vanilla grenade activation,
> but still reports repeating-rifle behavior. No automatic fire is implemented.
> Fragmentation test preserves all rifle payloads; see FRAGMENTATION_TEST.md.

# Infantry automatic-fire investigation - 2026-10-21

## Confirmed baseline

The user confirms the diagnostic rifle reloads faster than vanilla in-game.
This establishes that modified combat values are being used. It does not
establish individual automatic fire. The faster-repeat unit is preserved in
build/automatic-research/working-fast-rifle-fallback.pack and the project backup.
Its SHA256 is D4564DA9973DBCF0ABEB20EC3126882C157155812FAD5EE9BE29EC8009817367.
It remains installed; the optional experiment below is NOT automatically enabled.

## Installed engine/asset evidence

Decoded data.pack land stats show only two observed firing_mechanism values:
matchlock and none. The schema references unit_stats_firing_mechanism_enum, but
no packed enum table was found. This does not prove that undocumented values
cannot exist; inventing an automatic/burst enum would be unsupported.

| Dependency | Tosa rifle | Gatling |
| --- | --- | --- |
| firing_mechanism | matchlock | none |
| main man animation table | boshin_man_rifle_trained | shogun_man_katana crew |
| gun type | empty | boshin_gatling_gun |
| skeleton_missile | foot_musket | cannon_crew |
| gun engine type | absent | Boshin_Gatling_Gun |
| projectile reload value | 6 | 18 |
| projectile_number | 1 | 1 |

The real animations/animation_tables/animation_tables.txt defines the rifle
with skeleton_type man_shogun. Its fragment chain inherits FIRE and KNEEL_FIRE
from shogun_man_musket_combat_fragment, then overrides reload transitions and
cycles with boshin_man_rifle_combat_fragment. FIRE refers to mus_fire.anim;
reload has separate entry/cycle/exit files. Rifle reload=1 changes the requested
cadence but does not create an automatic-fire animation or multiple shot events.

The same animation table file defines boshin_engine_gatling_gun on a different
skeleton_type gatling_gun. boshin_gatling_gun_fragment explicitly maps ENGINE_FIRE
and ENGINE_FIRE_LOOP to gatling_fire.anim. The engine, crew, projectile launch
particle and rig form a different system. Putting that engine clip onto a human
would not establish compatible bones or shot origin. No Gatling-to-human
substitution has been made.

The only installed projectile row with projectile_number greater than one is
shogun_donderbuss (six bullet projectiles). There is no temporal spacing field
in that projectile schema. This provides a multiple-projectile example, not a
verified sequential burst mechanism. Rifle/Gatling both use one projectile.
Increasing the count must not be called automatic fire.

Eight actual rifle/musket/pistol/Gatling/Armstrong configuration fragments and
the animation-table files were extracted locally under build/automatic-research.
Pistol and dual-pistol fragments also map FIRE plus distinct reload states;
they do not expose an infantry FIRE_LOOP state in the inspected fragments.
No bytecode instrumentation or parsed binary shot-event timeline was obtained.
Clip frame/event synchronization, engine dispatch and animation cycle floors
remain unverified; database and fragment inspection alone cannot establish them.

## Feasibility conclusion

No verified route to true human-infantry automatic fire was found in the
existing inspected settings/assets. Gatling proves a gun-engine loop exists,
not that the infantry controller can use it. A true implementation would need
a working infantry repeated-shot scheduler and compatible human firing events,
plus believable animation timing. Neither is exposed by the inspected infantry
configuration. This is a concrete current limitation, not a proof that all
custom animation work or reverse engineering is impossible.

The closest currently working approximation is rapid repeated single fire.
Independent/staggered rifle fire could make a squad's aggregate output more
continuous, but cannot truthfully be called a Type 20 firing bursts per soldier.
The next minimal experiment tests only that scheduling question.

## Optional one-variable experiment

build/steel_sakura_free_fire_experiment.pack differs from the preserved fallback
in exactly two packed files: the custom infantry firing_mechanism changes from
matchlock to none; its displayed name becomes EXP NONE - same fast rifle stats.
Reload remains 1, projectile_number remains 1, all_ranks_fire and every animation
reference remain unchanged. All other packed payloads, including artillery,
abilities, gun/projectile data and controls, are byte-for-byte identical.

none is observed on other installed missile units and Gatling, but its use with
the rifle animation/skeleton is a hypothesis. It may change firing scheduling,
do nothing, disable shooting, or produce bad transitions. This is NOT a build
claimed to implement automatic fire. It deliberately avoids a bundle of changes
that would hide which parameter caused a result.

RPFM reopened the modified DB and localisation. Differential validation verifies
the one-field change and every untouched payload. That is offline integrity,
not engine acceptance. Reports: build/automatic-research/free-fire-report.json
and experiment-rpfm-evidence.json. Rebuild locally using
scripts/build_free_fire_experiment.ps1 with the preserved fallback installed.

To test, close the game, then run from the project directory:

```powershell
python scripts/select_rifle_experiment.py experiment
```

This replaces the existing data/steel_sakura_combined_test.pack after backing
it up. It does not add a second active pack or change loading lists. Do not
manually enable the separate experiment pack alongside the combined pack.
To restore the confirmed faster-repeat fallback:

```powershell
python scripts/select_rifle_experiment.py fallback
```

## Exact next battle observation

Use original Sengoku Custom Battle, Oda, EXP NONE infantry against a stationary
target about 100-150 range away. Use a shallow line so rear ranks do not confuse
the scheduling observation. At 1-10 FPS use the in-game timer, not wall time.
Observe 10-20 simulation seconds and pause frequently. Record:

1. Does the unit fire at all? Are posture/movement and projectile origins normal?
2. Do soldiers fire independently/staggered or remain in synchronized volleys?
3. Does ONE visible soldier fire several sequential shots before the usual
   rifle reload action, or still fire one shot and perform a repeating-rifle cycle?
4. Does ammo decrease normally, and does cease fire actually stop firing?

Compare against the preserved fallback in a separate run. Artillery and ability
buttons should behave exactly as before; they are not test variables here.
If none causes no change or breaks firing, revert. That result rejects this
configuration route and supports retaining honest rapid single-fire gameplay
until compatible animation/controller support is established.

Confirmed automatic fire is still unimplemented. No feature-complete claim is
made for this experiment.
