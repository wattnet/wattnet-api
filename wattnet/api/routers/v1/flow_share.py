"""API router for flow share endpoints in the wattnet API application."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import flow_share_service
from wattnet.api.models.flow_share import FlowShare
from wattnet.api.utils import validation

router = APIRouter()

# Query parameter defaults
_zone_query = Query(
    None,
    description=(
        "Filter by origin wattnet zone code (mutually exclusive with lat/lon)"
    ),
)

_lat_query = Query(
    None,
    ge=-90,
    le=90,
    description="Latitude in decimal degrees (DD)",
)

_lon_query = Query(
    None,
    ge=-180,
    le=180,
    description="Longitude in decimal degrees (DD)",
)

_destination_zone_query = Query(
    None,
    description=(
        "Filter by destination wattnet zone code "
        "(mutually exclusive with destination_lat/destination_lon)"
    ),
)

_destination_lat_query = Query(
    None,
    ge=-90,
    le=90,
    description="Latitude in decimal degrees (DD) for destination zone",
)

_destination_lon_query = Query(
    None,
    ge=-180,
    le=180,
    description="Longitude in decimal degrees (DD) for destination zone",
)

_start_query = Query(
    None,
    description=(
        "Start datetime for filtering (ISO 8601 format). "
        "Datetime must be UTC or timezone-aware. "
        "(YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)"
    ),
)

_end_query = Query(
    None,
    description=(
        "End datetime for filtering (ISO 8601 format). "
        "Datetime must be UTC or timezone-aware. "
        "(YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)"
    ),
)


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
Retrieve the flow share of energy from a given origin zone to other zones
in the network.

This metric represents, for a specific origin zone, the percentage of its total
energy production that is exported to each destination zone.

Filters:
- `zone`: origin wattnet zone code (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup origin zone code.
- `destination_zone`: Optional destination zone code to filter flow shares.
- `destination_lat` and `destination_lon`: Coordinates to lookup destination
  zone code (mutually exclusive with `destination_zone`).
- `start` and `end`: Filter by datetime range (both required if one is provided).
  If not provided, only last available data is returned.
""",
)
@version(1)
def get_flow_share(
    zone: Optional[str] = _zone_query,
    lat: Optional[float] = _lat_query,
    lon: Optional[float] = _lon_query,
    destination_zone: Optional[str] = _destination_zone_query,
    destination_lat: Optional[float] = _destination_lat_query,
    destination_lon: Optional[float] = _destination_lon_query,
    start: Optional[datetime] = _start_query,
    end: Optional[datetime] = _end_query,
) -> List[FlowShare]:
    """Convert datetimes to UTC, validate filters, and fetch flow share data.

    :param zone: Optional origin wattnet zone code (mutually exclusive with lat/lon)
    :type zone: Optional[str]

    :param lat: Optional latitude in decimal degrees (mutually exclusive with zone)
    :type lat: Optional[float]

    :param lon: Optional longitude in decimal degrees (mutually exclusive with zone)
    :type lon: Optional[float]

    :param destination_zone: Optional destination wattnet zone code to
    filter flow shares (mutually exclusive with destination_lat/destination_lon)
    :type destination_zone: Optional[str]

    :param destination_lat: Optional latitude in decimal degrees for destination zone
    (mutually exclusive with destination_zone)
    :type destination_lat: Optional[float]

    :param destination_lon: Optional longitude in decimal degrees for destination zone
    (mutually exclusive with destination_zone)
    :type destination_lon: Optional[float]

    :param start: Optional start datetime for filtering (ISO 8601 format).
    Datetime must be UTC or timezone-aware. If provided, end must also be provided.
    (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)

    :param end: Optional end datetime for filtering (ISO 8601 format).
    Datetime must be UTC or timezone-aware. If provided, start must also be provided.
    (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)

    :return: List of flow share data matching the given filters
    :rtype: List[FlowShare]
    """
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
