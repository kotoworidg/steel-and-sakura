param(
    [ValidateSet('list','probe','build','validate','assets','existing-mod','inspect-ui','inspect-air','inspect-modern','build-artillery','validate-artillery','build-modern','validate-modern')][string]$Action = 'list',
    [string]$GameRoot = 'D:\Games\Total War - SHOGUN 2'
)

$ErrorActionPreference = 'Stop'
$endpoint = 'http://127.0.0.1:45127/mcp'
$sessionId = $null
$requestId = 0

function Invoke-Mcp([string]$method, [hashtable]$parameters = @{}) {
    $script:requestId++
    $headers = @{ Accept='application/json, text/event-stream' }
    if ($script:sessionId) { $headers['Mcp-Session-Id'] = $script:sessionId }
    $body = @{ jsonrpc='2.0'; id=$script:requestId; method=$method; params=$parameters } | ConvertTo-Json -Depth 40 -Compress
    $response = Invoke-WebRequest -Uri $endpoint -Method Post -Body $body -ContentType 'application/json' -Headers $headers -TimeoutSec 180
    if ($response.Headers['Mcp-Session-Id']) { $script:sessionId = [string]($response.Headers['Mcp-Session-Id'] | Select-Object -First 1); Write-Host ('MCP session: ' + $script:sessionId) }
    $dataLine = ($response.Content -split "`n" | Where-Object { $_ -like 'data: *' } | Select-Object -Last 1)
    if (!$dataLine) { throw "MCP returned no data: $($response.Content)" }
    $message = $dataLine.Substring(6).Trim() | ConvertFrom-Json -AsHashtable
    if ($message.error) { throw ($message.error | ConvertTo-Json -Depth 10) }
    return $message.result
}

function Invoke-Tool([string]$name, [hashtable]$arguments = @{}) {
    $result = Invoke-Mcp 'tools/call' @{ name=$name; arguments=$arguments }
    if ($result.isError) { throw ($name + ': ' + ($result | ConvertTo-Json -Depth 10)) }
    return $result
}

$null = Invoke-Mcp 'initialize' @{ protocolVersion='2025-03-26'; capabilities=@{}; clientInfo=@{ name='steel-sakura'; version='0.1' } }
if ($Action -eq 'list') {
    $tools = Invoke-Mcp 'tools/list'
    $tools.tools | Where-Object { $_.name -match 'game|pack|schema|file|table|unit|depend' } |
      Select-Object name,description,inputSchema | ConvertTo-Json -Depth 20 |
      Set-Content -LiteralPath 'build\inventory\rpfm_mcp_tools.json' -Encoding utf8
    Write-Output ('Tool count: ' + $tools.tools.Count)
    Write-Output 'Saved tool definitions to build\inventory\rpfm_mcp_tools.json'
} elseif ($Action -eq 'probe') {
    $game = Invoke-Tool 'set_game_selected' @{ game_name='shogun_2'; rebuild_dependencies=$false }
    Write-Output ('GAME=' + ($game | ConvertTo-Json -Depth 12 -Compress))
    $schema = Invoke-Tool 'is_schema_loaded'
    Write-Output ('SCHEMA=' + ($schema | ConvertTo-Json -Depth 8 -Compress))
    foreach ($name in @('data.pack','data_fots.pack')) {
        $path = Join-Path (Join-Path $GameRoot 'data') $name
        $opened = Invoke-Tool 'open_packfiles' @{ paths=@($path) }
        Write-Output ('OPEN_'+$name+'=' + ($opened | ConvertTo-Json -Depth 8 -Compress))
    }
    $packs = Invoke-Tool 'list_open_packs'
    Write-Output ('PACKS=' + ($packs | ConvertTo-Json -Depth 12 -Compress))
    $findings = @{}
    foreach ($folder in @('db')) {
        $files = Invoke-Tool 'get_packed_files_names_starting_with_path_from_all_sources' @{ path=('{"Folder":"'+$folder+'"}') }
        $parsed = $files.content[0].text | ConvertFrom-Json -AsHashtable
        $paths = @($parsed.HashMapDataSourceHashSetContainerPath.PackFile | ForEach-Object { $_.File })
        $findings[$folder] = $paths
        Write-Output ('FILES_'+$folder+' count=' + $paths.Count + ' sample=' + (($paths | Where-Object { $_ -match 'unit|missile|projectile|recruit' } | Select-Object -First 15) -join ', '))
    }
    $findings | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath 'build\inventory\relevant_pack_paths.json' -Encoding utf8
    $packKey = Join-Path (Join-Path $GameRoot 'data') 'data.pack'
    foreach ($table in @('unit_stats_land','units','building_units_allowed','projectiles','gun_type_to_projectiles','units_to_groupings_military_permissions')) {
        $path = @($findings.db | Where-Object { $_ -match ('^db/'+$table+'_tables/') } | Select-Object -First 1)[0]
        if (!$path) { continue }
        $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$packKey; path=$path; source='PackFile' }
        $target = 'build\inventory\table_' + $table + '.json'
        $decoded.content[0].text | Set-Content -LiteralPath $target -Encoding utf8
        Write-Output ('DECODE_'+$table+' error='+$decoded.isError+' chars='+$decoded.content[0].text.Length+' file='+$target)
    }
} elseif ($Action -eq 'build') {
    $null = Invoke-Tool 'set_game_selected' @{ game_name='shogun_2'; rebuild_dependencies=$false }
    $created = Invoke-Tool 'new_pack'
    $pack = $created.content[0].text | ConvertFrom-Json -AsHashtable
    Write-Output ('NEW=' + ($pack | ConvertTo-Json -Depth 5 -Compress))
    $packKey = $pack.String
    if (!$packKey) { throw 'Could not determine new pack key' }
    $null = Invoke-Tool 'set_pack_file_type' @{ pack_key=$packKey; pack_file_type='"Mod"' }
    foreach ($name in @('unit_stats_land','units','building_units_allowed','units_to_groupings_military_permissions')) {
        $source = Get-Content -LiteralPath ('source\infantry\'+$name+'.json') -Raw | ConvertFrom-Json -AsHashtable
        $path = 'db/'+$source.table+'/steel_sakura_infantry'
        $newFile = @{ DB=@('steel_sakura_infantry',$source.table,$source.version) } | ConvertTo-Json -Compress -Depth 5
        $null = Invoke-Tool 'new_packed_file' @{ pack_key=$packKey; path=$path; new_file=$newFile }
        $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$packKey; path=$path; source='PackFile' }
        $wrapper = $decoded.content[0].text | ConvertFrom-Json -AsHashtable
        $table = $wrapper.DBRFileInfo[0].table
        $table.table_data = @(,$source.row)
        $wrapper.DBRFileInfo[0].table = $table
        $modified = @{ DB=$wrapper.DBRFileInfo[0] } | ConvertTo-Json -Depth 70 -Compress
        $saved = Invoke-Tool 'save_packed_file_from_view' @{ pack_key=$packKey; path=$path; data=$modified }
        Write-Output ('TABLE='+$name+' result='+($saved.content[0].text))
    }
    $strings = Get-Content -LiteralPath 'src\infantry_localisation.json' -Raw | ConvertFrom-Json -AsHashtable
    $locPath = 'text/db/steel_sakura_units.loc'
    $null = Invoke-Tool 'new_packed_file' @{ pack_key=$packKey; path=$locPath; new_file='{"Loc":"steel_sakura_units"}' }
    $locDecoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$packKey; path=$locPath; source='PackFile' }
    $locWrapper = $locDecoded.content[0].text | ConvertFrom-Json -AsHashtable
    $locTable = $locWrapper.LocRFileInfo[0].table
    $locTable.table_data = @($strings.entries | ForEach-Object { ,@(@{StringU16=$_.key},@{StringU16=$_.text},@{Boolean=$_.tooltip}) })
    $locWrapper.LocRFileInfo[0].table = $locTable
    $locModified = @{ Loc=$locWrapper.LocRFileInfo[0] } | ConvertTo-Json -Depth 70 -Compress
    $locSaved = Invoke-Tool 'save_packed_file_from_view' @{ pack_key=$packKey; path=$locPath; data=$locModified }
    Write-Output ('LOC=steel_sakura_units result='+($locSaved.content[0].text))
    $assetName = 'steel_sakura_automatic_rifle_squad.tga'
    $assetFolders = @('icons','icons_square','info','recruitment_large','recruitment_small')
    $assetSources = @($assetFolders | ForEach-Object { (Resolve-Path -LiteralPath ('assets\infantry\'+$_+'\'+$assetName)).Path })
    $assetDestinations = @($assetFolders | ForEach-Object { @{ File=('ui/units/'+$_+'/'+$assetName) } }) | ConvertTo-Json -Depth 5 -Compress
    $added = Invoke-Tool 'add_packed_files' @{ pack_key=$packKey; source_paths=$assetSources; destination_paths=$assetDestinations }
    Write-Output ('ICON_FILES='+$assetSources.Count+' result='+($added.content[0].text))
    $output = (Join-Path (Resolve-Path 'build').Path 'steel_sakura_infantry_prototype.pack')
    $savedPack = Invoke-Tool 'save_pack_as' @{ pack_key=$packKey; path=$output }
    Write-Output ('PACK='+$output+' result='+($savedPack.content[0].text))
} elseif ($Action -eq 'validate') {
    $null = Invoke-Tool 'set_game_selected' @{ game_name='shogun_2'; rebuild_dependencies=$false }
    $output = (Resolve-Path 'build\steel_sakura_infantry_prototype.pack').Path
    $opened = Invoke-Tool 'open_packfiles' @{ paths=@($output) }
    $info = ($opened.content[0].text | ConvertFrom-Json -AsHashtable).StringContainerInfo[1]
    if ($info.pfh_version -ne 'PFH3' -or $info.pfh_file_type -ne 'Mod') { throw 'Unexpected pack header' }
    foreach ($name in @('unit_stats_land','units','building_units_allowed','units_to_groupings_military_permissions')) {
        $source = Get-Content -LiteralPath ('source\infantry\'+$name+'.json') -Raw | ConvertFrom-Json -AsHashtable
        $path = 'db/'+$source.table+'/steel_sakura_infantry'
        $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$output; path=$path; source='PackFile' }
        $table = ($decoded.content[0].text | ConvertFrom-Json -AsHashtable).DBRFileInfo[0].table
        if ($table.definition.version -ne $source.version) { throw "Version mismatch: $name" }
        if ($table.table_data.Count -ne 1) { throw "Row count mismatch: $name" }
        if ($table.table_data[0].Count -ne $source.row.Count) { throw "Field count mismatch: $name" }
        for ($cellIndex=0; $cellIndex -lt $source.row.Count; $cellIndex++) {
            $builtCell = $table.table_data[0][$cellIndex] | ConvertTo-Json -Depth 10 -Compress
            $sourceCell = $source.row[$cellIndex] | ConvertTo-Json -Depth 10 -Compress
            if ($builtCell -ne $sourceCell) { throw "Cell mismatch: $name column $cellIndex" }
        }
        Write-Output ('VERIFIED='+$name+' version='+$table.definition.version+' cells='+$table.table_data[0].Count)
        if ($name -eq 'unit_stats_land') {
            $men = $table.table_data[0][$source.fields.IndexOf('men')].I32
            if ($men -ne 40) { throw "Expected 40 men, got $men" }
            Write-Output 'VERIFIED=men 40'
        }
    }
    $locPath = 'text/db/steel_sakura_units.loc'
    $locDecoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$output; path=$locPath; source='PackFile' }
    $locTable = ($locDecoded.content[0].text | ConvertFrom-Json -AsHashtable).LocRFileInfo[0].table
    $expectedLoc = (Get-Content -LiteralPath 'src\infantry_localisation.json' -Raw | ConvertFrom-Json -AsHashtable).entries
    if ($locTable.table_data.Count -ne $expectedLoc.Count) { throw 'Localisation row count mismatch' }
    for ($i=0; $i -lt $expectedLoc.Count; $i++) {
        $row = $locTable.table_data[$i]
        if ($row[0].StringU16 -ne $expectedLoc[$i].key -or $row[1].StringU16 -ne $expectedLoc[$i].text -or $row[2].Boolean -ne $expectedLoc[$i].tooltip) {
            throw "Localisation mismatch at row $i"
        }
    }
    Write-Output ('VERIFIED=localisation rows='+$locTable.table_data.Count)
    $assetName = 'steel_sakura_automatic_rifle_squad.tga'
    $assetFolders = @('icons','icons_square','info','recruitment_large','recruitment_small')
    $assetContainerPaths = @($assetFolders | ForEach-Object { @{ File=('ui/units/'+$_+'/'+$assetName) } })
    $assetMap = @{ PackFile=$assetContainerPaths } | ConvertTo-Json -Depth 5 -Compress
    $verifyDestination = Join-Path (Resolve-Path 'build\validation').Path ('pack-assets-'+[guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $verifyDestination | Out-Null
    $null = Invoke-Tool 'extract_packed_files' @{ pack_key=$output; source_paths=$assetMap; destination_path=$verifyDestination; export_as_tsv=$false }
    foreach ($folder in $assetFolders) {
        $sourceFile = (Resolve-Path -LiteralPath ('assets\infantry\'+$folder+'\'+$assetName)).Path
        $extractedFile = Join-Path $verifyDestination ('ui\units\'+$folder+'\'+$assetName)
        if (!(Test-Path -LiteralPath $extractedFile)) { throw "Missing packed icon: $folder" }
        $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourceFile).Hash
        $extractedHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $extractedFile).Hash
        if ($sourceHash -ne $extractedHash) { throw "Packed icon differs: $folder" }
    }
    Write-Output ('VERIFIED=icon files '+$assetFolders.Count)
    Write-Output ('VERIFIED=pack '+$output)
} elseif ($Action -in @('build-artillery','build-modern')) {
    $modern = $Action -eq 'build-modern'
    $sourceFolder = if ($modern) { 'source\modern_artillery' } else { 'source\tank' }
    $artifact = if ($modern) { 'steel_sakura_modern_artillery_prototype' } else { 'steel_sakura_artillery_mechanics_test' }
    $null = Invoke-Tool 'set_game_selected' @{ game_name='shogun_2'; rebuild_dependencies=$false }
    $created = Invoke-Tool 'new_pack'
    $packKey = ($created.content[0].text | ConvertFrom-Json -AsHashtable).String
    if (!$packKey) { throw 'Could not determine artillery test pack key' }
    $null = Invoke-Tool 'set_pack_file_type' @{ pack_key=$packKey; pack_file_type='"Mod"' }
    foreach ($file in Get-ChildItem -LiteralPath $sourceFolder -Filter '*.json') {
        $name = $file.BaseName
        $source = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json -AsHashtable
        $path = 'db/'+$source.table+'/'+$artifact
        $newFile = @{ DB=@($artifact,$source.table,$source.version) } | ConvertTo-Json -Compress -Depth 5
        $null = Invoke-Tool 'new_packed_file' @{ pack_key=$packKey; path=$path; new_file=$newFile }
        $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$packKey; path=$path; source='PackFile' }
        $wrapper = $decoded.content[0].text | ConvertFrom-Json -AsHashtable
        $wrapper.DBRFileInfo[0].table.table_data = @(,$source.row)
        $modified = @{ DB=$wrapper.DBRFileInfo[0] } | ConvertTo-Json -Depth 70 -Compress
        $null = Invoke-Tool 'save_packed_file_from_view' @{ pack_key=$packKey; path=$path; data=$modified }
        Write-Output ('ARTILLERY_TEST_TABLE='+$name)
    }
    if ($modern) {
        $strings = Get-Content 'build\modern_localisation.json' -Raw | ConvertFrom-Json -AsHashtable
        $locPath = 'text/db/steel_sakura_modern_artillery.loc'
        $null = Invoke-Tool 'new_packed_file' @{ pack_key=$packKey; path=$locPath; new_file='{"Loc":"steel_sakura_modern_artillery"}' }
        $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$packKey; path=$locPath; source='PackFile' }
        $wrapper = $decoded.content[0].text | ConvertFrom-Json -AsHashtable
        $wrapper.LocRFileInfo[0].table.table_data = @($strings | ForEach-Object { ,@(@{StringU16=$_.key},@{StringU16=$_.text},@{Boolean=$_.tooltip}) })
        $null = Invoke-Tool 'save_packed_file_from_view' @{ pack_key=$packKey; path=$locPath; data=(@{Loc=$wrapper.LocRFileInfo[0]} | ConvertTo-Json -Depth 70 -Compress) }
    }
    $output = (Join-Path (Resolve-Path 'build').Path ($artifact+'.pack'))
    $null = Invoke-Tool 'save_pack_as' @{ pack_key=$packKey; path=$output }
    Write-Output ('ARTILLERY_TEST_PACK='+$output)
} elseif ($Action -in @('validate-artillery','validate-modern')) {
    $modern = $Action -eq 'validate-modern'
    $sourceFolder = if ($modern) { 'source\modern_artillery' } else { 'source\tank' }
    $artifact = if ($modern) { 'steel_sakura_modern_artillery_prototype' } else { 'steel_sakura_artillery_mechanics_test' }
    $null = Invoke-Tool 'set_game_selected' @{ game_name='shogun_2'; rebuild_dependencies=$false }
    $output = (Resolve-Path ('build\'+$artifact+'.pack')).Path
    $opened = Invoke-Tool 'open_packfiles' @{ paths=@($output) }
    $info = ($opened.content[0].text | ConvertFrom-Json -AsHashtable).StringContainerInfo[1]
    if ($info.pfh_version -ne 'PFH3' -or $info.pfh_file_type -ne 'Mod') { throw 'Unexpected artillery test pack header' }
    foreach ($file in Get-ChildItem -LiteralPath $sourceFolder -Filter '*.json') {
        $name = $file.BaseName
        $source = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json -AsHashtable
        $path = 'db/'+$source.table+'/'+$artifact
        $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$output; path=$path; source='PackFile' }
        $table = ($decoded.content[0].text | ConvertFrom-Json -AsHashtable).DBRFileInfo[0].table
        if ($table.definition.version -ne $source.version -or $table.table_data.Count -ne 1 -or $table.table_data[0].Count -ne $source.row.Count) {
            throw "Artillery test table shape mismatch: $name"
        }
        for ($cellIndex=0; $cellIndex -lt $source.row.Count; $cellIndex++) {
            $builtCell = $table.table_data[0][$cellIndex] | ConvertTo-Json -Depth 10 -Compress
            $sourceCell = $source.row[$cellIndex] | ConvertTo-Json -Depth 10 -Compress
            if ($builtCell -ne $sourceCell) { throw "Artillery test cell mismatch: $name column $cellIndex" }
        }
        Write-Output ('VERIFIED_ARTILLERY_TEST='+$name)
    }
    Write-Output ('VERIFIED_ARTILLERY_TEST_PACK='+$output)
    if ($modern) {
        $strings = @(Get-Content 'build\modern_localisation.json' -Raw | ConvertFrom-Json -AsHashtable)
        $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$output; path='text/db/steel_sakura_modern_artillery.loc'; source='PackFile' }
        $rows = ($decoded.content[0].text | ConvertFrom-Json -AsHashtable).LocRFileInfo[0].table.table_data
        if ($rows.Count -ne $strings.Count) { throw 'Modern localisation count mismatch' }
        for ($i=0; $i -lt $strings.Count; $i++) {
            if ($rows[$i][0].StringU16 -ne $strings[$i].key -or $rows[$i][1].StringU16 -ne $strings[$i].text -or $rows[$i][2].Boolean -ne $strings[$i].tooltip) {
                throw "Modern localisation mismatch: $i"
            }
        }
        New-Item -ItemType Directory -Force 'build\validation' | Out-Null
        @{ status='VERIFIED_OFFLINE_ONLY'; pack_sha256=(Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash; runtime_tested=$false; tables=10 } | ConvertTo-Json | Set-Content 'build\validation\modern-artillery-report.json' -Encoding utf8
    }
} elseif ($Action -eq 'assets') {
    $null = Invoke-Tool 'set_game_selected' @{ game_name='shogun_2'; rebuild_dependencies=$false }
    foreach ($name in @('models.pack','models2.pack')) {
        $path = Join-Path (Join-Path $GameRoot 'data') $name
        $null = Invoke-Tool 'open_packfiles' @{ paths=@($path) }
    }
    $result = Invoke-Tool 'get_packed_files_names_starting_with_path_from_all_sources' @{ path='{"Folder":""}' }
    $parsed = $result.content[0].text | ConvertFrom-Json -AsHashtable
    $paths = @($parsed.HashMapDataSourceHashSetContainerPath.PackFile | ForEach-Object { $_.File })
    $matches = @($paths | Where-Object { $_ -match 'aircraft|a6m|zero|aeroplane|airplane|biplane|balloon|flying|flight|bird|wing|airship|tank|armstrong|gatling|gun_train' } | Sort-Object)
    $matches | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath 'build\inventory\asset_path_matches.json' -Encoding utf8
    Write-Output ('ASSET_PATHS='+$paths.Count+' MATCHES='+$matches.Count)
    $matches | Select-Object -First 60
} elseif ($Action -eq 'inspect-modern') {
    $null = Invoke-Tool 'set_game_selected' @{ game_name='shogun_2'; rebuild_dependencies=$false }
    $data = Join-Path (Join-Path $GameRoot 'data') 'data.pack'
    $null = Invoke-Tool 'open_packfiles' @{ paths=@($data) }
    foreach ($name in @('gun_types','gun_type_to_projectiles','projectiles_explosions','unit_abilities','unit_special_abilities','unit_to_unit_abilities_junctions','uniforms')) {
        $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$data; path=('db/'+$name+'_tables/'+$name); source='PackFile' }
        $decoded.content[0].text | Set-Content -LiteralPath ('build\inventory\table_'+$name+'.json') -Encoding utf8
        Write-Output ('DECODE='+$name+' chars='+$decoded.content[0].text.Length)
    }
    $loc = Join-Path (Join-Path $GameRoot 'data') 'local_en.pack'
    $null = Invoke-Tool 'open_packfiles' @{ paths=@($loc) }
    $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$loc; path='text/db/unit_abilities.loc'; source='PackFile' }
    $decoded.content[0].text | Set-Content 'build\inventory\loc_unit_abilities.json' -Encoding utf8
    $mod = Join-Path (Join-Path $GameRoot 'data\MyMods') 'mods_modern_units_otomo.pack'
    if (Test-Path -LiteralPath $mod) {
        $null = Invoke-Tool 'open_packfiles' @{ paths=@($mod) }
        foreach ($name in @('gun_types','gun_type_to_projectiles','projectiles','projectiles_explosions','uniforms','unit_abilities','unit_special_abilities','unit_to_unit_abilities_junctions')) {
            $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$mod; path=('db/'+$name+'_tables/'+$name); source='PackFile' }
            $decoded.content[0].text | Set-Content ('build\inventory\existing_mod_'+$name+'.json') -Encoding utf8
        }
    }
} elseif ($Action -eq 'inspect-air') {
    $null = Invoke-Tool 'set_game_selected' @{ game_name='shogun_2'; rebuild_dependencies=$false }
    $data = Join-Path (Join-Path $GameRoot 'data') 'data.pack'
    $null = Invoke-Tool 'open_packfiles' @{ paths=@($data) }
    $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$data; path='db/battle_entities_tables/battle_entities'; source='PackFile' }
    $decoded.content[0].text | Set-Content -LiteralPath 'build\inventory\table_battle_entities.json' -Encoding utf8
    Write-Output ('DECODE=battle_entities chars='+$decoded.content[0].text.Length)
} elseif ($Action -eq 'inspect-ui') {
    $null = Invoke-Tool 'set_game_selected' @{ game_name='shogun_2'; rebuild_dependencies=$false }
    $data = Join-Path (Join-Path $GameRoot 'data') 'data.pack'
    $loc = Join-Path (Join-Path $GameRoot 'data') 'local_en.pack'
    $null = Invoke-Tool 'open_packfiles' @{ paths=@($data) }
    $paths = @(
        'db/battle_type_unit_to_faction_presets_tables/battle_type_unit_to_faction_presets',
        'db/battle_type_faction_presets_tables/battle_type_faction_presets'
    )
    foreach ($path in $paths) {
        $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$data; path=$path; source='PackFile' }
        $name = ($path -split '/')[1] -replace '_tables$',''
        $decoded.content[0].text | Set-Content -LiteralPath ('build\inventory\table_'+$name+'.json') -Encoding utf8
        Write-Output ('DECODE='+$name+' chars='+$decoded.content[0].text.Length)
    }
    $null = Invoke-Tool 'open_packfiles' @{ paths=@($loc) }
    $locDecoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$loc; path='text/db/units.loc'; source='PackFile' }
    $locDecoded.content[0].text | Set-Content -LiteralPath 'build\inventory\loc_units.json' -Encoding utf8
    Write-Output ('DECODE=units.loc chars='+$locDecoded.content[0].text.Length)
    $descriptionDecoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$loc; path='text/db/unit_description_texts.loc'; source='PackFile' }
    $descriptionDecoded.content[0].text | Set-Content -LiteralPath 'build\inventory\loc_unit_description_texts.json' -Encoding utf8
    Write-Output ('DECODE=unit_description_texts.loc chars='+$descriptionDecoded.content[0].text.Length)
    $samplePaths = @('icons_square','icons','info','recruitment_large','recruitment_small') | ForEach-Object {
        @{ File=('ui/units/'+$_+'/ashigaru_inf_matchlock_ashigaru.tga') }
    }
    $sampleSource = @{ PackFile=$samplePaths } | ConvertTo-Json -Depth 5 -Compress
    $sampleTarget = (Join-Path (Resolve-Path 'build\inventory').Path 'sample-icon')
    New-Item -ItemType Directory -Force -Path $sampleTarget | Out-Null
    $extracted = Invoke-Tool 'extract_packed_files' @{ pack_key=$data; source_paths=$sampleSource; destination_path=$sampleTarget; export_as_tsv=$false }
    Write-Output ('EXTRACT_SAMPLE_ICON=' + ($extracted.content[0].text))
    $result = Invoke-Tool 'get_packed_files_names_starting_with_path_from_all_sources' @{ path='{"Folder":""}' }
    $parsed = $result.content[0].text | ConvertFrom-Json -AsHashtable
    $paths = @($parsed.HashMapDataSourceHashSetContainerPath.PackFile | ForEach-Object { $_.File })
    $paths | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath 'build\inventory\all_data_local_paths.json' -Encoding utf8
    $matches = @($paths | Where-Object { $_ -match '(^text/|^ui/|\.loc$|unit_card|unit_icon|unit_info)' } | Sort-Object)
    $matches | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath 'build\inventory\ui_localisation_paths.json' -Encoding utf8
    Write-Output ('UI_LOCALISATION_PATHS='+$matches.Count)
    $matches | Select-Object -First 80
} else {
    $null = Invoke-Tool 'set_game_selected' @{ game_name='shogun_2'; rebuild_dependencies=$false }
    $mod = Join-Path (Join-Path $GameRoot 'data\MyMods') 'mods_modern_units_otomo.pack'
    $null = Invoke-Tool 'open_packfiles' @{ paths=@($mod) }
    $result = Invoke-Tool 'get_packed_files_names_starting_with_path_from_all_sources' @{ path='{"Folder":"db"}' }
    $parsed = $result.content[0].text | ConvertFrom-Json -AsHashtable
    $paths = @($parsed.HashMapDataSourceHashSetContainerPath.PackFile | ForEach-Object { $_.File })
    $paths | Sort-Object | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath 'build\inventory\existing_mod_paths.json' -Encoding utf8
    Write-Output ('EXISTING_MOD_DB_FILES='+$paths.Count)
    $paths | Where-Object { $_ -match 'units_tables|unit_stats_land_tables|building_units_allowed_tables' }
    foreach ($name in @('units','unit_stats_land','building_units_allowed')) {
        $path = @($paths | Where-Object { $_ -match ('^db/'+$name+'_tables/') } | Select-Object -First 1)[0]
        if (!$path) { continue }
        $decoded = Invoke-Tool 'decode_packed_file' @{ pack_key=$mod; path=$path; source='PackFile' }
        $decoded.content[0].text | Set-Content -LiteralPath ('build\inventory\existing_mod_'+$name+'.json') -Encoding utf8
    }
}
