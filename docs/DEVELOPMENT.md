# Development Setup

## Tools Required

```bash
# Windows (winget)
winget install astral-sh.uv
winget install Git.Git
winget install Casey.Just

# Verify
uv --version
git --version
just --version
```

## Setup

```bash
git clone https://github.com/sandraschi/4g-usb-phone-mcp
cd 4g-usb-phone-mcp
uv sync
```

## Common Tasks

```bash
just serve          # Run in stdio mode
just serve-http     # Run in SSE/HTTP mode on port 11072
just check          # Verify server imports and tools register
```

## Code Standards

- **Tool design**: Portmanteau pattern with `operation` enum (see
  mcp-central-docs/standards/TOOL_DESIGN_STANDARDS.md)
- **Docstrings**: `Annotated` + `Field` for parameter docs, no `Args:` blocks
- **Returns**: Dict with `success`, `message`, `data` keys
- **FastMCP**: 3.4.2 minimum, dual transport (stdio + SSE)

## Project Structure

```
src/four_g_phone_mcp/
├── __init__.py
├── server.py           # FastMCP app definition
├── main.py             # Entry point, dual transport
├── balong_client.py    # Huawei Balong HTTP API client
└── tools/
    ├── __init__.py     # Re-exports for tool registration
    └── modem_tools.py  # Portmanteau tool + Prefab card
```
