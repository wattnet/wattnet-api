"""
Integration tests for GET /v1/generation.

These tests exercise the full pipeline:
  HTTP request → router validation → GenerationService → JSON serialisation

The only mock boundary is MetricsRepository.query_metrics.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from tests.unit.service.helpers import FakeMetric

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)
_URL = "/v1/generation"


def _metric(**kw) -> FakeMetric:
    defaults = {
        "zone": "ES",
        "unit": "MW",
        "production_type": "solar",
        "data_state": "official",
        "datasource": "ENTSO-E",
        "valid": True,
        "zone_status": "complete",
    }
    defaults.update(kw)
    return FakeMetric(timestamp=_NOW, value=100.0, metadata=defaults)


# ── Happy path ────────────────────────────────────────────────────────────────


def test_returns_200_empty_list(client, mock_db) -> None:
    """Empty DB produces a 200 with an empty list.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(_URL).status_code == 200
    assert client.get(_URL).json() == []


def test_returns_generation_structure(client, mock_db) -> None:
    """A single metric produces a correctly nested Generation object.

    :return: None
    :rtype: None
    """
    mock_db([_metric()])
    r = client.get(_URL)
    assert r.status_code == 200
    body = r.json()
    assert body[0]["zone"] == "ES"
    assert body[0]["series"][0]["production"][0]["production_type"] == "solar"


def test_zone_filter_is_uppercased(client, mock_db) -> None:
    """Lowercase zone query param must be uppercased before reaching the service.

    :return: None
    :rtype: None
    """
    mock_db([_metric(zone="FR")])
    r = client.get(f"{_URL}?zone=fr")
    assert r.status_code == 200
    assert r.json()[0]["zone"] == "FR"


def test_lat_lon_zone_found(client, mock_db, mock_geo) -> None:
    """Valid lat/lon that resolves to a zone returns 200.

    :return: None
    :rtype: None
    """
    mock_geo("ES")
    mock_db([_metric()])
    assert client.get(f"{_URL}?lat=40&lon=-3").status_code == 200


def test_lat_lon_zone_not_found_returns_404(client, mock_db, mock_geo) -> None:
    """lat/lon that resolves to no zone must return 404.

    :return: None
    :rtype: None
    """
    mock_geo(None)
    mock_db([])
    assert client.get(f"{_URL}?lat=0&lon=0").status_code == 404


# ── Validation errors ─────────────────────────────────────────────────────────


def test_zone_and_lat_together_returns_400(client, mock_db) -> None:
    """Providing both zone and lat is rejected with 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?zone=ES&lat=40").status_code == 400


def test_lat_without_lon_returns_400(client, mock_db) -> None:
    """Providing lat without lon is rejected with 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?lat=40").status_code == 400


def test_start_without_end_returns_400(client, mock_db) -> None:
    """Providing start without end is rejected with 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?start=2025-01-01T00:00:00Z").status_code == 400


def test_start_after_end_returns_400(client, mock_db) -> None:
    """Providing start > end is rejected with 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    r = client.get(f"{_URL}?start=2025-01-02T00:00:00Z&end=2025-01-01T00:00:00Z")
    assert r.status_code == 400


def test_invalid_production_type_returns_400(client, mock_db) -> None:
    """An unrecognised production_type must be rejected with 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?production_type=unknown").status_code == 400


def test_valid_production_type_passes(client, mock_db) -> None:
    """A recognised production_type must be accepted.

    :return: None
    :rtype: None
    """
    mock_db([_metric(production_type="solar")])
    assert client.get(f"{_URL}?production_type=solar").status_code == 200
