"""API for wattnet."""

# Start server with: uvicorn wattnet.api:app --reload
# Open browser to: http://localhost:8000/

# Documentation and tester with Swagger UI: http://localhost:8000/docs
# Documentation with ReDoc: http://localhost:8000/redoc

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator
from urllib.parse import urlparse

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_versioning import VersionedFastAPI
from mcp.server.transport_security import TransportSecuritySettings

from wattnet.api.buildinfo import build_version
from wattnet.api.cache import CacheControlMiddleware
from wattnet.api.errors import install_error_handlers
from wattnet.api.mcp.server import mcp_server
from wattnet.api.rest.v1 import api_router_v1
from wattnet.api.rest.v1.status import check_storage_system
from wattnet.api.settings import settings
from wattnet.api.utils import log

# Get logger
LOG = log.get(__name__)

# Get the directory where this file is located for relative paths
_API_DIR = Path(__file__).parent


def authentication_documentation(developer_portal_url: str | None) -> str:
    """Explain how to get a token, when the deployment names its developer portal.

    :param developer_portal_url: URL of the portal where accounts create their API
        credentials, or None to leave the section out
    :return: Markdown section of the API description, or an empty string
    """
    if not developer_portal_url:
        return ""
    return (
        "### Authentication\n\n"
        "The data endpoints require an OAuth 2.0 access token, sent in the "
        "`Authorization: Bearer <token>` header. To get one, create a free account "
        f"at [{urlparse(developer_portal_url).netloc or developer_portal_url}]"
        f"({developer_portal_url}), create an API credential there and use its "
        "client ID and secret to request a token, as shown in the portal. To try "
        "the endpoints from this page, select **Authorize**, paste the token and "
        "send the requests. Tokens are short-lived: when one expires, request a "
        "new one with the same credential.\n\n"
    )


summary = (
    "A comprehensive RESTful API for integrating wattnet into your applications. "
    "Query real-time, historical, and forecasted electricity footprints, "
    "create dashboards, automate analyses, and extend wattnet’s capabilities. "
    "Fully documented with OpenAPI 3.1."
)

description = (
    '<a href="https://wattnet.eu" target="_blank" '
    'rel="noopener noreferrer">'
    '<img width="200" '
    'src="/static/images/wattnet-logo-full-light-transparent-cropped.png" '
    'alt="Wattnet Logo" '
    'style="margin: 1rem 0;">'
    "</a>\n\n"
    "[![GitHub]"
    "(https://img.shields.io/badge/github.com%2Fwattnet-242424"
    "?style=flat&logo=github&logoColor=white"
    "&labelColor=444444)]"
    "(https://github.com/wattnet) "
    "[![Website]"
    "(https://img.shields.io/badge/wattnet.eu-1D488C"
    "?style=flat&logo=data:image/svg+xml;base64,"
    "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBpZD0id2F0dG5l"
    "dC1pY29uIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjE4"
    "MCAxODAgNjQwIDY0MCI+CiAgPGRlZnM+CiAgICA8c3R5bGU+CiAgICAgIC5jbHMtMSB7CiAg"
    "ICAgICAgZmlsbDogI2ZmZjsKICAgICAgfQogICAgPC9zdHlsZT4KICA8L2RlZnM+CiAgPGcg"
    "aWQ9ImNvbG9yIj4KICAgIDxwYXRoIGlkPSJTdmdqc0cxODUyIiBjbGFzcz0iY2xzLTEiIGQ9"
    "Ik03OTcuODUsNDYwLjg0bC0yLjMyLTIwLjIyaC0xOC41MmMtMTEzLjYyLDAtMTk0LjU5LDI3"
    "LjEyLTI0Ni43Miw3OC45OC0xLjg5LDEuODgtMy41Niw0LjQ0LTUuMzgsNi4zMywxOC4zNCwy"
    "My40OSwzMi4wNiw0OC4wNyw0Mi4zLDczLjM5LDMyLjM3LTQ5Ljg5LDg2Ljg0LTk2LjMxLDE3"
    "My4yNS0xMjEuOTUtOTAuNyw1OC43Mi0xMzMuNjIsMTQ1LjMyLTE1MC4zNSwyMTMuMDUsMy41"
    "LDI3LjM5LDQuNzgsNTYuMDgsNC43OCw4Ni4yNSwwLDIuNi0uMjMsNS4xOC0uNTYsNy43LDQz"
    "Ljg4LTE0LjU4LDg0LjEtMzkuNzgsMTE3LjY5LTczLjIyLDY2LjE4LTY1LjgzLDk3LjUzLTE1"
    "Ny42Niw4NS44NS0yNTAuM1pNNTUzLjM2LDc3Ni42OGMwLTEwMC44NS0xMy45OC0xODQuNzUt"
    "ODYuNjctMjU3LjA4LTUyLjExLTUxLjg2LTEzMS43NS03OC45OC0yNDUuMzctNzguOThoLTE4"
    "LjUybC0yLjMxLDIwLjIyYy0xMS42OSw5Mi42NCwxOS41NSwxODQuNDgsODUuNzEsMjUwLjI5"
    "LDU2LjgsNTYuNTMsMTMyLjM3LDg4LjE2LDIxMi44LDg4LjE2LDEyLjYsMCwyNC4zOS0uNTYs"
    "MzYuODktMi4xMmwxNy40Ni0yLjA3di0xOC40M2gwWk0zMzAuMTEsNjY4LjQzYy00My44OC00"
    "My42NS02OC4yOC0xMDAuMjEtNjkuODctMTYwLjk2LDc0Ljg3LDQuODUsMTI5LjgxLDI0LjI0"
    "LDE2My40OCw1Ny43NSw0NC42Miw0NC40MSw2NC4wMSw5Mi40Nyw2OC40MSwxNzIuNzItNjEu"
    "MjEtMS42Ny0xMTguNTItMjYuMi0xNjIuMDItNjkuNVpNNzc5LjU1LDM2Ny41bC00Ni44NS0x"
    "MDguNjZjLTUuNS0xMi43LTE3LjUyLTEzLjQtMjYuNjktMS41M2wtMTMuMDMsMTYuODVjLTUy"
    "LjUxLTQ0LjM0LTEyMC4zNC03NC4xNi0xOTQuNDQtNzQuMTYtMTMxLjU0LDAtMjQzLjYsODQu"
    "ODQtMjg0LjUsMTk4LjY4aDcuMjljMjIuMzYsMCw0My41NSwzLjg5LDYzLjY5LDUuNzcsMzYu"
    "NjctODEuMTIsMTE4LjQ3LTEzNi40LDIxMy41Mi0xMzYuNCw1OC43NSwwLDExMi40OSwyMi40"
    "MSwxNTMuNjMsNTguMTNsLS4yMi42NS0xMy4zNSwxNy40NWMtOS4xOSwxMS44OC01LjQzLDIz"
    "LjMzLDguMzMsMjUuMzRsMTE3LjU1LDE3LjMyYzEzLjgsMi4wMywyMC41Ny02LjcsMTUuMDct"
    "MTkuNDJaIi8+CiAgPC9nPgo8L3N2Zz4K"
    "&labelColor=5374A7)]"
    "(https://wattnet.eu) "
    "[![Dashboard]"
    "(https://img.shields.io/badge/dashboard.wattnet.eu-94CE24"
    "?style=flat&logo=data:image/svg+xml;base64,"
    "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBpZD0id2F0dG5l"
    "dC1pY29uIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjE4"
    "MCAxODAgNjQwIDY0MCI+CiAgPGRlZnM+CiAgICA8c3R5bGU+CiAgICAgIC5jbHMtMSB7CiAg"
    "ICAgICAgZmlsbDogI2ZmZjsKICAgICAgfQogICAgPC9zdHlsZT4KICA8L2RlZnM+CiAgPGcg"
    "aWQ9ImNvbG9yIj4KICAgIDxwYXRoIGlkPSJTdmdqc0cxODUyIiBjbGFzcz0iY2xzLTEiIGQ9"
    "Ik03OTcuODUsNDYwLjg0bC0yLjMyLTIwLjIyaC0xOC41MmMtMTEzLjYyLDAtMTk0LjU5LDI3"
    "LjEyLTI0Ni43Miw3OC45OC0xLjg5LDEuODgtMy41Niw0LjQ0LTUuMzgsNi4zMywxOC4zNCwy"
    "My40OSwzMi4wNiw0OC4wNyw0Mi4zLDczLjM5LDMyLjM3LTQ5Ljg5LDg2Ljg0LTk2LjMxLDE3"
    "My4yNS0xMjEuOTUtOTAuNyw1OC43Mi0xMzMuNjIsMTQ1LjMyLTE1MC4zNSwyMTMuMDUsMy41"
    "LDI3LjM5LDQuNzgsNTYuMDgsNC43OCw4Ni4yNSwwLDIuNi0uMjMsNS4xOC0uNTYsNy43LDQz"
    "Ljg4LTE0LjU4LDg0LjEtMzkuNzgsMTE3LjY5LTczLjIyLDY2LjE4LTY1LjgzLDk3LjUzLTE1"
    "Ny42Niw4NS44NS0yNTAuM1pNNTUzLjM2LDc3Ni42OGMwLTEwMC44NS0xMy45OC0xODQuNzUt"
    "ODYuNjctMjU3LjA4LTUyLjExLTUxLjg2LTEzMS43NS03OC45OC0yNDUuMzctNzguOThoLTE4"
    "LjUybC0yLjMxLDIwLjIyYy0xMS42OSw5Mi42NCwxOS41NSwxODQuNDgsODUuNzEsMjUwLjI5"
    "LDU2LjgsNTYuNTMsMTMyLjM3LDg4LjE2LDIxMi44LDg4LjE2LDEyLjYsMCwyNC4zOS0uNTYs"
    "MzYuODktMi4xMmwxNy40Ni0yLjA3di0xOC40M2gwWk0zMzAuMTEsNjY4LjQzYy00My44OC00"
    "My42NS02OC4yOC0xMDAuMjEtNjkuODctMTYwLjk2LDc0Ljg3LDQuODUsMTI5LjgxLDI0LjI0"
    "LDE2My40OCw1Ny43NSw0NC42Miw0NC40MSw2NC4wMSw5Mi40Nyw2OC40MSwxNzIuNzItNjEu"
    "MjEtMS42Ny0xMTguNTItMjYuMi0xNjIuMDItNjkuNVpNNzc5LjU1LDM2Ny41bC00Ni44NS0x"
    "MDguNjZjLTUuNS0xMi43LTE3LjUyLTEzLjQtMjYuNjktMS41M2wtMTMuMDMsMTYuODVjLTUy"
    "LjUxLTQ0LjM0LTEyMC4zNC03NC4xNi0xOTQuNDQtNzQuMTYtMTMxLjU0LDAtMjQzLjYsODQu"
    "ODQtMjg0LjUsMTk4LjY4aDcuMjljMjIuMzYsMCw0My41NSwzLjg5LDYzLjY5LDUuNzcsMzYu"
    "NjctODEuMTIsMTE4LjQ3LTEzNi40LDIxMy41Mi0xMzYuNCw1OC43NSwwLDExMi40OSwyMi40"
    "MSwxNTMuNjMsNTguMTNsLS4yMi42NS0xMy4zNSwxNy40NWMtOS4xOSwxMS44OC01LjQzLDIz"
    "LjMzLDguMzMsMjUuMzRsMTE3LjU1LDE3LjMyYzEzLjgsMi4wMywyMC41Ny02LjcsMTUuMDct"
    "MTkuNDJaIi8+CiAgPC9nPgo8L3N2Zz4K"
    "&labelColor=1E8449)]"
    "(https://dashboard.wattnet.eu) "
    "[![Docker Hub]"
    "(https://img.shields.io/badge/hub.docker.com%2Fu%2Fwattnet-1D63ED"
    "?style=flat&logo=docker&logoColor=white"
    "&labelColor=003F8C)]"
    "(https://hub.docker.com/u/wattnet)\n\n"
    "#### An open-source service for tracking the environmental "
    "footprint of electricity across Europe.\n\n"
    "Explore the environmental footprint of electricity, powered "
    "by open data. Access real-time, historical, and forecasted "
    "indicators on the carbon and water impact of electricity "
    "consumption across Europe.\n\n"
    "Wattnet is designed for researchers, developers, and "
    "decision-makers who rely on accurate, transparent, and "
    "reproducible environmental metrics.\n\n"
    "For more information, please visit our "
    "[official website](https://wattnet.eu) "
    "or our "
    "[GitHub Organization](https://github.com/wattnet).\n\n"
    "[![Website Banner](/static/images/banner.png)]"
    "(https://wattnet.eu)\n\n"
    + authentication_documentation(settings.developer_portal_url)
    + "### Funding and acknowledgments\n\n"
    "This work was developed within the "
    "[GreenDIGIT](https://greendigit-project.eu/) project, funded "
    "by the European Union’s Horizon Europe research and "
    "innovation programme under grant agreement No. "
    "[101131207](https://cordis.europa.eu/project/id/101131207), "
    "and by the Swiss State Secretariat for Education, Research "
    "and Innovation (SERI).\n\n"
    '<img width="648" '
    'src="/static/images/funding-logos.png" '
    'alt="Funded by the European Union, the Swiss State '
    "Secretariat for Education, Research and Innovation (SERI), "
    'and the GreenDIGIT project" '
    'style="margin: 1rem 0;">\n\n'
    "### About the service\n\n"
    "A service provided by "
    '<a href="https://www.csic.es" target="_blank" '
    'rel="noopener noreferrer" '
    'style="color: #0366d6; text-decoration: none;">'
    "Spanish National Research Council (CSIC)</a>, "
    "deployed on the Scientific Cloud at "
    '<a href="https://ifca.unican.es/" target="_blank" '
    'rel="noopener noreferrer" '
    'style="color: #0366d6; text-decoration: none;">'
    "Institute of Physics of Cantabria (IFCA)</a>, "
    "developed by the "
    '<a href="https://advancedcomputing.ifca.es" '
    'target="_blank" rel="noopener noreferrer" '
    'style="color: #0366d6; text-decoration: none;">'
    "IFCA Advanced Computing and e-Science Group</a>.\n\n"
    "##### © 2026 Spanish National Research Council (CSIC). "
    "All rights reserved."
)

main_documentation = """
### API Documentation

#### Endpoints

- [`/latest`](/latest/docs) - Latest Version of the wattnet API
- [`/v1`](/v1/docs) - Version 1 of the wattnet API

"""

# Create the FastAPI app
app = FastAPI(title="wattnet RESTful API", description=description)


# Include the API routers for different versions
app.include_router(api_router_v1)

versioned_app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/v{major}",
    include_in_schema=True,
    enable_latest=True,
    summary=summary,
    description=description + main_documentation,
    version=build_version(),
    terms_of_service="https://wattnet.eu/terms",
)

# The versioned apps that VersionedFastAPI mounts do not inherit the handlers of the
# parent, so each one answers its errors with the stable ``code``.
for _route in versioned_app.routes:
    if isinstance(getattr(_route, "app", None), FastAPI):
        install_error_handlers(_route.app)
install_error_handlers(versioned_app)

versioned_app.add_middleware(
    CacheControlMiddleware, max_age=settings.cache_max_age_seconds
)

# Add favicon route
versioned_app.mount(
    "/static", StaticFiles(directory=str(_API_DIR / "static")), name="static"
)


# The MCP interface: the same app, served at /mcp (the gateway maps mcp.wattnet.eu to
# it). It is outside /v1, so it is not in the OpenAPI and the cache does not touch it.
# The DNS rebinding check is off: the gate is the boundary, as it is for REST.
_mcp_app = mcp_server.streamable_http_app(
    streamable_http_path="/mcp",
    json_response=True,
    stateless_http=True,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)
versioned_app.router.routes.extend(_mcp_app.routes)


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Run the session manager of MCP: the mounted apps do not run a lifespan."""
    async with _mcp_app.router.lifespan_context(_mcp_app):
        yield


versioned_app.router.lifespan_context = _lifespan


@versioned_app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    """Route for favicon.ico."""
    return FileResponse(_API_DIR / "static" / "favicon.ico")


@versioned_app.get("/healthz", include_in_schema=False)
def healthz() -> dict:
    """Liveness probe: the process answers, with no call to the storage or others."""
    return {"status": "ok"}


@versioned_app.get("/readyz", include_in_schema=False)
def readyz() -> JSONResponse:
    """Readiness probe: 200 when the storage answers, 503 when it does not."""
    if check_storage_system():
        return JSONResponse({"status": "ready"})
    return JSONResponse({"status": "not ready"}, status_code=503)


def main() -> None:
    """Start the wattnet API server."""
    # Run the server
    LOG.info("Starting wattnet RESTful API server...")
    LOG.debug(f"Settings: {settings}")
    uvicorn.run(
        versioned_app,
        host=settings.host,
        port=settings.port,
        log_level="info" if not settings.debug else "debug",
    )


if __name__ == "__main__":  # pragma: no cover
    main()
