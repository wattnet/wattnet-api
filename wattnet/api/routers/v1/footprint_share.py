"""API router for footprint share endpoints in the wattnet API application."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import footprint_share_service
from wattnet.api.models.footprint_share import FootprintShare
from wattnet.api.utils import validation

router = APIRouter()

# Query parameter defaults
_zone_query = Query(
    None,
    description=("Destination zone code (mutually exclusive with lat/lon)"),
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

_source_zone_query = Query(
    None,
    description=("Origin zone code (mutually exclusive with source_lat/source_lon)"),
)

_source_lat_query = Query(
    None,
    ge=-90,
    le=90,
    description="Latitude for origin zone",
)

_source_lon_query = Query(
    None,
    ge=-180,
    le=180,
    description="Longitude for origin zone",
)

_footprint_type_query = Query(
    None,
    description=(
        "Type of footprint to filter [carbon, water]. "
        "If not provided, all types are returned."
    ),
)

_scope_query = Query(
    None,
    description=(
        "Filter footprints by scope [operational, life-cycle]. "
        "Default is 'life-cycle'."
    ),
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
    response_model=List[FootprintShare],
    status_code=200,
    responses={
        200: {
            "description": "List of footprint share data matching the given filters",
            "model": List[FootprintShare],
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
    summary="Retrieve footprint share data",
    description="""Retrieve the footprint of a destination zone decomposed
into contributions from each origin zone.

Filters:
- `zone`: Destination wattnet zone code
  (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup destination
  zone code.
- `source_zone`: Optional origin zone to filter
  contributions.
- `source_lat` and `source_lon`: Coordinates to lookup
  origin zone (mutually exclusive with `source_zone`).
- `footprint_type`: carbon or water
- `scope`: operational or life-cycle
- `start` / `end`: Datetime range to filter
  (both required if one is provided). Only last available
  data is returned if omitted.
""",
)
@version(1)
def get_footprint_share(
    zone: Optional[str] = _zone_query,
    lat: Optional[float] = _lat_query,
    lon: Optional[float] = _lon_query,
    source_zone: Optional[str] = _source_zone_query,
    source_lat: Optional[float] = _source_lat_query,
    source_lon: Optional[float] = _source_lon_query,
    footprint_type: Optional[str] = _footprint_type_query,
    scope: Optional[str] = _scope_query,
    start: Optional[datetime] = _start_query,
    end: Optional[datetime] = _end_query,
) -> List[FootprintShare]:
    """Endpoint to retrieve footprint share data filtered.

    :param zone: Destination wattnet zone code (mutually exclusive with lat/lon)
    :type zone: Optional[str]

    :param lat: Latitude in decimal degrees (DD)
    :type lat: Optional[float]

    :param lon: Longitude in decimal degrees (DD)
    :type lon: Optional[float]

    :param source_zone: Origin zone code for contributions
    (mutually exclusive with source_lat/source_lon)
    :type source_zone: Optional[str]

    :param source_lat: Latitude for origin zone
    :type source_lat: Optional[float]

    :param source_lon: Longitude for origin zone
    :type source_lon: Optional[float]

    :param footprint_type: Type of footprint to filter [carbon, water].
    If not provided, all types are returned.
    :type footprint_type: Optional[str]

    :param scope: Filter footprints by scope [operational, life-cycle].
    Default is 'life-cycle'.

    :param start: Start datetime for filtering (ISO 8601 format).
    Datetime must be UTC or timezone-aware.
    (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)
    :type start: Optional[datetime]

    :param end: End datetime for filtering (ISO 8601 format).
    Datetime must be UTC or timezone-aware.
    (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)
    :type end: Optional[datetime]

    :return: List of footprint share data matching the given filters
    :rtype: List[FootprintShare]
    """
    # Convert to UTC if provided
    if start:
        start = validation.make_utc_aware(start)
    if end:
        end = validation.make_utc_aware(end)

    # Validate destination zone
    zone = validation.validate_location_filters(zone, lat, lon)

    # Validate source zone
    source_zone = validation.validate_location_filters(
        source_zone, source_lat, source_lon
    )

    # Validate time range
    validation.validate_time_range(start, end)
    validation.validate_footprint_type(footprint_type)
    validation.validate_scope(scope)

    # Fetch footprint share data
    footprint_shares = footprint_share_service.get_footprint_share(
        zone=zone.upper() if zone else None,
        source=source_zone.upper() if source_zone else None,
        footprint_type=footprint_type.lower() if footprint_type else None,
        scope=scope.lower() if scope else "life-cycle",
        start=start,
        end=end,
    )

    return footprint_shares
