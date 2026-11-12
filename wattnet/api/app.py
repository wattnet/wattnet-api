"""API for wattnet."""

# Start server with: uvicorn app:app --reload
# Open browser to: http://localhost:8000/

# Documentation and tester with Swagger UI: http://localhost:8000/docs
# Documentation with ReDoc: http://localhost:8000/redoc

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi_versioning import VersionedFastAPI

from wattnet.api.routers.v1 import api_router_v1
from wattnet.api.settings import settings
from wattnet.api.utils import log

# Get logger
LOG = log.get(__name__)

# Get the directory where this file is located for relative paths
_API_DIR = Path(__file__).parent

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
    "### Funding and acknowledgments\n\n"
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
    version="1.0.0",
    terms_of_service="https://wattnet.eu/terms",
)

# Add favicon route
versioned_app.mount(
    "/static", StaticFiles(directory=str(_API_DIR / "static")), name="static"
)


@versioned_app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    """Route for favicon.ico."""
    return FileResponse(_API_DIR / "static" / "favicon.ico")


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
