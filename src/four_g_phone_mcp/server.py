from fastmcp import FastMCP

from four_g_phone_mcp.tools import modem_phone, show_modem_health_card

mcp = FastMCP(
    "4g-usb-phone-mcp",
    instructions="Huawei Balong 4G USB modem control — signal, SMS, network, admin",
    version="0.1.0",
)

mcp.tool()(modem_phone)
mcp.tool()(show_modem_health_card)
