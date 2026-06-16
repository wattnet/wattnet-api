"""
Unit tests for wattnet.api.service.mix_share module.

These tests validate:
- Empty repository returns empty list
- Hierarchical grouping: MixShare → MixShareSeries → MixShareBlock
- Separation into series by (valid, zone_status) pairs
- Separation into blocks by origin zone (source label)
- Chronological ordering of values within blocks
- Correct unit is always '%'
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tests.unit.service.helpers import FakeMetric, FakeRepo
from wattnet.api.service.mix_share import MixShareService

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)


def _m(
    ts: datetime,
    value: float,
    zone: str = "ES",
    source: str = "FR",
    valid: bool = True,
    zone_status: str = "complete",
) -> FakeMetric:
    """Build a FakeMetric with mix share metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param zone: Destination zone code
    :param source: Origin zone code
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
            "valid": valid,
            "zone_status": zone_status,
        },
    )


# ============================================================
# get_mix_share — basic
# ============================================================


def test_get_mix_share_returns_empty_when_no_metrics() -> None:
    """Empty repository must produce an empty result.

    :return: None
    :rtype: None
    """
    svc = MixShareService(metrics_repo=FakeRepo([]))
    assert svc.get_mix_share() == []


def test_get_mix_share_unit_is_percent() -> None:
    """The unit field on every MixShare must always be '%'.

    :return: None
    :rtype: None
    """
    svc = MixShareService(metrics_repo=FakeRepo([_m(_NOW, 0.3)]))
    assert svc.get_mix_share()[0].unit == "%"


# ============================================================
# _group_metrics — structure
# ============================================================


def test_get_mix_share_one_object_per_zone() -> None:
    """Metrics for separate zones must produce separate MixShare objects.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, 0.3, zone="ES"), _m(_NOW, 0.4, zone="FR")]
    svc = MixShareService(metrics_repo=FakeRepo(metrics))

    results = svc.get_mix_share()

    assert len(results) == 2
    assert {r.zone for r in results} == {"ES", "FR"}


def test_get_mix_share_separate_blocks_by_origin() -> None:
    """Metrics with different source zones must produce separate MixShareBlocks.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 0.3, source="FR"),
        _m(_NOW + timedelta(hours=1), 0.2, source="PT"),
    ]
    svc = MixShareService(metrics_repo=FakeRepo(metrics))

    blocks = svc.get_mix_share()[0].series[0].shares

    assert {b.origin for b in blocks} == {"FR", "PT"}


def test_get_mix_share_separate_series_by_validity() -> None:
    """Different (valid, zone_status) pairs must create separate MixShareSeries.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 0.3, valid=True, zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 0.2, valid=False, zone_status="preview"),
    ]
    svc = MixShareService(metrics_repo=FakeRepo(metrics))

    assert len(svc.get_mix_share()[0].series) == 2


def test_get_mix_share_with_origin_filter() -> None:
    """Calling get_mix_share(origin=...) must not raise and returns a list.

    :return: None
    :rtype: None
    """
    svc = MixShareService(metrics_repo=FakeRepo([]))
    assert svc.get_mix_share(origin="FR") == []


def test_get_mix_share_block_values_sorted_by_timestamp() -> None:
    """Values within a block must be sorted ascending by timestamp.

    :return: None
    :rtype: None
    """
    t0 = _NOW
    t2 = _NOW + timedelta(hours=2)
    t1 = _NOW + timedelta(hours=1)

    metrics = [_m(t0, 0.1), _m(t2, 0.3), _m(t1, 0.2)]
    svc = MixShareService(metrics_repo=FakeRepo(metrics))

    values = svc.get_mix_share()[0].series[0].shares[0].values

    assert values[0][0] == t0
    assert values[1][0] == t1
    assert values[2][0] == t2


# ============================================================
# get_mix_share — filter forwarding
# ============================================================


def test_get_mix_share_none_source_falls_back_to_unknown() -> None:
    """A metric missing the 'source' key must produce origin='unknown', not crash.

    :return: None
    :rtype: None
    """
    metric = FakeMetric(
        timestamp=_NOW,
        value=0.5,
        metadata={"zone": "ES", "valid": True, "zone_status": "complete"},
    )
    svc = MixShareService(metrics_repo=FakeRepo([metric]))

    block = svc.get_mix_share()[0].series[0].shares[0]

    assert block.origin == "unknown"


def test_get_mix_share_with_zone_filter() -> None:
    """zone filter branch is executed when provided.

    :return: None
    :rtype: None
    """
    svc = MixShareService(metrics_repo=FakeRepo([]))
    assert svc.get_mix_share(zone="ES") == []
