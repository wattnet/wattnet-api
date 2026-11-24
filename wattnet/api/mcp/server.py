"""The MCP server: each tool runs a REST handler, so both share every rule.

The tool takes the parameters of the handler (with their descriptions and limits),
applies the access policy of the tier of the request, and calls the handler. Nothing
of the reading is written twice: a change in the handler or in the services reaches
both interfaces.
"""

import functools
import inspect
import json
from typing import Annotated, Any, Callable

from fastapi import HTTPException
from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from wattnet.api import access
from wattnet.api.buildinfo import build_version
from wattnet.api.mcp.spec import ToolSpec
from wattnet.api.mcp.tools import ALL_TOOLS
from wattnet.api.rest.v1 import api_router_v1
from wattnet.api.utils import log

LOG = log.get(__name__)

_INSTRUCTIONS = (
    "Wattnet: electricity data of the zones of the grid (generation, load, imports, "
    "exports, mix), their environmental footprints and impacts, the shares and the "
    "factors. Start with list_zones to know the zone codes. Datetimes are ISO 8601 "
    "in UTC; ask start and end together, or only the latest data is returned."
)


def _error(code: str, detail: str, status: int) -> ToolError:
    return ToolError(json.dumps({"code": code, "detail": detail, "status": status}))


def _tier(ctx: Context) -> str | None:
    """Return the tier that the gate put in the request, if there is one."""
    request = ctx.request_context.request
    return request.headers.get(access.TIER_HEADER) if request is not None else None


def _tool(spec: ToolSpec) -> Callable[..., Any]:
    """Build the function of a tool from the REST handler of the spec."""
    handler = spec.handler
    parameters = []
    for p in inspect.signature(handler).parameters.values():
        q = p.default  # a Query(...): the default, the limits and the description
        field = Field(description=q.description)
        annotation = Annotated[p.annotation, *q.metadata, field]  # type: ignore[name-defined]
        parameters.append(p.replace(annotation=annotation, default=q.default))
    parameters.append(
        inspect.Parameter("ctx", inspect.Parameter.KEYWORD_ONLY, annotation=Context)
    )

    @functools.wraps(handler)
    def run(**kwargs: Any) -> Any:
        ctx = kwargs.pop("ctx")
        asked = {k: v for k, v in kwargs.items() if v is not None}
        try:
            if spec.group is not None:
                access.enforce(spec.group, _tier(ctx), asked)
            return handler(**kwargs)
        except HTTPException as e:  # ApiError too: it keeps its stable code
            raise _error(
                getattr(e, "code", "error"), str(e.detail), e.status_code
            ) from None
        except Exception:
            LOG.exception(f"The tool {spec.name} failed")
            raise _error(
                "internal_error", "The request could not be answered.", 500
            ) from None

    returns = inspect.signature(handler).return_annotation
    run.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
        parameters, return_annotation=returns
    )
    # The SDK finds the Context and the output type through the annotations.
    run.__annotations__ = {p.name: p.annotation for p in parameters}
    run.__annotations__["return"] = returns
    return run


def build_server() -> MCPServer:
    """Return the server with a tool for every spec."""
    # subscriptions=False: the server has nothing to notify, and a client that listens
    # would keep a request open (and one of the concurrent requests of the account) for
    # as long as it stays connected.
    server = MCPServer(
        "Wattnet",
        instructions=_INSTRUCTIONS,
        version=build_version(),
        subscriptions=False,
    )
    routes = {r.endpoint: r for r in api_router_v1.routes if hasattr(r, "endpoint")}
    for spec in ALL_TOOLS:
        route = routes[spec.handler]
        description = (getattr(route, "description", None) or "").strip()
        server.tool(name=spec.name, description=description or None)(_tool(spec))
    return server


mcp_server = build_server()
