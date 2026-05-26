"""Integration tests for GET /v1/mix."""

from __future__ import annotations

from datetime import UTC, datetime

from tests.unit.service.helpers import FakeMetric

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)
_URL = "/v1/mix"


def _m(**kw) -> FakeMetric:
    d = {"zone": "ES", "unit": "MW", "production_type": "solar",
         "data_state": "official", "datasource": "flow_tracing",
         "valid": True, "zone_status": "complete"}
    d.update(kw)
    return FakeMetric(_NOW, 200.0, d)


def test_200_empty(client, mock_db) -> None:
    """Empty DB returns 200 with empty list.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(_URL).status_code == 200
    assert client.get(_URL).json() == []


def test_returns_mix_structure(client, mock_db) -> None:
    """Valid metric produces a correctly nested Mix object.

    :return: None
    :rtype: None
    """
    mock_db([_m()])
    body = client.get(_URL).json()
    assert body[0]["zone"] == "ES"
    assert body[0]["series"][0]["production"][0]["production_type"] == "solar"


def test_zone_uppercased(client, mock_db) -> None:
    """Lowercase zone param must be uppercased before service call.

    :return: None
    :rtype: None
    """
    mock_db([_m(zone="PT")])
    assert client.get(f"{_URL}?zone=pt").json()[0]["zone"] == "PT"


def test_invalid_production_type_returns_400(client, mock_db) -> None:
    """Unknown production_type must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?production_type=invalid").status_code == 400


def test_valid_production_type_passes(client, mock_db) -> None:
    """Known production_type must be accepted.

    :return: None
    :rtype: None
    """
    mock_db([_m(production_type="wind_onshore")])
    assert client.get(f"{_URL}?production_type=wind_onshore").status_code == 200


def test_zone_and_lat_returns_400(client, mock_db) -> None:
    """Providing both zone and lat must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?zone=ES&lat=40").status_code == 400


def test_start_without_end_returns_400(client, mock_db) -> None:
    """start without end must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?start=2025-01-01T00:00:00Z").status_code == 400
