# Single In-Game Test Card — Burst5 R3 Experiment

**Date:** 2026-10-22 | **Status:** PREPARED — AWAITS EXPLICIT ENGINE-HOOK APPROVAL

## Experiment Summary

The **Burst5 R3** external x86 debug controller is built and validated offline. It targets the native B firing callback (RVA 0x3D4320) and attempts **three additional paced dispatches** after the native two-shot burst, for a total of **five shots**. It is **fail-closed**: exact engine hashes, dual-key identity, native ammo calibration, animation/target continuity, and memory guards must all pass. No DLL injection, no game binary edits, no pack changes. Sustained auto is disabled.

**This test requires separate explicit user approval for engine-hook activation** before launch. Do not run without it.

---

## Protected Assets (Must Not Change)

| Asset | Path | SHA256 | Notes |
|-------|------|--------|-------|
| **Working two-shot Suppression Fire R2** | `build/type20-five-shot/confirmed-suppression-r2.pack` | `1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD` | Installed pack before artillery test; verified fallback |
| **Working two-shot burst (auto-cycle)** | `build/type20-auto-cycle/confirmed-burst.pack` | `0B497A435F4E28C2C068D7C90B60BA9D0C0FFA353BABD46242EF2FED2222D270` | Byte-identical confirmed two-shot |
| **Working no-reload burst (suppression)** | `build/type20-suppression/confirmed-no-reload-bursts.pack` | `56CCB4B44FC1520C379045ED3EC30D3EA13D6B3FB5BCF701A7259CC19EAD1299` | Byte-identical |
| **Game DLL** | `D:\Games\Total War - SHOGUN 2\empire.retail.dll` | `022FAE2E2DA92B59B8B1B8EE52887003C624E3C8ECA060B209F5D792A7F874F5` | Original, unmodified |
| **Game EXE** | `D:\Games\Total War - SHOGUN 2\shogun2.exe` | `0AB284186E0BE3FBCDE34E2F800E3C0328008F3219490C7C25E822ADD837C4A9` | Original, unmodified |
| **Installed artillery test pack** | `D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack` | `2D57C29074E15A3903E6C7900D652770CB27D7023A8A349BDF0C1C5BDDB67AB3` | Current installed — **will be restored to R2 before test** |

**Rollback to working R2 before test:**
```powershell
python -B scripts/type20_native_suppression.py rollback
```
This restores the confirmed Suppression Fire R2 pack (hash `1737D02D...`).

---

## Test Battle Configuration

**Game:** Total War: Shogun 2 (non-Steam) + Fall of the Samurai  
**Path:** `D:\Games\Total War - SHOGUN 2`  
**Mode:** Original Sengoku Custom Battle

| Parameter | Value |
|-----------|-------|
| **Faction** | Oda |
| **Player Unit** | **TYPE20 SUPPRESSION FIX R2** (40-man riflemen, key `steel_sakura_type20_suppressive_test`) |
| **Protection** | Yari infantry screen in front (prevents cavalry overrun confound) |
| **Enemy** | Slow melee infantry only (e.g., Yari Ashigaru) — no cavalry, no artillery, no other shooters |
| **Abilities** | **All OFF** — do not activate Suppression Fire or any special ability |
| **Terrain** | Flat open ground |
| **Range** | ~100–150 (rifle effective range) |
| **Formation** | Shallow lines, no overlap |
| **Fire-at-will** | Off initially; manual fire order |

---

## Test Procedure

1. **Close game completely.** Restore working R2 pack:
   ```powershell
   python -B scripts/type20_native_suppression.py rollback
   ```
   Verify installed pack hash = `1737D02D67F0C9100BBCC5255057C12B532F9805482D18ADC910542653D96DCD`

2. **Launch game.** Enter Sengoku Custom Battle as Oda. Select the **TYPE20 SUPPRESSION FIX R2** unit (display name) alongside yari screen. Face stationary melee infantry.

3. **Pause before firing.** Obtain Shogun2 PID:
   ```powershell
   (Get-Process shogun2).Id
   ```

4. **Launch Burst5 R3 with explicit approval:**
   ```powershell
   python -B scripts/burst5_build.py launch --approved-engine-hook --pid <PID>
   ```
   - Accept UAC prompt (required for debugger attach).
   - The host attaches, pauses at OS breakpoint, installs hardware breakpoints, and resumes.

5. **Unpause game.** Order the riflemen to fire (manual fire order, not fire-at-will).

6. **Observe one firing cycle:**
   - Watch for **five distinct projectile launches/impacts** from front-rank soldiers during ONE firing cycle.
   - Note ammunition indicator before/after.
   - Record whether shots are visibly separate (0.1s native tick pacing = ~100ms between extra dispatches).

7. **Issue Stop/Cease-Fire order.** Observe immediate interruption (no extra shots after order).

8. **Issue Move order.** Observe interruption (no shots while moving).

9. **Resume firing** if unit still has ammo. Observe whether additional burst cycles work.

10. **Host auto-stops after 90 seconds** or manual early stop:
    ```powershell
    python -B scripts/burst5_rollback.py
    ```
    This detaches controller, restores debug registers, verifies game/fallback hashes.

---

## Evidence to Capture

| Question | How to Judge |
|----------|--------------|
| **Unit identity confirmed?** | Unit card reads "TYPE20 SUPPRESSION FIX R2"; key `steel_sakura_type20_suppressive_test` |
| **Five separate shots?** | Five distinct muzzle flashes/impacts from SAME soldier in ONE cycle, ~100ms apart (use replay/slow sim if needed). Two shots = native; three extra = experiment. |
| **Ammunition consumed per shot?** | Ammo counter decrements 5× per cycle (or native accounting observed). Do not equate UI tick with projectile without evidence. |
| **Stop order interrupts?** | No shots fired after cease-fire command. |
| **Move order interrupts?** | No shots fired while moving. |
| **Sustained auto?** | **Disabled** in R3 — do not expect continuous fire beyond five-shot cap. |
| **Unsafe continued firing?** | Shots after stop/move/death = failure; report immediately. |

**Recording:** One short video or compact report covering above. Do not infer per-soldier shots from whole-unit volley totals.

---

## What This Test CAN Prove

- Custom unit identity mapped to native callback.
- Native two-shot burst + three paced extra dispatches = five shots.
- Native ammunition accounting followed per extra dispatch.
- Cease-fire / movement cancellation works.
- Animation/target continuity maintained.

## What This Test CANNOT Prove

- Universal engine five-shot capability (only this controller path tested).
- Sustained automatic fire (disabled in R3).
- Long-term stability across campaign/multiplayer.
- Projectile damage/accuracy of extra shots (visual confirmation only).

---

## Rollback Commands

| Action | Command |
|--------|---------|
| **Detach controller, verify hashes** | `python -B scripts/burst5_rollback.py` |
| **Full project-file rollback** | `python -B scripts/burst5_rollback.py --project-files` |
| **Restore R2 pack (working two-shot)** | `python -B scripts/type20_native_suppression.py rollback` |
| **Restore artillery test pack** | `python scripts/artillery_nuclear.py rollback` |

All rollback commands verify backup SHA256s before restoring. They refuse if later edits exist.

---

## Offline Validation (Already Passed)

- **51 admission scenarios** (identity, ammo, cancellation, lifetime, target loss, expiry, low update rate)
- **1,000 randomized schedules** — no catch-up volley at 1 FPS
- **11 instruction assertions** — R3 scope correction verified
- **9 code compatibility masks** — ASLR arithmetic at 3 bases
- **Synthetic debugger transport** — attach/detach/cleanup validated
- **Binary validation** — PE, CLR, instruction boundaries, call targets
- **Game/fallback hashes unchanged** — confirmed

---

## Unresolved Risks (Known)

1. **Unit record at `unit+0xB9C`** and **string-wrapper discovery** are candidates, not runtime-verified mappings.
2. **`action+0xF78` as ammunition** — two native delta-one observations required before extending.
3. **Cease-fire/movement/death gates** use native dispatch, animation continuity, validity predicate, target continuity, origin displacement — exact order/death semantics unverified.
4. **Action may end/change animation** before extra shots — safely ends attempt.
5. **No runtime evidence** yet that R3 admits any actor (first live run rejected all 703 on shooter-field predicate; R3 removes that gate).

---

## Activation Gate

**This experiment will NOT run without your explicit approval.** Reply with:

> **APPROVED: Run Burst5 R3 engine-hook test in one battle as specified.**

Then I will execute the test and report the complete outcome (evidence, hashes, unresolved items). No incremental tests, no partial results, no repeated requests.

If the result is inconclusive or blocked, I will report that honestly. Further in-game testing requires a new user request.