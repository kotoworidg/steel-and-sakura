# Type 20 Rifle and Grenade Section 0.3.0 — 27 October 2026

Supported-mechanics fallback, built from the preserved two-shot baseline.
Select Oda's **JSDF Type 20 - Rifle and Grenade Section** in a Sengoku custom battle.
This release needs no runtime helper, debugger, injection or binary patch.

## What changes from the installed five-round candidate

| Gameplay setting | Installed candidate, helper off | This release |
| --- | --- | --- |
| Type 20 grenade assignment | Missing; another rifle squad had it | Actual Type 20 receives Blinding Grenades |
| Armour | 2 | 8 |
| Selectable loose formation | 2 x 3 spacing | 3 x 4.5 spacing |
| Firing clips | Experimental paired 0.5-second marker | Byte-identical confirmed two-shot clips |

The new grenade assignment reuses the pack's existing fragmentation chain and the
inherited native unarmed throw animation. No shared grenade definition changes
are added. The existing button still says **Blinding Grenades**: native ability
60 seconds / 180-second recharge; projectile range 5–75; percussive explosion
radius 4 / damage 8 / three fragments with damage 0.5 each. These are data settings.
Throw execution, casualties and return to rifle firing have NOT been verified on
this Type 20. Native blinding behavior may persist. Its inherited shared relink
also affects other units already assigned Blinding Grenades, as before.

Armour 8 uses the native armour scale (also used by Portuguese Terços); health
remains 1 and bullet immunity remains off. It is a generic protection setting,
not a calibrated model of modern body armour. Loose formation is player-selected;
ordinary close spacing stays 1.4 x 2.4. Soldiers still follow native player orders.

Rifle settings remain damage 3 / AP / one projectile per native event, velocity
850, range 450, accuracy 80, finite 210 native ammo and native reload timer 1.
These remain two-shot cycles, not five-round bursts. All-rank fire, guard capability
and no skirmish retreat are retained. Stop/Move/cease-fire/targeting and actual
damage need in-game confirmation. No extra ammo writes or scripted damage exist.

Rapid Volley remains native 60 seconds / 300-second recharge, with 60-second
initial recharge. The optional Suppression Fire pack is unchanged: 30 / 120,
a native projectile switch and loading/accuracy modifiers. It alters the shared
native suppression ability for other assigned units, so core-only is the default.
It is NOT full-auto. Individual magazines and five-round fire remain unfinished.
The earlier five-round runtime test was unsuccessful; counters did not prove
projectiles or damage.

## Install and recovery

Built and offline-validated does not mean installed or verified in-game.
The previous C89B3F9F candidate remains installed, helper disabled. Installation
requires separate authorization. Close SHOGUN 2 and leave runtime helpers off.

Extract the ZIP into a writable directory. Python 3.10+ is required. Preview:

    python -B .\install_type20.py install --dry-run

After installation is authorized:

    python -B .\install_type20.py install

The installer accepts the pinned game EXE/DLL and explicitly recognized prior
pack hashes. It targets only the two named packs directly in data and their two
loading lists. It preserves Modern Otomo and unrelated content. Every change has
a timestamped, hash-verified backup and immutable intent manifest before writing.
It prints a receipt and the exact one-command rollback:

    python -B .\install_type20.py rollback --receipt "<printed manifest path>"

Rollback restores the exact pre-install candidate/configuration and refuses
subsequent user edits. To restore the original confirmed two-shot archive instead:

    python -B .\recovery\install_type20.py install --dry-run
    python -B .\recovery\install_type20.py install

That recovery also creates a reversible receipt. Retain the extracted release and
its backups. The optional native suppression module is available only by explicit
choice using install --with-suppression; it is unnecessary for the test below.
Original-baseline recovery rejects that option because its bullet does not exist.

## One focused manual acceptance battle

After an authorized install, start one Sengoku Custom Battle: Oda, the exact
**Rifle and Grenade Section** above, versus slow melee infantry, with an enemy
archer unit for the protection check. Leave all runtime helpers off.

1. Check armour 8 in the unit panel. Toggle loose formation and verify the broader
   footprint; return to close formation and verify units hold the commanded line.
2. From 100–150 range, order rifle fire. Require visible impacts/casualties and
   decreasing ammunition, then Stop, Move, retarget and cease fire. Native two-shot
   cycles must resume only when orders permit. No five-shot claim is being tested.
3. With Fire at Will off, approach a fresh melee target to approximately 25 range.
   Activate **Blinding Grenades**, allow the native reload/throw interval, and
   observe launched grenades, impacts and enemy count before/after. A button or
   flash alone is not a damage pass. After expiry, order rifle fire and require
   ordinary damaging shots again.
4. Under comparable incoming arrows, check the protection change against the
   preserved prior build if needed. Armour display alone does not prove casualty
   reduction. Record failures or crashes instead of treating offline checks as
   gameplay certification.

## Build provenance

The previous session's three-build ledger remains intact. The new supplied
implementation request explicitly permits up to three builds this session and
mandates the supported fallback. This release records its own dated ledger and
the historical ledger hash. Build/reopen/validate commands:

    python -B scripts/type20_field_release.py build --iteration 1
    python -B scripts/type20_field_release.py validate
    python -B scripts/type20_field_release.py reopen
    python -B -m unittest discover -s tests -p "test_*.py" -v

Do not overwrite an existing iteration. The builder preserves all 35 unrelated
baseline payloads byte-for-byte, including artillery, recruitment, UI textures,
grenade definitions and confirmed animations. Only the private Type 20 unit,
statistics, rifle table, text and ability junction differ from the original
baseline; rifle tuning differences already existed in release 0.1.0.
