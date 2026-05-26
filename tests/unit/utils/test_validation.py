"""
Unit tests for wattnet.api.utils.validation module.

These tests validate each validation function in isolation:
- validate_location_filters: zone/lat-lon mutual exclusion, geo lookup
- validate_time_range: completeness and ordering of start/end
- validate_aggregation_params: aggregate=True requires dates
- make_utc_aware: naive and aware datetime normalisation
- validate_footprint_type, validate_factor_type, validate_production_type
- validate_scope, validate_operational_scope
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from wattnet.api.utils.validation import (
    make_utc_aware,
    validate_aggregation_params,
    validate_factor_type,
    validate_footprint_type,
    validate_location_filters,
    validate_operational_scope,
    validate_production_type,
    validate_scope,
    validate_time_range,
)

_NOW = datetime(2025, 6, 1, 12, 0, 0, tzinfo=UTC)
_LATER = _NOW + timedelta(hours=2)

_GEO_PATH = "wattnet.api.utils.validation.geo.get_zone_code"


# ============================================================
# validate_location_filters
# ============================================================


def test_zone_only_returns_zone() -> None:
    """zone_id with no coordinates must be returned as-is."""
    assert validate_location_filters("ES", None, None) == "ES"


def test_all_none_returns_none() -> None:
    """No zone, no coordinates must return None."""
    assert validate_location_filters(None, None, None) is None


def test_zone_and_lat_raises_400() -> None:
    """Providing zone_id together with lat must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_location_filters("ES", 40.0, None)
    assert exc.value.status_code == 400


def test_zone_and_lon_raises_400() -> None:
    """Providing zone_id together with lon must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_location_filters("ES", None, -3.0)
    assert exc.value.status_code == 400


def test_only_lat_raises_400() -> None:
    """Providing lat without lon must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_location_filters(None, 40.0, None)
    assert exc.value.status_code == 400


def test_only_lon_raises_400() -> None:
    """Providing lon without lat must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_location_filters(None, None, -3.0)
    assert exc.value.status_code == 400


def test_lat_lon_found_returns_zone() -> None:
    """Valid coordinates returning a zone must return that zone code."""
    with patch(_GEO_PATH, return_value="ES"):
        result = validate_location_filters(None, 40.0, -3.0)
    assert result == "ES"


def test_lat_lon_not_found_raises_404() -> None:
    """Coordinates with no matching zone must raise 404."""
    with patch(_GEO_PATH, return_value=None):
        with pytest.raises(HTTPException) as exc:
            validate_location_filters(None, 0.0, 0.0)
    assert exc.value.status_code == 404


# ============================================================
# validate_time_range
# ============================================================


def test_time_range_both_none_passes() -> None:
    """Both start and end as None must not raise."""
    validate_time_range(None, None)


def test_time_range_valid_range_passes() -> None:
    """start < end must not raise."""
    validate_time_range(_NOW, _LATER)


def test_time_range_start_without_end_raises_400() -> None:
    """start without end must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_time_range(_NOW, None)
    assert exc.value.status_code == 400


def test_time_range_end_without_start_raises_400() -> None:
    """end without start must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_time_range(None, _LATER)
    assert exc.value.status_code == 400


def test_time_range_start_after_end_raises_400() -> None:
    """start > end must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_time_range(_LATER, _NOW)
    assert exc.value.status_code == 400


# ============================================================
# validate_aggregation_params
# ============================================================


def test_aggregate_false_no_dates_passes() -> None:
    """aggregate=False without dates must not raise."""
    validate_aggregation_params(False, None, None)


def test_aggregate_true_with_dates_passes() -> None:
    """aggregate=True with both dates must not raise."""
    validate_aggregation_params(True, _NOW, _LATER)


def test_aggregate_true_no_start_raises_400() -> None:
    """aggregate=True without start must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_aggregation_params(True, None, _LATER)
    assert exc.value.status_code == 400


def test_aggregate_true_no_end_raises_400() -> None:
    """aggregate=True without end must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_aggregation_params(True, _NOW, None)
    assert exc.value.status_code == 400


def test_aggregate_true_no_dates_raises_400() -> None:
    """aggregate=True without any dates must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_aggregation_params(True, None, None)
    assert exc.value.status_code == 400


# ============================================================
# make_utc_aware
# ============================================================


def test_make_utc_aware_naive_gets_utc() -> None:
    """Naive datetime must be returned with UTC timezone."""
    naive = datetime(2025, 6, 1, 12, 0, 0)
    result = make_utc_aware(naive)
    assert result.tzinfo is not None
    assert result.utcoffset().total_seconds() == 0


def test_make_utc_aware_utc_unchanged() -> None:
    """UTC-aware datetime must stay UTC."""
    result = make_utc_aware(_NOW)
    assert result.utcoffset().total_seconds() == 0


def test_make_utc_aware_non_utc_converted() -> None:
    """Non-UTC aware datetime must be converted to UTC."""
    cet = timezone(timedelta(hours=2))
    dt_cet = datetime(2025, 6, 1, 14, 0, 0, tzinfo=cet)
    result = make_utc_aware(dt_cet)
    assert result.utcoffset().total_seconds() == 0
    assert result.hour == 12


# ============================================================
# validate_footprint_type
# ============================================================


def test_footprint_type_none_passes() -> None:
    """None footprint_type must not raise."""
    validate_footprint_type(None)


def test_footprint_type_carbon_passes() -> None:
    """'carbon' must be accepted."""
    validate_footprint_type("carbon")


def test_footprint_type_water_passes() -> None:
    """'water' must be accepted."""
    validate_footprint_type("water")


def test_footprint_type_invalid_raises_400() -> None:
    """Unknown footprint_type must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_footprint_type("nuclear")
    assert exc.value.status_code == 400


# ============================================================
# validate_factor_type
# ============================================================


def test_factor_type_none_passes() -> None:
    """None factor_type must not raise."""
    validate_factor_type(None)


def test_factor_type_carbon_passes() -> None:
    """'carbon' must be accepted."""
    validate_factor_type("carbon")


def test_factor_type_water_passes() -> None:
    """'water' must be accepted."""
    validate_factor_type("water")


def test_factor_type_case_insensitive_passes() -> None:
    """Factor type check must be case-insensitive."""
    validate_factor_type("Carbon")


def test_factor_type_invalid_raises_400() -> None:
    """Unknown factor_type must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_factor_type("methane")
    assert exc.value.status_code == 400


# ============================================================
# validate_production_type
# ============================================================


def test_production_type_none_passes() -> None:
    """None production_type must not raise."""
    validate_production_type(None)


def test_production_type_solar_passes() -> None:
    """'solar' must be accepted."""
    validate_production_type("solar")


def test_production_type_wind_offshore_passes() -> None:
    """'wind_offshore' must be accepted."""
    validate_production_type("wind_offshore")


def test_production_type_case_insensitive_passes() -> None:
    """Production type check must be case-insensitive."""
    validate_production_type("Solar")


def test_production_type_invalid_raises_400() -> None:
    """Unknown production_type must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_production_type("fusion")
    assert exc.value.status_code == 400


# ============================================================
# validate_scope
# ============================================================


def test_scope_none_passes() -> None:
    """None scope must not raise."""
    validate_scope(None)


def test_scope_operational_passes() -> None:
    """'operational' must be accepted."""
    validate_scope("operational")


def test_scope_life_cycle_passes() -> None:
    """'life-cycle' must be accepted."""
    validate_scope("life-cycle")


def test_scope_invalid_raises_400() -> None:
    """Unknown scope must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_scope("political")
    assert exc.value.status_code == 400


# ============================================================
# validate_operational_scope
# ============================================================


def test_operational_scope_none_passes() -> None:
    """None scope must not raise."""
    validate_operational_scope(None)


def test_operational_scope_operational_passes() -> None:
    """'operational' must be accepted."""
    validate_operational_scope("operational")


def test_operational_scope_life_cycle_raises_400() -> None:
    """'life-cycle' is not allowed for operational-only endpoints."""
    with pytest.raises(HTTPException) as exc:
        validate_operational_scope("life-cycle")
    assert exc.value.status_code == 400


def test_operational_scope_invalid_raises_400() -> None:
    """Unknown scope must raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_operational_scope("global")
    assert exc.value.status_code == 400
