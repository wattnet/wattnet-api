"""Validation utilities for wattnet API endpoints."""

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import Request, status
from fastapi.dependencies.utils import get_flat_dependant

from wattnet.api.errors import ApiError
from wattnet.api.service import geo

VALID_FOOTPRINT_TYPES = {"carbon", "water"}
VALID_FACTOR_TYPES = {"carbon", "water"}
VALID_IMPACT_TYPES = {"water"}
VALID_PRODUCTION_TYPES = {
    "biomass",
    "coal",
    "gas",
    "geothermal",
    "hydro_pumped_storage",
    "hydro_reservoir",
    "hydro_river",
    "marine",
    "nuclear",
    "oil",
    "other",
    "other_renewable",
    "solar",
    "waste",
    "wind_offshore",
    "wind_onshore",
}
VALID_SCOPES = {"operational", "life-cycle"}
VALID_OPERATIONAL_SCOPE = {"operational"}


def validate_location_filters(
    zone: Optional[str], lat: Optional[float], lon: Optional[float]
) -> Optional[str]:
    """Validate zone and lat/lon inputs.

    Validate that either zone or lat/lon are provided (but not both),
    and return the resolved zone.

    :param zone: wattnet zone code (mutually exclusive with lat/lon)
    :type zone: Optional[str]

    :param lat: Latitude in decimal degrees (DD)
    :type lat: Optional[float]

    :param lon: Longitude in decimal degrees (DD)
    :type lon: Optional[float]

    :raises HTTPException: If validation fails:
        - If both zone and lat/lon are provided (400)
        - If only one of lat or lon is provided (400)
        - If lat/lon are provided but no zone is found for those coordinates (404)
    """
    if zone and (lat is not None or lon is not None):
        raise ApiError(
            status_code=400,
            code="zone_and_coordinates_conflict",
            detail="If zone is provided, latitude and longitude must NOT be provided.",
        )
    if (lat is not None) != (lon is not None):
        raise ApiError(
            status_code=400,
            code="coordinates_incomplete",
            detail="Both latitude and longitude must be provided together.",
        )
    if lat is not None and lon is not None:
        zone_from_coords = geo.get_zone_code(lat, lon)
        if not zone_from_coords:
            raise ApiError(
                status_code=404,
                code="zone_not_found_for_coordinates",
                detail="No zone found for the provided coordinates.",
            )
        return zone_from_coords
    return zone


def validate_footprint_type(footprint_type: Optional[str]) -> None:
    """Validate that footprint_type is one of the allowed values.

    :param footprint_type: Type of footprint to filter (e.g., carbon, water)
    :type footprint_type: Optional[str]

    :raises HTTPException: If footprint_type is invalid (400)
    """
    if (
        footprint_type is not None
        and footprint_type.lower() not in VALID_FOOTPRINT_TYPES
    ):
        raise ApiError(
            status_code=400,
            code="invalid_footprint_type",
            detail=f"Invalid footprint_type '{footprint_type}'. "
            + f"Valid values are {sorted(VALID_FOOTPRINT_TYPES)}",
        )


def validate_factor_type(factor_type: Optional[str]) -> None:
    """Validate that factor_type is one of the allowed values.

    :param factor_type: Type of factor to filter (e.g., carbon, water)
    :type factor_type: Optional[str]

    :raises HTTPException: If factor_type is invalid (400)
    """
    if factor_type is not None and factor_type.lower() not in VALID_FACTOR_TYPES:
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="invalid_factor_type",
            detail=(
                f"Invalid factor_type '{factor_type}'. "
                f"Valid values are: {sorted(VALID_FACTOR_TYPES)}."
            ),
        )


def validate_impact_type(impact_type: Optional[str]) -> None:
    """Validate that impact_type is one of the allowed values.

    :param impact_type: Type of impact to filter (e.g., water)
    :type impact_type: Optional[str]

    :raises HTTPException: If impact_type is invalid (400)
    """
    if impact_type is not None and impact_type.lower() not in VALID_IMPACT_TYPES:
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="invalid_impact_type",
            detail=(
                f"Invalid impact_type '{impact_type}'. "
                f"Valid values are: {sorted(VALID_IMPACT_TYPES)}."
            ),
        )


def validate_production_type(production_type: Optional[str]) -> None:
    """Validate that production_type is one of the allowed values.

    :param production_type: Type of production to filter (e.g., solar, wind, hydro)
    :type production_type: Optional[str]

    :raises HTTPException: If production_type is invalid (400)
    """
    if (
        production_type is not None
        and production_type.lower() not in VALID_PRODUCTION_TYPES
    ):
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="invalid_production_type",
            detail=(
                f"Invalid production_type '{production_type}'. "
                f"Valid values are: {sorted(VALID_PRODUCTION_TYPES)}."
            ),
        )


def validate_scope(scope: Optional[str]) -> None:
    """Validate that scope is one of the allowed values.

    :param scope: Scope to filter (e.g., operational, life-cycle)
    :type scope: Optional[str]

    :raises HTTPException: If scope is invalid (400)
    """
    if scope is not None and scope.lower() not in VALID_SCOPES:
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="invalid_scope",
            detail=(
                f"Invalid scope '{scope}'. Valid values are: {sorted(VALID_SCOPES)}."
            ),
        )


def validate_operational_scope(scope: Optional[str]) -> None:
    """Validate that scope is operational when provided.

    :param scope: Scope to filter (operational only)
    :type scope: Optional[str]

    :raises HTTPException: If scope is invalid (400)
    """
    if scope is not None and scope.lower() not in VALID_OPERATIONAL_SCOPE:
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="invalid_operational_scope",
            detail=(
                f"Invalid scope '{scope}'. Valid values are: "
                f"{sorted(VALID_OPERATIONAL_SCOPE)}."
            ),
        )


def make_utc_aware(dt: datetime) -> datetime:
    """Convert a datetime to UTC timezone-aware datetime.

    :param dt: Datetime to convert
    :type dt: datetime
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo("UTC"))


def validate_time_range(start: Optional[datetime], end: Optional[datetime]) -> None:
    """Validate datetime range inputs.

    Validate that start and end datetimes are both provided together
    and that start is before end.

    :param start: Start datetime for filtering
    :type start: Optional[datetime]

    :param end: End datetime for filtering
    :type end: Optional[datetime]

    :raises HTTPException: If validation fails (400)
    """
    if (start and not end) or (end and not start):
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="time_range_incomplete",
            detail="Both start and end datetimes must be provided.",
        )
    if start and end and start > end:
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="time_range_inverted",
            detail="start datetime must be before end datetime.",
        )


def validate_aggregation_params(
    aggregate: bool,
    start: Optional[datetime],
    end: Optional[datetime],
) -> None:
    """Validate that if aggregate=True, then start and end datetimes are provided.

    :param aggregate: Whether to aggregate data over time intervals
    :type aggregate: bool

    :param start: Start datetime for filtering
    :type start: Optional[datetime]

    :param end: End datetime for filtering
    :type end: Optional[datetime]

    :raises HTTPException: If validation fails (400)
    """
    if aggregate and (start is None or end is None):
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="aggregate_requires_time_range",
            detail="start and end datetimes are required when aggregate=True.",
        )


def validate_query_parameters(request: Request) -> None:
    """Refuse a query string that the endpoint would otherwise read in silence.

    No parameter of the API is a list, so a repeated one has no meaning: the
    server would keep one value and drop the rest. A name the endpoint does not
    know (a typo such as ``zon``) would be ignored and widen the query, and an
    empty value (``zone=``) would count as not sent.

    :param request: The request being served
    :type request: Request

    :raises HTTPException: 400 for an unknown, repeated or empty parameter
    """
    dependant = get_flat_dependant(request.scope["route"].dependant)
    known = {p.alias for p in dependant.query_params}
    seen: set[str] = set()
    for name, value in request.query_params.multi_items():
        if name not in known:
            raise ApiError(
                status_code=400,
                code="unknown_parameter",
                detail=(
                    f"Unknown query parameter '{name}'. "
                    f"Accepted: {', '.join(sorted(known)) or 'none'}."
                ),
            )
        if name in seen:
            raise ApiError(
                status_code=400,
                code="repeated_parameter",
                detail=f"The query parameter '{name}' is repeated; send it once.",
            )
        if value == "":
            raise ApiError(
                status_code=400,
                code="empty_parameter",
                detail=f"The query parameter '{name}' is empty; give it a value.",
            )
        seen.add(name)
