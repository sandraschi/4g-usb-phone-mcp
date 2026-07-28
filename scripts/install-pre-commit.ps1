$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

uv sync --group dev
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
uv run pre-commit install
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
uv run pre-commit run --all-files
exit $LASTEXITCODE
