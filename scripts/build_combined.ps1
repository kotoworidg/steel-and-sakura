$ErrorActionPreference='Stop'
pwsh -NoProfile -File scripts/build.ps1
if($LASTEXITCODE -ne 0){throw 'Infantry build failed'}
pwsh -NoProfile -File scripts/build.ps1 -ModernArtillery
if($LASTEXITCODE -ne 0){throw 'Artillery build failed'}
foreach($action in @('inspect','assets')) {
 pwsh -NoProfile -File scripts/combined_mcp.ps1 -Action $action
 if($LASTEXITCODE -ne 0){throw "Combined $action failed"}
}
python scripts/prepare_combined.py
if($LASTEXITCODE -ne 0){throw 'Combined preparation failed'}
pwsh -NoProfile -File scripts/combined_mcp.ps1 -Action build
if($LASTEXITCODE -ne 0){throw 'Combined build failed'}
python scripts/clean_pack_metadata.py build/steel_sakura_combined_test.pack
if($LASTEXITCODE -ne 0){throw 'Combined metadata cleanup failed'}
pwsh -NoProfile -File scripts/combined_mcp.ps1 -Action validate
if($LASTEXITCODE -ne 0){throw 'Combined reopen failed'}
python scripts/validate_combined.py
if($LASTEXITCODE -ne 0){throw 'Combined reference validation failed'}
