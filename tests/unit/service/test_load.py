"""
Unit tests for wattnet.api.service.load module.

These tests validate:
- Filtering of invalid (None/negative) metric values
- Hierarchical grouping: Load → LoadSeries → LoadBlock
- Separation into series by (valid, zone_status) pairs
- Separation into blocks by (data_state, datasource)
- Chronological ordering of values within blocks
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from tests.unit.service.helpers import FakeMetric, FakeRepo
from wattnet.api.service.load import LoadService

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)


def _m(
    ts: datetime,
    value: float | None,
    zone: str = "ES",
    unit: str = "MW",
    data_state: str = "official",
    datasource: str = "ENTSO-E",
    valid: bool = True,
    zone_status: str = "complete",
) -> FakeMetric:
    """Build a FakeMetric with load metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param zone: Zone code
    :param unit: Energy unit
    :param data_state: Data state
    :param datasource: Data provider
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
            "data_state": data_state,
            "datasource": datasource,
            "valid": valid,
            "zone_status": zone_status,
        },
    )


# ============================================================
# get_load — basic filtering
# ============================================================


def test_get_load_returns_empty_when_no_metrics() -> None:
    """Empty repository must produce an empty result.

    :return: None
    :rtype: None
    """
    svc = LoadService(metrics_repo=FakeRepo([]))
    assert svc.get_load() == []


def test_get_load_filters_none_values() -> None:
    """Metrics with value=None must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, None), _m(_NOW + timedelta(hours=1), 5000.0)]
    svc = LoadService(metrics_repo=FakeRepo(metrics))

    results = svc.get_load()

    assert len(results) == 1
    assert results[0].series[0].blocks[0].values[0][1] == pytest.approx(5000.0)


def test_get_load_filters_negative_values() -> None:
    """Metrics with negative values must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, -1.0), _m(_NOW + timedelta(hours=1), 3000.0)]
    svc = LoadService(metrics_repo=FakeRepo(metrics))

    results = svc.get_load()

    assert len(results) == 1
    assert results[0].series[0].blocks[0].values[0][1] == pytest.approx(3000.0)


# ============================================================
# _group_metrics — structure
# ============================================================


def test_get_load_one_object_per_zone() -> None:
    """Metrics for separate zones must produce separate Load objects.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, 1000.0, zone="ES"), _m(_NOW, 2000.0, zone="FR")]
    svc = LoadService(metrics_repo=FakeRepo(metrics))

    results = svc.get_load()

    assert len(results) == 2
    assert {r.zone for r in results} == {"ES", "FR"}


def test_get_load_separate_series_by_validity() -> None:
    """Different (valid, zone_status) pairs must create separate LoadSeries.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 1000.0, valid=True, zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 900.0, valid=False, zone_status="preview"),
    ]
    svc = LoadService(metrics_repo=FakeRepo(metrics))

    results = svc.get_load()

    assert len(results[0].series) == 2


def test_get_load_separate_blocks_by_data_state() -> None:
    """Different data_state values in the same series must produce separate blocks.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 1000.0, data_state="official"),
        _m(_NOW + timedelta(hours=1), 900.0, data_state="estimated"),
    ]
    svc = LoadService(metrics_repo=FakeRepo(metrics))

    blocks = svc.get_load()[0].series[0].blocks

    assert {b.data_state for b in blocks} == {"official", "estimated"}


def test_get_load_block_values_sorted_by_timestamp() -> None:
    """Values within a block must be sorted ascending by timestamp.

    :return: None
    :rtype: None
    """
    t0 = _NOW
    t2 = _NOW + timedelta(hours=2)
    t1 = _NOW + timedelta(hours=1)

    metrics = [_m(t0, 1.0), _m(t2, 3.0), _m(t1, 2.0)]
    svc = LoadService(metrics_repo=FakeRepo(metrics))

    values = svc.get_load()[0].series[0].blocks[0].values

    assert values[0][0] == t0
    assert values[1][0] == t1
    assert values[2][0] == t2
