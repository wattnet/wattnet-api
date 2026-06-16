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
    "?style=for-the-badge&logo=github&logoColor=white"
    "&labelColor=444444)]"
    "(https://github.com/wattnet) "
    "[![Website]"
    "(https://img.shields.io/badge/wattnet.eu-1D488C"
    "?style=for-the-badge&logo=leaflet&logoColor=white"
    "&labelColor=5374A7)]"
    "(https://wattnet.eu) "
    "[![Dashboard]"
    "(https://img.shields.io/badge/dashboard_(beta)-94CE24"
    "?style=for-the-badge&logo=chartdotjs&logoColor=white"
    "&labelColor=6FCA3A)]"
    "(https://dashboard.wattnet.eu)\n\n"
    "#### An open-source service for tracking the environmental "
    "footprint of electricity across Europe.\n\n"
    "Explore environmental footprint of electricity powered "
    "by open data.\n\n"
    "Access real-time, historical, and forecasted data on "
    "the carbon and water impact of electricity consumption "
    "across Europe.\n\n"
    "Designed for data-driven research, supporting informed "
    "decision-making for a more sustainable future.\n\n"
    "For more information, please visit our "
    "[official website](https://wattnet.eu) "
    "or our "
    "[GitHub Organization](https://github.com/wattnet)\n\n"
    "[![Website Banner](/static/images/banner.png)]"
    "(https://wattnet.eu)\n\n"
    "### Funding and acknowledgments\n\n"
    "This work is funded from the European Union’s Horizon "
    "Europe research and innovation programme through the "
    "[GreenDIGIT project](https://greendigit-project.eu/), "
    "under the grant agreement No. "
    "[101131207](https://cordis.europa.eu/project/id/101131207)\n\n"
    '<div style="display: flex; justify-content: space-between; '
    'align-items: center; margin-top: 1rem; margin-bottom: 1rem;">'
    '<img width="250" '
    'src="/static/images/EN_FundedbytheEU_RGB_POS.png" '
    'alt="EU Funded Logo">'
    '<img width="220" '
    'src="/static/images/GreenDIGIT logo color horizontal2.png" '
    'alt="GreenDIGIT Logo" '
    'style="padding-bottom: 0.2rem;">'
    "</div>\n\n"
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
    terms_of_service="https://github.com/wattnet",
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
