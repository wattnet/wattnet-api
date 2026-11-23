"""The tools, by domain; each module lists the REST handlers it offers."""

from wattnet.api.mcp.spec import ToolSpec
from wattnet.api.mcp.tools import (
    energy,
    environmental,
    factors,
    shares,
    status,
    zones,
)

ALL_TOOLS: list[ToolSpec] = [
    *zones.TOOLS,
    *energy.TOOLS,
    *environmental.TOOLS,
    *shares.TOOLS,
    *factors.TOOLS,
    *status.TOOLS,
]
