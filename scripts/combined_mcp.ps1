param([ValidateSet('inspect','assets','build','validate')][string]$Action='inspect')
$ErrorActionPreference='Stop'
$requestedAction=$Action
$code=Get-Content scripts/rpfm_mcp.ps1 -Raw
Invoke-Expression ($code.Substring(0,$code.IndexOf('$null = Invoke-Mcp ''initialize''')))
$Action=$requestedAction
try { $null=Invoke-RestMethod http://127.0.0.1:45127/version -TimeoutSec 2 } catch { Start-Process (Resolve-Path tools/rpfm-5.2.0/rpfm_server.exe).Path -WorkingDirectory (Resolve-Path tools/rpfm-5.2.0).Path -WindowStyle Hidden; Start-Sleep -Seconds 2 }
$null=Invoke-Mcp 'initialize' @{protocolVersion='2025-03-26';capabilities=@{};clientInfo=@{name='combined-repair';version='1'}}
$null=Invoke-Tool 'set_game_selected' @{game_name='shogun_2';rebuild_dependencies=$false}

$pack='D:\Games\Total War - SHOGUN 2\data\data.pack'
if($Action -eq 'inspect') {
 $null=Invoke-Tool 'open_packfiles' @{paths=@($pack)}
 foreach($name in @('units_to_exclusive_faction_permissions','groupings_military','effect_bonus_value_unit_ability_junctions','unit_info_card_abilities_strings')) {
  $result=Invoke-Tool 'decode_packed_file' @{pack_key=$pack;path=('db/'+$name+'_tables/'+$name);source='PackFile'}
  $result.content[0].text | Set-Content ('build/inventory/table_'+$name+'.json') -Encoding utf8
 }
} elseif($Action -eq 'assets') {
 $null=Invoke-Tool 'open_packfiles' @{paths=@($pack)}
 $paths=Get-Content build/inventory/all_data_local_paths.json -Raw | ConvertFrom-Json
 $selected=@($paths | Where-Object { $_ -like 'ui/*' -and ($_ -match '/button_(blinding_grenade|shrapnel_shot)_' -or $_ -match '/(blinding_grenade|shrapnel_shot)_icon.tga$') })
 if($selected.Count -ne 16){throw 'Expected sixteen observed ability UI assets'}
 $dest=Join-Path (Get-Location).Path 'build/combined/vanilla-ui'
 New-Item -ItemType Directory -Force $dest | Out-Null
 $map=@{PackFile=@($selected | ForEach-Object { @{File=$_} })} | ConvertTo-Json -Depth 5 -Compress
 $null=Invoke-Tool 'extract_packed_files' @{pack_key=$pack;source_paths=$map;destination_path=$dest;export_as_tsv=$false}
 Write-Output 'EXTRACTED=16 vanilla ability UI references'
} else {
 $manifest=Get-Content build/combined/manifest.json -Raw | ConvertFrom-Json -AsHashtable
 $output=Join-Path (Get-Location).Path 'build/steel_sakura_combined_test.pack'
 if($Action -eq 'build') {
  $created=Invoke-Tool 'new_pack';$key=($created.content[0].text | ConvertFrom-Json -AsHashtable).String
  $null=Invoke-Tool 'set_pack_file_type' @{pack_key=$key;pack_file_type='"Mod"'}
 } else {
  $key=$output;$opened=Invoke-Tool 'open_packfiles' @{paths=@($output)}
  $info=($opened.content[0].text | ConvertFrom-Json -AsHashtable).StringContainerInfo[1]
  if($info.pfh_version -ne 'PFH3' -or $info.pfh_file_type -ne 'Mod'){throw 'Bad combined pack header'}
 }
 foreach($name in ($manifest.tables.Keys | Sort-Object)) {
  $source=$manifest.tables[$name];$path='db/'+$source.table+'/steel_sakura_combined'
  if($Action -eq 'build') {
   $null=Invoke-Tool 'new_packed_file' @{pack_key=$key;path=$path;new_file=(@{DB=@('steel_sakura_combined',$source.table,$source.version)}|ConvertTo-Json -Compress)}
  }
  $decoded=Invoke-Tool 'decode_packed_file' @{pack_key=$key;path=$path;source='PackFile'}
  $wrapper=$decoded.content[0].text | ConvertFrom-Json -AsHashtable
  if($Action -eq 'build') {
   $wrapper.DBRFileInfo[0].table.table_data=$source.rows
   $null=Invoke-Tool 'save_packed_file_from_view' @{pack_key=$key;path=$path;data=(@{DB=$wrapper.DBRFileInfo[0]}|ConvertTo-Json -Depth 70 -Compress)}
  } else {
   $table=$wrapper.DBRFileInfo[0].table
   if($table.definition.version -ne $source.version -or ($table.table_data|ConvertTo-Json -Depth 70 -Compress) -cne ($source.rows|ConvertTo-Json -Depth 70 -Compress)){throw "Combined DB mismatch $name"}
  }
  Write-Output ($Action+' TABLE='+$name+' rows='+$source.rows.Count)
 }
 $locPath='text/db/steel_sakura_combined.loc'
 $expectedRows=@($manifest.localisation | ForEach-Object { ,@(@{StringU16=$_.key},@{StringU16=$_.text},@{Boolean=$_.tooltip}) })
 if($Action -eq 'build') {$null=Invoke-Tool 'new_packed_file' @{pack_key=$key;path=$locPath;new_file='{"Loc":"steel_sakura_combined"}'}}
 $decoded=Invoke-Tool 'decode_packed_file' @{pack_key=$key;path=$locPath;source='PackFile'}
 $wrapper=$decoded.content[0].text|ConvertFrom-Json -AsHashtable
 if($Action -eq 'build') {
  $wrapper.LocRFileInfo[0].table.table_data=$expectedRows
  $null=Invoke-Tool 'save_packed_file_from_view' @{pack_key=$key;path=$locPath;data=(@{Loc=$wrapper.LocRFileInfo[0]}|ConvertTo-Json -Depth 70 -Compress)}
  $sources=@($manifest.assets|ForEach-Object {$_.source})
  $destinations=@($manifest.assets|ForEach-Object {@{File=$_.destination}})|ConvertTo-Json -Depth 5 -Compress
  $null=Invoke-Tool 'add_packed_files' @{pack_key=$key;source_paths=$sources;destination_paths=$destinations}
  $null=Invoke-Tool 'save_pack_as' @{pack_key=$key;path=$output}
 } else {
  if(($wrapper.LocRFileInfo[0].table.table_data|ConvertTo-Json -Depth 70 -Compress) -cne ($expectedRows|ConvertTo-Json -Depth 70 -Compress)){throw 'Combined localisation mismatch'}
  $dest=Join-Path (Get-Location).Path ('build/combined/verify-'+[guid]::NewGuid().ToString('N'))
  New-Item -ItemType Directory -Force $dest|Out-Null
  $map=@{PackFile=@($manifest.assets|ForEach-Object {@{File=$_.destination}})}|ConvertTo-Json -Depth 5 -Compress
  $null=Invoke-Tool 'extract_packed_files' @{pack_key=$key;source_paths=$map;destination_path=$dest;export_as_tsv=$false}
  foreach($asset in $manifest.assets) {
   if((Get-FileHash -LiteralPath $asset.source -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath (Join-Path $dest $asset.destination) -Algorithm SHA256).Hash){throw 'Combined UI payload mismatch'}
  }
  @{status='VERIFIED_OFFLINE_ONLY';runtime_status='PENDING_USER_CONFIRMATION';pack_sha256=(Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash;tables=$manifest.tables.Count;assets=$manifest.assets.Count}|ConvertTo-Json|Set-Content build/combined/rpfm-report.json -Encoding utf8
 }
 Write-Output ('COMBINED='+$output)
}
