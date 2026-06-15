"""
Unit tests for wattnet.api.service.impacts module.

These tests validate:
- Routing by impact_type in get_impacts
- Filtering of invalid/negative metric values
- Aggregation logic and zone_status priority resolution
- Time-series grouping by validity subgroups
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import pytest

from wattnet.api.models.impact import ImpactAggregate
from wattnet.api.service.impacts import ImpactService

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

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
_END = _NOW + timedelta(hours=2)


def _make_water_metric(
    ts: datetime,
    value: Optional[float],
    zone: str = "ES",
    scope: str = "operational",
    zone_status: str = "complete",
    valid: str = "true",
    unit: str = "stress-l/kWh",
) -> FakeMetric:
    """Return a FakeMetric with water-impact metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param zone: Zone code
    :param scope: Scope
    :param zone_status: Zone status string
    :param valid: Validity string ('true'/'false')
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
            "scope": scope,
            "zone_status": zone_status,
            "valid": valid,
            "unit": unit,
        },
    )


# ============================================================
# get_impacts — routing by impact_type
# ============================================================


def test_get_impacts_none_type_returns_water_results() -> None:
    """impact_type=None should include water results.

    :return: None
    :rtype: None
    """
    metric = _make_water_metric(_NOW, 5.0)
    svc = ImpactService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impacts(impact_type=None)

    assert len(results) == 1


def test_get_impacts_water_type_returns_water_results() -> None:
    """impact_type='water' should include water results.

    :return: None
    :rtype: None
    """
    metric = _make_water_metric(_NOW, 5.0)
    svc = ImpactService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impacts(impact_type="water")

    assert len(results) == 1


def test_get_impacts_unknown_type_returns_empty() -> None:
    """Unsupported impact_type should produce an empty list.

    :return: None
    :rtype: None
    """
    metric = _make_water_metric(_NOW, 5.0)
    svc = ImpactService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impacts(impact_type="carbon")

    assert results == []


# ============================================================
# _get_water_impacts — value filtering
# ============================================================


def test_get_impacts_filters_none_values() -> None:
    """Metrics with value=None must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_water_metric(_NOW, None),
        _make_water_metric(_NOW + timedelta(hours=1), 3.0),
    ]
    svc = ImpactService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impacts()

    assert len(results) == 1
    assert results[0].series[0].values[0][1] == pytest.approx(3.0, rel=1e-9)


def test_get_impacts_filters_negative_values() -> None:
    """Metrics with negative values must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_water_metric(_NOW, -1.0),
        _make_water_metric(_NOW + timedelta(hours=1), 2.0),
    ]
    svc = ImpactService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impacts()

    assert len(results) == 1
    assert results[0].series[0].values[0][1] == pytest.approx(2.0, rel=1e-9)


def test_get_impacts_returns_empty_when_all_invalid() -> None:
    """All-invalid metric list should produce no Impact objects.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_water_metric(_NOW, None),
        _make_water_metric(_NOW, -5.0),
    ]
    svc = ImpactService(metrics_repo=FakeRepo(metrics))

    assert svc.get_impacts() == []


# ============================================================
# _get_water_impacts — series vs aggregate mode
# ============================================================


def test_get_impacts_returns_series_by_default() -> None:
    """Without aggregate=True the result should be an Impact with series.

    :return: None
    :rtype: None
    """
    from wattnet.api.models.impact import Impact

    metric = _make_water_metric(_NOW, 5.0)
    svc = ImpactService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impacts(aggregate=False)

    assert len(results) == 1
    assert isinstance(results[0], Impact)
    assert results[0].series[0].values[0][1] == pytest.approx(5.0, rel=1e-9)


def test_get_impacts_returns_aggregate_when_requested() -> None:
    """aggregate=True with start/end should return ImpactAggregate objects.

    :return: None
    :rtype: None
    """
    metric = _make_water_metric(_NOW, 10.0)
    svc = ImpactService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impacts(aggregate=True, start=_NOW, end=_END)

    assert len(results) == 1
    assert isinstance(results[0], ImpactAggregate)


# ============================================================
# _aggregate_metrics — zone_status priority
# ============================================================


def test_aggregate_zone_status_picks_lowest_priority() -> None:
    """When metrics mix 'complete' and 'preview', the result must be 'preview'.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_water_metric(_NOW, 10.0, zone_status="complete"),
        _make_water_metric(_NOW + timedelta(hours=1), 10.0, zone_status="preview"),
    ]
    svc = ImpactService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impacts(aggregate=True, start=_NOW, end=_END)

    assert results[0].zone_status == "preview"


def test_aggregate_zone_status_missing_is_lowest() -> None:
    """'missing' has the lowest priority and must win over 'preview'/'complete'.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_water_metric(_NOW, 10.0, zone_status="complete"),
        _make_water_metric(_NOW + timedelta(hours=1), 10.0, zone_status="missing"),
    ]
    svc = ImpactService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impacts(aggregate=True, start=_NOW, end=_END)

    assert results[0].zone_status == "missing"


def test_aggregate_valid_false_when_any_invalid() -> None:
    """Aggregate is invalid if any metric has valid != 'true'.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_water_metric(_NOW, 10.0, valid="true"),
        _make_water_metric(_NOW + timedelta(hours=1), 10.0, valid="false"),
    ]
    svc = ImpactService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impacts(aggregate=True, start=_NOW, end=_END)

    assert results[0].valid is False


def test_aggregate_valid_true_when_all_valid() -> None:
    """Aggregate is valid only when all metrics have valid='true'.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_water_metric(_NOW, 10.0, valid="true"),
        _make_water_metric(_NOW + timedelta(hours=1), 5.0, valid="true"),
    ]
    svc = ImpactService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impacts(aggregate=True, start=_NOW, end=_END)

    assert results[0].valid is True


def test_aggregate_coverage_global() -> None:
    """use_global=True must produce coverage='global'.

    :return: None
    :rtype: None
    """
    metric = _make_water_metric(_NOW, 5.0)
    svc = ImpactService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impacts(aggregate=True, start=_NOW, end=_END, use_global=True)

    assert results[0].coverage == "global"


def test_aggregate_coverage_local() -> None:
    """use_global=False must produce coverage='local'.

    :return: None
    :rtype: None
    """
    metric = _make_water_metric(_NOW, 5.0)
    svc = ImpactService(metrics_repo=FakeRepo([metric]))

    results = svc.get_impacts(aggregate=True, start=_NOW, end=_END, use_global=False)

    assert results[0].coverage == "local"


# ============================================================
# _group_metrics_series — series grouping
# ============================================================


def test_series_groups_by_validity_subgroups() -> None:
    """Metrics with different valid/zone_status pairs must produce separate series.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_water_metric(_NOW, 1.0, valid="true", zone_status="complete"),
        _make_water_metric(
            _NOW + timedelta(hours=1), 2.0, valid="false", zone_status="preview"
        ),
    ]
    svc = ImpactService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impacts(aggregate=False)

    assert len(results) == 1
    assert len(results[0].series) == 2


def test_series_groups_separate_zones() -> None:
    """Metrics for different zones must produce separate Impact objects.

    :return: None
    :rtype: None
    """
    metrics = [
        _make_water_metric(_NOW, 1.0, zone="ES"),
        _make_water_metric(_NOW, 2.0, zone="FR"),
    ]
    svc = ImpactService(metrics_repo=FakeRepo(metrics))

    results = svc.get_impacts(aggregate=False)

    assert len(results) == 2
    zones = {r.zone for r in results}
    assert zones == {"ES", "FR"}


# ============================================================
# get_impacts — filter forwarding
# ============================================================


def test_get_impacts_with_zone_filter() -> None:
    """zone filter branch is executed when provided.

    :return: None
    :rtype: None
    """
    svc = ImpactService(metrics_repo=FakeRepo([]))
    assert svc.get_impacts(zone="ES") == []


def test_get_impacts_with_scope_filter() -> None:
    """scope filter branch is executed when provided.

    :return: None
    :rtype: None
    """
    svc = ImpactService(metrics_repo=FakeRepo([]))
    assert svc.get_impacts(scope="operational") == []
