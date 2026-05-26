"""
Unit tests for wattnet.api.service.flow_share module.

These tests validate:
- Empty repository returns empty list
- Hierarchical grouping: FlowShare → FlowShareSeries → FlowShareBlock
- Separation into series by (valid, zone_status) pairs
- Separation into blocks by target (destination) zone
- Chronological ordering of values within blocks
- Correct unit is always '%'
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from tests.unit.service.helpers import FakeMetric, FakeRepo
from wattnet.api.service.flow_share import FlowShareService

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)


def _m(
    ts: datetime,
    value: float,
    zone: str = "ES",
    target: str = "FR",
    valid: bool = True,
    zone_status: str = "complete",
) -> FakeMetric:
    """Build a FakeMetric with flow share metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param zone: Origin zone code
    :param target: Destination zone code (DB label is 'target')
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
            "target": target,
            "valid": valid,
            "zone_status": zone_status,
        },
    )


# ============================================================
# get_flow_share — basic
# ============================================================


def test_get_flow_share_returns_empty_when_no_metrics() -> None:
    """Empty repository must produce an empty result.

    :return: None
    :rtype: None
    """
    svc = FlowShareService(metrics_repo=FakeRepo([]))
    assert svc.get_flow_share() == []


def test_get_flow_share_unit_is_percent() -> None:
    """The unit field on every FlowShare must always be '%'.

    :return: None
    :rtype: None
    """
    svc = FlowShareService(metrics_repo=FakeRepo([_m(_NOW, 0.5)]))
    assert svc.get_flow_share()[0].unit == "%"


# ============================================================
# _group_metrics — structure
# ============================================================


def test_get_flow_share_one_object_per_zone() -> None:
    """Metrics for separate origin zones must produce separate FlowShare objects.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, 0.3, zone="ES"), _m(_NOW, 0.4, zone="FR")]
    svc = FlowShareService(metrics_repo=FakeRepo(metrics))

    results = svc.get_flow_share()

    assert len(results) == 2
    assert {r.zone for r in results} == {"ES", "FR"}


def test_get_flow_share_separate_blocks_by_target() -> None:
    """Metrics with different target zones must produce separate FlowShareBlocks.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 0.3, target="FR"),
        _m(_NOW + timedelta(hours=1), 0.2, target="PT"),
    ]
    svc = FlowShareService(metrics_repo=FakeRepo(metrics))

    blocks = svc.get_flow_share()[0].series[0].flows

    assert {b.destination for b in blocks} == {"FR", "PT"}


def test_get_flow_share_destination_mapped_from_target_label() -> None:
    """The FlowShareBlock 'destination' field must be populated from the 'target' label.

    :return: None
    :rtype: None
    """
    svc = FlowShareService(metrics_repo=FakeRepo([_m(_NOW, 0.5, target="DE")]))

    block = svc.get_flow_share()[0].series[0].flows[0]

    assert block.destination == "DE"


def test_get_flow_share_separate_series_by_validity() -> None:
    """Different (valid, zone_status) pairs must create separate FlowShareSeries.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 0.3, valid=True, zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 0.2, valid=False, zone_status="preview"),
    ]
    svc = FlowShareService(metrics_repo=FakeRepo(metrics))

    assert len(svc.get_flow_share()[0].series) == 2


def test_get_flow_share_block_values_sorted_by_timestamp() -> None:
    """Values within a block must be sorted ascending by timestamp.

    :return: None
    :rtype: None
    """
    t0 = _NOW
    t2 = _NOW + timedelta(hours=2)
    t1 = _NOW + timedelta(hours=1)

    metrics = [_m(t0, 0.1), _m(t2, 0.3), _m(t1, 0.2)]
    svc = FlowShareService(metrics_repo=FakeRepo(metrics))

    values = svc.get_flow_share()[0].series[0].flows[0].values

    assert values[0][0] == t0
    assert values[1][0] == t1
    assert values[2][0] == t2
