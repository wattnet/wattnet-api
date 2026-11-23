"""API router for zones endpoints."""

from typing import List

import yaml
from fastapi import APIRouter
from fastapi_versioning import version

from wattnet.api.dependencies import zone_service
from wattnet.api.errors import ApiError
from wattnet.api.models.zone import Zone
from wattnet.api.utils import log

LOG = log.get(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=List[Zone],
    status_code=200,
    responses={
        200: {
            "description": "List of zones with metadata and neighbours",
            "model": List[Zone],
        }
    },
    summary="Retrieve zones",
    description=(
        "Retrieve all configured zones including their metadata and the list "
        "of electrically connected neighbouring zones."
    ),
)
@version(1)
def get_zones() -> List[Zone]:
    """Return all zones with neighbours."""
    try:
        return zone_service.get_zones()
    except (ValueError, yaml.YAMLError) as exc:
        # The text of the error is for the log: it can name files and settings.
        LOG.error(f"Zones could not be loaded: {exc}")
        raise ApiError(
            status_code=500,
            detail="The zones could not be loaded.",
            code="zones_unavailable",
        ) from exc
