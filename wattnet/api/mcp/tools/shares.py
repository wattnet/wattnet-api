"""Shares metrics tools."""

from wattnet.api.mcp.spec import ToolSpec
from wattnet.api.rest.v1.flow_share import get_flow_share
from wattnet.api.rest.v1.footprint_share import get_footprint_share
from wattnet.api.rest.v1.impact_share import get_impact_share
from wattnet.api.rest.v1.mix_share import get_mix_share

TOOLS = [
    ToolSpec("get_flow_share", get_flow_share, "shares_metrics"),
    ToolSpec("get_mix_share", get_mix_share, "shares_metrics"),
    ToolSpec("get_footprint_share", get_footprint_share, "shares_metrics"),
    ToolSpec("get_impact_share", get_impact_share, "shares_metrics"),
]
