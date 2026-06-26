default: serve

# Run in stdio mode (Claude Desktop)
serve:
    uv run python -m four_g_phone_mcp.main

# Run in HTTP/SSE mode on port 11072
serve-http:
    uv run python -m four_g_phone_mcp.main

# Type-check
check:
    uv run python -c "import four_g_phone_mcp; print('OK')"

# Lint
lint:
    uv run ruff check src/

# Format
fmt:
    uv run ruff format src/
