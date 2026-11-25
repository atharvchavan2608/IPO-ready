# Archive only the explicitly superseded demo/build paths. Never deletes files.
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$archiveRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot 'archive/legacy-20261022'))
$boundary = $projectRoot.TrimEnd('\') + '\'
if (-not $archiveRoot.StartsWith($boundary, [StringComparison]::OrdinalIgnoreCase)) { throw 'Archive target escapes project' }
$entries = @('app', 'notebooks', 'outputs/poc', 'tests/test_engine.py', 'scripts/build_proposal.py', 'scripts/build_notebook.py', 'scripts/build_demo_snapshot.py', 'scripts/check_demo.cjs', 'survey_builder.mjs', 'verify_survey.py', 'fetch_research_sources.py')
$moves = @()
$files = @()
foreach ($relative in $entries) {
    $source = [IO.Path]::GetFullPath((Join-Path $projectRoot $relative))
    $destination = [IO.Path]::GetFullPath((Join-Path $archiveRoot $relative))
    if (-not $source.StartsWith($boundary, [StringComparison]::OrdinalIgnoreCase) -or -not $destination.StartsWith($archiveRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Move escapes intended workspace' }
    if (-not (Test-Path -LiteralPath $source)) { throw "Source missing: $relative" }
    if (Test-Path -LiteralPath $destination) { throw "Archive target already exists: $relative" }
    $item = Get-Item -LiteralPath $source
    $selectedFiles = if ($item.PSIsContainer) { @(Get-ChildItem -LiteralPath $source -File -Recurse) } else { @($item) }
    foreach ($file in $selectedFiles) {
        if ($file.FullName.Contains('\__pycache__\')) { continue }
        $original = $file.FullName.Substring($boundary.Length).Replace('\', '/')
        $files += [PSCustomObject]@{ original_path = $original; archived_path = 'archive/legacy-20261022/' + $original; sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant(); bytes = $file.Length }
    }
    $moves += [PSCustomObject]@{ Source = $source; Destination = $destination }
}
# All targets are verified before any move. Use native literal-path operations end-to-end.
foreach ($move in $moves) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $move.Destination) | Out-Null
    Move-Item -LiteralPath $move.Source -Destination $move.Destination
}
foreach ($file in $files) {
    $retained = Join-Path $projectRoot $file.archived_path
    if ((Get-FileHash -LiteralPath $retained -Algorithm SHA256).Hash.ToLowerInvariant() -ne $file.sha256) { throw 'Archive hash verification failed' }
}
$manifest = [PSCustomObject]@{ archived_on = '2026-11-12'; reason = 'User requested archiving superseded demo code; research and evidence remain active'; files = $files }
$json = $manifest | ConvertTo-Json -Depth 5
[IO.File]::WriteAllText((Join-Path $archiveRoot 'manifest.json'), $json + "`n", [Text.UTF8Encoding]::new($false))
Write-Output ("Archived and verified {0} files under {1}" -f $files.Count, $archiveRoot)
