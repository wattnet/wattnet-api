"""Integration tests for GET /v1/zones."""

from __future__ import annotations

import pytest

_URL = "/v1/zones"


@pytest.fixture
def mock_zones(monkeypatch):
    """Return a callable that configures what ZoneService.get_zones returns.

    :param monkeypatch: pytest monkeypatch fixture
    :return: callable(zones) that sets the return value for get_zones
    """
    def _configure(zones):
        monkeypatch.setattr(
            "wattnet.api.dependencies.zone_service.get_zones",
            lambda: zones,
        )
    return _configure


def test_200_empty(client, mock_zones) -> None:
    """Empty zones list returns 200 with empty list.

    :return: None
    :rtype: None
    """
    mock_zones([])
    r = client.get(_URL)
    assert r.status_code == 200
    assert r.json() == []


def test_returns_zone_structure(client, mock_zones) -> None:
    """Service result is serialised and returned as JSON list.

    :return: None
    :rtype: None
    """
    from wattnet.api.models.zone import Zone

    zone = Zone(
        zone="ES",
        full_name="Spain",
        eic_code="10YES-REE------0",
        country_code="ESP",
        country_name="Spain",
        provider="ENTSO-E",
        neighbours=["FR", "PT"],
    )
    mock_zones([zone])
    body = client.get(_URL).json()
    assert body[0]["zone"] == "ES"
    assert "FR" in body[0]["neighbours"]


def test_multiple_zones_returned(client, mock_zones) -> None:
    """Multiple zones are all returned in the response.

    :return: None
    :rtype: None
    """
    from wattnet.api.models.zone import Zone

    zones = [
        Zone(zone="ES", full_name="Spain", eic_code="10YES-REE------0",
             country_code="ESP", country_name="Spain", provider="ENTSO-E",
             neighbours=["FR"]),
        Zone(zone="FR", full_name="France", eic_code="10YFR-RTE------C",
             country_code="FRA", country_name="France", provider="ENTSO-E",
             neighbours=["ES", "DE"]),
    ]
    mock_zones(zones)
    body = client.get(_URL).json()
    assert len(body) == 2
    zone_ids = {z["zone"] for z in body}
    assert zone_ids == {"ES", "FR"}
