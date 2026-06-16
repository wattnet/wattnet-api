"""API router for impact endpoints in the wattnet API application."""

from datetime import datetime
from typing import List, Optional, Union

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import impact_service
from wattnet.api.models.impact import Impact, ImpactAggregate
from wattnet.api.utils import validation

router = APIRouter()

_zone_query = Query(
    None,
    description="Filter by wattnet zone code (mutually exclusive with lat/lon)",
)
_lat_query = Query(None, ge=-90, le=90, description="Latitude in decimal degrees (DD)")
_lon_query = Query(
    None, ge=-180, le=180, description="Longitude in decimal degrees (DD)"
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
_aggregate_query = Query(
    False,
    description=(
        "If true, return aggregated impacts over the time range. "
        "If false (default), return time series grouped by status."
    ),
)
_use_global_query = Query(
    True,
    description=(
        "If true (default), return the global impact including electricity "
        "exchanges via flow tracing. If false, use only the local impact "
        "based on local generation."
    ),
)


@router.get(
    "",
    response_model=Union[List[ImpactAggregate], List[Impact]],
    status_code=200,
    responses={
        200: {
            "description": "List of impacts matching the given filters",
            "model": Union[List[ImpactAggregate], List[Impact]],
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
    summary="Retrieve environmental impacts",
    description="""Retrieve a list of environmental impacts filtered by:

- `zone`: wattnet zone code (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup zone code.
- `impact_type`: Type of impact. Valid values: [water].
    If not provided, all types are returned.
- `scope`: Scope of the impact. Valid values: [operational].
    Default is 'operational'.
- `start` and `end`: Filter by datetime range (both required if one is
    provided). If not provided, only last available data is returned.
- `aggregate`: If true, return aggregated impacts over the time range.
    If false (default), return time series grouped by status.
- `use_global`: If true (default), return the global impact including
    electricity exchanges via flow tracing. If false, use only the local
    impact based on local generation.

If `lat` and `lon` are provided, the corresponding zone will be
determined automatically.

Note: If `aggregate` is true, `start` and `end` are required.
""",
)
@version(1)
def get_impacts(
    zone: Optional[str] = _zone_query,
    lat: Optional[float] = _lat_query,
    lon: Optional[float] = _lon_query,
    impact_type: Optional[str] = _impact_type_query,
    scope: Optional[str] = _scope_query,
    start: Optional[datetime] = _start_query,
    end: Optional[datetime] = _end_query,
    aggregate: bool = _aggregate_query,
    use_global: bool = _use_global_query,
) -> Union[List[ImpactAggregate], List[Impact]]:
    """Endpoint to retrieve environmental impacts."""
    if start:
        start = validation.make_utc_aware(start)
    if end:
        end = validation.make_utc_aware(end)

    zone = validation.validate_location_filters(zone, lat, lon)
    validation.validate_impact_type(impact_type)
    validation.validate_operational_scope(scope)
    validation.validate_time_range(start, end)
    validation.validate_aggregation_params(aggregate, start, end)

    return impact_service.get_impacts(
        zone=zone.upper() if zone else None,
        impact_type=impact_type.lower() if impact_type else "water",
        scope=scope.lower() if scope else "operational",
        start=start,
        end=end,
        aggregate=aggregate,
        use_global=use_global,
    )
