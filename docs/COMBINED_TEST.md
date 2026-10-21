# Combined Oda test - pending user confirmation

## Previous loading and missing units

The active user.script.txt names packs directly in game data. Before this fix:
- data/steel_sakura_infantry_prototype.pack was 204827 bytes and contained the
  grenade database rows but no custom grenade textures.
- data/MyMods/steel_sakura_infantry_prototype.pack was 204403 bytes; later
  metadata cleanup had updated this different copy.
- Both mod_list.txt and user.script.txt named the infantry pack, with no artillery
  entry. No artillery pack was installed in either directory.
- Root data copies of Otomo and the intro-skip pack matched active script names.
  Their duplicate MyMods copies are preserved as unrelated mods.

This diagnosis uses the inspected configuration, pack contents, and the user's
confirmed convention. No process trace captured individual loader reads.

## Grenade and nuclear ability dependencies

The installed infantry pack correctly assigned steel_sakura_throw_grenades to
SteelSakura_Automatic_Rifle_Squad. The corresponding unit-ability and special-
ability rows pointed to the existing grenade projectile, and required no ninja
technology effect. Vanilla blinding_grenade instead uses an enabling technology
junction. The previous custom build omitted every ability button texture.

The combined test retains the custom keys and adds the missing seven button
states and one icon per ability using observed vanilla paths with custom key
names. Matching unit_info_card_abilities_strings and localisation are included.
Icons are local copies of existing game assets, not new artwork. All vanilla
ability rows/textures remain intact, protecting Otomo and other units.

Missing textures are a verified omission, not a proven sole explanation for the
missing button. Generic UI ability slots were observed, but arbitrary ability-key
recognition remains UNVERIFIED. This build tests the full chain without global
ability overrides. If buttons remain absent, custom-key/engine binding needs a
controlled vanilla-key diagnostic. Do not treat activation as tested if no
button is present.

Nuclear Shell remains linked through its custom ability to its separate nuclear
projectile and explosion. Throw Grenades retains two 20-second activations and
90-second recharge; Nuclear Shell retains one 30-second firing window. Neither
window promises a single projectile. These are experimental gameplay settings.

## Oda selection relationships

Both units have explicit oda/allowed=true exclusive-faction permissions cloned
from working Oda Matchlock Ashigaru, japan military permissions, uniforms, all
three multiplayer-era flags, and empty religion/resource/building gates.
Artillery now uses Sengoku European Cannons' mp_siege_and_stealth frontend
category, special caste and siege icon. The Armstrong artillery_foot class,
rig, four guns, forty crew and firing flags are retained. This addresses a
potential frontend filtering mismatch but selection still needs runtime testing.
AI army presets are not the hand-selected roster and were not used as a substitute.

## Test procedure

Use original Sengoku Custom Battle, Oda, a disposable land battle:

| Category | Unit name | Expected button after selecting unit |
| --- | --- | --- |
| Matchlock / gun infantry (mp_gun) | Modern Infantry Squad (Type 20) | Throw Grenades |
| Siege / artillery (mp_siege_and_stealth) | Modern Artillery Battery (FH70) | Nuclear Shell |

Tosa and Armstrong assets remain temporary placeholders. The repeating-rifle
baseline is not modern automatic fire. Confirm forty men and four guns using
appropriate unit-size settings, then confirm both buttons in the battle phase.
Test grenades at range 5-35, nuclear rounds below range 550 with loaded guns.
Record absent, disabled, and activating buttons separately. Then observe visible
hand throws, explosions, friendly fire, reload, expiry and return to ordinary fire.
The Otomo mod may extend ordinary Armstrong range to 600; nuclear range is 550.

Build: pwsh -NoProfile -File scripts/build_combined.ps1
Install: python scripts/install_combined.py
Destination: D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack
See INSTALL.md in the project root for verified backup and rollback behavior.

Milestone remains PENDING_USER_CONFIRMATION until the user confirms both units
and both buttons appear. Offline pack validity cannot establish engine behavior.
