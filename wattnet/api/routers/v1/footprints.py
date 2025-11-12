from datetime import datetime
from typing import List, Optional, Union

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.models.footprint import Footprint, FootprintAggregate
from wattnet.api.service.footprints import FootprintService
from wattnet.api.utils import validation as validation

router = APIRouter()

footprint_service = FootprintService()


@router.get(
    "",
    response_model=Union[List[FootprintAggregate], List[Footprint]],
    status_code=200,
    responses={
        200: {
            "description": "List of footprints matching the given filters",
            "model": Union[List[FootprintAggregate], List[Footprint]],
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
    summary="Retrieve environmental footprints",
    description="""
Retrieve a list of environmental footprints filtered by:

- `zone`: wattnet zone code (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup zone code.
- `footprint_type`: Type of footprint. Valid values: [carbon, water]
- `scope`: Scope of the footprint. Valid values: [operational, life-cycle]. Default is 'life-cycle'.
- `start` and `end`: Filter by datetime range (both required if one is provided).
- `aggregate`: If true, return aggregated footprints over the time range. If false (default), return time series grouped by status.
- `use_global`: If true (default), compute the global footprint including electricity exchanges via flow tracing. If false, use only the local footprint based on local generation.

If `lat` and `lon` are provided, the corresponding zone will be determined automatically.
""",
)
@version(1)
def get_footprints(
    zone: Optional[str] = Query(
        None,
        description="Filter by wattnet zone code (mutually exclusive with lat/lon)",
    ),
    lat: Optional[float] = Query(
        None, ge=-90, le=90, description="Latitude in decimal degrees (DD)"
    ),
    lon: Optional[float] = Query(
        None, ge=-180, le=180, description="Longitude in decimal degrees (DD)"
    ),
    footprint_type: Optional[str] = Query(
        None,
        description="Type of footprint to filter [carbon, water]. If not provided, all types are returned.",
    ),
    scope: Optional[str] = Query(
        "life-cycle",
        description="Filter footprints by scope [operational, life-cycle]. Default is 'life-cycle'.",
    ),
    start: Optional[datetime] = Query(
        None, description="Start datetime for filtering (ISO 8601 format)"
    ),
    end: Optional[datetime] = Query(
        None, description="End datetime for filtering (ISO 8601 format)"
    ),
    aggregate: bool = Query(
        False,
        description="If true, return aggregated footprints over the time range. If false (default), return time series grouped by status.",
    ),
    use_global: bool = Query(
        True,
        description="If true (default), compute the global footprint including electricity exchanges via flow tracing. If false, use only the local footprint based on local generation.",
    ),
):
    if start:
        start = validation.make_utc_aware(start)
    if end:
        end = validation.make_utc_aware(end)

    zone = validation.validate_location_filters(zone, lat, lon)
    validation.validate_footprint_type(footprint_type)
    validation.validate_scope(scope)
    validation.validate_time_range(start, end)

    footprints = footprint_service.get_footprints(
        zone=zone.upper() if zone else None,
        footprint_type=footprint_type.lower() if footprint_type else None,
        scope=scope.lower() if scope else "life-cycle",
        start=start,
        end=end,
        aggregate=aggregate,
        use_global=use_global,
    )

    return footprints
