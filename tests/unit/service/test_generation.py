"""
Unit tests for wattnet.api.service.generation module.

These tests validate:
- Filtering of invalid (None/negative) metric values
- Hierarchical grouping: Generation → GenerationSeries → ProductionBlock
- Separation into series by (valid, zone_status) pairs
- Separation into blocks by (production_type, data_state, datasource)
- Chronological ordering of values within blocks
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tests.unit.service.helpers import FakeMetric, FakeRepo
from wattnet.api.service.generation import GenerationService

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)


def _m(
    ts: datetime,
    value: float | None,
    zone: str = "ES",
    unit: str = "MW",
    production_type: str = "solar",
    data_state: str = "official",
    datasource: str = "ENTSO-E",
    valid: bool = True,
    zone_status: str = "complete",
) -> FakeMetric:
    """Build a FakeMetric with generation metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param zone: Zone code
    :param unit: Energy unit
    :param production_type: Energy source type
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
            "production_type": production_type,
            "data_state": data_state,
            "datasource": datasource,
            "valid": valid,
            "zone_status": zone_status,
        },
    )


# ============================================================
# get_generation — basic filtering
# ============================================================


def test_get_generation_returns_empty_when_no_metrics() -> None:
    """Empty repository must produce an empty result.

    :return: None
    :rtype: None
    """
    svc = GenerationService(metrics_repo=FakeRepo([]))
    assert svc.get_generation() == []


def test_get_generation_filters_none_values() -> None:
    """Metrics with value=None must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, None),
        _m(_NOW + timedelta(hours=1), 100.0),
    ]
    svc = GenerationService(metrics_repo=FakeRepo(metrics))

    results = svc.get_generation()

    assert len(results) == 1
    assert results[0].series[0].production[0].values[0][1] == pytest.approx(100.0)


def test_get_generation_filters_negative_values() -> None:
    """Metrics with negative values must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, -50.0),
        _m(_NOW + timedelta(hours=1), 200.0),
    ]
    svc = GenerationService(metrics_repo=FakeRepo(metrics))

    results = svc.get_generation()

    assert len(results) == 1
    assert results[0].series[0].production[0].values[0][1] == pytest.approx(200.0)


def test_get_generation_returns_empty_when_all_filtered() -> None:
    """All-invalid metrics must produce no Generation objects.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, None), _m(_NOW, -1.0)]
    svc = GenerationService(metrics_repo=FakeRepo(metrics))
    assert svc.get_generation() == []


# ============================================================
# _group_metrics — structure
# ============================================================


def test_get_generation_one_object_per_zone() -> None:
    """Metrics for separate zones must produce separate Generation objects.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, zone="ES"),
        _m(_NOW, 200.0, zone="FR"),
    ]
    svc = GenerationService(metrics_repo=FakeRepo(metrics))

    results = svc.get_generation()

    assert len(results) == 2
    zones = {r.zone for r in results}
    assert zones == {"ES", "FR"}


def test_get_generation_separate_series_by_validity() -> None:
    """Different (valid, zone_status) pairs must create separate GenerationSeries.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, valid=True, zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 80.0, valid=False, zone_status="preview"),
    ]
    svc = GenerationService(metrics_repo=FakeRepo(metrics))

    results = svc.get_generation()

    assert len(results[0].series) == 2


def test_get_generation_separate_blocks_by_production_type() -> None:
    """Different production types in the same series must produce separate blocks.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, production_type="solar"),
        _m(_NOW, 50.0, production_type="wind_onshore"),
    ]
    svc = GenerationService(metrics_repo=FakeRepo(metrics))

    results = svc.get_generation()
    blocks = results[0].series[0].production

    types = {b.production_type for b in blocks}
    assert types == {"solar", "wind_onshore"}


def test_get_generation_block_values_sorted_by_timestamp() -> None:
    """Values within a block must be sorted ascending by timestamp.

    :return: None
    :rtype: None
    """
    t0 = _NOW
    t1 = _NOW + timedelta(hours=2)
    t2 = _NOW + timedelta(hours=1)

    metrics = [_m(t0, 1.0), _m(t1, 3.0), _m(t2, 2.0)]
    svc = GenerationService(metrics_repo=FakeRepo(metrics))

    values = svc.get_generation()[0].series[0].production[0].values

    assert values[0][0] == t0
    assert values[1][0] == t2
    assert values[2][0] == t1


# ============================================================
# get_generation — filter forwarding
# ============================================================


def test_get_generation_with_zone_filter() -> None:
    """zone filter branch is executed when provided.

    :return: None
    :rtype: None
    """
    svc = GenerationService(metrics_repo=FakeRepo([]))
    assert svc.get_generation(zone="ES") == []


def test_get_generation_with_production_type_filter() -> None:
    """production_type filter branch is executed when provided.

    :return: None
    :rtype: None
    """
    svc = GenerationService(metrics_repo=FakeRepo([]))
    assert svc.get_generation(production_type="solar") == []
