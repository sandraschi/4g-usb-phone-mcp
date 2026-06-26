# 4g-usb-phone-mcp

Turn a $35 USB LTE dongle into an AI-controllable cellular modem — check
signal, send SMS, reboot, lock bands. No eSIM, no Android, no voice. Just a
raw data pipe with AT-grade telemetry, exposed through MCP.

```
Plug in a Huawei E3372 → talk to it from Claude:
  "what's my signal strength?"
  "send an SMS to +43664..."
  "lock to 4G only"
```

## The Fascinating Part

This is **not a phone**. The Huawei Balong dongle has no eSIM, no Android, no
SIP stack, no headphone jack for calls. It's a $35 USB stick with a 4G modem
inside — the same silicon that shipped in 2015 flagships — giving you genuine
LTE Cat4 (150/50 Mbps) over a USB cable.

The "phone" in the repo name is ironic: it's a data pipe pretending to be a
phone, and that's what makes it useful. Network engineers, field ops people,
and IoT tinkerers get **cellular signal telemetry in AI chat** for the price
of a pizza.

## Features

- Live signal metrics (RSRP, RSRQ, SINR, bars) from the Balong HTTP API
- Send and receive SMS directly from the modem (no cloud gateway)
- Lock network mode (4G-only, 3G-only, auto)
- Reboot the modem remotely
- Rich Prefab health card with operator, cell ID, traffic counters
- All over a $35 USB stick — no SIM reader, no phone, no cloud API key

## Quick Install

```json
{
  "mcpServers": {
    "4g-phone": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\4g-usb-phone-mcp", "run",
               "python", "-m", "four_g_phone_mcp.main"],
      "env": { "PYTHONUNBUFFERED": "1" }
    }
  }
}
```

Plug in the dongle, add this to `claude_desktop_config.json`, restart. Done.

For full install options see [INSTALL.md](INSTALL.md).

## What You Can Do

```
"What's my 4G signal strength?"

"Send an SMS to +436641234567: 'Server room temp is 42C — check it.'"

"Reboot the modem."

"Lock to 4G only — I'm in a fringe area."

"Show me the modem health card."
```

## How it runs

| Mode | Description |
|------|-------------|
| **stdio (Claude Desktop)** | Default — zero config after `uv sync` |
| **SSE (HTTP)** | `$env:MCP_PORT=11072` for remote agents |

The modem is always **headless** — it's a USB stick with no screen. The MCP
server is its control panel.

## Fleet Ecosystem

These repos form a three-layer field-telecom stack:

| Layer | Repo | What it does | Hardware |
|-------|------|-------------|----------|
| **Voice** | [telephony-mcp](https://github.com/sandraschi/telephony-mcp) | PSTN calls via SIP trunk | Asterisk Docker |
| **Data** | **4g-usb-phone-mcp** (you are here) | Signal, SMS, modem control | Huawei E3372 ($35) |
| **RF** | `sdr-mcp` _(planned)_ | Spectrum analysis, private cell | RTL-SDR / HackRF |

- `telephony-mcp` places PSTN voice calls over the LTE link this server provides
- A future `sdr-mcp` will see the raw RF spectrum — diagnosing *why* signal is
  bad, not just *that* it is — for $25 (RTL-SDR v4), the price of a low-end
  field spectrometer.

See `llms-full.txt` for detailed integration scenarios covering all three layers.

## Documentation

| Doc | Contents |
|-----|----------|
| [Installation](INSTALL.md) | All install methods, prerequisites |
| [Configuration](docs/CONFIGURATION.md) | Env vars (BALONG_HOST, etc.) |
| [Tool Reference](docs/TOOLS.md) | Full tool list with examples |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues |
| [Full Reference](llms-full.txt) | Extensive Balong hardware tech doc |

## Requirements

- Python 3.12+ with `uv`
- Huawei E3372 or E8372 USB LTE modem (~$25–55)
- Standard nano-SIM with data plan

## License

MIT
