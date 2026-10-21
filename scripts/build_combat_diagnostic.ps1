$ErrorActionPreference='Stop'
pwsh -NoProfile -File scripts/build_combined.ps1
if($LASTEXITCODE -ne 0){throw 'Baseline build failed'}
python scripts/apply_combat_diagnostic.py
if($LASTEXITCODE -ne 0){throw 'Diagnostic manifest failed'}
pwsh -NoProfile -File scripts/combined_mcp.ps1 -Action build
if($LASTEXITCODE -ne 0){throw 'Diagnostic pack build failed'}
python scripts/clean_pack_metadata.py build/steel_sakura_combined_test.pack
if($LASTEXITCODE -ne 0){throw 'Diagnostic metadata cleanup failed'}
pwsh -NoProfile -File scripts/combined_mcp.ps1 -Action validate
if($LASTEXITCODE -ne 0){throw 'Diagnostic RPFM reopen failed'}
python scripts/validate_combined.py
if($LASTEXITCODE -ne 0){throw 'Diagnostic references failed'}
