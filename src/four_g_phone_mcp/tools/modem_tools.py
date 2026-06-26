"""4G USB modem tools — portmanteau pattern."""

from __future__ import annotations

import os
from typing import Any

from fastmcp import Context

from four_g_phone_mcp.balong_client import BalongClient, _signal_strength_bars


def _get_client(ctx: Context) -> BalongClient:
    host = os.environ.get("BALONG_HOST", "192.168.8.1")
    port = int(os.environ.get("BALONG_PORT", "80"))
    timeout = float(os.environ.get("BALONG_TIMEOUT", "5"))
    return BalongClient(host=host, port=port, timeout=timeout)


async def modem_phone(
    operation: str,
    ctx: Context = None,
    phone: str = "",
    message: str = "",
    sms_index: int = 0,
    net_mode: str = "auto",
) -> dict[str, Any]:
    """Unified control for a Huawei Balong 4G USB modem.

    [RATIONALE] Consolidates all modem operations (status, SMS, network,
    admin reboot) into one portmanteau tool so agents don't need 8 separate
    tool definitions for a simple USB device.

    Operations:
    - status: Full modem status — signal strength, network type, operator, traffic
    - signal: Signal metrics (RSRP, RSRQ, SINR, RSSI bars)
    - sms_list: List SMS inbox messages
    - sms_send: Send an SMS (requires phone=+43xxx, message=...)
    - sms_delete: Delete an SMS by index
    - reboot: Power-cycle the modem
    - net_mode: Set network mode (auto / 4g / 3g / 2g)

    ## Return Format
    {"success": bool, "message": str, "data": {...}}

    ## Examples
    modem_phone(operation="status")
    modem_phone(operation="sms_send", phone="+436641234567", message="Hello")
    modem_phone(operation="reboot")
    """
    client = _get_client(ctx)

    if operation == "status":
        try:
            status = await client.full_status()
            return {
                "success": True,
                "message": f"Modem OK — {status['operator']['full_name']} ({status['network']['type']}) "
                f"signal: {status['signal']['bars']}/4 bars",
                "data": status,
            }
        except Exception as e:
            return {"success": False, "message": f"Modem unreachable: {e}", "data": {}}

    if operation == "signal":
        try:
            sig = await client.get_signal()
            plmn = await client.get_plmn()
            return {
                "success": True,
                "message": f"RSRP {sig.rsrp} dBm ({_signal_strength_bars(sig.rsrp)}/4 bars), "
                f"RSRQ {sig.rsrq} dB, SINR {sig.sinr} dB — {plmn.full_name}",
                "data": {
                    "rsrp_dbm": sig.rsrp,
                    "rsrq_db": sig.rsrq,
                    "sinr_db": sig.sinr,
                    "bars": _signal_strength_bars(sig.rsrp),
                    "operator": plmn.full_name,
                    "rat": plmn.rat,
                },
            }
        except Exception as e:
            return {"success": False, "message": f"Signal query failed: {e}", "data": {}}

    if operation == "sms_list":
        try:
            msgs = await client.list_sms()
            return {
                "success": True,
                "message": f"{len(msgs)} SMS messages",
                "data": {"messages": msgs},
            }
        except Exception as e:
            return {"success": False, "message": f"SMS list failed: {e}", "data": {}}

    if operation == "sms_send":
        if not phone or not message:
            return {
                "success": False,
                "message": "Both phone= and message= are required",
                "data": {},
            }
        try:
            ok = await client.send_sms(phone, message)
            return {
                "success": ok,
                "message": "SMS sent" if ok else "SMS send failed",
                "data": {"phone": phone},
            }
        except Exception as e:
            return {"success": False, "message": f"SMS send error: {e}", "data": {}}

    if operation == "sms_delete":
        try:
            ok = await client.delete_sms(sms_index)
            return {
                "success": ok,
                "message": f"SMS {sms_index} deleted" if ok else "Delete failed",
                "data": {"index": sms_index},
            }
        except Exception as e:
            return {"success": False, "message": f"SMS delete error: {e}", "data": {}}

    if operation == "reboot":
        try:
            ok = await client.reboot()
            return {
                "success": ok,
                "message": "Modem rebooting..." if ok else "Reboot command failed",
                "data": {},
            }
        except Exception as e:
            return {"success": False, "message": f"Reboot error: {e}", "data": {}}

    if operation == "net_mode":
        try:
            ok = await client.set_net_mode(net_mode)
            return {
                "success": ok,
                "message": f"Network mode set to {net_mode}" if ok else "Failed to set mode",
                "data": {"mode": net_mode},
            }
        except Exception as e:
            return {"success": False, "message": f"Net mode error: {e}", "data": {}}

    return {
        "success": False,
        "message": f"Unknown operation: {operation}",
        "data": {"valid_operations": [
            "status", "signal", "sms_list", "sms_send",
            "sms_delete", "reboot", "net_mode",
        ]},
    }


async def show_modem_health_card(ctx: Context = None) -> Any:
    """Show a rich Prefab card with live modem status.

    ## Return Format
    PrefabApp card or plain-text fallback.

    ## Examples
    show_modem_health_card()
    """
    client = _get_client(ctx)

    try:
        status = await client.full_status()
    except Exception as e:
        from prefab_ui import PrefabApp
        from prefab_ui.components import Div, Text

        app = PrefabApp(title="4G Modem — Offline")
        app.add(Div())
        app.add(Text(str(e)))
        return {"content": f"Modem unreachable: {e}", "structured_content": app}

    from prefab_ui import PrefabApp
    from prefab_ui.components import Badge, Div, Heading, Row, Text

    app = PrefabApp(title="4G Modem")
    sig = status["signal"]
    net = status["network"]
    op = status["operator"]
    dev = status["device"]

    Heading(f"{dev['name']} — {op['full_name'] or op['short_name']}")
    Div()

    bars = sig["bars"]
    color = "green" if bars >= 3 else "yellow" if bars >= 1 else "red"
    Badge(f"Signal: {sig['rsrp_dbm']} dBm ({bars}/4)", color=color)
    Badge(f"Network: {net['type']}", color="green" if net["status"] == "901" else "gray")
    Div()

    Row(label="Operator", value=op["full_name"] or op["short_name"])
    Row(label="RAT", value=op["rat"])
    Row(label="RSRP", value=f"{sig['rsrp_dbm']} dBm")
    Row(label="RSRQ", value=f"{sig['rsrq_db']} dB")
    Row(label="SINR", value=f"{sig['sinr_db']} dB")
    Row(label="Cell ID", value=sig["cell_id"] or "—")
    Row(label="WAN IP", value=dev["wan_ip"] or "—")
    Row(label="Uptime", value=f"{net['uptime_seconds'] // 60}m {net['uptime_seconds'] % 60}s")
    Row(label="FW", value=dev["firmware"])
    Div()

    Heading("Traffic", level=2)
    tr = status["traffic"]
    Row(label="Session DL", value=f"{tr['current_download_kb'] / 1024:.1f} MB")
    Row(label="Session UL", value=f"{tr['current_upload_kb'] / 1024:.1f} MB")

    text = (
        f"**{dev['name']}** on {op['full_name']} ({net['type']}) — "
        f"Signal {sig['bars']}/4 bars, RSRP {sig['rsrp_dbm']} dBm, "
        f"WAN {dev['wan_ip'] or '—'}"
    )
    return {"content": text, "structured_content": app}
