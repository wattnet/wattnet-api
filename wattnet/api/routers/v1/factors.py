from datetime import datetime
from typing import List, Optional, Union

from fastapi import APIRouter, Query, status
from fastapi_versioning import version

from wattnet.api.dependencies import factor_service
from wattnet.api.models.factor import Factor, FactorAggregate
from wattnet.api.utils import validation as validation

router = APIRouter()


@router.get(
    "",
    response_model=Union[List[FactorAggregate], List[Factor]],
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "List of factors matching the given filters",
            "model": Union[List[FactorAggregate], List[Factor]],
        },
        400: {
            "description": "Invalid input parameters",
            "content": {"application/json": {"example": {"detail": "Error message"}}},
        },
    },
    summary="Retrieve factors",
    description="""
Retrieve a list of factors filtered by:

- `factor_type`: Type of factor. Valid values: carbon, water. If not provided, all types are returned.
- `scope`: Scope of the factor. Valid values: operational, life-cycle. If not provided, all scopes are returned.
- `production_type`: Production type filter. Valid values include: biomass, coal, gas, geothermal, hydro_reservoir, hydro_river, marine, nuclear, oil, other, other_renewable, solar, waste, wind_offshore, wind_onshore.
- `start` and `end`: Datetime range to filter factors (both required if one is provided). If not provided, only last available data is returned.
- `aggregate`: If true, return aggregated footprints over the time range. If false (default), return time series grouped by fields.

Note: If `aggregate` is true, `start` and `end` are required to define the aggregation period.
""",
)
@version(1)
def get_factors(
    factor_type: Optional[str] = Query(
        None,
        description="Filter factors by type [carbon, water]. If not provided, all types are returned.",
    ),
    scope: Optional[str] = Query(
        None,
        description="Filter factors by scope [operational, life-cycle]. If not provided, all scopes are returned.",
    ),
    production_type: Optional[str] = Query(
        None,
        description=(
            "Filter factors by production type. Valid values: biomass, coal, gas, geothermal, hydro_reservoir, hydro_river, marine, nuclear, oil, other, other_renewable, solar, waste, wind_offshore, wind_onshore If not provided, all types are returned."
        ),
    ),
    start: Optional[datetime] = Query(
        None,
        description="Start datetime for filtering (ISO 8601 format). Datetime must be UTC or timezone-aware. (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)",
    ),
    end: Optional[datetime] = Query(
        None,
        description="End datetime for filtering (ISO 8601 format). Datetime must be UTC or timezone-aware. (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00)",
    ),
    aggregate: Optional[bool] = Query(
        False,
        description="If true, return aggregated factors over the time range. If false (default), return time series grouped by fields.",
    ),
):

    print(type(start))

    # Make sure start and end are UTC aware
    if start:
        print(start)
        start = validation.make_utc_aware(start)
        print(start)
    if end:
        end = validation.make_utc_aware(end)

    # Validate inputs
    validation.validate_factor_type(factor_type)
    validation.validate_scope(scope)
    validation.validate_production_type(production_type)
    validation.validate_time_range(start, end)

    return factor_service.get_factors(
        factor_type=factor_type.lower() if factor_type else None,
        scope=scope.lower() if scope else None,
        production_type=production_type.lower() if production_type else None,
        start=start,
        end=end,
        aggregate=aggregate,
    )
