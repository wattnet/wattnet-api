"""API router for mix generation data endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import mix_service
from wattnet.api.models.mix import Mix
from wattnet.api.utils import validation

router = APIRouter()

_zone_query = Query(
    None,
    description=("Filter by wattnet zone code (mutually exclusive with lat/lon)"),
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

_production_type_query = Query(
    None,
    description=(
        "Filter mix generation by production type. "
        "Valid values: biomass, coal, gas, geothermal, "
        "hydro_reservoir, hydro_river, hydro_pumped_storage, marine, "
        "nuclear, oil, other, other_renewable, solar, waste, "
        "wind_offshore, wind_onshore. "
        "If not provided, all types are returned."
    ),
)

_start_query = Query(
    None,
    description=(
        "Start datetime for filtering (ISO 8601 format). "
        "Datetime must be UTC or timezone-aware. "
        "(YYYY-MM-DDTHH:MM:SSZ or "
        "YYYY-MM-DDTHH:MM:SS+00:00)"
    ),
)

_end_query = Query(
    None,
    description=(
        "End datetime for filtering (ISO 8601 format). "
        "Datetime must be UTC or timezone-aware. "
        "(YYYY-MM-DDTHH:MM:SSZ or "
        "YYYY-MM-DDTHH:MM:SS+00:00)"
    ),
)


@router.get(
    "",
    response_model=List[Mix],
    status_code=200,
    responses={
        200: {
            "description": "List of mix data matching the given filters",
            "model": List[Mix],
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
    summary="Retrieve mix data",
    description="""Retrieve a list of mix generation data filtered by:
- `zone`: wattnet zone code (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup zone code.
- `production_type`: Type of production to filter
  (e.g., solar, wind, hydro). If not provided, all types are returned.
- `start` and `end`: Filter by datetime range
  (both required if one is provided). If not provided,
  only last available data is returned.
""",
)
@version(1)
def get_mix(
    zone: Optional[str] = _zone_query,
    lat: Optional[float] = _lat_query,
    lon: Optional[float] = _lon_query,
    production_type: Optional[str] = _production_type_query,
    start: Optional[datetime] = _start_query,
    end: Optional[datetime] = _end_query,
) -> List[Mix]:
    """Endpoint to retrieve mix generation data filtered."""
    if start:
        start = validation.make_utc_aware(start)
    if end:
        end = validation.make_utc_aware(end)

    zone = validation.validate_location_filters(zone, lat, lon)
    validation.validate_production_type(production_type)
    validation.validate_time_range(start, end)

    return mix_service.get_mix(
        zone=zone.upper() if zone else None,
        production_type=production_type.lower() if production_type else None,
        start=start,
        end=end,
    )
