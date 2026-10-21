$ErrorActionPreference='Stop'
$code=Get-Content scripts/rpfm_mcp.ps1 -Raw
Invoke-Expression ($code.Substring(0,$code.IndexOf('$null = Invoke-Mcp ''initialize''')))
try { $null=Invoke-RestMethod http://127.0.0.1:45127/version -TimeoutSec 2 } catch { Start-Process (Resolve-Path tools/rpfm-5.2.0/rpfm_server.exe).Path -WorkingDirectory (Resolve-Path tools/rpfm-5.2.0).Path -WindowStyle Hidden; Start-Sleep -Seconds 2 }
$null=Invoke-Mcp 'initialize' @{protocolVersion='2025-03-26';capabilities=@{};clientInfo=@{name='type20-research';version='1'}}
$null=Invoke-Tool 'set_game_selected' @{game_name='shogun_2';rebuild_dependencies=$false}
$pack='D:\Games\Total War - SHOGUN 2\data\data.pack'
$null=Invoke-Tool 'open_packfiles' @{paths=@($pack)}
$all=Get-Content build/inventory/all_data_local_paths.json -Raw|ConvertFrom-Json
$selected=@($all|Where-Object { $_ -like '*.anim' -and ($_ -match '/mus_fire.anim$|/mus_kneel_fire.anim$|/dual_pistol_fire.anim$|/pistol_fire.anim$|/rider_dual_pistol_[rlfb]_fire.anim$|/gatling_fire.anim$|/gat_op_fire.anim$|/gat_loader_fire.anim$')})
$dest=Join-Path (Get-Location).Path 'build/type20-research/vanilla'
New-Item -ItemType Directory -Force $dest|Out-Null
$selected+=@('animations/animation_tables/animation_tables.txt')
$map=@{PackFile=@($selected|ForEach-Object {@{File=$_}})}|ConvertTo-Json -Depth 6 -Compress
$null=Invoke-Tool 'extract_packed_files' @{pack_key=$pack;source_paths=$map;destination_path=$dest;export_as_tsv=$false}
foreach($table in @('warscape_equipment_themes','warscape_equipment_items')) {
 $d=Invoke-Tool 'decode_packed_file' @{pack_key=$pack;path=('db/'+$table+'_tables/'+$table);source='PackFile'}
 $d.content[0].text|Set-Content ('build/type20-research/base_'+$table+'.json') -Encoding utf8
}
$installed='D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack'
$null=Invoke-Tool 'open_packfiles' @{paths=@($installed)}
foreach($table in @('units','unit_stats_land','projectiles','uniforms','units_to_groupings_military_permissions','units_to_exclusive_faction_permissions','unit_to_unit_abilities_junctions','building_units_allowed')) {
 $path='db/'+$table+'_tables/steel_sakura_combined'
 $result=Invoke-Tool 'decode_packed_file' @{pack_key=$installed;path=$path;source='PackFile'}
 $result.content[0].text|Set-Content ('build/type20-research/installed_'+$table+'.json') -Encoding utf8
}
Write-Output ('Extracted observed animation files/registry: '+$selected.Count)
