"""Validation utilities for wattnet API endpoints."""

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status

from wattnet.api.service import geo

VALID_FOOTPRINT_TYPES = {"carbon", "water"}
VALID_FACTOR_TYPES = {"carbon", "water"}
VALID_PRODUCTION_TYPES = {
    "biomass",
    "coal",
    "gas",
    "geothermal",
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
    zone_id: Optional[str], lat: Optional[float], lon: Optional[float]
) -> Optional[str]:
    """Validate zone_id and lat/lon inputs.

    Validate that either zone_id or lat/lon are provided (but not both),
    and return the resolved zone_id.

    :param zone_id: wattnet zone code (mutually exclusive with lat/lon)
    :type zone_id: Optional[str]

    :param lat: Latitude in decimal degrees (DD)
    :type lat: Optional[float]

    :param lon: Longitude in decimal degrees (DD)
    :type lon: Optional[float]

    :raises HTTPException: If validation fails:
        - If both zone_id and lat/lon are provided (400)
        - If only one of lat or lon is provided (400)
        - If lat/lon are provided but no zone is found for those coordinates (404)
    """
    if zone_id and (lat is not None or lon is not None):
        raise HTTPException(
            status_code=400,
            detail="If zone_id is provided, latitude and longitude"
            "must NOT be provided.",
        )
    if (lat is not None) != (lon is not None):
        raise HTTPException(
            status_code=400,
            detail="Both latitude and longitude must be provided together.",
        )
    if lat is not None and lon is not None:
        zone_id_from_coords = geo.get_zone_code(lat, lon)
        if not zone_id_from_coords:
            raise HTTPException(
                status_code=404,
                detail="No zone found for the provided coordinates.",
            )
        return zone_id_from_coords
    return zone_id


def validate_footprint_type(footprint_type: Optional[str]) -> None:
    """Validate that footprint_type is one of the allowed values.

    :param footprint_type: Type of footprint to filter (e.g., carbon, water)
    :type footprint_type: Optional[str]

    :raises HTTPException: If footprint_type is invalid (400)
    """
    if footprint_type is not None and footprint_type not in VALID_FOOTPRINT_TYPES:
        raise HTTPException(
            status_code=400,
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid factor_type '{factor_type}'. "
                f"Valid values are: {sorted(VALID_FACTOR_TYPES)}."
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both start and end datetimes must be provided.",
        )
    if start and end and start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start and end datetimes are required when aggregate=True.",
        )
