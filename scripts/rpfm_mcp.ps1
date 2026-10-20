param(
    [ValidateSet('list','probe','build','validate','assets','existing-mod')][string]$Action = 'list',
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
        Write-Output ('VERIFIED='+$name+' version='+$table.definition.version+' cells='+$table.table_data[0].Count)
        if ($name -eq 'unit_stats_land') {
            $men = $table.table_data[0][$source.fields.IndexOf('men')].I32
            if ($men -ne 40) { throw "Expected 40 men, got $men" }
            Write-Output 'VERIFIED=men 40'
        }
    }
    Write-Output ('VERIFIED=pack '+$output)
} elseif ($Action -eq 'assets') {
    $null = Invoke-Tool 'set_game_selected' @{ game_name='shogun_2'; rebuild_dependencies=$false }
    foreach ($name in @('models.pack','models2.pack')) {
        $path = Join-Path (Join-Path $GameRoot 'data') $name
        $null = Invoke-Tool 'open_packfiles' @{ paths=@($path) }
    }
    $result = Invoke-Tool 'get_packed_files_names_starting_with_path_from_all_sources' @{ path='{"Folder":""}' }
    $parsed = $result.content[0].text | ConvertFrom-Json -AsHashtable
    $paths = @($parsed.HashMapDataSourceHashSetContainerPath.PackFile | ForEach-Object { $_.File })
    $matches = @($paths | Where-Object { $_ -match 'aircraft|a6m|zero|aeroplane|airplane|biplane|balloon|tank|armstrong|gatling|gun_train' } | Sort-Object)
    $matches | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath 'build\inventory\asset_path_matches.json' -Encoding utf8
    Write-Output ('ASSET_PATHS='+$paths.Count+' MATCHES='+$matches.Count)
    $matches | Select-Object -First 60
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
