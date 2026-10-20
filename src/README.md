# Editable source

`unit-specs.json` is the human-authored intent and status record. It is not a game DB schema.
The actual infantry DB row inputs are generated locally in `source/infantry/` from the user's installed game data by `scripts/prepare_infantry_source.py`. Those generated rows are excluded from Git and source release archives.

Tank and aircraft entries are research goals only. No substitute units are packaged as either one.
