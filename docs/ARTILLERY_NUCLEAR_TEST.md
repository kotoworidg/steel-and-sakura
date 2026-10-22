# FH70-inspired Nuclear Shell test — 2026-10-22

## Installed, gameplay unconfirmed

Installed directly into:
`D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack`.
SHA256 `2D57C29074E15A3903E6C7900D652770CB27D7023A8A349BDF0C1C5BDDB67AB3`.
Generated build: `build/steel_sakura_artillery_nuclear_test.pack`.

Custom Battle: original Sengoku, **Oda**, artillery/siege roster.
Unit name: **FH70 BATTERY - NUCLEAR TEST**.
Button label: **Nuclear Shell (TEST)**, using native `shrapnel_shot`.
The unit has 40 crew and four Armstrong placeholder cannons. It is FH70-inspired;
no modern howitzer model, new towing/deployment system or nuclear simulation is
claimed. Roster visibility, ability activation, projectile switching and blast
behavior all still require user testing.

## What was actually added

- A private projectile `steel_sakura_nuclear_projectile_v1` cloned from actual
  `boshin_armstrong_gun_shell`, linked to a private explosion. Range 900 matches
  the existing custom conventional shell; reload 60, calibration area 10, one
  projectile per firing event. All other fields retain the observed source row.
- A private explosion `steel_sakura_nuclear_explosion_v1`: percussive shockwave,
  radius **40**, damage **100** in database units. Its four shell fragments retain
  the vanilla Armstrong count, avoiding a large fragment multiplication.
- Existing `Cannon_common_air_explosion_lrg` for air/ground visuals, verified in
  the actual `boshin_bombardment_large` explosion row. No visual scaling is assumed.
  **No mushroom cloud, fallout or radiation system is implemented.**
- Native Shrapnel Shot temporarily relinked to the private projectile, configured
  for **one 15-second activation per battle**. The shell's 60-second reload is
  intended to discourage repeat volleys within the window. Exactly one shell or
  exactly one volley is not guaranteed by these values; four guns can fire.
- Updated native ability text/localization to **Nuclear Shell (TEST)**.
- Explicit artillery unit cards at all five observed UI paths, copied locally
  from the native Armstrong cards. The unit's icon/info references now point to
  these real assets instead of unspecified placeholders. This is a verifiable
  asset improvement, not proof of the cause of the earlier roster problem.
- A recognizable unit name and descriptions. Existing Oda permission, Japan
  grouping, four-gun stats, Armstrong gun type and conventional ammo stay intact.

## What remains unchanged

All rifle, firing-animation, grenade and `suppression_fire` DB payloads remain
byte-identical to the preserved working build. The shared units/localization files
change only artillery fields/strings and the named nuclear ability localization.
No infantry rows or their strings are edited. No vanilla archives, unrelated mod
files or saves are modified.

The pack contains 114 game payloads. Of the original 105, only the combined units
and localization payloads changed; all **103 others are byte-identical**. Four new
DB payloads and five locally copied artillery cards were added.

## Shared ability scope — explicitly approved

The user approved: **“Install the nuclear-shell test”** after being told this uses
the shared native Shrapnel Shot definition. While this test is loaded, all units
assigned `shrapnel_shot` receive the test label, private projectile and one-use
activation settings. The inspected vanilla assignments are:

- Boshin_Art_Armstrong_Guns_MP
- Boshin_Art_Armstrong_Guns
- Boshin_Art_Parrot_Guns_MP
- Boshin_Art_Parrot_Guns

Any Otomo units assigned the same key are also affected. This is a temporary
shared test, not a per-unit ability override. The separate previously approved
native Suppression Fire override remains unchanged.

## Source evidence and offline validation

Actual installed baseline R2 hash:
`1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD`.
Preserved at `build/artillery-nuclear-test/working-rifle-baseline.pack`.

The blast values stay below/equal to inspected native maxima: ship_magazine has
radius 70 and damage 100; a naval torpedo has radius 25 and damage 100. These rows
support the data values, not runtime land compatibility or performance claims.
Native Armstrong has radius 4 and damage 16. Its percussive detonator and existing
four-fragment structure are retained in the private explosion.

Native Armstrong's gun/projectile junction contains its normal shell only;
its special ammo is supplied by the ability. The test keeps that same relationship
rather than inventing an additional normal-ammo junction for the nuclear round.
The numeric unit index 1465 has no collision in inspected vanilla/Otomo units.

RPFM round-trips all five touched/new DB tables and localization. Validation checks
private keys, projectile-to-explosion and ability-to-projectile references, actual
native particle evidence, four-gun stats, Oda permission, card files, unchanged
infantry rows/strings and byte-level preservation of the baseline payloads.
The installed hash equals the generated build hash. This is not gameplay proof.

Evidence files under ignored `build/artillery-nuclear-test/`:
`manifest.json`, `rpfm-roundtrip.json`, `validation.json`,
`shared-override-consent.json`, and `installation.json`.

## Build and reversible installation

Prerequisites: project Python, existing local source exports/native card extracts,
and installed RPFM MCP server at localhost:45127.

```powershell
# Prepare, build and offline validate:
powershell -File scripts/build_artillery_nuclear.ps1
# Build/install only with recorded shared-scope consent and game closed:
powershell -File scripts/build_artillery_nuclear.ps1 -Install
# Revalidate the current generated pack:
python scripts/artillery_nuclear.py validate
# Restore the exact working rifle/Suppression Fire R2 pack:
python scripts/artillery_nuclear.py rollback
```

The native cards were extracted with RPFM from owned data.pack into the ignored
build folder. No proprietary cards are committed or redistributed as source.

Installation backed up the current pack, root mod_list.txt and user.script.txt.
It preserves their bytes, refuses a running game/unknown pack hash/extra Steel &
Sakura packs, and checks installed hash equality. The reused installer logs mode
`control` and retains its historical `type20-path-control-` backup prefix.
Exact backup: `backups/type20-path-control-20261022-005937-017190`.

## Short test at 1–10 FPS

1. Restart Shogun 2. Sengoku Custom Battle → Oda → artillery/siege roster.
   Find **FH70 BATTERY - NUCLEAR TEST**. Report the exact name or absence.
2. Bring one battery and a dense enemy infantry formation. Let the guns load;
   put a target within range and keep friendly troops clear of the impact area.
3. Fire one conventional volley first if desired for comparison. Once the guns
   are ready, activate **Nuclear Shell (TEST)** and order fire immediately.
4. Check button activation, actual shell launches, impact explosion and casualties.
   A four-gun volley is possible. Judge the area/damage separately from the stock
   explosion visual; a mushroom cloud is not expected.
5. After the ability window, confirm ordinary shells return and the action is
   spent. At low FPS use the battle clock, not 15 wall-clock seconds. Verify rifles
   still behave as before. Do not count any of these as passed without observation.

If the unit is absent, diagnose its actual roster filter/asset/availability path
before changing blast values. If the button activates but no enlarged blast occurs,
trace projectile switching and percussive detonation rather than raising damage
blindly. If performance is poor, preserve the result and reduce the bounded test's
fragment/visual load based on evidence.
