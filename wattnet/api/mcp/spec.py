"""The description of a tool: which REST handler it offers and under which group."""

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class ToolSpec:
    """A tool of the MCP interface.

    ``group`` is the group of the access policy of the REST endpoint, or None if the
    endpoint is open (the status).
    """

    name: str
    handler: Callable
    group: Optional[str]
