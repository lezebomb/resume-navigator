param(
    [switch]$WhatIfOnly = $true
)

$targets = @(
    ".tmp",
    "scraper/browser_profile",
    "scraper/dp_profile",
    "__pycache__",
    "apps/web/__pycache__",
    "backend/__pycache__",
    "tests/__pycache__"
)

Write-Host "Cleanup targets:"
foreach ($target in $targets) {
    $resolved = Join-Path $PSScriptRoot "..\$target"
    $path = [System.IO.Path]::GetFullPath($resolved)
    if (Test-Path -LiteralPath $path) {
        Write-Host " - $path"
        if (-not $WhatIfOnly) {
            Remove-Item -LiteralPath $path -Recurse -Force
        }
    }
}

if ($WhatIfOnly) {
    Write-Host ""
    Write-Host "Dry run only. Re-run with:"
    Write-Host ".\scripts\cleanup_local_artifacts.ps1 -WhatIfOnly:`$false"
}
