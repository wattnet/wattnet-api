"""
Unit tests for wattnet.api.service.mix module.

These tests validate:
- Filtering of invalid (None/negative) metric values
- Hierarchical grouping: Mix → MixSeries → MixBlock
- Pruning of empty series and empty top-level Mix objects
- Separation into blocks by (production_type, data_state, datasource)
- Chronological ordering of values within blocks
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from tests.unit.service.helpers import FakeMetric, FakeRepo
from wattnet.api.service.mix import MixService

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)


def _m(
    ts: datetime,
    value: float | None,
    zone: str = "ES",
    unit: str = "MW",
    production_type: str = "solar",
    data_state: str = "official",
    datasource: str = "flow_tracing",
    valid: bool = True,
    zone_status: str = "complete",
) -> FakeMetric:
    """Build a FakeMetric with mix metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param zone: Zone code
    :param unit: Energy unit
    :param production_type: Energy source type
    :param data_state: Data state
    :param datasource: Data source
    :param valid: Validity flag
    :param zone_status: Zone status
    :return: FakeMetric
    :rtype: FakeMetric
    """
    return FakeMetric(
        timestamp=ts,
        value=value,
        metadata={
            "zone": zone,
            "unit": unit,
            "production_type": production_type,
            "data_state": data_state,
            "datasource": datasource,
            "valid": valid,
            "zone_status": zone_status,
        },
    )


# ============================================================
# get_mix — basic filtering
# ============================================================


def test_get_mix_returns_empty_when_no_metrics() -> None:
    """Empty repository must produce an empty result.

    :return: None
    :rtype: None
    """
    svc = MixService(metrics_repo=FakeRepo([]))
    assert svc.get_mix() == []


def test_get_mix_filters_none_values() -> None:
    """Metrics with value=None must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, None), _m(_NOW + timedelta(hours=1), 300.0)]
    svc = MixService(metrics_repo=FakeRepo(metrics))

    results = svc.get_mix()

    assert len(results) == 1
    assert results[0].series[0].production[0].values[0][1] == pytest.approx(300.0)


def test_get_mix_filters_negative_values() -> None:
    """Metrics with negative values must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, -10.0), _m(_NOW + timedelta(hours=1), 150.0)]
    svc = MixService(metrics_repo=FakeRepo(metrics))

    results = svc.get_mix()

    assert len(results) == 1
    assert results[0].series[0].production[0].values[0][1] == pytest.approx(150.0)


# ============================================================
# _group_metrics — structure
# ============================================================


def test_get_mix_one_object_per_zone() -> None:
    """Metrics for separate zones must produce separate Mix objects.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, 100.0, zone="ES"), _m(_NOW, 200.0, zone="FR")]
    svc = MixService(metrics_repo=FakeRepo(metrics))

    results = svc.get_mix()

    assert len(results) == 2
    assert {r.zone for r in results} == {"ES", "FR"}


def test_get_mix_separate_blocks_by_production_type() -> None:
    """Different production types must produce separate MixBlock objects.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, production_type="solar"),
        _m(_NOW, 80.0, production_type="wind_onshore"),
    ]
    svc = MixService(metrics_repo=FakeRepo(metrics))

    blocks = svc.get_mix()[0].series[0].production

    assert {b.production_type for b in blocks} == {"solar", "wind_onshore"}


def test_get_mix_separate_series_by_validity() -> None:
    """Different (valid, zone_status) pairs must create separate MixSeries.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, valid=True, zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 80.0, valid=False, zone_status="preview"),
    ]
    svc = MixService(metrics_repo=FakeRepo(metrics))

    results = svc.get_mix()

    assert len(results[0].series) == 2


def test_get_mix_block_values_sorted_by_timestamp() -> None:
    """Values within a block must be sorted ascending by timestamp.

    :return: None
    :rtype: None
    """
    t0 = _NOW
    t2 = _NOW + timedelta(hours=2)
    t1 = _NOW + timedelta(hours=1)

    metrics = [_m(t0, 1.0), _m(t2, 3.0), _m(t1, 2.0)]
    svc = MixService(metrics_repo=FakeRepo(metrics))

    values = svc.get_mix()[0].series[0].production[0].values

    assert values[0][0] == t0
    assert values[1][0] == t1
    assert values[2][0] == t2
