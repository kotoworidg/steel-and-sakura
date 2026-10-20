# Infantry prototype: in-game check

The installed pack is `data\MyMods\steel_sakura_infantry_prototype.pack`.
The original `mod_list.txt` is backed up in this project's
`backups/before-prototype-install-2026-10-18/` directory.

1. Start the original Sengoku campaign with the current mod list.
2. At a province with a Fort, inspect recruitment for **Automatic Rifle
   Squad**. Record whether it appears, its displayed name/card, and unit size.
3. Recruit it and enter a battle. Record whether all 40 soldiers render,
   move, aim, fire, reload, and behave correctly.
4. Record whether firing looks like the expected rapid-fire weapon. The
   prototype currently uses FoTS Tosa repeating-rifle data, so true automatic
   fire is not established by the pack inspection.
5. If the game crashes or the unit is absent, save the relevant logs or a
   screenshot and report the exact stage. Do not edit or delete saves.

To remove the prototype, remove only its added line from the root
`mod_list.txt`, then remove only
`data\MyMods\steel_sakura_infantry_prototype.pack`. The backed-up mod list
can be restored if its other entries have not changed in the meantime.
