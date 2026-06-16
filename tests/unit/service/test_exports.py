"""
Unit tests for wattnet.api.service.exports module.

These tests validate:
- Filtering of invalid (None/negative) metric values
- Hierarchical grouping: Export → ExportSeries → ExportBlock
- Separation into series by (valid, zone_status) pairs
- Separation into blocks by (to/destination, data_state, datasource)
- Chronological ordering of values within blocks
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tests.unit.service.helpers import FakeMetric, FakeRepo
from wattnet.api.service.exports import ExportService

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)


def _m(
    ts: datetime,
    value: float | None,
    zone: str = "ES",
    unit: str = "MW",
    to: str = "FR",
    data_state: str = "official",
    datasource: str = "ENTSO-E",
    valid: bool = True,
    zone_status: str = "complete",
) -> FakeMetric:
    """Build a FakeMetric with export metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param zone: Origin zone code
    :param unit: Energy unit
    :param to: Destination zone label (DB uses 'to')
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
            "to": to,
            "data_state": data_state,
            "datasource": datasource,
            "valid": valid,
            "zone_status": zone_status,
        },
    )


# ============================================================
# get_exports — basic filtering
# ============================================================


def test_get_exports_returns_empty_when_no_metrics() -> None:
    """Empty repository must produce an empty result.

    :return: None
    :rtype: None
    """
    svc = ExportService(metrics_repo=FakeRepo([]))
    assert svc.get_exports() == []


def test_get_exports_filters_none_values() -> None:
    """Metrics with value=None must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, None), _m(_NOW + timedelta(hours=1), 400.0)]
    svc = ExportService(metrics_repo=FakeRepo(metrics))

    results = svc.get_exports()

    assert len(results) == 1
    assert results[0].series[0].exports[0].values[0][1] == pytest.approx(400.0)


def test_get_exports_filters_negative_values() -> None:
    """Metrics with negative values must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, -10.0), _m(_NOW + timedelta(hours=1), 300.0)]
    svc = ExportService(metrics_repo=FakeRepo(metrics))

    results = svc.get_exports()

    assert len(results) == 1
    assert results[0].series[0].exports[0].values[0][1] == pytest.approx(300.0)


# ============================================================
# _group_metrics — structure
# ============================================================


def test_get_exports_one_object_per_zone() -> None:
    """Metrics for separate origin zones must produce separate Export objects.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, 100.0, zone="ES"), _m(_NOW, 200.0, zone="FR")]
    svc = ExportService(metrics_repo=FakeRepo(metrics))

    results = svc.get_exports()

    assert len(results) == 2
    assert {r.zone for r in results} == {"ES", "FR"}


def test_get_exports_separate_blocks_by_destination() -> None:
    """Metrics to different destinations must produce separate ExportBlocks.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, to="FR"),
        _m(_NOW + timedelta(hours=1), 50.0, to="PT"),
    ]
    svc = ExportService(metrics_repo=FakeRepo(metrics))

    blocks = svc.get_exports()[0].series[0].exports

    assert {b.destination for b in blocks} == {"FR", "PT"}


def test_get_exports_destination_field_is_populated() -> None:
    """The ExportBlock 'destination' field must be populated from the 'to' label.

    :return: None
    :rtype: None
    """
    svc = ExportService(metrics_repo=FakeRepo([_m(_NOW, 100.0, to="DE")]))

    block = svc.get_exports()[0].series[0].exports[0]

    assert block.destination == "DE"


def test_get_exports_separate_series_by_validity() -> None:
    """Different (valid, zone_status) pairs must create separate ExportSeries.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, valid=True, zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 80.0, valid=False, zone_status="preview"),
    ]
    svc = ExportService(metrics_repo=FakeRepo(metrics))

    assert len(svc.get_exports()[0].series) == 2


def test_get_exports_with_destination_filter() -> None:
    """Calling get_exports(destination=...) must not raise and returns a list.

    :return: None
    :rtype: None
    """
    svc = ExportService(metrics_repo=FakeRepo([]))
    assert svc.get_exports(destination="FR") == []


def test_get_exports_block_values_sorted_by_timestamp() -> None:
    """Values within a block must be sorted ascending by timestamp.

    :return: None
    :rtype: None
    """
    t0 = _NOW
    t2 = _NOW + timedelta(hours=2)
    t1 = _NOW + timedelta(hours=1)

    metrics = [_m(t0, 1.0), _m(t2, 3.0), _m(t1, 2.0)]
    svc = ExportService(metrics_repo=FakeRepo(metrics))

    values = svc.get_exports()[0].series[0].exports[0].values

    assert values[0][0] == t0
    assert values[1][0] == t1
    assert values[2][0] == t2


# ============================================================
# get_exports — filter forwarding
# ============================================================


def test_get_exports_with_zone_filter() -> None:
    """zone filter branch is executed when provided.

    :return: None
    :rtype: None
    """
    svc = ExportService(metrics_repo=FakeRepo([]))
    assert svc.get_exports(zone="ES") == []


def test_get_exports_with_destination_filter() -> None:
    """destination filter branch is executed when provided.

    :return: None
    :rtype: None
    """
    svc = ExportService(metrics_repo=FakeRepo([]))
    assert svc.get_exports(destination="FR") == []
