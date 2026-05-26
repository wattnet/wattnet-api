"""
Unit tests for wattnet.api.service.scores module.

These tests validate:
- Filtering of None metric values (scores allow any value including negative)
- Series vs aggregate mode routing
- Aggregation: zone_status priority resolution, valid flag, coverage
- Time-series grouping by (scope, zone) and validity subgroups
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Optional

import pytest

from tests.unit.service.helpers import FakeMetric, FakeRepo
from wattnet.api.models.score import GreenScore, GreenScoreAggregate
from wattnet.api.service.scores import ScoreService

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)
_END = _NOW + timedelta(hours=2)


def _m(
    ts: datetime,
    value: Optional[float],
    zone: str = "ES",
    scope: str = "operational",
    valid: str = "true",
    zone_status: str = "complete",
) -> FakeMetric:
    """Build a FakeMetric with score metadata.

    :param ts: Timestamp
    :param value: Metric value (None → excluded)
    :param zone: Zone code
    :param scope: Score scope
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
            "scope": scope,
            "valid": valid,
            "zone_status": zone_status,
        },
    )


# ============================================================
# get_scores — filtering
# ============================================================


def test_get_scores_returns_empty_when_no_metrics() -> None:
    """Empty repository must produce an empty result.

    :return: None
    :rtype: None
    """
    svc = ScoreService(metrics_repo=FakeRepo([]))
    assert svc.get_scores() == []


def test_get_scores_filters_none_values() -> None:
    """Metrics with value=None must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, None), _m(_NOW + timedelta(hours=1), 75.0)]
    svc = ScoreService(metrics_repo=FakeRepo(metrics))

    results = svc.get_scores()

    assert len(results) == 1


def test_get_scores_keeps_negative_values() -> None:
    """Unlike other services, ScoreService does not filter out negative values.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, -10.0), _m(_NOW + timedelta(hours=1), 50.0)]
    svc = ScoreService(metrics_repo=FakeRepo(metrics))

    results = svc.get_scores()

    assert len(results) == 1
    values = results[0].series[0].values
    assert len(values) == 2


# ============================================================
# get_scores — series vs aggregate routing
# ============================================================


def test_get_scores_returns_green_score_by_default() -> None:
    """Default (aggregate=False) must return GreenScore time-series objects.

    :return: None
    :rtype: None
    """
    svc = ScoreService(metrics_repo=FakeRepo([_m(_NOW, 70.0)]))

    results = svc.get_scores(aggregate=False)

    assert isinstance(results[0], GreenScore)


def test_get_scores_returns_aggregate_when_requested() -> None:
    """aggregate=True with start/end must return GreenScoreAggregate objects.

    :return: None
    :rtype: None
    """
    svc = ScoreService(metrics_repo=FakeRepo([_m(_NOW, 70.0)]))

    results = svc.get_scores(aggregate=True, start=_NOW, end=_END)

    assert isinstance(results[0], GreenScoreAggregate)


def test_get_scores_no_start_end_falls_back_to_series() -> None:
    """aggregate=True without start/end must fall back to series mode.

    :return: None
    :rtype: None
    """
    svc = ScoreService(metrics_repo=FakeRepo([_m(_NOW, 70.0)]))

    results = svc.get_scores(aggregate=True)

    assert isinstance(results[0], GreenScore)


# ============================================================
# _aggregate_metrics — zone_status / valid / coverage
# ============================================================


def test_score_aggregate_zone_status_picks_lowest_priority() -> None:
    """Mixed 'complete'/'missing' must resolve to 'missing'.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 70.0, zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 60.0, zone_status="missing"),
    ]
    svc = ScoreService(metrics_repo=FakeRepo(metrics))

    results = svc.get_scores(aggregate=True, start=_NOW, end=_END)

    assert results[0].zone_status == "missing"


def test_score_aggregate_valid_false_when_any_invalid() -> None:
    """Aggregate is invalid when at least one metric has valid='false'.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 70.0, valid="true"),
        _m(_NOW + timedelta(hours=1), 60.0, valid="false"),
    ]
    svc = ScoreService(metrics_repo=FakeRepo(metrics))

    results = svc.get_scores(aggregate=True, start=_NOW, end=_END)

    assert results[0].valid is False


def test_score_aggregate_coverage_global() -> None:
    """use_global=True must produce coverage='global'.

    :return: None
    :rtype: None
    """
    svc = ScoreService(metrics_repo=FakeRepo([_m(_NOW, 70.0)]))

    results = svc.get_scores(aggregate=True, start=_NOW, end=_END, use_global=True)

    assert results[0].coverage == "global"


def test_score_aggregate_coverage_local() -> None:
    """use_global=False must produce coverage='local'.

    :return: None
    :rtype: None
    """
    svc = ScoreService(metrics_repo=FakeRepo([_m(_NOW, 70.0)]))

    results = svc.get_scores(aggregate=True, start=_NOW, end=_END, use_global=False)

    assert results[0].coverage == "local"


# ============================================================
# _group_metrics_series — series grouping
# ============================================================


def test_score_series_separate_zones() -> None:
    """Metrics for different zones must produce separate GreenScore objects.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, 70.0, zone="ES"), _m(_NOW, 80.0, zone="FR")]
    svc = ScoreService(metrics_repo=FakeRepo(metrics))

    results = svc.get_scores(aggregate=False)

    assert len(results) == 2
    assert {r.zone for r in results} == {"ES", "FR"}


def test_score_series_groups_by_validity_subgroups() -> None:
    """Metrics with different valid/zone_status must produce separate series.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 70.0, valid="true", zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 50.0, valid="false", zone_status="preview"),
    ]
    svc = ScoreService(metrics_repo=FakeRepo(metrics))

    results = svc.get_scores(aggregate=False)

    assert len(results[0].series) == 2
