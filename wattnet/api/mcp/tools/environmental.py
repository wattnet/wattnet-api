"""Environmental metrics tools."""

from wattnet.api.mcp.spec import ToolSpec
from wattnet.api.rest.v1.footprints import get_footprints
from wattnet.api.rest.v1.impacts import get_impacts
from wattnet.api.rest.v1.scores import get_scores

TOOLS = [
    ToolSpec("get_footprints", get_footprints, "environmental_metrics"),
    ToolSpec("get_impacts", get_impacts, "environmental_metrics"),
    ToolSpec("get_environmental_score", get_scores, "environmental_metrics"),
]
