# Ability UI and artillery compatibility inspection

## Observed in installed files

The installed `data.pack` contains a binary `ui/battle ui/layout` with the
`Version054` header. Byte-string inspection finds `BattleSpecialAbilityPanel`,
`generic_abilities`, `BattleSpecialAbilityButton`, and seven distinct slot
names, `button_ability1_DY` through `button_ability7_DY`.

The installed `ui/templates/template.unit_ability_entry.luac` includes the
symbol `InitialiseBattleUIUnitAbilityEntry`. This is an observed Lua bytecode
string, not a verified callable modding API. No UI binary has been patched.

**Inference:** generic slots make dynamic ability binding plausible. They do
not prove arbitrary ability keys are supported. The new Nuclear Shell button,
its texture naming convention and activation remain unverified.

## Concrete interaction with the existing Otomo mod

The decoded `mods_modern_units_otomo.pack` tables contain these changes to
the ordinary Armstrong projectile/explosion keys:

| Field | Base game | Existing mod |
| --- | ---: | ---: |
| Projectile effective range | 550 | 600 |
| Explosion detonation radius | 4 | 5 |
| Explosion detonation speed | 10 | 15 |

No matching Armstrong gun-type or gun-to-projectile row was found in those
two inspected mod tables. This is a limited comparison, not a complete
compatibility guarantee or load-order determination.

Our artillery references the shared ordinary Armstrong gun, but its nuclear
projectile is a separate key with range 550. If the existing mod's overrides
take effect, ordinary rounds may reach targets the nuclear projectile cannot.
Test the ability initially at less than 550 range with loaded guns.

## Reproduce

With the project-local RPFM server running:

```powershell
pwsh -NoProfile -File scripts/rpfm_mcp.ps1 -Action inspect-modern
pwsh -NoProfile -File scripts/rpfm_mcp.ps1 -Action inspect-ability-ui
python scripts/inspect_ability_evidence.py
```

The initial `probe` inventory supplies base projectile data. Raw UI files
remain under ignored `build/inventory/ability-ui/`. The JSON evidence report
records source hashes, byte offsets and table differences under
`build/inventory/ability-evidence-report.json`. Neither raw UI files nor
game-table exports belong in the shareable source ZIP.

## Next decisions

- In-game: check generic slot creation and skill activation before editing UI.
- If no button appears: investigate engine/UI binding with a supported UI
  decoder. Do not replace strings in an undocumented binary layout.
- If shared ammunition causes inconsistent range: consider separate normal
  gun/projectile/explosion keys, retaining verified model and animation links.
- Keep the nuclear firing-window limit provisional until reload behavior is
  observed. Do not describe it as a single-shell skill.
