"""API router for footprint data endpoints."""

from datetime import datetime
from typing import List, Optional, Union

from fastapi import APIRouter, Query
from fastapi_versioning import version

from wattnet.api.dependencies import footprint_service
from wattnet.api.models.footprint import Footprint, FootprintAggregate
from wattnet.api.utils import validation as validation

router = APIRouter()

# Query parameter defaults
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

_footprint_type_query = Query(
    None,
    description=(
        "Type of footprint to filter [carbon, water]. "
        "If not provided, all types are returned."
    ),
)

_scope_query = Query(
    "life-cycle",
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

_aggregate_query = Query(
    False,
    description=(
        "If true, return aggregated footprints over the time range. "
        "If false (default), return time series grouped by status."
    ),
)

_use_global_query = Query(
    True,
    description=(
        "If true (default), compute the global footprint including "
        "electricity exchanges via flow tracing. If false, use only "
        "the local footprint based on local generation."
    ),
)


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
    description="""Retrieve a list of environmental footprints filtered by:

- `zone`: wattnet zone code
  (mutually exclusive with `lat` and `lon`).
- `lat` and `lon`: Coordinates to lookup zone code.
- `footprint_type`: Type of footprint. Valid values:
  [carbon, water]. If not provided, all types are returned.
- `scope`: Scope of the footprint. Valid values:
  [operational, life-cycle]. Default is 'life-cycle'.
- `start` and `end`: Filter by datetime range
  (both required if one is provided). If not provided,
  only last available data is returned.
- `aggregate`: If true, return aggregated footprints over
  the time range. If false (default), return time series
  grouped by status.
- `use_global`: If true (default), compute the global
  footprint including electricity exchanges via flow tracing.
  If false, use only the local footprint based on local
  generation.

If `lat` and `lon` are provided, the corresponding zone
will be determined automatically.

Note: If `aggregate` is true, `start` and `end` are required
to define the aggregation period.
""",
)
@version(1)
def get_footprints(
    zone: Optional[str] = _zone_query,
    lat: Optional[float] = _lat_query,
    lon: Optional[float] = _lon_query,
    footprint_type: Optional[str] = _footprint_type_query,
    scope: Optional[str] = _scope_query,
    start: Optional[datetime] = _start_query,
    end: Optional[datetime] = _end_query,
    aggregate: bool = _aggregate_query,
    use_global: bool = _use_global_query,
) -> Union[List[FootprintAggregate], List[Footprint]]:
    """Endpoint to retrieve environmental footprints filtered.

    :param zone: Main wattnet zone code (mutually exclusive with lat/lon)
    :type zone: Optional[str]

    :param lat: Latitude in decimal degrees (DD)
    :type lat: Optional[float]

    :param lon: Longitude in decimal degrees (DD)
    :type lon: Optional[float]

    :param footprint_type: Type of footprint to filter [carbon, water].
    If not provided, all types are returned.
    :type footprint_type: Optional[str]

    :param scope: Filter footprints by scope [operational, life-cycle].
    Default is 'life-cycle'.
    :type scope: Optional[str]

    :param start: Start datetime for filtering (ISO 8601 format).
    Datetime must be UTC or timezone-aware.
    (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)
    :type start: Optional[datetime]

    :param end: End datetime for filtering (ISO 8601 format).
    Datetime must be UTC or timezone-aware.
    (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)
    :type end: Optional[datetime]

    :param aggregate: If true, return aggregated footprints over the time range.
    If false (default), return time series grouped by status.
    :type aggregate: bool

    :param use_global: If true (default), compute the global footprint including
    electricity exchanges via flow tracing. If false, use only the local
    footprint based on local generation.
    :type use_global: bool

    :return: List of footprints matching the given filters
    :rtype: Union[List[FootprintAggregate], List[Footprint]]
    """
    if start:
        start = validation.make_utc_aware(start)
    if end:
        end = validation.make_utc_aware(end)

    zone = validation.validate_location_filters(zone, lat, lon)
    validation.validate_footprint_type(footprint_type)
    validation.validate_scope(scope)
    validation.validate_time_range(start, end)
    validation.validate_aggregation_params(aggregate, start, end)

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
