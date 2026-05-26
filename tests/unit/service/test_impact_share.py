"""
Unit tests for wattnet.api.service.impact_share module.

These tests validate:
- Routing by impact_type in get_impact_share
- Empty result when no metrics are found
- Correct nesting of ImpactShare → ImpactShareSeries → ImpactShareBlock
- Fallback to 'unknown' for None source values
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Dict, List, Optional

import pytest

from wattnet.api.models.impact_share import ImpactShare
from wattnet.api.service.impact_share import ImpactShareService

# ============================================================
# Test doubles
# ============================================================


@dataclass
class FakeMetric:
    """Minimal Metric test double.

    :param timestamp: Timestamp of the metric
    :type timestamp: datetime
    :param value: Metric value
    :type value: float | None
    :param metadata: Metadata dictionary
    :type metadata: Dict[str, object]
    """

    timestamp: datetime
    value: Optional[float]
    metadata: Dict[str, object]


class FakeRepo:
    """Configurable MetricsRepository stub.

    :param metrics: Metrics to return from query_metrics
    :type metrics: List[FakeMetric]
    """

    def __init__(self, metrics: List[FakeMetric]) -> None:
        """Initialise with a fixed list of metrics.

        :param metrics: Metrics returned by query_metrics
        :type metrics: List[FakeMetric]
        """
        self._metrics = metrics

    def query_metrics(
        self,
        metric_name: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        labels: Optional[Dict] = None,
    ) -> List[FakeMetric]:
        """Return preconfigured metrics regardless of filters.

        :param metric_name: Ignored
        :param start: Ignored
        :param end: Ignored
        :param labels: Ignored
        :return: Preconfigured metric list
        :rtype: List[FakeMetric]
        """
        return self._metrics


# ============================================================
# Helpers
# ============================================================

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)


def _make_share_metric(
    ts: datetime,
    value: float,
    zone: str = "ES",
    source: str = "FR",
    scope: str = "operational",
    valid: bool = True,
    zone_status: str = "complete",
    unit: str = "stress-l/kWh",
) -> FakeMetric:
    """Return a FakeMetric with impact-share metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param zone: Destination zone
    :param source: Origin zone
    :param scope: Scope
    :param valid: Validity flag
    :param zone_status: Zone status
    :param unit: Unit string
    :return: FakeMetric
    :rtype: FakeMetric
    """
    return FakeMetric(
        timestamp=ts,
        value=value,
        metadata={
            "impact_type": "water",
            "zone": zone,
            "source": source,
            "scope": scope,
            "valid": valid,
            "zone_status": zone_status,
            "unit": unit,
        },
    )


# ============================================================
# get_impact_share — routing by impact_type
# ============================================================


def test_get_impact_share_none_type_returns_water_results() -> None:
    """impact_type=None should include water results.

    :return: None
    :rtype: None
    """
    metric = _make_share_metric(_NOW, 0.5)
    svc = ImpactShareService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impact_share(impact_type=None)

    assert len(results) == 1


def test_get_impact_share_water_type_returns_results() -> None:
    """impact_type='water' should include water results.

    :return: None
    :rtype: None
    """
    metric = _make_share_metric(_NOW, 0.5)
    svc = ImpactShareService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impact_share(impact_type="water")

    assert len(results) == 1


def test_get_impact_share_unknown_type_returns_empty() -> None:
    """Unsupported impact_type should produce an empty list.

    :return: None
    :rtype: None
    """
    metric = _make_share_metric(_NOW, 0.5)
    svc = ImpactShareService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impact_share(impact_type="carbon")

    assert results == []


# ============================================================
# _get_water_impact_share — empty repo
# ============================================================


def test_get_impact_share_returns_empty_when_no_metrics() -> None:
    """Empty repository should produce an empty result list.

    :return: None
    :rtype: None
    """
    svc = ImpactShareService(metrics_repo=FakeRepo([]))

    results = svc.get_impact_share()

    assert results == []


# ============================================================
# _group_metrics — structure
# ============================================================


def test_group_metrics_creates_one_share_per_zone() -> None:
    """Metrics for separate zones must produce separate ImpactShare objects.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_share_metric(_NOW, 0.3, zone="ES"),
        _make_share_metric(_NOW, 0.2, zone="FR"),
    ]
    svc = ImpactShareService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impact_share()

    assert len(results) == 2
    zones = {r.zone for r in results}
    assert zones == {"ES", "FR"}


def test_group_metrics_creates_one_block_per_source() -> None:
    """Metrics with different sources in the same zone must produce separate blocks.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_share_metric(_NOW, 0.3, zone="ES", source="FR"),
        _make_share_metric(_NOW + timedelta(hours=1), 0.2, zone="ES", source="PT"),
    ]
    svc = ImpactShareService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impact_share()

    assert len(results) == 1
    blocks = results[0].series[0].blocks
    sources = {b.source for b in blocks}
    assert sources == {"FR", "PT"}


def test_group_metrics_values_are_sorted_by_timestamp() -> None:
    """Values within a block must be sorted ascending by timestamp.

    :return: None
    :rtype: None
    """
    t0 = _NOW
    t1 = _NOW + timedelta(hours=2)
    t2 = _NOW + timedelta(hours=1)

    metrics = [
        _make_share_metric(t0, 0.1),
        _make_share_metric(t1, 0.3),
        _make_share_metric(t2, 0.2),
    ]
    svc = ImpactShareService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impact_share()
    values = results[0].series[0].blocks[0].values

    assert values[0][0] == t0
    assert values[1][0] == t2
    assert values[2][0] == t1


def test_group_metrics_none_source_becomes_unknown() -> None:
    """A metric with source=None must be assigned source='unknown'.

    :return: None
    :rtype: None
    """
    metric = _make_share_metric(_NOW, 0.5, source=None)  # type: ignore[arg-type]
    metric.metadata["source"] = None
    svc = ImpactShareService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impact_share()

    assert results[0].series[0].blocks[0].source == "unknown"


def test_group_metrics_separate_series_by_validity() -> None:
    """Metrics with different valid/zone_status must produce separate series.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_share_metric(_NOW, 0.4, valid=True, zone_status="complete"),
        _make_share_metric(
            _NOW + timedelta(hours=1), 0.2, valid=False, zone_status="preview"
        ),
    ]
    svc = ImpactShareService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impact_share()

    assert len(results[0].series) == 2


def test_group_metrics_result_is_impact_share_instance() -> None:
    """Returned objects must be ImpactShare instances.

    :return: None
    :rtype: None
    """
    metric = _make_share_metric(_NOW, 0.5)
    svc = ImpactShareService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impact_share()

    assert isinstance(results[0], ImpactShare)
