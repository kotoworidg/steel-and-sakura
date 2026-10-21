$ErrorActionPreference='Stop'
$requestedAction='inspect'
$code=Get-Content scripts/rpfm_mcp.ps1 -Raw
Invoke-Expression ($code.Substring(0,$code.IndexOf('$null = Invoke-Mcp ''initialize''')))
$Action=$requestedAction
try { $null=Invoke-RestMethod http://127.0.0.1:45127/version -TimeoutSec 2 } catch { Start-Process (Resolve-Path tools/rpfm-5.2.0/rpfm_server.exe).Path -WorkingDirectory (Resolve-Path tools/rpfm-5.2.0).Path -WindowStyle Hidden; Start-Sleep -Seconds 2 }
$null=Invoke-Mcp 'initialize' @{protocolVersion='2025-03-26';capabilities=@{};clientInfo=@{name='combined-repair';version='1'}}
$null=Invoke-Tool 'set_game_selected' @{game_name='shogun_2';rebuild_dependencies=$false}




python scripts/prepare_frag_test.py
if($LASTEXITCODE -ne 0){throw 'Fragmentation preparation failed'}
$manifest=Get-Content build/fragmentation-test/manifest.json -Raw|ConvertFrom-Json -AsHashtable
$key=$manifest.fallback;$output=$manifest.experiment
$null=Invoke-Tool 'open_packfiles' @{paths=@($key)}
foreach($name in ($manifest.tables.Keys|Sort-Object)) {
 $source=$manifest.tables[$name];$path='db/'+$source.table+'/steel_sakura_frag_test'
 $null=Invoke-Tool 'new_packed_file' @{pack_key=$key;path=$path;new_file=(@{DB=@('steel_sakura_frag_test',$source.table,$source.version)}|ConvertTo-Json -Compress)}
 $decoded=Invoke-Tool 'decode_packed_file' @{pack_key=$key;path=$path;source='PackFile'}
 $wrapper=$decoded.content[0].text|ConvertFrom-Json -AsHashtable
 $wrapper.DBRFileInfo[0].table.table_data=$source.rows
 $null=Invoke-Tool 'save_packed_file_from_view' @{pack_key=$key;path=$path;data=(@{DB=$wrapper.DBRFileInfo[0]}|ConvertTo-Json -Depth 70 -Compress)}
}
$null=Invoke-Tool 'save_pack_as' @{pack_key=$key;path=$output}
python scripts/clean_pack_metadata.py $output
if($LASTEXITCODE -ne 0){throw 'Metadata cleanup failed'}
$null=Invoke-Tool 'open_packfiles' @{paths=@($output)}
foreach($name in ($manifest.tables.Keys|Sort-Object)) {
 $source=$manifest.tables[$name];$path='db/'+$source.table+'/steel_sakura_frag_test'
 $decoded=Invoke-Tool 'decode_packed_file' @{pack_key=$output;path=$path;source='PackFile'}
 $table=($decoded.content[0].text|ConvertFrom-Json -AsHashtable).DBRFileInfo[0].table
 if($table.definition.version -ne $source.version -or ($table.table_data|ConvertTo-Json -Depth 70 -Compress) -cne ($source.rows|ConvertTo-Json -Depth 70 -Compress)){throw "Fragmentation round-trip mismatch $name"}
 Write-Output ('VERIFIED_FRAG='+$name+' rows='+$source.rows.Count)
}
@{status='VERIFIED_OFFLINE_ONLY';pack_sha256=(Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash}|ConvertTo-Json|Set-Content build/fragmentation-test/rpfm-report.json -Encoding utf8
python scripts/validate_frag_test.py
if($LASTEXITCODE -ne 0){throw 'Fragmentation differential verification failed'}
