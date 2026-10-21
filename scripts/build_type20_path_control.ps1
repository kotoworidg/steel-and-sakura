param([switch]$Install)
$ErrorActionPreference='Stop'
python scripts/type20_path_control.py prepare
if($LASTEXITCODE -ne 0){throw 'Control preparation failed'}
$m=Get-Content build/type20-path-control/manifest.json -Raw|ConvertFrom-Json -AsHashtable
$code=Get-Content scripts/rpfm_mcp.ps1 -Raw
Invoke-Expression ($code.Substring(0,$code.IndexOf('$null = Invoke-Mcp ''initialize''')))
$null=Invoke-Mcp 'initialize' @{protocolVersion='2025-03-26';capabilities=@{};clientInfo=@{name='type20-path-control';version='1'}}
$null=Invoke-Tool 'set_game_selected' @{game_name='shogun_2';rebuild_dependencies=$false}
$key=$m.failed_event
$null=Invoke-Tool 'open_packfiles' @{paths=@($key)}
$units='db/units_tables/steel_sakura_type20_event_test'
$d=Invoke-Tool 'decode_packed_file' @{pack_key=$key;path=$units;source='PackFile'}
$beforeUnits=$d.content[0].text|ConvertFrom-Json -AsHashtable
$w=$d.content[0].text|ConvertFrom-Json -AsHashtable
$fields=@($w.DBRFileInfo[0].table.definition.fields|ForEach-Object {$_.name})
if($w.DBRFileInfo[0].table.table_data.Count -ne 1){throw 'Expected single experimental unit'}
$w.DBRFileInfo[0].table.table_data[0][$fields.IndexOf('on_screen_name')].StringU16=$m.title
$null=Invoke-Tool 'save_packed_file_from_view' @{pack_key=$key;path=$units;data=(@{DB=$w.DBRFileInfo[0]}|ConvertTo-Json -Depth 70 -Compress)}
$expectedUnits=$w
$loc='text/db/steel_sakura_type20_event_test.loc'
$d=Invoke-Tool 'decode_packed_file' @{pack_key=$key;path=$loc;source='PackFile'}
$beforeLoc=$d.content[0].text|ConvertFrom-Json -AsHashtable
$w=$d.content[0].text|ConvertFrom-Json -AsHashtable
foreach($row in $w.LocRFileInfo[0].table.table_data) {
 if($row[0].StringU16 -eq ('units_on_screen_name_'+$m.unit)){$row[1].StringU16=$m.title}
 elseif($row[0].StringU16 -like 'unit_description_texts_description_text_*'){$row[1].StringU16='CONTROL ONLY: hold the firing pose about four seconds before ONE shot. Tests animation selection; not automatic fire.'}
 else {$row[1].StringU16='Private full combat fragment replaces inherited FIRE/KNEEL_FIRE bindings. Eighty held frames and delayed primary shot marker. Original riflemen and all combat statistics unchanged.'}
}
$expectedLoc=$w
$null=Invoke-Tool 'save_packed_file_from_view' @{pack_key=$key;path=$loc;data=(@{Loc=$w.LocRFileInfo[0]}|ConvertTo-Json -Depth 70 -Compress)}
$sources=@($m.assets|ForEach-Object {$_.source})
$paths=@($m.assets|ForEach-Object {@{File=$_.destination}})|ConvertTo-Json -Depth 5 -Compress
$null=Invoke-Tool 'add_packed_files' @{pack_key=$key;source_paths=$sources;destination_paths=$paths}
$out=Join-Path (Get-Location).Path 'build/steel_sakura_type20_path_control.pack'
$null=Invoke-Tool 'save_pack_as' @{pack_key=$key;path=$out}
python scripts/clean_pack_metadata.py $out
if($LASTEXITCODE -ne 0){throw 'Control cleanup failed'}
$null=Invoke-Tool 'open_packfiles' @{paths=@($out)}
$d=Invoke-Tool 'decode_packed_file' @{pack_key=$out;path=$units;source='PackFile'}
$afterUnits=$d.content[0].text|ConvertFrom-Json -AsHashtable
if(($afterUnits.DBRFileInfo[0].table.table_data|ConvertTo-Json -Depth 70 -Compress) -cne ($expectedUnits.DBRFileInfo[0].table.table_data|ConvertTo-Json -Depth 70 -Compress)){throw 'Control unit roundtrip mismatch'}
$d=Invoke-Tool 'decode_packed_file' @{pack_key=$out;path=$loc;source='PackFile'}
$afterLoc=$d.content[0].text|ConvertFrom-Json -AsHashtable
if(($afterLoc.LocRFileInfo[0].table.table_data|ConvertTo-Json -Depth 70 -Compress) -cne ($expectedLoc.LocRFileInfo[0].table.table_data|ConvertTo-Json -Depth 70 -Compress)){throw 'Control loc roundtrip mismatch'}
@{before_units=$beforeUnits;after_units=$afterUnits;before_loc=$beforeLoc;after_loc=$afterLoc}|ConvertTo-Json -Depth 70|Set-Content build/type20-path-control/rpfm-evidence.json -Encoding utf8
python scripts/type20_path_control.py validate
if($LASTEXITCODE -ne 0){throw 'Control validation failed'}
if($Install) {
 python scripts/type20_path_control.py install
 if($LASTEXITCODE -ne 0){throw 'Control install failed'}
}
