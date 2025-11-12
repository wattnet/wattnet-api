from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query, status
from fastapi_versioning import version

from wattnet.api.models.factor import Factor as FactorSchema
from wattnet.api.service.factors import FactorService
from wattnet.api.utils import validation as validation

router = APIRouter()
factor_service = FactorService()


@router.get(
    "",
    response_model=List[FactorSchema],
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "List of factors matching the given filters",
            "model": List[FactorSchema],
        },
        400: {
            "description": "Invalid input parameters",
            "content": {"application/json": {"example": {"detail": "Error message"}}},
        },
    },
    summary="Retrieve factors",
    description="""
Retrieve a list of factors filtered by:

- `factor_type`: Type of factor. Valid values: carbon, water.
- `scope`: Scope of the factor. Valid values: operational, life-cycle.
- `production_type`: Production type filter. Valid values include: biomass, coal, gas, geothermal, hydro_reservoir, hydro_river, marine, nuclear, oil, other, other_renewable, solar, waste, wind_offshore, wind_onshore.
- `start` and `end`: Datetime range to filter factors.

Note: Both `start` and `end` must be provided together.
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
            "Filter factors by production type. Valid values: biomass, coal, gas, geothermal, hydro_reservoir, "
            "hydro_river, marine, nuclear, oil, other, other_renewable, solar, waste, wind_offshore, wind_onshore"
        ),
    ),
    start: Optional[datetime] = Query(
        None, description="Start datetime for filtering (ISO 8601 format)"
    ),
    end: Optional[datetime] = Query(
        None, description="End datetime for filtering (ISO 8601 format)"
    ),
):

    # Make sure start and end are UTC aware
    if start:
        start = validation.make_utc_aware(start)
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
    )
