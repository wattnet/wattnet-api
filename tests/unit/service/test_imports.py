"""
Unit tests for wattnet.api.service.imports module.

These tests validate:
- Filtering of invalid (None/negative) metric values
- Hierarchical grouping: Import → ImportSeries → ImportBlock
- Separation into series by (valid, zone_status) pairs
- Separation into blocks by (from/source, data_state, datasource)
- Chronological ordering of values within blocks
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tests.unit.service.helpers import FakeMetric, FakeRepo
from wattnet.api.service.imports import ImportService

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)


def _m(
    ts: datetime,
    value: float | None,
    zone: str = "ES",
    unit: str = "MW",
    from_zone: str = "FR",
    data_state: str = "official",
    datasource: str = "ENTSO-E",
    valid: bool = True,
    zone_status: str = "complete",
) -> FakeMetric:
    """Build a FakeMetric with import metadata.

    :param ts: Timestamp
    :param value: Metric value
    :param zone: Destination zone code
    :param unit: Energy unit
    :param from_zone: Origin zone label (DB uses 'from')
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
            "from": from_zone,
            "data_state": data_state,
            "datasource": datasource,
            "valid": valid,
            "zone_status": zone_status,
        },
    )


# ============================================================
# get_imports — basic filtering
# ============================================================


def test_get_imports_returns_empty_when_no_metrics() -> None:
    """Empty repository must produce an empty result.

    :return: None
    :rtype: None
    """
    svc = ImportService(metrics_repo=FakeRepo([]))
    assert svc.get_imports() == []


def test_get_imports_filters_none_values() -> None:
    """Metrics with value=None must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, None), _m(_NOW + timedelta(hours=1), 500.0)]
    svc = ImportService(metrics_repo=FakeRepo(metrics))

    results = svc.get_imports()

    assert len(results) == 1
    assert results[0].series[0].imports[0].values[0][1] == pytest.approx(500.0)


def test_get_imports_filters_negative_values() -> None:
    """Metrics with negative values must be excluded.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, -5.0), _m(_NOW + timedelta(hours=1), 250.0)]
    svc = ImportService(metrics_repo=FakeRepo(metrics))

    results = svc.get_imports()

    assert len(results) == 1
    assert results[0].series[0].imports[0].values[0][1] == pytest.approx(250.0)


# ============================================================
# _group_metrics — structure
# ============================================================


def test_get_imports_one_object_per_zone() -> None:
    """Metrics for separate destination zones must produce separate Import objects.

    :return: None
    :rtype: None
    """
    metrics = [_m(_NOW, 100.0, zone="ES"), _m(_NOW, 200.0, zone="FR")]
    svc = ImportService(metrics_repo=FakeRepo(metrics))

    results = svc.get_imports()

    assert len(results) == 2
    assert {r.zone for r in results} == {"ES", "FR"}


def test_get_imports_separate_blocks_by_source() -> None:
    """Metrics from different origin zones must produce separate ImportBlocks.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, from_zone="FR"),
        _m(_NOW + timedelta(hours=1), 50.0, from_zone="PT"),
    ]
    svc = ImportService(metrics_repo=FakeRepo(metrics))

    blocks = svc.get_imports()[0].series[0].imports

    assert {b.source for b in blocks} == {"FR", "PT"}


def test_get_imports_source_field_is_populated_from_from_label() -> None:
    """The ImportBlock 'source' field must be populated from the 'from' label.

    :return: None
    :rtype: None
    """
    svc = ImportService(metrics_repo=FakeRepo([_m(_NOW, 100.0, from_zone="DE")]))

    block = svc.get_imports()[0].series[0].imports[0]

    assert block.source == "DE"


def test_get_imports_separate_series_by_validity() -> None:
    """Different (valid, zone_status) pairs must create separate ImportSeries.

    :return: None
    :rtype: None
    """
    metrics = [
        _m(_NOW, 100.0, valid=True, zone_status="complete"),
        _m(_NOW + timedelta(hours=1), 80.0, valid=False, zone_status="preview"),
    ]
    svc = ImportService(metrics_repo=FakeRepo(metrics))

    assert len(svc.get_imports()[0].series) == 2


def test_get_imports_with_source_filter() -> None:
    """Calling get_imports(source=...) must not raise and returns a list.

    :return: None
    :rtype: None
    """
    svc = ImportService(metrics_repo=FakeRepo([]))
    assert svc.get_imports(source="FR") == []


def test_get_imports_block_values_sorted_by_timestamp() -> None:
    """Values within a block must be sorted ascending by timestamp.

    :return: None
    :rtype: None
    """
    t0 = _NOW
    t2 = _NOW + timedelta(hours=2)
    t1 = _NOW + timedelta(hours=1)

    metrics = [_m(t0, 1.0), _m(t2, 3.0), _m(t1, 2.0)]
    svc = ImportService(metrics_repo=FakeRepo(metrics))

    values = svc.get_imports()[0].series[0].imports[0].values

    assert values[0][0] == t0
    assert values[1][0] == t1
    assert values[2][0] == t2


# ============================================================
# get_imports — filter forwarding
# ============================================================


def test_get_imports_with_zone_filter() -> None:
    """zone filter branch is executed when provided.

    :return: None
    :rtype: None
    """
    svc = ImportService(metrics_repo=FakeRepo([]))
    assert svc.get_imports(zone="ES") == []


def test_get_imports_with_source_filter() -> None:
    """source filter branch is executed when provided.

    :return: None
    :rtype: None
    """
    svc = ImportService(metrics_repo=FakeRepo([]))
    assert svc.get_imports(source="FR") == []
