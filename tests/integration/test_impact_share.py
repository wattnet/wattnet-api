"""Integration tests for GET /v1/impact_share."""

from __future__ import annotations

from datetime import datetime, timezone

from tests.unit.service.helpers import FakeMetric

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
_URL = "/v1/impact-share"


def _m(**kw) -> FakeMetric:
    d = {"zone": "ES", "unit": "stress-l/kWh", "impact_type": "water",
         "scope": "operational", "source": "FR", "valid": "true", "zone_status": "complete"}
    d.update(kw)
    return FakeMetric(_NOW, 0.8, d)


def test_200_empty(client, mock_db) -> None:
    """Empty DB returns 200 with empty list.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(_URL).status_code == 200
    assert client.get(_URL).json() == []


def test_returns_impact_share_structure(client, mock_db) -> None:
    """Valid metric produces a correctly nested ImpactShare object.

    :return: None
    :rtype: None
    """
    mock_db([_m()])
    body = client.get(_URL).json()
    assert body[0]["zone"] == "ES"
    assert body[0]["impact_type"] == "water"
    assert body[0]["series"][0]["blocks"][0]["source"] == "FR"


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


def test_invalid_impact_type_returns_400(client, mock_db) -> None:
    """Unknown impact_type must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?impact_type=carbon").status_code == 400


def test_valid_impact_type_passes(client, mock_db) -> None:
    """Known impact_type must be accepted.

    :return: None
    :rtype: None
    """
    mock_db([_m()])
    assert client.get(f"{_URL}?impact_type=water").status_code == 200


def test_invalid_scope_returns_400(client, mock_db) -> None:
    """Invalid scope must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?scope=life-cycle").status_code == 400


def test_start_without_end_returns_400(client, mock_db) -> None:
    """start without end must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?start=2025-01-01T00:00:00Z").status_code == 400


def test_source_zone_and_source_lat_returns_400(client, mock_db) -> None:
    """Providing both source_zone and source_lat must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?source_zone=FR&source_lat=48").status_code == 400


def test_start_and_end_returns_200(client, mock_db) -> None:
    """Valid start and end datetimes must return 200.

    :return: None
    :rtype: None
    """
    mock_db([])
    r = client.get(f"{_URL}?start=2025-01-01T00:00:00Z&end=2025-01-02T00:00:00Z")
    assert r.status_code == 200
