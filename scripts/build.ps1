param([switch]$SkipPrepare)

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
if (!$SkipPrepare) { python scripts\prepare_infantry_source.py; if ($LASTEXITCODE -ne 0) { throw 'Source preparation failed' } }
pwsh -NoProfile -File scripts\rpfm_mcp.ps1 -Action build
if ($LASTEXITCODE -ne 0) { throw 'Pack build failed' }
pwsh -NoProfile -File scripts\rpfm_mcp.ps1 -Action validate
if ($LASTEXITCODE -ne 0) { throw 'Pack validation failed' }
python scripts\validate_offline.py
if ($LASTEXITCODE -ne 0) { throw 'Offline validation failed' }
python -m unittest discover -s tests -p 'test_*.py'
if ($LASTEXITCODE -ne 0) { throw 'Offline regression tests failed' }
