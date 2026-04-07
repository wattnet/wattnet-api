"""API router for score endpoints in the wattnet API application."""

from datetime import datetime
from typing import List, Optional, Union

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import score_service
from wattnet.api.models.score import GreenScore, GreenScoreAggregate
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
_scope_query = Query(
    "life-cycle",
    description="Filter by scope [operational, life-cycle]. Default is 'life-cycle'.",
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
        "If true, return aggregated scores over the time range. "
        "If false (default), return time series grouped by status."
    ),
)
_use_global_query = Query(
    True,
    description=(
        "If true (default), return the global score based on global impacts "
        "and footprints including electricity exchanges. If false, use only "
        "local generation data."
    ),
)


@router.get(
    "",
    response_model=Union[List[GreenScoreAggregate], List[GreenScore]],
    status_code=200,
    responses={
        200: {
            "description": "List of scores matching the given filters",
            "model": Union[List[GreenScoreAggregate], List[GreenScore]],
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
    summary="Retrieve GreenScore metrics",
    description="""Retrieve GreenScore metrics filtered by:

- `zone`: wattnet zone code (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup zone code.
- `scope`: Scope of the score. Valid values: [operational, life-cycle].
  Default is 'life-cycle'.
- `start` and `end`: Filter by datetime range (both required if one is
  provided). If not provided, only last available data is returned.
- `aggregate`: If true, return aggregated scores over the time range.
  If false (default), return time series grouped by status.
- `use_global`: If true (default), return the global score based on
  global impacts and footprints including electricity exchanges.
  If false, use only local generation data.

If `lat` and `lon` are provided, the corresponding zone will be
determined automatically.

Note: If `aggregate` is true, `start` and `end` are required.
""",
)
@version(1)
def get_scores(
    zone: Optional[str] = _zone_query,
    lat: Optional[float] = _lat_query,
    lon: Optional[float] = _lon_query,
    scope: Optional[str] = _scope_query,
    start: Optional[datetime] = _start_query,
    end: Optional[datetime] = _end_query,
    aggregate: bool = _aggregate_query,
    use_global: bool = _use_global_query,
) -> Union[List[GreenScoreAggregate], List[GreenScore]]:
    """Endpoint to retrieve GreenScore metrics."""
    if start:
        start = validation.make_utc_aware(start)
    if end:
        end = validation.make_utc_aware(end)

    zone = validation.validate_location_filters(zone, lat, lon)
    validation.validate_scope(scope)
    validation.validate_time_range(start, end)
    validation.validate_aggregation_params(aggregate, start, end)

    return score_service.get_scores(
        zone=zone.upper() if zone else None,
        scope=scope.lower() if scope else "life-cycle",
        start=start,
        end=end,
        aggregate=aggregate,
        use_global=use_global,
    )
