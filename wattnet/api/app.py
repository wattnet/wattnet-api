"""API for wattnet."""

# Start server with: uvicorn app:app --reload
# Open browser to: http://localhost:8000/

# Documentation and tester with Swagger UI: http://localhost:8000/docs
# Documentation with ReDoc: http://localhost:8000/redoc


import uvicorn
from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI

from wattnet.api.routers.v1 import api_router as api_router_v1
from wattnet.api.settings import settings
from wattnet.api.utils import log

# Get logger
LOG = log.get(__name__)

description = """

For more information, please visit our [GitHub Organization](https://github.com/wattnet)

<a href="https://github.com/wattnet">
    <img src="https://img.shields.io/badge/github.com-wattnet-1D488C?logo=github&logoColor=white" alt="GitHub">
</a>

### Funding and acknowledgments

This work is funded from the European Union’s Horizon Europe research and innovation programme through the [GreenDIGIT project](https://greendigit-project.eu/), under the grant agreement No. [101131207](https://cordis.europa.eu/project/id/101131207)

<div style="display: flex; justify-content: space-between; align-items: center;">
  <img width="300" src="https://www.europris.org/wp-content/uploads/2023/10/EN-Funded-by-the-EU-POS-2.png" alt="EU Funded Logo">
  <img width="100" src="https://greendigit-project.eu/wp-content/uploads/2025/03/cropped-GD_logo.png" alt="GreenDIGIT Logo">
</div>

---

A service provided by <a href="https://www.csic.es" target="_blank" rel="noopener noreferrer" style="color: #0366d6; text-decoration: none;">Spanish National Research Council (CSIC)</a>,&nbsp;
deployed at <a href="https://ifca.unican.es/" target="_blank" rel="noopener noreferrer" style="color: #0366d6; text-decoration: none;">Institute of Physics of Cantabria (IFCA)</a>,&nbsp;
developed by the <a href="https://advancedcomputing.ifca.es" target="_blank" rel="noopener noreferrer" style="color: #0366d6; text-decoration: none;">IFCA Advanced Computing and e-Science Group</a>.

"""

main_documentation = """
### API Documentation

#### Endpoints

- [`/v1`](/v1/docs) - Version 1 of the wattnet API

"""

# Create the FastAPI app
app = FastAPI(
    title="wattnet RESTful API",
    description=description,
)

# Include the API routers for different versions
app.include_router(api_router_v1)

versioned_app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/v{major}",
    include_in_schema=True,
    enable_latest=True,
    summary="An open-source service for tracking the environmental footprint of electricity across Europe.",
    description=description + main_documentation,
    version="1.0.0",
    terms_of_service="https://github.com/wattnet",
)


def main():
    """Main function to run the server."""

    # Run the server
    LOG.info("Starting wattnet RESTful API server...")
    uvicorn.run(
        versioned_app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info" if not settings.api_debug else "debug",
    )


if __name__ == "__main__":
    main()
