from fastapi import APIRouter
from fastapi_versioning import version

from wattnet.api.models.zone import Zone, ZoneInfo

router = APIRouter()


@router.get("", response_model=list[ZoneInfo])
@version(1)
def get_zones():
    """Get all zones"""


@router.get("/{id}", response_model=Zone)
@version(1)
def get_zone(id: str):
    """Get a zone by ID"""
