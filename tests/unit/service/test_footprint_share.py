"""
Unit tests for wattnet.api.service.footprint_share module.

These tests validate:
- Empty repository returns empty list
- Hierarchical grouping: FootprintShare → FootprintShareSeries → FootprintShareBlock
- Separation into series by (valid, zone_status) pairs
- Separation into blocks by source zone, with None → 'unknown'
- Chronological ordering of values within blocks
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from tests.unit.service.helpers import FakeMetric, FakeRepo
from wattnet.api.service.footprint_share import FootprintShareService

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)


def _m(
    ts: datetime,
    value: float,
    zone: str = "ES",
    source: str = "FR",
    footprint_type: str = "carbon",
    scope: str = "operational",
    unit: str = "gCO2/kWh",
    valid: bool = True,
    zone_status: str = "complete",
) -> FakeMetric:
    """Build a FakeMetric with footprint share metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param zone: Destination zone code
    :param source: Origin zone code
    :param footprint_type: Footprint type
    :param scope: Footprint scope
    :param unit: Footprint unit
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
            "source": source,
            "footprint_type": footprint_type,
            "scope": scope,
            "unit": unit,
            "valid": valid,
            "zone_status": zone_status,
        },
    )


# ============================================================
# get_footprint_share — basic
# ============================================================


def test_get_footprint_share_returns_empty_when_no_metrics() -> None:
    """Empty repository must produce an empty result.

    :return: None
    :rtype: None
    """
    svc = FootprintShareService(metrics_repo=FakeRepo([]))
    assert svc.get_footprint_share() == []


# ============================================================
# _group_metrics — structure
# ============================================================


def test_get_footprint_share_one_object_per_zone() -> None:
    """Metrics for separate zones must produce separate FootprintShare objects.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, 120.0, zone="ES"), _m(_NOW, 80.0, zone="FR")]
    svc = FootprintShareService(metrics_repo=FakeRepo(metrics))

    results = svc.get_footprint_share()

    assert len(results) == 2
    assert {r.zone for r in results} == {"ES", "FR"}


def test_get_footprint_share_separate_blocks_by_source() -> None:
    """Metrics with different source zones must produce separate blocks.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 120.0, source="FR"),
        _m(_NOW + timedelta(hours=1), 60.0, source="PT"),
    ]
    svc = FootprintShareService(metrics_repo=FakeRepo(metrics))

    blocks = svc.get_footprint_share()[0].series[0].blocks

    assert {b.source for b in blocks} == {"FR", "PT"}


def test_get_footprint_share_none_source_becomes_unknown() -> None:
    """A metric with source=None must be assigned source='unknown'.

    :return: None
    :rtype: None
    """
    metric = _m(_NOW, 0.5)
    metric.metadata["source"] = None
    svc = FootprintShareService(metrics_repo=FakeRepo([metric]))

    block = svc.get_footprint_share()[0].series[0].blocks[0]

    assert block.source == "unknown"


def test_get_footprint_share_separate_series_by_validity() -> None:
    """Different (valid, zone_status) pairs must create separate series.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 120.0, valid=True, zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 80.0, valid=False, zone_status="preview"),
    ]
    svc = FootprintShareService(metrics_repo=FakeRepo(metrics))

    assert len(svc.get_footprint_share()[0].series) == 2


def test_get_footprint_share_block_values_sorted_by_timestamp() -> None:
    """Values within a block must be sorted ascending by timestamp.

    :return: None
    :rtype: None
    """
    t0 = _NOW
    t2 = _NOW + timedelta(hours=2)
    t1 = _NOW + timedelta(hours=1)

    metrics = [_m(t0, 1.0), _m(t2, 3.0), _m(t1, 2.0)]
    svc = FootprintShareService(metrics_repo=FakeRepo(metrics))

    values = svc.get_footprint_share()[0].series[0].blocks[0].values

    assert values[0][0] == t0
    assert values[1][0] == t1
    assert values[2][0] == t2
