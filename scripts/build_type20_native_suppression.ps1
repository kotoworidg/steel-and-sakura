param([switch]$Install)
$ErrorActionPreference='Stop'
python scripts/type20_native_suppression.py prepare
if($LASTEXITCODE -ne 0){throw 'Preparation failed'}
$manifest=Get-Content build/type20-native-suppression/manifest.json -Raw|ConvertFrom-Json -AsHashtable
$code=Get-Content scripts/rpfm_mcp.ps1 -Raw
Invoke-Expression ($code.Substring(0,$code.IndexOf('$null = Invoke-Mcp ''initialize''')))
$null=Invoke-Mcp 'initialize' @{protocolVersion='2025-03-26';capabilities=@{};clientInfo=@{name='native-suppression-fix';version='2'}}
$null=Invoke-Tool 'set_game_selected' @{game_name='shogun_2';rebuild_dependencies=$false}
$key=$manifest.source
$null=Invoke-Tool 'open_packfiles' @{paths=@($key)}
foreach($n in ($manifest.tables.Keys|Sort-Object)) {
 $t=$manifest.tables[$n];$path=$t.path
 if($t.new){$null=Invoke-Tool 'new_packed_file' @{pack_key=$key;path=$path;new_file=(@{DB=@('steel_sakura_type20_native_suppression',$t.table,$t.version)}|ConvertTo-Json -Compress)}}
 $d=Invoke-Tool 'decode_packed_file' @{pack_key=$key;path=$path;source='PackFile'}
 $w=$d.content[0].text|ConvertFrom-Json -AsHashtable
 if(($w.DBRFileInfo[0].table.definition.fields.name -join ',') -cne ($t.fields -join ',')){throw ('Schema field mismatch: '+$n)}
 $w.DBRFileInfo[0].table.table_data=$t.rows
 $null=Invoke-Tool 'save_packed_file_from_view' @{pack_key=$key;path=$path;data=(@{DB=$w.DBRFileInfo[0]}|ConvertTo-Json -Depth 70 -Compress)}
}
$loc='text/db/steel_sakura_type20_suppression.loc'
$d=Invoke-Tool 'decode_packed_file' @{pack_key=$key;path=$loc;source='PackFile'}
$w=$d.content[0].text|ConvertFrom-Json -AsHashtable
$rows=@($manifest.localisation|ForEach-Object {,@(@{StringU16=$_.key},@{StringU16=$_.text},@{Boolean=$_.tooltip})})
$w.LocRFileInfo[0].table.table_data=$rows
$null=Invoke-Tool 'save_packed_file_from_view' @{pack_key=$key;path=$loc;data=(@{Loc=$w.LocRFileInfo[0]}|ConvertTo-Json -Depth 70 -Compress)}
$output=Join-Path (Get-Location).Path 'build/steel_sakura_type20_native_suppression.pack'
$null=Invoke-Tool 'save_pack_as' @{pack_key=$key;path=$output}
python scripts/clean_pack_metadata.py $output
if($LASTEXITCODE -ne 0){throw 'Metadata cleanup failed'}
$null=Invoke-Tool 'open_packfiles' @{paths=@($output)}
$decoded=@{}
foreach($n in ($manifest.tables.Keys|Sort-Object)){
 $t=$manifest.tables[$n];$d=Invoke-Tool 'decode_packed_file' @{pack_key=$output;path=$t.path;source='PackFile'};$w=$d.content[0].text|ConvertFrom-Json -AsHashtable
 if(($w.DBRFileInfo[0].table.table_data|ConvertTo-Json -Depth 70 -Compress) -cne ($t.rows|ConvertTo-Json -Depth 70 -Compress)){throw ('Round-trip mismatch: '+$n)}
 $decoded[$n]=$w
}
$d=Invoke-Tool 'decode_packed_file' @{pack_key=$output;path=$loc;source='PackFile'};$w=$d.content[0].text|ConvertFrom-Json -AsHashtable
if(($w.LocRFileInfo[0].table.table_data|ConvertTo-Json -Depth 70 -Compress) -cne ($rows|ConvertTo-Json -Depth 70 -Compress)){throw 'Localisation mismatch'}
$decoded.localisation=$w;$decoded|ConvertTo-Json -Depth 70|Set-Content build/type20-native-suppression/rpfm-roundtrip.json -Encoding utf8
python scripts/type20_native_suppression.py validate
if($LASTEXITCODE -ne 0){throw 'Validation failed'}
if($Install){python scripts/type20_native_suppression.py install;if($LASTEXITCODE -ne 0){throw 'Installation failed'}}
