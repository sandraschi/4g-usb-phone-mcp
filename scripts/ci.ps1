# Windows-only local CI (same gates as .github/workflows/ci.yml)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "== 4g-usb-phone-mcp CI (Windows) ==" -ForegroundColor Cyan

Write-Host "`n[1/3] uv sync --group dev" -ForegroundColor Yellow
uv sync --group dev
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n[2/3] ruff check + format" -ForegroundColor Yellow
uv run ruff check src
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
uv run ruff format --check src
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n[3/3] pytest (skipped if no tests)" -ForegroundColor Yellow
if (Test-Path "tests") {
  uv run pytest -q --tb=short
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
  Write-Host "No tests directory; skipping pytest." -ForegroundColor DarkGray
}

Write-Host "`nCI passed." -ForegroundColor Green
