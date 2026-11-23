"""Energy metrics tools."""

from wattnet.api.mcp.spec import ToolSpec
from wattnet.api.rest.v1.exports import get_exports
from wattnet.api.rest.v1.generation import get_generation
from wattnet.api.rest.v1.imports import get_imports
from wattnet.api.rest.v1.load import get_load
from wattnet.api.rest.v1.mix import get_mix

TOOLS = [
    ToolSpec("get_generation", get_generation, "energy_metrics"),
    ToolSpec("get_load", get_load, "energy_metrics"),
    ToolSpec("get_imports", get_imports, "energy_metrics"),
    ToolSpec("get_exports", get_exports, "energy_metrics"),
    ToolSpec("get_mix", get_mix, "energy_metrics"),
]
