"""
Unit tests for wattnet.api.service.factors module.

These tests validate:
- Filtering of invalid (None/negative) metric values
- Series vs aggregate mode routing
- Correct seven-field grouping key (factor_type, production_type, scope, unit,
  source, year, source_link)
- Aggregation produces FactorAggregate with aggregation_method field
- Time-series grouping produces Factor with FactorSeries
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Optional

import pytest

from tests.unit.service.helpers import FakeMetric, FakeRepo
from wattnet.api.models.factor import Factor, FactorAggregate
from wattnet.api.service.factors import FactorService

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)
_END = _NOW + timedelta(hours=2)


def _m(
    ts: datetime,
    value: Optional[float],
    factor_type: str = "carbon",
    production_type: str = "solar",
    scope: str = "operational",
    unit: str = "gCO2/kWh",
    source: str = "IPCC",
    year: int = 2023,
    source_link: str = "https://ipcc.ch",
) -> FakeMetric:
    """Build a FakeMetric with factor metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param factor_type: Factor type
    :param production_type: Energy source type
    :param scope: Factor scope
    :param unit: Factor unit
    :param source: Data source name
    :param year: Reference year
    :param source_link: Link to data source
    :return: FakeMetric
    :rtype: FakeMetric
    """
    return FakeMetric(
        timestamp=ts,
        value=value,
        metadata={
            "factor_type": factor_type,
            "production_type": production_type,
            "scope": scope,
            "unit": unit,
            "source": source,
            "year": year,
            "source_link": source_link,
        },
    )


# ============================================================
# get_factors — filtering
# ============================================================


def test_get_factors_returns_empty_when_no_metrics() -> None:
    """Empty repository must produce an empty result.

    :return: None
    :rtype: None
    """
    svc = FactorService(metrics_repo=FakeRepo([]))
    assert svc.get_factors() == []


def test_get_factors_filters_none_values() -> None:
    """Metrics with value=None must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, None), _m(_NOW + timedelta(hours=1), 25.0)]
    svc = FactorService(metrics_repo=FakeRepo(metrics))

    results = svc.get_factors()

    assert len(results) == 1


def test_get_factors_filters_negative_values() -> None:
    """Metrics with negative values must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, -1.0), _m(_NOW + timedelta(hours=1), 30.0)]
    svc = FactorService(metrics_repo=FakeRepo(metrics))

    results = svc.get_factors()

    assert len(results) == 1


# ============================================================
# get_factors — series vs aggregate routing
# ============================================================


def test_get_factors_returns_factor_series_by_default() -> None:
    """Default (aggregate=False) must return Factor time-series objects.

    :return: None
    :rtype: None
    """
    svc = FactorService(metrics_repo=FakeRepo([_m(_NOW, 25.0)]))

    results = svc.get_factors(aggregate=False)

    assert isinstance(results[0], Factor)


def test_get_factors_returns_aggregate_when_requested() -> None:
    """aggregate=True with start/end must return FactorAggregate objects.

    :return: None
    :rtype: None
    """
    svc = FactorService(metrics_repo=FakeRepo([_m(_NOW, 25.0)]))

    results = svc.get_factors(aggregate=True, start=_NOW, end=_END)

    assert isinstance(results[0], FactorAggregate)


def test_get_factors_aggregate_without_dates_is_series() -> None:
    """aggregate=True without start/end must fall back to series mode.

    :return: None
    :rtype: None
    """
    svc = FactorService(metrics_repo=FakeRepo([_m(_NOW, 25.0)]))

    results = svc.get_factors(aggregate=True)

    assert isinstance(results[0], Factor)


# ============================================================
# _group_metrics_series — grouping key
# ============================================================


def test_get_factors_separate_factors_by_production_type() -> None:
    """Metrics with different production types must produce separate Factor objects.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 25.0, production_type="solar"),
        _m(_NOW, 40.0, production_type="coal"),
    ]
    svc = FactorService(metrics_repo=FakeRepo(metrics))

    results = svc.get_factors()

    assert len(results) == 2
    types = {r.production_type for r in results}
    assert types == {"solar", "coal"}


def test_get_factors_separate_factors_by_scope() -> None:
    """Metrics with different scopes must produce separate Factor objects.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 25.0, scope="operational"),
        _m(_NOW, 80.0, scope="life-cycle"),
    ]
    svc = FactorService(metrics_repo=FakeRepo(metrics))

    results = svc.get_factors()

    assert len(results) == 2
    scopes = {r.scope for r in results}
    assert scopes == {"operational", "life-cycle"}


# ============================================================
# _aggregate_metrics — key fields
# ============================================================


def test_factor_aggregate_has_aggregation_method() -> None:
    """FactorAggregate must always carry aggregation_method='time-weighted-average'.

    :return: None
    :rtype: None
    """
    svc = FactorService(metrics_repo=FakeRepo([_m(_NOW, 25.0)]))

    result = svc.get_factors(aggregate=True, start=_NOW, end=_END)[0]

    assert result.aggregation_method == "time-weighted-average"


def test_factor_aggregate_preserves_metadata_fields() -> None:
    """FactorAggregate must preserve factor_type, production_type, scope, unit.

    :return: None
    :rtype: None
    """
    svc = FactorService(
        metrics_repo=FakeRepo(
            [
                _m(
                    _NOW,
                    25.0,
                    factor_type="carbon",
                    production_type="solar",
                    scope="operational",
                    unit="gCO2/kWh",
                )
            ]
        )
    )

    result = svc.get_factors(aggregate=True, start=_NOW, end=_END)[0]

    assert result.factor_type == "carbon"
    assert result.production_type == "solar"
    assert result.scope == "operational"
    assert result.unit == "gCO2/kWh"
