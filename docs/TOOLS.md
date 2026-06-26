# Tool Reference

## modem_phone — Portmanteau Modem Control

All modem operations go through this single portmanteau tool.

### Operations

| operation | Parameters | Description |
|-----------|-----------|-------------|
| `status` | — | Full modem status — device info, signal, network, operator, traffic |
| `signal` | — | Live signal metrics — RSRP, RSRQ, SINR, RSSI bars |
| `sms_list` | — | List SMS inbox messages |
| `sms_send` | `phone`, `message` | Send an SMS (phone must be E.164 format, e.g. +436641234567) |
| `sms_delete` | `sms_index` | Delete an SMS by its index number |
| `reboot` | — | Power-cycle the modem |
| `net_mode` | `net_mode` | Set network mode: `auto`, `4g`, `3g`, `2g` |

### Return Format

```json
{
  "success": true,
  "message": "Modem OK — A1.net (LTE) signal: 3/4 bars",
  "data": { ... }
}
```

### Examples

```
modem_phone(operation="status")
modem_phone(operation="signal")
modem_phone(operation="sms_send", phone="+436641234567", message="Hello from Claude")
modem_phone(operation="sms_list")
modem_phone(operation="sms_delete", sms_index=5)
modem_phone(operation="reboot")
modem_phone(operation="net_mode", net_mode="4g")
```

### Signal Values Reference

| Metric | Good | Marginal | Poor |
|--------|------|----------|------|
| RSRP | > -95 dBm | -95 to -110 dBm | < -110 dBm |
| RSRQ | > -10 dB | -10 to -15 dB | < -15 dB |
| SINR | > 15 dB | 5 to 15 dB | < 5 dB |
| Bars | 3–4 | 1–2 | 0 |

---

## show_modem_health_card — Prefab Status Card

Renders a rich in-chat card with live modem status. Fallback to plain text
in hosts that don't support MCP Apps.

```
show_modem_health_card()
```

Displays: operator name, signal bars, RSRP, RSRQ, SINR, cell ID, WAN IP,
uptime, firmware version, and session traffic counters.
