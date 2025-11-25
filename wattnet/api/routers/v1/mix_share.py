from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import mix_share_service
from wattnet.api.models.mix_share import MixShare
from wattnet.api.utils import validation

router = APIRouter()


@router.get(
    "",
    response_model=List[MixShare],
    status_code=200,
    responses={
        200: {
            "description": "List of mix share data matching the given filters",
            "model": List[MixShare],
        },
        400: {
            "description": "Invalid input parameters",
            "content": {"application/json": {"example": {"detail": "Error message"}}},
        },
        404: {
            "description": "No zone found for the provided coordinates",
            "content": {"application/json": {"example": {"detail": "Error message"}}},
        },
    },
    summary="Retrieve mix share data",
    description="""
Retrieve the percentage of energy in the mix of a destination zone that comes from each origin zone (including itself).

Filters:
- `zone`: Destination wattnet zone code (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup destination zone code.
- `origin_zone`: Optional origin zone code to filter contributions.
- `origin_lat` and `origin_lon`: Coordinates to lookup origin zone (mutually exclusive with `origin_zone`).
- `start` and `end`: Filter by datetime range (both required if one is provided). Only last available data is returned if omitted.
""",
)
@version(1)
def get_mix_share(
    zone: Optional[str] = Query(
        None,
        description="Filter by destination wattnet zone code (mutually exclusive with lat/lon)",
    ),
    lat: Optional[float] = Query(
        None,
        ge=-90,
        le=90,
        description="Latitude in decimal degrees (DD) for destination zone",
    ),
    lon: Optional[float] = Query(
        None,
        ge=-180,
        le=180,
        description="Longitude in decimal degrees (DD) for destination zone",
    ),
    origin_zone: Optional[str] = Query(
        None,
        description="Filter by origin wattnet zone code (mutually exclusive with origin_lat/origin_lon)",
    ),
    origin_lat: Optional[float] = Query(
        None,
        ge=-90,
        le=90,
        description="Latitude in decimal degrees (DD) for origin zone",
    ),
    origin_lon: Optional[float] = Query(
        None,
        ge=-180,
        le=180,
        description="Longitude in decimal degrees (DD) for origin zone",
    ),
    start: Optional[datetime] = Query(
        None, description="Start datetime for filtering (ISO 8601 format, UTC-aware)"
    ),
    end: Optional[datetime] = Query(
        None, description="End datetime for filtering (ISO 8601 format, UTC-aware)"
    ),
):

    if start:
        start = validation.make_utc_aware(start)
    if end:
        end = validation.make_utc_aware(end)

    # Validate zones
    zone = validation.validate_location_filters(zone, lat, lon)
    origin_zone = validation.validate_location_filters(
        origin_zone, origin_lat, origin_lon
    )

    # Validate time range
    validation.validate_time_range(start, end)

    # Fetch mix share data
    mix_shares = mix_share_service.get_mix_share(
        zone=zone.upper() if zone else None,
        origin=origin_zone.upper() if origin_zone else None,
        start=start,
        end=end,
    )

    return mix_shares
