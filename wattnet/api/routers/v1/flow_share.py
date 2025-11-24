from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import flow_share_service
from wattnet.api.models.flow_share import FlowShare
from wattnet.api.utils import validation

router = APIRouter()


@router.get(
    "",
    response_model=List[FlowShare],
    status_code=200,
    responses={
        200: {
            "description": "List of flow share data matching the given filters",
            "model": List[FlowShare],
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
    summary="Retrieve flow share data",
    description="""
Retrieve the flow share of energy from a given origin zone to other zones in the network.

This metric represents, for a specific origin zone, the percentage of its total energy production that is exported to each destination zone. 

Filters:
- `zone`: origin wattnet zone code (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup origin zone code.
- `destination_zone`: Optional destination zone code to filter flow shares.
- `destination_lat` and `destination_lon`: Coordinates to lookup destination zone code (mutually exclusive with `destination_zone`).
- `start` and `end`: Filter by datetime range (both required if one is provided). If not provided, only last available data is returned.
""",
)
@version(1)
def get_flow_share(
    zone: Optional[str] = Query(
        None,
        description="Filter by origin wattnet zone code (mutually exclusive with lat/lon)",
    ),
    lat: Optional[float] = Query(
        None, ge=-90, le=90, description="Latitude in decimal degrees (DD)"
    ),
    lon: Optional[float] = Query(
        None, ge=-180, le=180, description="Longitude in decimal degrees (DD)"
    ),
    destination_zone: Optional[str] = Query(
        None,
        description="Filter by destination wattnet zone code (mutually exclusive with destination_lat/destination_lon)",
    ),
    destination_lat: Optional[float] = Query(
        None,
        ge=-90,
        le=90,
        description="Latitude in decimal degrees (DD) for destination zone",
    ),
    destination_lon: Optional[float] = Query(
        None,
        ge=-180,
        le=180,
        description="Longitude in decimal degrees (DD) for destination zone",
    ),
    start: Optional[datetime] = Query(
        None,
        description="Start datetime for filtering (ISO 8601 format). Datetime must be UTC or timezone-aware. (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)",
    ),
    end: Optional[datetime] = Query(
        None,
        description="End datetime for filtering (ISO 8601 format). Datetime must be UTC or timezone-aware. (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)",
    ),
):

    # Convert to UTC if provided
    if start:
        start = validation.make_utc_aware(start)
    if end:
        end = validation.make_utc_aware(end)

    # Validate origin zone
    zone = validation.validate_location_filters(zone, lat, lon)

    # Validate destination zone
    destination_zone = validation.validate_location_filters(
        destination_zone, destination_lat, destination_lon
    )

    # Validate time range
    validation.validate_time_range(start, end)

    # Fetch flow share data
    flow_shares = flow_share_service.get_flow_share(
        zone=zone.upper() if zone else None,
        destination=destination_zone.upper() if destination_zone else None,
        start=start,
        end=end,
    )

    return flow_shares
