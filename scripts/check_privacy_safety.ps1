Write-Host "== Resume Navigator privacy safety check ==" -ForegroundColor Cyan

$trackedFiles = git ls-files 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Git tracked files are unavailable. Run this inside the repository." -ForegroundColor Red
    exit 1
}

$trackedRisks = @()
$trackedWarnings = @()
$secretPattern = '(?i)(api[_-]?key|secret|token|password|client_secret)\s*[:=]\s*["''][^"''\s]{8,}'
$binarySuffixes = @('.png', '.jpg', '.jpeg', '.gif', '.pdf', '.doc', '.docx', '.zip', '.db', '.sqlite', '.sqlite3')

foreach ($file in $trackedFiles) {
    $normalized = $file -replace '\\', '/'

    if (($normalized -match '\.env($|\.)' -and $normalized -ne '.env.example') -or
        $normalized -match '\.pdf$' -or
        $normalized -match '\.docx?$' -or
        $normalized -match '^data/(runtime|uploads|exports)/' -or
        $normalized -match '^scraper/(browser_profile|dp_profile|chrome_debug_profile|cookies|data)/') {
        $trackedRisks += $normalized
        continue
    }

    $suffix = [System.IO.Path]::GetExtension($normalized).ToLowerInvariant()
    if ($binarySuffixes -contains $suffix) {
        continue
    }

    if (Test-Path $normalized) {
        $match = Select-String -Path $normalized -Pattern $secretPattern -SimpleMatch:$false -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($match) {
            $trackedWarnings += "${normalized}:$($match.LineNumber)"
        }
    }
}

Write-Host ""
Write-Host "[1] Tracked privacy risks" -ForegroundColor Yellow
if ($trackedRisks.Count -gt 0) {
    $trackedRisks | ForEach-Object { Write-Host "RISK  $_" -ForegroundColor Red }
} else {
    Write-Host "No tracked PDFs/DOCX/.env/runtime/browser-profile paths detected." -ForegroundColor Green
}

Write-Host ""
Write-Host "[2] Potential tracked secret hints" -ForegroundColor Yellow
if ($trackedWarnings.Count -gt 0) {
    $trackedWarnings | ForEach-Object { Write-Host "WARN  $_" -ForegroundColor Yellow }
    Write-Host "Please manually review the lines above before pushing." -ForegroundColor Yellow
} else {
    Write-Host "No obvious secret-pattern hits were detected in tracked text files." -ForegroundColor Green
}

Write-Host ""
Write-Host "[3] Local private files present but ignored" -ForegroundColor Yellow
$localPrivateFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -in @('.pdf', '.doc', '.docx') -or ($_.Name -like '.env*' -and $_.Name -ne '.env.example')
    } |
    Where-Object {
        $_.FullName -notmatch '\\.git\\'
    } |
    Select-Object -First 20

if ($localPrivateFiles) {
    $localPrivateFiles | ForEach-Object {
        Write-Host "LOCAL $_" -ForegroundColor DarkYellow
    }
    Write-Host "These files can stay local as long as they remain ignored and untracked." -ForegroundColor Green
} else {
    Write-Host "No local private office/document/env files were found." -ForegroundColor Green
}

Write-Host ""
Write-Host "Privacy safety check complete." -ForegroundColor Cyan
