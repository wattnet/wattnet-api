"""Status tools."""

from wattnet.api.mcp.spec import ToolSpec
from wattnet.api.rest.v1.status import status

TOOLS = [ToolSpec("get_status", status, None)]
