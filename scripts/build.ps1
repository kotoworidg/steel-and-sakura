param([switch]$SkipPrepare, [switch]$ArtilleryTest, [switch]$ModernArtillery)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root
$redirect = Join-Path $env:APPDATA 'FrodoWazEre\rpfm\config\config_folder.txt'
$config = (Resolve-Path 'tools\rpfm-config\data').Path
if (!(Test-Path -LiteralPath $redirect) -or (Get-Content -LiteralPath $redirect -Raw).Trim() -ne $config) {
    throw "RPFM config redirect is missing or points elsewhere: $redirect"
}
if (!(Test-Path 'tools\rpfm-5.2.0\rpfm_server.exe')) { throw 'Project-local RPFM server is missing' }
try { $null = Invoke-RestMethod 'http://127.0.0.1:45127/version' -TimeoutSec 2 } catch {
    New-Item -ItemType Directory -Force -Path 'build\logs' | Out-Null
    $exe = (Resolve-Path 'tools\rpfm-5.2.0\rpfm_server.exe').Path
    $working = (Resolve-Path 'tools\rpfm-5.2.0').Path
    $log = (Resolve-Path 'build\logs').Path
    Start-Process -FilePath $exe -WorkingDirectory $working -WindowStyle Hidden -RedirectStandardOutput (Join-Path $log 'rpfm-server.out.log') -RedirectStandardError (Join-Path $log 'rpfm-server.err.log') | Out-Null
    for ($i=0; $i -lt 20; $i++) {
        Start-Sleep -Milliseconds 500
        try { $null = Invoke-RestMethod 'http://127.0.0.1:45127/version' -TimeoutSec 2; break } catch {}
    }
}
$version = Invoke-RestMethod 'http://127.0.0.1:45127/version' -TimeoutSec 3
if ($version.version -ne '5.2.0') { throw "Expected RPFM 5.2.0, found $($version.version)" }
if ($ModernArtillery) {
    pwsh -NoProfile -File scripts\rpfm_mcp.ps1 -Action inspect-modern -GameRoot 'D:\Games\Total War - SHOGUN 2'
    if ($LASTEXITCODE -ne 0) { throw 'Modern artillery data inspection failed' }
    python scripts\prepare_modern_artillery.py
    if ($LASTEXITCODE -ne 0) { throw 'Modern artillery preparation failed' }
    pwsh -NoProfile -File scripts\rpfm_mcp.ps1 -Action build-modern
    if ($LASTEXITCODE -ne 0) { throw 'Modern artillery build failed' }
    python scripts\clean_pack_metadata.py build\steel_sakura_modern_artillery_prototype.pack
    if ($LASTEXITCODE -ne 0) { throw 'Metadata cleanup failed' }
    pwsh -NoProfile -File scripts\rpfm_mcp.ps1 -Action validate-modern
    if ($LASTEXITCODE -ne 0) { throw 'Modern artillery validation failed' }
    python scripts\validate_modern_artillery.py
    if ($LASTEXITCODE -ne 0) { throw 'Modern artillery reference validation failed' }
    exit 0
}
if ($ArtilleryTest) {
    python scripts\prepare_artillery_test.py
    if ($LASTEXITCODE -ne 0) { throw 'Artillery test source preparation failed' }
    pwsh -NoProfile -File scripts\rpfm_mcp.ps1 -Action build-artillery
    if ($LASTEXITCODE -ne 0) { throw 'Artillery test pack build failed' }
    pwsh -NoProfile -File scripts\rpfm_mcp.ps1 -Action validate-artillery
    if ($LASTEXITCODE -ne 0) { throw 'Artillery test pack validation failed' }
    exit 0
}
if (!$SkipPrepare) { python scripts\prepare_infantry_source.py; if ($LASTEXITCODE -ne 0) { throw 'Source preparation failed' } }
python scripts\generate_infantry_icon.py
if ($LASTEXITCODE -ne 0) { throw 'Icon generation failed' }
pwsh -NoProfile -File scripts\rpfm_mcp.ps1 -Action build
if ($LASTEXITCODE -ne 0) { throw 'Pack build failed' }
python scripts\clean_pack_metadata.py build\steel_sakura_infantry_prototype.pack
if ($LASTEXITCODE -ne 0) { throw 'Metadata cleanup failed' }
pwsh -NoProfile -File scripts\rpfm_mcp.ps1 -Action validate
if ($LASTEXITCODE -ne 0) { throw 'Pack validation failed' }
python scripts\validate_offline.py
if ($LASTEXITCODE -ne 0) { throw 'Offline validation failed' }
python -m unittest discover -s tests -p 'test_*.py'
if ($LASTEXITCODE -ne 0) { throw 'Offline regression tests failed' }
