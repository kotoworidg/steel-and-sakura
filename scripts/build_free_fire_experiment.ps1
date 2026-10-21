$ErrorActionPreference='Stop'
$requestedAction='inspect'
$code=Get-Content scripts/rpfm_mcp.ps1 -Raw
Invoke-Expression ($code.Substring(0,$code.IndexOf('$null = Invoke-Mcp ''initialize''')))
$Action=$requestedAction
try { $null=Invoke-RestMethod http://127.0.0.1:45127/version -TimeoutSec 2 } catch { Start-Process (Resolve-Path tools/rpfm-5.2.0/rpfm_server.exe).Path -WorkingDirectory (Resolve-Path tools/rpfm-5.2.0).Path -WindowStyle Hidden; Start-Sleep -Seconds 2 }
$null=Invoke-Mcp 'initialize' @{protocolVersion='2025-03-26';capabilities=@{};clientInfo=@{name='combined-repair';version='1'}}
$null=Invoke-Tool 'set_game_selected' @{game_name='shogun_2';rebuild_dependencies=$false}




$root=(Get-Location).Path
$installed='D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack'
$fallback=Join-Path $root 'build/automatic-research/working-fast-rifle-fallback.pack'
$output=Join-Path $root 'build/steel_sakura_free_fire_experiment.pack'
if(Test-Path -LiteralPath $fallback) {
 if((Get-FileHash -LiteralPath $fallback -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $installed -Algorithm SHA256).Hash){throw 'Preserved fallback differs from installed pack; do not overwrite it'}
} else { Copy-Item -LiteralPath $installed -Destination $fallback }
$null=Invoke-Tool 'open_packfiles' @{paths=@($fallback)}
$statsPath='db/unit_stats_land_tables/steel_sakura_combined'
$decoded=Invoke-Tool 'decode_packed_file' @{pack_key=$fallback;path=$statsPath;source='PackFile'}
$wrapper=$decoded.content[0].text|ConvertFrom-Json -AsHashtable
$before=$decoded.content[0].text|ConvertFrom-Json -AsHashtable
$table=$wrapper.DBRFileInfo[0].table
$fields=@($table.definition.fields|ForEach-Object {$_.name})
$keyIndex=$fields.IndexOf('key');$mechanismIndex=$fields.IndexOf('firing_mechanism')
$matches=@($table.table_data|Where-Object { $_[$keyIndex].StringU16 -eq 'SteelSakura_Automatic_Rifle_Squad' })
if($matches.Count -ne 1){throw 'Expected one custom infantry row'}
if($matches[0][$mechanismIndex].StringU16 -ne 'matchlock'){throw 'Fallback is not the confirmed matchlock baseline'}
foreach($row in $table.table_data) {
 if($row[$keyIndex].StringU16 -eq 'SteelSakura_Automatic_Rifle_Squad'){$row[$mechanismIndex].StringU16='none'}
}
$wrapper.DBRFileInfo[0].table=$table
$null=Invoke-Tool 'save_packed_file_from_view' @{pack_key=$fallback;path=$statsPath;data=(@{DB=$wrapper.DBRFileInfo[0]}|ConvertTo-Json -Depth 70 -Compress)}
$locPath='text/db/steel_sakura_combined.loc'
$decoded=Invoke-Tool 'decode_packed_file' @{pack_key=$fallback;path=$locPath;source='PackFile'}
$loc=$decoded.content[0].text|ConvertFrom-Json -AsHashtable
$beforeLoc=$decoded.content[0].text|ConvertFrom-Json -AsHashtable
foreach($row in $loc.LocRFileInfo[0].table.table_data) {
 if($row[0].StringU16 -eq 'units_on_screen_name_SteelSakura_Automatic_Rifle_Squad'){$row[1].StringU16='EXP NONE - same fast rifle stats'}
}
$null=Invoke-Tool 'save_packed_file_from_view' @{pack_key=$fallback;path=$locPath;data=(@{Loc=$loc.LocRFileInfo[0]}|ConvertTo-Json -Depth 70 -Compress)}
$null=Invoke-Tool 'save_pack_as' @{pack_key=$fallback;path=$output}
python scripts/clean_pack_metadata.py $output
if($LASTEXITCODE -ne 0){throw 'Experiment cleanup failed'}
$null=Invoke-Tool 'open_packfiles' @{paths=@($output)}
$actual=Invoke-Tool 'decode_packed_file' @{pack_key=$output;path=$statsPath;source='PackFile'}
$actualWrapper=$actual.content[0].text|ConvertFrom-Json -AsHashtable
if(($actualWrapper.DBRFileInfo[0].table.table_data|ConvertTo-Json -Depth 70 -Compress) -cne ($table.table_data|ConvertTo-Json -Depth 70 -Compress)){throw 'Experiment DB round trip differs'}
$actualLoc=Invoke-Tool 'decode_packed_file' @{pack_key=$output;path=$locPath;source='PackFile'}
$actualLocWrapper=$actualLoc.content[0].text|ConvertFrom-Json -AsHashtable
if(($actualLocWrapper.LocRFileInfo[0].table.table_data|ConvertTo-Json -Depth 70 -Compress) -cne ($loc.LocRFileInfo[0].table.table_data|ConvertTo-Json -Depth 70 -Compress)){throw 'Experiment localisation round trip differs'}
$evidence=@{before_stats=$before;after_stats=$actualWrapper;before_loc=$beforeLoc;after_loc=$actualLocWrapper;fallback=$fallback;experiment=$output}
$evidence|ConvertTo-Json -Depth 70|Set-Content build/automatic-research/experiment-rpfm-evidence.json -Encoding utf8
Write-Output 'RPFM verified one mechanism change; installed fallback was not modified.'
python scripts/validate_free_fire_experiment.py
if($LASTEXITCODE -ne 0){throw 'Experiment differential verification failed'}
