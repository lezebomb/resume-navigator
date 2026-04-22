Write-Host "== Resume Navigator publish readiness check ==" -ForegroundColor Cyan

Write-Host ""
Write-Host "[1] Git repository status" -ForegroundColor Yellow
git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not inside a git repository." -ForegroundColor Red
} else {
    Write-Host "Git repository detected." -ForegroundColor Green
}

Write-Host ""
Write-Host "[2] Git remote" -ForegroundColor Yellow
$remote = git remote -v
if ($remote) {
    $remote
} else {
    Write-Host "No remote configured yet." -ForegroundColor Red
}

Write-Host ""
Write-Host "[3] Git user config" -ForegroundColor Yellow
$gitName = git config --get user.name
$gitEmail = git config --get user.email
if ($gitName) {
    Write-Host "user.name  = $gitName" -ForegroundColor Green
} else {
    Write-Host "user.name is not configured." -ForegroundColor Red
}
if ($gitEmail) {
    Write-Host "user.email = $gitEmail" -ForegroundColor Green
} else {
    Write-Host "user.email is not configured." -ForegroundColor Red
}

Write-Host ""
Write-Host "[4] GitHub CLI" -ForegroundColor Yellow
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    Write-Host "gh found at $($gh.Source)" -ForegroundColor Green
    gh auth status
} else {
    Write-Host "gh is not installed." -ForegroundColor Red
    Write-Host "Install from: https://cli.github.com/"
}

Write-Host ""
Write-Host "[5] Working tree status" -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "Check complete." -ForegroundColor Cyan
