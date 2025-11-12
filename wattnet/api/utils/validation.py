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


def validate_location_filters(
    zone_id: Optional[str], lat: Optional[float], lon: Optional[float]
) -> Optional[str]:
    if zone_id and (lat is not None or lon is not None):
        raise HTTPException(
            status_code=400,
            detail="If zone_id is provided, latitude and longitude must NOT be provided",
        )
    if (lat is not None) != (lon is not None):
        raise HTTPException(
            status_code=400,
            detail="Both latitude and longitude must be provided together",
        )
    if lat is not None and lon is not None:
        zone_id_from_coords = geo.get_zone_code(lat, lon)
        if not zone_id_from_coords:
            raise HTTPException(
                status_code=404,
                detail="No zone found for the provided coordinates",
            )
        return zone_id_from_coords
    return zone_id


def validate_footprint_type(footprint_type: Optional[str]):
    if footprint_type is not None and footprint_type not in VALID_FOOTPRINT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid footprint_type '{footprint_type}'. Valid values are {sorted(VALID_FOOTPRINT_TYPES)}",
        )


def validate_factor_type(factor_type: Optional[str]):
    if factor_type is not None and factor_type.lower() not in VALID_FACTOR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid factor_type '{factor_type}'. "
                f"Valid values are: {sorted(VALID_FACTOR_TYPES)}"
            ),
        )


def validate_production_type(production_type: Optional[str]):
    if (
        production_type is not None
        and production_type.lower() not in VALID_PRODUCTION_TYPES
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid production_type '{production_type}'. "
                f"Valid values are: {sorted(VALID_PRODUCTION_TYPES)}"
            ),
        )


def validate_scope(scope: Optional[str]):
    if scope is not None and scope.lower() not in VALID_SCOPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid scope '{scope}'. " f"Valid values are: {sorted(VALID_SCOPES)}"
            ),
        )


def make_utc_aware(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo("UTC"))


def validate_time_range(start: Optional[datetime], end: Optional[datetime]):
    if (start and not end) or (end and not start):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both start and end datetimes must be provided",
        )
    if start and end and start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start datetime must be before end datetime",
        )
