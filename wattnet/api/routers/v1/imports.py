from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import import_service
from wattnet.api.models.imports import Import
from wattnet.api.utils import validation

router = APIRouter()


@router.get(
    "",
    response_model=List[Import],
    status_code=200,
    responses={
        200: {
            "description": "List of import data matching the given filters",
            "model": List[Import],
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
    summary="Retrieve import data",
    description="""
Retrieve a list of import data filtered by:
- `zone`: wattnet zone code (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup the main zone code.
- `source_zone`: Optional origin zone code to filter imports.
- `source_lat` and `source_lon`: Coordinates to lookup origin zone code (mutually exclusive with `source_zone`).
- `start` and `end`: Filter by datetime range (both required if one is provided). If not provided, only last available data is returned.
""",
)
@version(1)
def get_imports(
    zone: Optional[str] = Query(
        None,
        description="Filter by main wattnet zone code (mutually exclusive with lat/lon)",
    ),
    lat: Optional[float] = Query(
        None, ge=-90, le=90, description="Latitude in decimal degrees (DD)"
    ),
    lon: Optional[float] = Query(
        None, ge=-180, le=180, description="Longitude in decimal degrees (DD)"
    ),
    source_zone: Optional[str] = Query(
        None,
        description="Origin zone code for imports (mutually exclusive with source_lat/source_lon)",
    ),
    source_lat: Optional[float] = Query(
        None, ge=-90, le=90, description="Latitude for origin zone"
    ),
    source_lon: Optional[float] = Query(
        None, ge=-180, le=180, description="Longitude for origin zone"
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

    # Validate main zone
    zone = validation.validate_location_filters(zone, lat, lon)

    # Validate source zone
    source_zone = validation.validate_location_filters(
        source_zone, source_lat, source_lon
    )

    # Validate time range
    validation.validate_time_range(start, end)

    # Fetch imports
    imports = import_service.get_imports(
        zone=zone.upper() if zone else None,
        source=source_zone.upper() if source_zone else None,
        start=start,
        end=end,
    )

    return imports
