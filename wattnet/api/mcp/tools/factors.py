"""Factors tools."""

from wattnet.api.mcp.spec import ToolSpec
from wattnet.api.rest.v1.factors import get_factors

TOOLS = [ToolSpec("get_factors", get_factors, "factors")]
