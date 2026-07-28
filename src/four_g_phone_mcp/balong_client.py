"""HTTP client for Huawei Balong LTE modems (E3372/E8372).

The Balong API is exposed at 192.168.8.1 by default.  Every state-changing
request requires a session token from /api/webserver/SesTokInfo.
"""

from __future__ import annotations

import asyncio
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC
from typing import Any

import httpx

BALONG_DEFAULT_HOST = "192.168.8.1"
BALONG_DEFAULT_PORT = 80

SESTOK_PATH = "/api/webserver/SesTokInfo"
DEVICE_INFO_PATH = "/api/device/information"
DEVICE_SIGNAL_PATH = "/api/device/signal"
MONITOR_STATUS_PATH = "/api/monitoring/status"
MONITOR_TRAFFIC_PATH = "/api/monitoring/traffic-statistics"
SMS_LIST_PATH = "/api/sms/sms-list"
SMS_SEND_PATH = "/api/sms/send-sms"
SMS_DELETE_PATH = "/api/sms/delete-sms"
NET_PLMN_PATH = "/api/net/current-plmn"
NET_MODE_PATH = "/api/net/net-mode"
DIALUP_PATH = "/api/dialup/modem"
DEVICE_REBOOT_PATH = "/api/device/control"


@dataclass
class ModemInfo:
    device_name: str = ""
    serial: str = ""
    imei: str = ""
    imsi: str = ""
    firmware_version: str = ""
    hardware_version: str = ""
    wan_ip: str = ""
    primary_dns: str = ""
    secondary_dns: str = ""


@dataclass
class SignalInfo:
    rssi: int = 0
    rscp: int = 0
    rsrp: int = -140
    rsrq: int = -20
    sinr: int = -20
    mode: str = "unknown"
    cell_id: str = ""
    pci: str = ""
    plmn: str = ""

    @property
    def rssi_dbm(self) -> int:
        """Convert RSSI LTE value to dBm.  0..31 → -51..-113 dBm."""
        v = self.rssi
        if v == 99:
            return -140
        return -113 + (2 * v)


@dataclass
class NetworkStatus:
    connection_status: str = "disconnected"
    network_type: str = "none"
    roaming: bool = False
    uptime_seconds: int = 0


@dataclass
class PlmnInfo:
    full_name: str = ""
    short_name: str = ""
    numeric: str = ""
    rat: str = ""


def _parse_xml(text: str) -> dict[str, str]:
    """Parse a simple Huawei-Balong XML response into a flat dict."""
    result: dict[str, str] = {}
    try:
        root = ET.fromstring(text)
        for child in root:
            if child.text is not None:
                result[child.tag] = child.text.strip()
    except ET.ParseError:
        pass
    return result


def _signal_strength_bars(rsrp: int) -> int:
    if rsrp >= -85:
        return 4
    if rsrp >= -95:
        return 3
    if rsrp >= -105:
        return 2
    if rsrp >= -115:
        return 1
    return 0


class BalongClient:
    """Low-level HTTP client for the Huawei Balong LTE API."""

    def __init__(
        self,
        host: str = BALONG_DEFAULT_HOST,
        port: int = BALONG_DEFAULT_PORT,
        timeout: float = 5.0,
    ) -> None:
        self._base = f"http://{host}:{port}"
        self._timeout = timeout
        self._session_id: str = ""
        self._token: str = ""
        self._lock = asyncio.Lock()

    async def _refresh_ses_token(self, client: httpx.AsyncClient) -> None:
        resp = await client.get(f"{self._base}{SESTOK_PATH}", timeout=self._timeout)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        ses = root.findtext("SessionID", "")
        tok = root.findtext("TokInfo", "")
        self._session_id = ses.strip()
        self._token = tok.strip()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        data: str | None = None,
    ) -> dict[str, str]:
        async with self._lock:
            async with httpx.AsyncClient(timeout=self._timeout, verify=False) as client:
                await self._refresh_ses_token(client)
                headers = {
                    "X-Requested-With": "XMLHttpRequest",
                    "Cookie": f"SessionID={self._session_id}",
                }
                if data is not None:
                    headers["Content-Type"] = "application/xml"
                resp = await client.request(
                    method,
                    f"{self._base}{path}",
                    headers=headers,
                    content=data,
                )
                resp.raise_for_status()
                return _parse_xml(resp.text)

    async def _get(self, path: str) -> dict[str, str]:
        return await self._request("GET", path)

    async def _post(self, path: str, data: str) -> dict[str, str]:
        return await self._request("POST", path, data=data)

    async def get_device_info(self) -> ModemInfo:
        raw = await self._get(DEVICE_INFO_PATH)
        return ModemInfo(
            device_name=raw.get("DeviceName", ""),
            serial=raw.get("SerialNumber", ""),
            imei=raw.get("Imei", ""),
            imsi=raw.get("Imsi", ""),
            firmware_version=raw.get("SoftwareVersion", ""),
            hardware_version=raw.get("HardwareVersion", ""),
            wan_ip=raw.get("WanIPAddress", ""),
            primary_dns=raw.get("PrimaryDns", ""),
            secondary_dns=raw.get("SecondaryDns", ""),
        )

    async def get_signal(self) -> SignalInfo:
        raw = await self._get(DEVICE_SIGNAL_PATH)
        return SignalInfo(
            rssi=int(raw.get("rssi", "99")),
            rscp=int(raw.get("rscp", "-140")),
            rsrp=int(raw.get("rsrp", "-140")),
            rsrq=int(raw.get("rsrq", "-20")),
            sinr=int(raw.get("sinr", "-20")),
            mode=raw.get("mode", "unknown"),
            cell_id=raw.get("cell_id", ""),
            pci=raw.get("pci", ""),
        )

    async def get_network_status(self) -> NetworkStatus:
        raw = await self._get(MONITOR_STATUS_PATH)
        return NetworkStatus(
            connection_status=raw.get("ConnectionStatus", "disconnected"),
            network_type=raw.get("CurrentNetworkType", "none"),
            roaming=raw.get("RoamingStatus", "0") == "1",
            uptime_seconds=int(raw.get("TotalConnectTime", "0")),
        )

    async def get_plmn(self) -> PlmnInfo:
        raw = await self._get(NET_PLMN_PATH)
        return PlmnInfo(
            full_name=raw.get("FullName", ""),
            short_name=raw.get("ShortName", ""),
            numeric=raw.get("Numeric", ""),
            rat=raw.get("Rat", ""),
        )

    async def get_traffic(self) -> dict[str, int]:
        raw = await self._get(MONITOR_TRAFFIC_PATH)
        return {
            "current_upload_kb": int(raw.get("CurrentUpload", "0")),
            "current_download_kb": int(raw.get("CurrentDownload", "0")),
            "total_upload_mb": int(raw.get("TotalUpload", "0")),
            "total_download_mb": int(raw.get("TotalDownload", "0")),
        }

    async def list_sms(
        self, page: int = 1, page_size: int = 20, unread_only: bool = False
    ) -> list[dict[str, str]]:
        xml = (
            f"<request>"
            f"  <PageIndex>{page}</PageIndex>"
            f"  <ReadCount>{page_size}</ReadCount>"
            f"  <BoxType>1</BoxType>"
            f"  <SortType>0</SortType>"
            f"  <Ascending>0</Ascending>"
            f"  <UnreadPreferred>{int(unread_only)}</UnreadPreferred>"
            f"</request>"
        )
        raw = await self._post(SMS_LIST_PATH, xml)
        messages: list[dict[str, str]] = []
        for _child_name in ("Message",):
            count = int(raw.get("Count", "0"))
            if count == 0:
                break
        return messages

    async def send_sms(self, phone: str, message: str) -> bool:
        xml = (
            f"<request>"
            f"  <Index>-1</Index>"
            f"  <Phones><Phone>{phone}</Phone></Phones>"
            f"  <Sca></Sca>"
            f"  <Content>{message}</Content>"
            f"  <Length>{len(message)}</Length>"
            f"  <Reserved>1</Reserved>"
            f"  <Date>{self._now_str()}</Date>"
            f"</request>"
        )
        result = await self._post(SMS_SEND_PATH, xml)
        return "OK" in str(result)

    async def delete_sms(self, sms_index: int) -> bool:
        xml = f"<request><Index>{sms_index}</Index></request>"
        result = await self._post(SMS_DELETE_PATH, xml)
        return "OK" in str(result)

    async def reboot(self) -> bool:
        xml = "<request><Control>1</Control></request>"
        result = await self._post(DEVICE_REBOOT_PATH, xml)
        return "OK" in str(result)

    async def set_net_mode(self, mode: str = "auto") -> bool:
        xml = (
            f"<request>"
            f"  <NetworkMode>{mode}</NetworkMode>"
            f"  <NetworkBand>0</NetworkBand>"
            f"  <LTEBand>0</LTEBand>"
            f"</request>"
        )
        result = await self._post(NET_MODE_PATH, xml)
        return "OK" in str(result)

    async def full_status(self) -> dict[str, Any]:
        info, signal, net, plmn, traffic = await asyncio.gather(
            self.get_device_info(),
            self.get_signal(),
            self.get_network_status(),
            self.get_plmn(),
            self.get_traffic(),
        )
        return {
            "device": {
                "name": info.device_name,
                "serial": info.serial,
                "imei": info.imei,
                "firmware": info.firmware_version,
                "wan_ip": info.wan_ip,
            },
            "signal": {
                "rsrp_dbm": signal.rsrp,
                "rsrq_db": signal.rsrq,
                "sinr_db": signal.sinr,
                "rssi_dbm": signal.rssi_dbm,
                "bars": _signal_strength_bars(signal.rsrp),
                "cell_id": signal.cell_id,
                "pci": signal.pci,
            },
            "network": {
                "status": net.connection_status,
                "type": net.network_type,
                "roaming": net.roaming,
                "uptime_seconds": net.uptime_seconds,
            },
            "operator": {
                "full_name": plmn.full_name,
                "short_name": plmn.short_name,
                "rat": plmn.rat,
            },
            "traffic": traffic,
        }

    @staticmethod
    def _now_str() -> str:
        from datetime import datetime

        return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
