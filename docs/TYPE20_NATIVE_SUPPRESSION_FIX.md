## 2026-10-22: Suppression Fire confirmed; five-shot controller limit investigated

User confirms the native ability activates, but bursts remain two shots and
continuous fire does not work. The requested five-shot burst is not implemented.
Read-only executable analysis found two scalar fire-time slots and two recovered
dispatch loops with a hard-coded count of two and two fired flags. See
[FIVE_SHOT_FEASIBILITY](TYPE20_FIVE_SHOT_FEASIBILITY.md) for instruction addresses,
reproducible audit, limits and the next technical gate. This is not a proof that
every engine controller has the same limit. R2 remains installed unchanged;
no fake five-shot build or further reload adjustment was made.

## 2026-10-21: native Suppression Fire R2 installed with user approval

The user approved the temporary shared native-ability override. Installed hash:
`1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD`.
Oda ranged infantry: **TYPE20 SUPPRESSION FIX R2**; expected native button:
**Suppression Fire**, configured for 30 seconds active / 120 seconds recharge.
Backups and installed/build hash checks completed; loading files unchanged.
Button visibility, activation and firing behavior await gameplay confirmation.
Animations and firing statistics were not changed in R2. Other native Suppression
Fire users receive the approved shared projectile/unlock behavior while enabled.
Rollback: `python scripts/type20_native_suppression.py rollback`.
Exact installation/backup record: `build/type20-native-suppression/installation.json`.
Earlier prepared/not-installed statements below are historical.

# Native Suppression Fire fix R2

## Why the preceding build failed

User report: the unit still behaved like the prior burst unit, possibly with a
faster interval, and **no Suppressive Fire ability** appeared.

The installed SHA256 was checked and still matched the intended preceding build:
`11B6BF8D14B868C31327495AD8E29CA35513DFFD3EA805DCF288D7E81B90BBD1`.
This rules out an installed-file hash mismatch at this inspection, not every
possible runtime loading issue.

That build assigned `dummy_suppression_fire`. The DLL does register that string
with a numeric identity, but the identity produced no visible player button in
the user's test. Its registration did not establish that it can be used as an
active player ability. The exact internal rejection/filter path has not been
recovered. The earlier conclusion was too optimistic.

It had shortened two-shot animation timing and added private projectile/ability
rows. It did **not** establish a continuous-fire controller, a longer burst, or a
working ability button. The result is retained rather than counted as success.

## R2 changes, exactly

Same unit key: `steel_sakura_type20_suppressive_test`.
New recognizable name: **TYPE20 SUPPRESSION FIX R2**.
Oda ranged infantry, Sengoku Custom Battle.

Only three existing payloads change:

1. Unit-to-ability assignment: `dummy_suppression_fire` → **`suppression_fire`**,
   the actual player ability assigned to vanilla Tosa riflemen and other FoTS units.
2. Unit name changes to the R2 identifier.
3. Unit localization describes the native-key test and its shared scope.

Two new DB payloads override exactly one field each in the shared native rows:

| Table/key | Field | Vanilla | R2 |
| --- | --- | --- | --- |
| unit_abilities / suppression_fire | requires_effect_enabling | true | false |
| unit_special_abilities / suppression_fire | activated_projectile | boshin_rifle_suppressive | steel_sakura_type20_suppressive_test_suppression_bullet |

The first removes the effect/technology gate for the native button. The second
uses the already-built private zero-reload suppressive projectile. It retains the
native **30-second active time and 120-second recharge**, native label/tooltip,
and existing native effects. No new UI identity or dummy icon is relied upon.
The expected English button label is **Suppression Fire**.

**No firing clips, event timing, reload values, damage, range, projectile counts,
unit stats, artillery or grenade payloads change in R2.** There are still two
established shots per animation cycle. R2 is a functional native-ability diagnostic,
not a claim that continuous automatic fire has been implemented.

## Shared scope and explicit installation approval

Native ability definitions are shared by key. This cannot be presented as a
per-unit-only override. The inspected vanilla assignment table contains 21 units
with `suppression_fire`; the full list is in the manifest and validation report.
Otomo's inspected ability definitions do not themselves override this native key,
but any unit assigned it would receive the shared behavior while R2 is loaded.

Other native users can gain the unlocked action and switch to the private
projectile during activation. That projectile retains diagnostic range 900,
damage 3, zero base reload, one bullet/event, suppression_shot type and calibration
area 2. This can significantly alter their combat balance. Native suppression
values stay intact; their exact runtime effects on our unit are still unconfirmed.

The build is prepared before asking for user approval of this shared test.
Installation requires `build/type20-native-suppression/shared-override-consent.json`
with the approved exact pack hash. This file must only be created after actual
human approval; a timeout or lack of reply is not approval. Earlier permission to
relink the grenade ability is not being treated as approval of this new shared
Suppression Fire change.

## Evidence, validation and preservation

Files:
- `build/type20-native-suppression/manifest.json`: source rows, exact changes and users.
- `build/type20-native-suppression/rpfm-roundtrip.json`: RPFM-decoded output rows.
- `build/type20-native-suppression/validation.json`: payload/hash/field comparisons.
- `build/type20-native-suppression/failed-dummy-ability.pack`: unchanged failed build.
- `src/type20-runtime-observations.json`: actual user observations including failure.

Offline validation confirms only the listed three existing payloads changed,
two were added, and **100 of the prior 103 payloads are byte-identical**. RPFM
round-trips all four touched DB tables and localization. Each shared row differs
from vanilla in only its named field. Assignment and projectile references resolve.
No game archives, saves or unrelated mods are overwritten. Build validity does
not prove the button will appear or that activation works.

Prepared build: `build/steel_sakura_type20_native_suppression.pack`.
SHA256: `1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD`.
Intended installed target:
`D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack`.
Check `build/type20-native-suppression/installation.json` for actual installation;
absence means this build has not been installed.

```powershell
# Build and offline validation only:
powershell -File scripts/build_type20_native_suppression.ps1
# Install only after shared-scope approval is recorded and the game is closed:
python scripts/type20_native_suppression.py install
# Restore the preserved user-confirmed no-reload-animation burst build:
python scripts/type20_native_suppression.py rollback
```

The existing installer backs up the current pack and mod loading configuration,
refuses extra Steel & Sakura packs or a running game, preserves loading files,
and checks installed/build hash equality. Its historical backup prefix remains
`type20-path-control-`; the exact backup is recorded on installation.

## Short in-game test

1. Restart and select Oda ranged infantry **TYPE20 SUPPRESSION FIX R2**. An older
   name means this revision is not the one being observed.
2. Select the unit during battle. Check for native **Suppression Fire**, not a
   button labelled Full Auto. Report whether it is absent, disabled or clickable.
3. Fire at a stationary target; activate the button. Watch for its active state,
   firing behavior, ammunition use and any suppression response on the target.
   Faster pairs of shots alone do not establish a continuous stream.
4. Use the battle clock at low FPS. After the configured 30-second active period,
   check that ordinary behavior returns and the action enters recharge.
5. Turn fire at will off and move the unit. It must stop after the current cycle
   and move normally. Avoid other abilities so their effects do not confuse this test.

If the native button is still missing, inspect Sengoku/FoTS UI gating, the actual
runtime loaded ability rows and availability conditions. Do not add more dummy
keys or rename a reload bonus Full Auto. If activation works, establish projectile
switching and rate/stop/ammo behavior before any further continuous-fire experiment.
