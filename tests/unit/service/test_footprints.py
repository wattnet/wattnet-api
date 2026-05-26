"""
Unit tests for wattnet.api.service.footprints module.

These tests validate:
- Filtering of invalid (None/negative) metric values
- Series vs aggregate mode routing
- Aggregation: zone_status priority resolution, valid flag, coverage
- Time-series grouping by (footprint_type, scope, zone, unit) and validity subgroups
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Optional

import pytest

from tests.unit.service.helpers import FakeMetric, FakeRepo
from wattnet.api.models.footprint import Footprint, FootprintAggregate
from wattnet.api.service.footprints import FootprintService

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)
_END = _NOW + timedelta(hours=2)


def _m(
    ts: datetime,
    value: Optional[float],
    zone: str = "ES",
    footprint_type: str = "carbon",
    scope: str = "operational",
    unit: str = "gCO2/kWh",
    valid: str = "true",
    zone_status: str = "complete",
) -> FakeMetric:
    """Build a FakeMetric with footprint metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param zone: Zone code
    :param footprint_type: Footprint type
    :param scope: Footprint scope
    :param unit: Footprint unit
    :param valid: Validity string ('true'/'false')
    :param zone_status: Zone status
    :return: FakeMetric
    :rtype: FakeMetric
    """
    return FakeMetric(
        timestamp=ts,
        value=value,
        metadata={
            "zone": zone,
            "footprint_type": footprint_type,
            "scope": scope,
            "unit": unit,
            "valid": valid,
            "zone_status": zone_status,
        },
    )


# ============================================================
# get_footprints — filtering
# ============================================================


def test_get_footprints_returns_empty_when_no_metrics() -> None:
    """Empty repository must produce an empty result.

    :return: None
    :rtype: None
    """
    svc = FootprintService(metrics_repo=FakeRepo([]))
    assert svc.get_footprints() == []


def test_get_footprints_filters_none_values() -> None:
    """Metrics with value=None must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, None), _m(_NOW + timedelta(hours=1), 200.0)]
    svc = FootprintService(metrics_repo=FakeRepo(metrics))

    results = svc.get_footprints()

    assert len(results) == 1


def test_get_footprints_filters_negative_values() -> None:
    """Metrics with negative values must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, -1.0), _m(_NOW + timedelta(hours=1), 150.0)]
    svc = FootprintService(metrics_repo=FakeRepo(metrics))

    results = svc.get_footprints()

    assert len(results) == 1


# ============================================================
# get_footprints — series vs aggregate routing
# ============================================================


def test_get_footprints_returns_footprint_series_by_default() -> None:
    """Default (aggregate=False) must return Footprint time-series objects.

    :return: None
    :rtype: None
    """
    svc = FootprintService(metrics_repo=FakeRepo([_m(_NOW, 100.0)]))

    results = svc.get_footprints(aggregate=False)

    assert isinstance(results[0], Footprint)


def test_get_footprints_returns_aggregate_when_requested() -> None:
    """aggregate=True with start/end must return FootprintAggregate objects.

    :return: None
    :rtype: None
    """
    svc = FootprintService(metrics_repo=FakeRepo([_m(_NOW, 100.0)]))

    results = svc.get_footprints(aggregate=True, start=_NOW, end=_END)

    assert isinstance(results[0], FootprintAggregate)


def test_get_footprints_series_without_start_end_is_series() -> None:
    """aggregate=True but missing start/end must fall back to series mode.

    :return: None
    :rtype: None
    """
    svc = FootprintService(metrics_repo=FakeRepo([_m(_NOW, 100.0)]))

    results = svc.get_footprints(aggregate=True)

    assert isinstance(results[0], Footprint)


# ============================================================
# _aggregate_metrics — zone_status / valid / coverage
# ============================================================


def test_footprint_aggregate_zone_status_picks_lowest_priority() -> None:
    """Mixed 'complete'/'preview' must resolve to 'preview'.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 100.0, zone_status="preview"),
    ]
    svc = FootprintService(metrics_repo=FakeRepo(metrics))

    results = svc.get_footprints(aggregate=True, start=_NOW, end=_END)

    assert results[0].zone_status == "preview"


def test_footprint_aggregate_valid_false_when_any_invalid() -> None:
    """Aggregate is invalid when at least one metric has valid='false'.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, valid="true"),
        _m(_NOW + timedelta(hours=1), 100.0, valid="false"),
    ]
    svc = FootprintService(metrics_repo=FakeRepo(metrics))

    results = svc.get_footprints(aggregate=True, start=_NOW, end=_END)

    assert results[0].valid is False


def test_footprint_aggregate_coverage_global() -> None:
    """use_global=True must produce coverage='global'.

    :return: None
    :rtype: None
    """
    svc = FootprintService(metrics_repo=FakeRepo([_m(_NOW, 100.0)]))

    results = svc.get_footprints(aggregate=True, start=_NOW, end=_END, use_global=True)

    assert results[0].coverage == "global"


def test_footprint_aggregate_coverage_local() -> None:
    """use_global=False must produce coverage='local'.

    :return: None
    :rtype: None
    """
    svc = FootprintService(metrics_repo=FakeRepo([_m(_NOW, 100.0)]))

    results = svc.get_footprints(
        aggregate=True, start=_NOW, end=_END, use_global=False
    )

    assert results[0].coverage == "local"


# ============================================================
# _group_metrics_series — series grouping
# ============================================================


def test_footprint_series_separate_zones() -> None:
    """Metrics for different zones must produce separate Footprint objects.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, 100.0, zone="ES"), _m(_NOW, 80.0, zone="FR")]
    svc = FootprintService(metrics_repo=FakeRepo(metrics))

    results = svc.get_footprints(aggregate=False)

    assert len(results) == 2
    assert {r.zone for r in results} == {"ES", "FR"}


def test_footprint_series_groups_by_validity_subgroups() -> None:
    """Metrics with different valid/zone_status must produce separate series.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, valid="true", zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 80.0, valid="false", zone_status="preview"),
    ]
    svc = FootprintService(metrics_repo=FakeRepo(metrics))

    results = svc.get_footprints(aggregate=False)

    assert len(results[0].series) == 2
