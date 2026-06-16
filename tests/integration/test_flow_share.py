"""Integration tests for GET /v1/flow_share."""

from __future__ import annotations

from datetime import datetime, timezone

from tests.unit.service.helpers import FakeMetric

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
_URL = "/v1/flow-share"


def _m(**kw) -> FakeMetric:
    d = {"zone": "ES", "unit": "%", "target": "FR",
         "valid": "true", "zone_status": "complete"}
    d.update(kw)
    return FakeMetric(_NOW, 15.0, d)


def test_200_empty(client, mock_db) -> None:
    """Empty DB returns 200 with empty list.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(_URL).status_code == 200
    assert client.get(_URL).json() == []


def test_returns_flow_share_structure(client, mock_db) -> None:
    """Valid metric produces a correctly nested FlowShare object.

    :return: None
    :rtype: None
    """
    mock_db([_m()])
    body = client.get(_URL).json()
    assert body[0]["zone"] == "ES"
    assert body[0]["series"][0]["flows"][0]["destination"] == "FR"


def test_zone_uppercased(client, mock_db) -> None:
    """Lowercase zone param must be uppercased before service call.

    :return: None
    :rtype: None
    """
    mock_db([_m(zone="PT")])
    assert client.get(f"{_URL}?zone=pt").json()[0]["zone"] == "PT"


def test_lat_lon_found(client, mock_db, mock_geo) -> None:
    """Valid coordinates returning a zone produce 200.

    :return: None
    :rtype: None
    """
    mock_geo("ES")
    mock_db([_m()])
    assert client.get(f"{_URL}?lat=40&lon=-3").status_code == 200


def test_lat_lon_not_found(client, mock_db, mock_geo) -> None:
    """Coordinates with no matching zone return 404.

    :return: None
    :rtype: None
    """
    mock_geo(None)
    mock_db([])
    assert client.get(f"{_URL}?lat=0&lon=0").status_code == 404


def test_zone_and_lat_returns_400(client, mock_db) -> None:
    """Providing both zone and lat must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?zone=ES&lat=40").status_code == 400


def test_lat_without_lon_returns_400(client, mock_db) -> None:
    """Providing lat without lon must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?lat=40").status_code == 400


def test_start_without_end_returns_400(client, mock_db) -> None:
    """start without end must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?start=2025-01-01T00:00:00Z").status_code == 400


def test_destination_zone_and_destination_lat_returns_400(client, mock_db) -> None:
    """Providing both destination_zone and destination_lat must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?destination_zone=FR&destination_lat=48").status_code == 400


def test_start_and_end_returns_200(client, mock_db) -> None:
    """Valid start and end datetimes must return 200.

    :return: None
    :rtype: None
    """
    mock_db([])
    r = client.get(f"{_URL}?start=2025-01-01T00:00:00Z&end=2025-01-02T00:00:00Z")
    assert r.status_code == 200
