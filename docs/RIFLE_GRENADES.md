Current equipment direction: see [Type 20 / FH70 specification](EQUIPMENT_DIRECTION.md).
Historical assets remain temporary; equipment accuracy has not been established.

# Rifle squad grenade prototype

The rifle squad now has an experimental **Throw Grenades** skill. The build
adds three namespaced ability/link rows to the infantry pack, using the installed
`blinding_grenade` ability structure and the existing explosive `grenade`
projectile. Vanilla ninja abilities are not overwritten.

Authored settings: two activations, 20-second active window, 90-second recharge.
The referenced grenade has effective range 35 and minimum range 5 in the
installed table. These are duration-based activations, not two individual
hand grenades. The projectile retains the installed grenade's explosion,
bounce and incendiary behavior; this is not a new modern fragmentation model.

The squad keeps its repeating-rifle equipment and animation set. Whether that
set can perform a visible grenade throw and return to rifle fire is UNVERIFIED.
The custom button and ability-key acceptance are also UNVERIFIED. No battle
has been run; successful pack decoding does not establish throwing behavior.

Rebuild with `pwsh -NoProfile -File scripts/build.ps1`. This produces seven DB
rows, seven English strings and five original cards. RPFM reopens every row
and string. The current build passed 119 offline checks and three existing
regression tests. The generated pack is in `build/`; the installed infantry
pack has not been updated with this grenade experiment.

For the first battle test: select the squad, confirm the ability button,
place a target between range 5 and 35, activate while stationary, and observe
hand motion, projectile origin, explosion, friendly fire and return to rifle
fire. Confirm recharge and two-activation limit. A bullet fired from a rifle
with an explosive impact does not satisfy the requested visible grenade throw.
If throwing fails, inspect rifle animation/equipment support before changing
unrelated combat stats.
