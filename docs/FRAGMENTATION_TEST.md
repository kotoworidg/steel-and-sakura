# Infantry fragmentation test V1 - 2026-10-21

## Separate results and scope

User confirms the grenade button activates and rifle reload is faster, but
individual fire remains repeating-rifle behavior. The installed pre-test pack
was the none-mechanism experiment (SHA E3B8F1DA...). This pass preserves that
rifle exactly. No new automatic-fire claim is made and no further reload
reduction, simultaneous-projectile trick, animation swap or Gatling rig is used.

See AUTOMATIC_FIRE_FINDINGS.md for actual rifle/Gatling fragment comparison:
Gatling has an ENGINE_FIRE_LOOP on its own skeleton; human rifle mappings have
FIRE plus reload entry/cycle/exit. Only matchlock and none firing mechanisms
were observed in installed units. The sole multi-projectile example is a
six-projectile donderbuss, with no exposed temporal burst spacing. No verified
human continuous/burst scheduler was found. Existing data/asset work therefore
has not established true automatic infantry fire. Rapid single-shot fire is
the confirmed fallback, not an accurate Howa Type 20 implementation.

## Why the old grenade barely killed

The working vanilla button activates blinding_grenade, whose activated_projectile
was blinding_grenade. That projectile has damage=0 and points to grenade_blinding:
blinding_shockwave, radius 15, damage about 0.0005, one low-damage particle, and
flash-grenade visuals. It is not a fragmentation configuration.

## New grenade assets

- steel_sakura_frag_projectile_v1 clones the WORKING blinding projectile motion,
  model, shot type, 75 range and 5 minimum range. Only its key, explosion reference
  and reload value (0 -> 20, from the vanilla grenade example) change.
- steel_sakura_frag_explosion_v1 uses the existing percussive impact detonator,
  shockwave type, radius 4, damage 8, three custom fragments and existing
  explode_grenade visuals. These are game test parameters, not real-world units
  or proven balanced damage values.
- steel_sakura_frag_fragment_v1 clones grenade_fragment with damage 0.5 instead
  of 0.1. No existing projectile or explosion row is replaced.

The existing unit assignment, button key, localisation, UI assets, technology
unlock and ability timings/uses remain unchanged. The button is still called
Blinding Grenades and may retain its old description. This intentionally avoids
confusing a display-text change with activation success. Because the ability ID
and projectile shot type remain the working blinding ones, additional hardcoded
blinding effects might persist; gameplay must establish the resulting behavior.

## Authorized temporary shared effect

The user explicitly approved temporarily redirecting the shared blinding_grenade
special ability to the unique fragmentation projectile. The only overwritten
vanilla row is that ability link; other users of the same ability (including
ninjas) also receive the fragmentation projectile while this test is enabled.
This is not a unit-specific permanent solution. Original vanilla grenade and
explosion definitions, vanilla archives and unrelated mods are unchanged.
The effect disappears on rollback to the preserved pack.

## Offline verification

RPFM created/reopened the three added tables and compared every cell with its
prepared row. Differential validation proves all 17 original packed files are
byte-for-byte unchanged. It checks source schemas/types, exact clone deltas,
projectile -> explosion -> fragment chain and the one approved ability relink.
Rifle stats/projectiles/animations, recruitment, all artillery payloads and
ability ownership/UI are identical to the working input. Runtime remains pending.

Build output: build/steel_sakura_frag_test.pack.
Fallback: build/fragmentation-test/working-infantry-grenade-fallback.pack.
Reports: build/fragmentation-test/validation-report.json and rpfm-report.json.
Installed filename remains data/steel_sakura_combined_test.pack; only one version
is enabled. Do not enable the separate build-output filename alongside it.

## Install, rebuild and rollback

Close the game before switching. From the project root:

```powershell
python scripts/select_frag_test.py test
```

This backs up the installed pack and both loading lists, verifies allowed hashes,
replaces only the combined pack, and leaves loading entries unchanged.

Rollback restores the exact working grenade/rifle baseline:

```powershell
python scripts/select_frag_test.py fallback
```

To rebuild, first restore fallback, then run
`pwsh -NoProfile -File scripts/build_frag_test.ps1`, then select test again.
The previous rifle-experiment selector rejects this new hash by design; use the
fragmentation selector to restore its input before using older selectors.

## Short low-FPS test

1. Fully restart. Original Sengoku Custom Battle, Oda. Use the existing modern
   rifle squad and a stationary dense infantry target. Keep other grenadiers
   out of this diagnostic because the approved link is shared.
2. At about 100-150 range, observe one soldier over 10-20 IN-GAME seconds.
   Count separate shot/reload cycles. Rifle behavior should match the confirmed
   fallback; no new automatic burst is implemented. Multiple simultaneous
   projectiles or more squad volleys do not establish automatic fire per soldier.
3. Turn off Fire at Will, move within roughly 25 range (minimum 5), and activate
   the same Blinding Grenades button. Ensure grenades actually launch before
   interpreting casualties. The reload=20 value can delay first/follow-up throws;
   allow 20-30 in-game seconds if needed, or the remaining activation window.
4. Pause before/after impacts and record enemy soldier count. Look for grenade
   explosions and meaningful casualties rather than only a flash/debuff. Keep
   friendly troops away from the target; friendly-fire behavior is untested.
5. Let the ability expire; restore Fire at Will and confirm rifle firing resumes.
   Report if the unit gets stuck throwing, ceases firing, or loses the button.

Use simulation time, not wall time, at 1-10 FPS. Compare grenade casualties with
the preserved fallback in a separate run if possible. A failure to launch, a
flash with no kills, and a kill-producing explosion are different outcomes.

Do not mark grenade lethality or combined operation complete until confirmed
in-game. Artillery, recruitment, models, tanks and aircraft are outside this pass.
