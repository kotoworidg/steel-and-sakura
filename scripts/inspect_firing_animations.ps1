$ErrorActionPreference='Stop'
$requestedAction='inspect'
$code=Get-Content scripts/rpfm_mcp.ps1 -Raw
Invoke-Expression ($code.Substring(0,$code.IndexOf('$null = Invoke-Mcp ''initialize''')))
$Action=$requestedAction
try { $null=Invoke-RestMethod http://127.0.0.1:45127/version -TimeoutSec 2 } catch { Start-Process (Resolve-Path tools/rpfm-5.2.0/rpfm_server.exe).Path -WorkingDirectory (Resolve-Path tools/rpfm-5.2.0).Path -WindowStyle Hidden; Start-Sleep -Seconds 2 }
$null=Invoke-Mcp 'initialize' @{protocolVersion='2025-03-26';capabilities=@{};clientInfo=@{name='combined-repair';version='1'}}
$null=Invoke-Tool 'set_game_selected' @{game_name='shogun_2';rebuild_dependencies=$false}



$dest=Join-Path (Get-Location).Path 'build/automatic-research'
New-Item -ItemType Directory -Force $dest | Out-Null
$pack='D:\Games\Total War - SHOGUN 2\data\data.pack'
$null=Invoke-Tool 'open_packfiles' @{paths=@($pack)}
$paths=@('animations/battleconfiguration/boshin_man_rifle_combat_fragment.txt','animations/battleconfiguration/shogun_man_musket_trained_fragment.txt','animations/battleconfiguration/shogun_man_musket_fragment.txt','animations/battleconfiguration/shogun_man_musket_combat_fragment.txt','animations/battleconfiguration/boshin_gatling_gun_fragment.txt','animations/battleconfiguration/boshin_armstrong_cannon_fragment.txt','animations/battleconfiguration/boshin_man_pistol_fragment.txt','animations/battleconfiguration/boshin_man_dual_pistol_fragment.txt')
$map=@{PackFile=@($paths|ForEach-Object {@{File=$_}})}|ConvertTo-Json -Depth 5 -Compress
$null=Invoke-Tool 'extract_packed_files' @{pack_key=$pack;source_paths=$map;destination_path=$dest;export_as_tsv=$false}
Write-Output 'Extracted eight observed animation configuration fragments.'
