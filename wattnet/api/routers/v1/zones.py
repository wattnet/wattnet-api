"""API router for zones endpoints."""

from typing import List

from fastapi import APIRouter
from fastapi_versioning import version

from wattnet.api.dependencies import zone_service
from wattnet.api.models.zone import Zone

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
    return zone_service.get_zones()
