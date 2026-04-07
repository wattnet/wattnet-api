"""API router for load data endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import load_service
from wattnet.api.models.load import Load
from wattnet.api.utils import validation

router = APIRouter()

_zone_query = Query(
    None,
    description="Filter by wattnet zone code (mutually exclusive with lat/lon)",
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
    response_model=List[Load],
    status_code=200,
    responses={
        200: {
            "description": "List of load data matching the given filters",
            "model": List[Load],
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
    summary="Retrieve load data",
    description="""Retrieve total electricity demand data filtered by:

- `zone`: wattnet zone code (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup zone code.
- `start` and `end`: Filter by datetime range (both required if one is
  provided). If not provided, only last available data is returned.

If `lat` and `lon` are provided, the corresponding zone will be
determined automatically.
""",
)
@version(1)
def get_load(
    zone: Optional[str] = _zone_query,
    lat: Optional[float] = _lat_query,
    lon: Optional[float] = _lon_query,
    start: Optional[datetime] = _start_query,
    end: Optional[datetime] = _end_query,
) -> List[Load]:
    """Endpoint to retrieve load (total electricity demand) data.

    :param zone: wattnet zone code (mutually exclusive with lat/lon)
    :type zone: Optional[str]

    :param lat: Latitude in decimal degrees (DD)
    :type lat: Optional[float]

    :param lon: Longitude in decimal degrees (DD)
    :type lon: Optional[float]

    :param start: Start datetime for filtering (ISO 8601 format).
        Datetime must be UTC or timezone-aware.
    :type start: Optional[datetime]

    :param end: End datetime for filtering (ISO 8601 format).
        Datetime must be UTC or timezone-aware.
    :type end: Optional[datetime]

    :return: List of load data matching the given filters
    :rtype: List[Load]
    """
    if start:
        start = validation.make_utc_aware(start)
    if end:
        end = validation.make_utc_aware(end)

    zone = validation.validate_location_filters(zone, lat, lon)
    validation.validate_time_range(start, end)

    return load_service.get_load(
        zone=zone.upper() if zone else None,
        start=start,
        end=end,
    )
