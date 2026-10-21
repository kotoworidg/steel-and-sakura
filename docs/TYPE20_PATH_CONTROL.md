# Type 20 animation-path control

Date: 2026-10-21. Current installed diagnostic; not an automatic-fire implementation.

## New gameplay evidence

The user explicitly confirms testing **Steel & Sakura - Type 20 Automatic Fire Test**,
rather than the older fallback, and reports that its firearms still are not automatic.
Record the previous two-marker build as FAILED_TO_ACHIEVE_AUTOMATIC_FIRE.
The exact number of damaging shots per individual cycle was not independently measured.

The installed pack before this pass matched the failed experiment's recorded SHA256:
8574F88C37FE2E6D8058785FC24CC25741C5573E2A6929C4B57C202E77B4420F.
The failed pack and its manifests/RPFM evidence are preserved under
build/type20-path-control/failed-*.

This rules out testing only the unchanged old unit. It does not yet establish
whether FIRE_TIME_2 was ignored, the private firing fragment was not selected,
or a two-event outcome still failed to resemble automatic fire.

## Why this control is different

The previous private fragment added FIRE/KNEEL_FIRE overrides after inherited
fragments. We have not proved fragment-priority behavior in the engine.
The control replaces the inherited musket combat fragment reference with a
private FULL copy of that fragment, changing only its FIRE and KNEEL_FIRE paths.
The extra override fragment reference is removed. This removes our dependency
on an unverified ordering assumption. It is not a proven diagnosis of the failure.

The two private clips now contain:
- 80 repetitions of their first pose frame, followed by every original motion frame.
- The same 48-bone rig and 20 FPS format.
- Duration extended by four seconds, with frame count updated accordingly.
- Exactly ONE FIRE_TIME shifted four seconds later.
- Original FIRE_POSITION; no FIRE_TIME_2 or FIRE_POSITION_2.

Standing: encoded first-shot time 4.05 seconds, clip length 5.0 seconds.
Kneeling: encoded first-shot time 4.00 seconds, clip length about 5.6 seconds.

This produces an intentionally noticeable hold if the engine consumes the clip
and honors its timing at the encoded playback speed. The engine may rescale
animation playback, so absence of an exact four-second interval alone does not
prove the file is ignored or that automatic infantry is impossible.

Reload, ammunition, damage, range, projectile count, weapon selectors, equipment,
fallback unit, grenades, artillery and recruitment are unchanged.
The only DB edit against the failed pack is the experimental unit's display-name
field; localization and four private animation/configuration files also change.

## Installed build and offline evidence

Build: build/steel_sakura_type20_path_control.pack.
Installed directly as:
D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack

Display name: **TYPE20 ANIMATION CHECK - 4s HOLD / ONE SHOT**.
Existing experimental unit key reused: steel_sakura_type20_automatic_fire_test.
It replaces the prior test variant; the original working riflemen remain alongside it.

SHA256:
3CDF8ADF3DDEC46FDD9E3379D37530B353DD8DCC5A55827E11FF9DF5B870768C

Backup of previously installed failed build and both load lists:
backups/type20-path-control-20261021-214523-685222.

Verified offline:
- RPFM reopened the edited unit-name row and localization and matched expected values.
- Packed path set unchanged; exactly six payloads differ from the failed experiment.
- All 20 pre-investigation fallback payloads remain byte-identical.
- Both clips parse; held frames match the first original pose, original motion tail
  matches byte-for-byte, rigs match, only the primary shot marker is delayed.
- Original global animation registry bytes preserved; private table substitutes
  the full combat fragment once and no longer inherits a competing musket FIRE binding.
- Generated asset bytes match packed bytes; installed SHA matches generated SHA.
- One active Steel Sakura pack; unrelated mods and loading lists preserved.
- Original archives and saves untouched.

Evidence: build/type20-path-control/{manifest.json,rpfm-evidence.json,validation.json,installation.json}.
These checks establish file integrity, not animation selection or shot timing in game.

## Short test suitable for low FPS

1. Fully restart. Original Sengoku Custom Battle -> Oda -> gun/matchlock infantry.
2. Select **TYPE20 ANIMATION CHECK - 4s HOLD / ONE SHOT** and the existing riflemen.
3. Use flat ground and a stationary target about 100-150 range away. Fire one squad
   at a time. Do not activate grenades or field artillery.
4. Watch the NEW control's first firing cycle. Does it hold the firing pose before
   one shot? Use the simulation clock, not wall-clock seconds; pause as needed.
5. Report:
   - Exact name visible?
   - New control holds before firing, or fires immediately like the old riflemen?
   - Approximately how much simulation time passes in the firing pose?
   - Any early shot during the hold, failure to shoot, bad muzzle origin or freezing?

This control is supposed to fire ONE shot. It is not supposed to look automatic.
An observed custom hold/delay is evidence that the private motion/event path is
consumed; it still does not prove numbered second-shot dispatch.

If the control is unchanged in appearance/timing, investigate registry selection,
fragment resolution and possible controller playback rescaling. Do not lower
reload again or call the whole engine incapable based only on that result.

## Rebuild and rollback

With game closed, from project root:

~~~powershell
powershell -NoProfile -File scripts/build_type20_path_control.ps1 -Install
~~~

Restore the pre-investigation working rifle/grenade/artillery pack:

~~~powershell
python scripts/type20_path_control.py rollback
~~~

Use this selector for the current control. Older selectors intentionally reject
unknown installed hashes. Do not enable the separately named build output beside
the combined installed pack.

## Next decision

If the path control is visible, preserve the observation and investigate whether
the rifle controller dispatches numbered events, with a controlled event comparison.
If it is not visible, prove clip selection before revisiting that hypothesis.
True automatic fire remains unimplemented and no engine-impossibility claim is made.
