# Installing 4g-usb-phone-mcp

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| Claude Desktop | Required MCP host | [download](https://claude.ai/download) |
| Git | Clone repo (Options C/D) | `winget install Git.Git` |
| Python + uv | Run server (Options C/D) | `winget install astral-sh.uv` |
| Huawei E3372/E8372 | LTE modem hardware | See Buying Guide in `llms-full.txt` |

> Windows: all installs via [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)
> macOS: use `brew install uv`
> Linux: use your distro package manager

## Option A — Plug and Play (Recommended)

1. Plug the Huawei E3372/E8372 into a USB port
2. Wait 30s for the modem to boot (the LED turns solid)
3. Verify you can reach http://192.168.8.1 in a browser
4. Clone and configure the server (see Option C for the Claude Desktop JSON)

## Option B — mcpb CLI

Not yet available. Coming in a future release.

## Option C — Manual Configuration

1. Clone the repo:
```bash
git clone https://github.com/sandraschi/4g-usb-phone-mcp
cd 4g-usb-phone-mcp
```

2. Install dependencies:
```bash
uv sync
```

3. Add to Claude Desktop config at `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "4g-phone": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\4g-usb-phone-mcp",
               "run", "python", "-m", "four_g_phone_mcp.main"],
      "env": { "PYTHONUNBUFFERED": "1" }
    }
  }
}
```

4. Restart Claude Desktop

## Option D — Developer Mode

For contributing or running from source with live reload.
See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## SSE Mode (HTTP)

Set `MCP_PORT` to run as an SSE server instead of stdio:

```json
{
  "mcpServers": {
    "4g-phone": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\4g-usb-phone-mcp",
               "run", "python", "-m", "four_g_phone_mcp.main"],
      "env": {
        "MCP_PORT": "11072",
        "MCP_HOST": "127.0.0.1"
      }
    }
  }
}
```

## Verify Installation

After installing, open Claude Desktop and say:

> "Check my modem signal strength"

You should see RSRP, RSRQ, SINR values and a bar indicator. If the modem
is not connected, you'll get "Modem unreachable" — check that the dongle
is plugged in and you can reach http://192.168.8.1.

## Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues.
