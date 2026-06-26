# Configuration

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BALONG_HOST` | `192.168.8.1` | IP address of the Huawei modem |
| `BALONG_PORT` | `80` | HTTP port of the modem web interface |
| `BALONG_TIMEOUT` | `5` | HTTP request timeout in seconds |
| `MCP_PORT` | — | Set to `11072` for SSE/HTTP mode (omit for stdio) |
| `MCP_HOST` | `127.0.0.1` | Bind address for SSE mode |

## Setting Variables

In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "4g-phone": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\4g-usb-phone-mcp",
               "run", "python", "-m", "four_g_phone_mcp.main"],
      "env": {
        "BALONG_HOST": "192.168.8.1",
        "BALONG_TIMEOUT": "10"
      }
    }
  }
}
```

## Modem Defaults

The Huawei E3372/E8372 ships with these factory defaults:
- **IP**: 192.168.8.1
- **DHCP range**: 192.168.8.100–200
- **Web UI**: http://192.168.8.1
- **Admin login**: admin / admin (on some firmware versions)
- **USB mode**: HiLink (RNDIS/CDC ECM network adapter)

No configuration changes on the modem are needed for the MCP server to work.
The server talks to the modem's existing HTTP API.
