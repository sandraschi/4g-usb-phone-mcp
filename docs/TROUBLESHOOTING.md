# Troubleshooting

## "Modem unreachable" error
**Cause**: Modem not plugged in, not booted, or on a different IP
**Fix**: Verify the LED is solid green/blue. Check `ping 192.168.8.1`. If
the modem uses a different IP (e.g. 192.168.1.1 on some carrier firmware),
set `BALONG_HOST` in env vars.

## Can't reach 192.168.8.1 in browser
**Cause**: RNDIS/CDC ECM driver not loaded, or modem in stick mode
**Fix**: On Windows, check Network Adapters for "Remote NDIS Compatible
Device". On macOS, check System Settings > Network for "Huawei Mobile".
On Linux, run `ip a` and look for a new interface. If the modem has no LED
activity, try a different USB port or cable.

## SMS not sent / "SMS send failed"
**Cause**: Modem SMS buffer full, or SIM does not support SMS, or APN
missing SMS configuration
**Fix**: Delete old SMS with `modem_phone(operation="sms_list")` then
`modem_phone(operation="sms_delete", sms_index=...)`. Verify the SIM
can send SMS by putting it in a phone first.

## Very slow speed (below 10 Mbps)
**Cause**: Poor signal, wrong LTE band, or carrier congestion
**Fix**: Run `modem_phone(operation="signal")`. If RSRP < -110 dBm,
reposition the modem (USB extension cable, move near a window). Try
`modem_phone(operation="net_mode", net_mode="4g")` to prevent 3G fallback.

## Modem locks up after reboot
**Cause**: Some firmware versions have a known issue with rapid reboot cycles
**Fix**: Wait 60 seconds between reboots. Unplug USB for 10s to cold-boot.

## Server doesn't appear in Claude Desktop
**Cause**: Config JSON is malformed, or path contains spaces
**Fix**: Validate at jsonlint.com. Wrap paths in quotes. Ensure `uv` is in
PATH (run `uv --version` from a terminal to verify).

## "command not found: uv"
**Cause**: uv not installed or not in PATH
**Fix**: `winget install astral-sh.uv` then restart terminal/Claude Desktop.

## Modem shows "no service" / no operator name
**Cause**: SIM not inserted, SIM locked, or no coverage on that LTE band
**Fix**: Check SIM is inserted correctly. If carrier-locked, unlock the
modem (see llms-full.txt for unlocking tools). Verify your carrier's LTE
bands match the modem SKU.
