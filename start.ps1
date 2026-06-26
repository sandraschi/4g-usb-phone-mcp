param([switch]$Headless, [switch]$NoBrowser)
$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSCommandPath
$Port = 11072

Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

$env:MCP_PORT = "$Port"
$env:MCP_HOST = "127.0.0.1"

Write-Host "Starting 4g-usb-phone-mcp on port $Port..." -ForegroundColor Cyan
uv run python -m four_g_phone_mcp.main
