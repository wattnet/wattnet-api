"""API router for export data endpoints in the wattnet API."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import export_service
from wattnet.api.models.exports import Export
from wattnet.api.utils import validation

router = APIRouter()

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
    description="Latitude in decimal degrees (DD) for origin zone",
)

_lon_query = Query(
    None,
    ge=-180,
    le=180,
    description="Longitude in decimal degrees (DD) for origin zone",
)

_destination_zone_query = Query(
    None,
    description=(
        "Destination zone code for exports "
        "(mutually exclusive with destination_lat/destination_lon)"
    ),
)

_destination_lat_query = Query(
    None,
    ge=-90,
    le=90,
    description="Latitude for destination zone",
)

_destination_lon_query = Query(
    None,
    ge=-180,
    le=180,
    description="Longitude for destination zone",
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
    response_model=List[Export],
    status_code=200,
    responses={
        200: {
            "description": "List of export data matching the given filters",
            "model": List[Export],
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
    summary="Retrieve export data",
    description="""Retrieve a list of export data filtered by:
- `zone`: origin wattnet zone code (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup the origin zone code.
- `destination_zone`: Optional destination zone code to filter exports.
- `destination_lat` and `destination_lon`: Coordinates to lookup destination zone
  code (mutually exclusive with `destination_zone`).
- `start` and `end`: Filter by datetime range (both required if one is provided).
  If not provided, only last available data is returned.
""",
)
@version(1)
def get_exports(
    zone: Optional[str] = _zone_query,
    lat: Optional[float] = _lat_query,
    lon: Optional[float] = _lon_query,
    destination_zone: Optional[str] = _destination_zone_query,
    destination_lat: Optional[float] = _destination_lat_query,
    destination_lon: Optional[float] = _destination_lon_query,
    start: Optional[datetime] = _start_query,
    end: Optional[datetime] = _end_query,
) -> List[Export]:
    """Endpoint to retrieve export data filtered by various parameters.

    :param zone: Origin wattnet zone code (mutually exclusive with lat/lon)
    :type zone: Optional[str]

    :param lat: Latitude for origin zone (mutually exclusive with zone)
    :type lat: Optional[float]

    :param lon: Longitude for origin zone (mutually exclusive with zone)
    :type lon: Optional[float]

    :param destination_zone: Destination zone code for exports
    (mutually exclusive with destination_lat/destination_lon)
    :type destination_zone: Optional[str]

    :param destination_lat: Latitude for destination zone
    (mutually exclusive with destination_zone)
    :type destination_lat: Optional[float]

    :param destination_lon: Longitude for destination zone
    (mutually exclusive with destination_zone)
    :type destination_lon: Optional[float]

    :param start: Start datetime for filtering (ISO 8601 format).
    Datetime must be UTC or timezone-aware.
    (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)
    :type start: Optional[datetime]

    :param end: End datetime for filtering (ISO 8601 format).
    Datetime must be UTC or timezone-aware.
    (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)
    :type end: Optional[datetime]

    :return: List of export data matching the given filters
    :rtype: List[Export]
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

    # Fetch exports
    exports = export_service.get_exports(
        zone=zone.upper() if zone else None,
        destination=destination_zone.upper() if destination_zone else None,
        start=start,
        end=end,
    )

    return exports
