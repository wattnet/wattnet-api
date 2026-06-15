"""
Unit tests for wattnet.api.service.operations module.

These tests validate:
- Grouping behavior by metadata keys
- Correct time-weighted average integration
- Edge cases in temporal boundaries
- Proper time-series construction and sorting
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import pytest

import wattnet.api.service.operations as ops

# ============================================================
# Test Model
# ============================================================


@dataclass
class FakeMetric:
    """
    Minimal Metric test double.

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


# ============================================================
# group_metrics_by_metadata
# ============================================================


def test_group_metrics_by_single_field() -> None:
    """Ensure metrics are grouped correctly by a single metadata field.

    :return: None
    :rtype: None
    """
    now: datetime = datetime.now(timezone.utc)

    metrics: List[FakeMetric] = [
        FakeMetric(now, 1.0, {"zone_id": "A"}),
        FakeMetric(now, 2.0, {"zone_id": "A"}),
        FakeMetric(now, 3.0, {"zone_id": "B"}),
    ]

    grouped = ops.group_metrics_by_metadata(metrics, ["zone_id"])

    assert len(grouped) == 2
    assert len(grouped[("A",)]) == 2
    assert len(grouped[("B",)]) == 1


def test_group_metrics_by_multiple_fields() -> None:
    """Ensure grouping works with multiple metadata fields.

    :return: None
    :rtype: None
    """
    now: datetime = datetime.now(timezone.utc)

    metrics: List[FakeMetric] = [
        FakeMetric(now, 1.0, {"zone_id": "A", "type": "solar"}),
        FakeMetric(now, 2.0, {"zone_id": "A", "type": "wind"}),
        FakeMetric(now, 3.0, {"zone_id": "A", "type": "solar"}),
    ]

    grouped = ops.group_metrics_by_metadata(metrics, ["zone_id", "type"])

    assert len(grouped) == 2
    assert len(grouped[("A", "solar")]) == 2
    assert len(grouped[("A", "wind")]) == 1


# ============================================================
# compute_time_weighted_average
# ============================================================


def test_compute_time_weighted_average_empty() -> None:
    """
    Ensure empty metric list returns 0.0.

    :return: None
    :rtype: None
    """
    result: float = ops.compute_time_weighted_average(
        [],
        datetime.now(timezone.utc),
        datetime.now(timezone.utc),
    )

    assert result == pytest.approx(0.0, rel=1e-9)


def test_compute_time_weighted_average_constant_value() -> None:
    """
    Ensure constant metric value over interval returns same value.

    :return: None
    :rtype: None
    """
    start: datetime = datetime(2025, 1, 1, 0, 0, 0)
    end: datetime = start + timedelta(hours=2)

    metrics: List[FakeMetric] = [
        FakeMetric(start, 10.0, {}),
    ]

    result: float = ops.compute_time_weighted_average(metrics, start, end)

    assert result == pytest.approx(10.0, rel=1e-9)


def test_compute_time_weighted_average_piecewise() -> None:
    """
    Validate correct integration of piecewise constant values.

    Example:
        0-1h: value 10
        1-2h: value 20
    Expected average = 15

    :return: None
    :rtype: None
    """
    start: datetime = datetime(2025, 1, 1, 0, 0, 0)
    mid: datetime = start + timedelta(hours=1)
    end: datetime = start + timedelta(hours=2)

    metrics: List[FakeMetric] = [
        FakeMetric(start, 10.0, {}),
        FakeMetric(mid, 20.0, {}),
    ]

    result: float = ops.compute_time_weighted_average(metrics, start, end)

    assert result == pytest.approx(15.0, rel=1e-9)


def test_compute_time_weighted_average_metric_at_end_returns_its_value() -> None:
    """Fallback when total_duration is 0 (metric timestamp == end).

    :return: None
    :rtype: None
    """
    start: datetime = datetime(2025, 1, 1, 0, 0, 0)
    end: datetime = start + timedelta(hours=1)

    metrics: List[FakeMetric] = [
        FakeMetric(end, 7.50, {}),
    ]

    result: float = ops.compute_time_weighted_average(metrics, start, end)

    assert result == pytest.approx(7.50, rel=1e-9)


def test_compute_time_weighted_average_partial_overlap() -> None:
    """
    Ensure integration respects start boundary clipping.

    :return: None
    :rtype: None
    """
    base: datetime = datetime(2025, 1, 1, 0, 0, 0)

    metrics: List[FakeMetric] = [
        FakeMetric(base, 10.0, {}),
        FakeMetric(base + timedelta(hours=1), 20.0, {}),
    ]

    # Start inside first segment
    start: datetime = base + timedelta(minutes=30)
    end: datetime = base + timedelta(hours=2)

    result: float = ops.compute_time_weighted_average(metrics, start, end)

    assert result > 10.0


# ============================================================
# build_time_series
# ============================================================


def test_build_time_series_sorted() -> None:
    """
    Ensure output is sorted by timestamp.

    :return: None
    :rtype: None
    """
    t0: datetime = datetime(2025, 1, 1, 1, 0, 0)
    t1: datetime = datetime(2025, 1, 1, 0, 0, 0)

    metrics: List[FakeMetric] = [
        FakeMetric(t0, 2.0, {}),
        FakeMetric(t1, 1.0, {}),
    ]

    series: List[Tuple[datetime, float]] = ops.build_time_series(metrics)

    assert series[0][0] == t1
    assert series[1][0] == t0


def test_compute_time_weighted_average_skips_none_value() -> None:
    """Metric with value=None is skipped; the next metric still contributes.

    :return: None
    :rtype: None
    """
    start: datetime = datetime(2025, 1, 1, 0, 0, 0)
    mid: datetime = start + timedelta(hours=1)
    end: datetime = start + timedelta(hours=2)

    metrics: List[FakeMetric] = [
        FakeMetric(start, None, {}),
        FakeMetric(mid, 20.0, {}),
    ]

    result: float = ops.compute_time_weighted_average(metrics, start, end)
    assert result == pytest.approx(20.0, rel=1e-9)


def test_resolve_zone_status_empty_returns_missing() -> None:
    """resolve_zone_status([]) must return 'missing' without raising.

    :return: None
    :rtype: None
    """
    assert ops.resolve_zone_status([]) == "missing"


def test_build_time_series_ignores_none_values() -> None:
    """
    Ensure metrics with None values are excluded.

    :return: None
    :rtype: None
    """
    t: datetime = datetime.now(timezone.utc)

    metrics: List[FakeMetric] = [
        FakeMetric(t, None, {}),
        FakeMetric(t + timedelta(hours=1), 5.0, {}),
    ]

    series = ops.build_time_series(metrics)

    assert len(series) == 1
    assert series[0][1] == pytest.approx(5.0, rel=1e-9)
