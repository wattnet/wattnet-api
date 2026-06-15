"""API router for impact share endpoints in the wattnet API application."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import impact_share_service
from wattnet.api.models.impact_share import ImpactShare
from wattnet.api.utils import validation

router = APIRouter()

_zone_query = Query(
    None,
    description="Destination zone code (mutually exclusive with lat/lon)",
)
_lat_query = Query(None, ge=-90, le=90, description="Latitude in decimal degrees (DD)")
_lon_query = Query(
    None, ge=-180, le=180, description="Longitude in decimal degrees (DD)"
)
_source_zone_query = Query(
    None,
    description="Origin zone code (mutually exclusive with source_lat/source_lon)",
)
_source_lat_query = Query(None, ge=-90, le=90, description="Latitude for origin zone")
_source_lon_query = Query(
    None, ge=-180, le=180, description="Longitude for origin zone"
)
_impact_type_query = Query(
    None,
    description=(
        "Type of impact to filter [water]. " "If not provided, all types are returned."
    ),
)
_scope_query = Query(
    "operational",
    description="Filter by scope [operational]. Default is 'operational'.",
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
    response_model=List[ImpactShare],
    status_code=200,
    responses={
        200: {
            "description": "List of impact share data matching the given filters",
            "model": List[ImpactShare],
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
    summary="Retrieve impact share data",
    description="""Retrieve the impact of a destination zone decomposed
into contributions from each origin zone.

Filters:
- `zone`: Destination wattnet zone code
  (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup destination zone.
- `source_zone`: Optional origin zone to filter contributions.
- `source_lat` and `source_lon`: Coordinates to lookup origin zone
  (mutually exclusive with `source_zone`).
- `impact_type`: water. If not provided, all types are returned.
- `scope`: operational. Default is 'operational'.
- `start` / `end`: Datetime range to filter (both required if one is
  provided). Only last available data is returned if omitted.
""",
)
@version(1)
def get_impact_share(
    zone: Optional[str] = _zone_query,
    lat: Optional[float] = _lat_query,
    lon: Optional[float] = _lon_query,
    source_zone: Optional[str] = _source_zone_query,
    source_lat: Optional[float] = _source_lat_query,
    source_lon: Optional[float] = _source_lon_query,
    impact_type: Optional[str] = _impact_type_query,
    scope: Optional[str] = _scope_query,
    start: Optional[datetime] = _start_query,
    end: Optional[datetime] = _end_query,
) -> List[ImpactShare]:
    """Endpoint to retrieve impact share data."""
    if start:
        start = validation.make_utc_aware(start)
    if end:
        end = validation.make_utc_aware(end)

    zone = validation.validate_location_filters(zone, lat, lon)
    source_zone = validation.validate_location_filters(
        source_zone, source_lat, source_lon
    )
    validation.validate_impact_type(impact_type)
    validation.validate_time_range(start, end)
    validation.validate_operational_scope(scope)

    return impact_share_service.get_impact_share(
        zone=zone.upper() if zone else None,
        source=source_zone.upper() if source_zone else None,
        impact_type=impact_type.lower() if impact_type else "water",
        scope=scope.lower() if scope else "operational",
        start=start,
        end=end,
    )
