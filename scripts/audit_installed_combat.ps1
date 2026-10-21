$ErrorActionPreference='Stop'
$requestedAction='inspect'
$code=Get-Content scripts/rpfm_mcp.ps1 -Raw
Invoke-Expression ($code.Substring(0,$code.IndexOf('$null = Invoke-Mcp ''initialize''')))
$Action=$requestedAction
try { $null=Invoke-RestMethod http://127.0.0.1:45127/version -TimeoutSec 2 } catch { Start-Process (Resolve-Path tools/rpfm-5.2.0/rpfm_server.exe).Path -WorkingDirectory (Resolve-Path tools/rpfm-5.2.0).Path -WindowStyle Hidden; Start-Sleep -Seconds 2 }
$null=Invoke-Mcp 'initialize' @{protocolVersion='2025-03-26';capabilities=@{};clientInfo=@{name='combined-repair';version='1'}}
$null=Invoke-Tool 'set_game_selected' @{game_name='shogun_2';rebuild_dependencies=$false}


$dest='build/diagnostic';New-Item -ItemType Directory -Force $dest | Out-Null
$installed='D:\Games\Total War - SHOGUN 2\data\steel_sakura_combined_test.pack'
$null=Invoke-Tool 'open_packfiles' @{paths=@($installed)}
foreach($name in @('units','unit_stats_land','projectiles','projectiles_explosions','unit_abilities','unit_special_abilities','unit_to_unit_abilities_junctions')) {
 $result=Invoke-Tool 'decode_packed_file' @{pack_key=$installed;path=('db/'+$name+'_tables/steel_sakura_combined');source='PackFile'}
 $result.content[0].text|Set-Content ($dest+'/installed_'+$name+'.json') -Encoding utf8
}
$original='D:\Games\Total War - SHOGUN 2\data\data.pack'
$null=Invoke-Tool 'open_packfiles' @{paths=@($original)}
foreach($name in @('units','unit_stats_land','projectiles','projectiles_explosions','gun_types','gun_type_to_projectiles','unit_abilities','unit_special_abilities','unit_to_unit_abilities_junctions')) {
 $result=Invoke-Tool 'decode_packed_file' @{pack_key=$original;path=('db/'+$name+'_tables/'+$name);source='PackFile'}
 $result.content[0].text|Set-Content ($dest+'/base_'+$name+'.json') -Encoding utf8
}
$other='D:\Games\Total War - SHOGUN 2\data\mods_modern_units_otomo.pack'
$null=Invoke-Tool 'open_packfiles' @{paths=@($other)}
foreach($name in @('units','unit_stats_land','projectiles','gun_types','gun_type_to_projectiles','unit_abilities','unit_special_abilities','unit_to_unit_abilities_junctions')) {
 $result=Invoke-Tool 'decode_packed_file' @{pack_key=$other;path=('db/'+$name+'_tables/'+$name);source='PackFile'}
 $result.content[0].text|Set-Content ($dest+'/otomo_'+$name+'.json') -Encoding utf8
}
Write-Output 'Decoded actual installed pack, vanilla combat chain and active Otomo tables.'
