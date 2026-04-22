param(
    [string]$PythonPath = "C:\Users\24981\AppData\Local\Programs\Python\Python312\python.exe",
    [string]$ResumePath = "",
    [string]$JdFile = "",
    [string]$OutputPath = "data\runtime\validation_result.json"
)

Write-Host "== Step 1: Running unit tests ==" -ForegroundColor Cyan
& $PythonPath -m unittest discover -s tests -p "test_*.py"
if ($LASTEXITCODE -ne 0) {
    throw "Unit tests failed."
}

Write-Host ""
Write-Host "== Step 2: Checking web entrypoint import ==" -ForegroundColor Cyan
& $PythonPath -c "from apps.web.main import app; print(app.title)"
if ($LASTEXITCODE -ne 0) {
    throw "FastAPI import smoke test failed."
}

if ($ResumePath -and $JdFile) {
    Write-Host ""
    Write-Host "== Step 3: Running local deterministic analysis ==" -ForegroundColor Cyan
    & $PythonPath scripts\run_local_analysis.py --resume $ResumePath --jd-file $JdFile --output $OutputPath
    if ($LASTEXITCODE -ne 0) {
        throw "Local analysis run failed."
    }
    Write-Host "Analysis result saved to $OutputPath" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "== Step 3 skipped ==" -ForegroundColor Yellow
    Write-Host "Provide -ResumePath and -JdFile if you want a real-file analysis smoke test."
}

Write-Host ""
Write-Host "Validation finished." -ForegroundColor Green
