"""Zones tools."""

from wattnet.api.mcp.spec import ToolSpec
from wattnet.api.rest.v1.zones import get_zones

TOOLS = [ToolSpec("list_zones", get_zones, "zones")]
