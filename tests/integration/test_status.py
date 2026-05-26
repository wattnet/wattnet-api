"""Integration tests for GET /v1/status endpoints."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

_URL = "/v1/status"


@pytest.fixture
def mock_requests_up(monkeypatch):
    """Patch requests.get to simulate all external services reachable.

    :param monkeypatch: pytest monkeypatch fixture
    """
    mock = MagicMock()
    mock.return_value.status_code = 200
    monkeypatch.setattr("wattnet.api.routers.v1.status.requests.get", mock)


@pytest.fixture
def mock_requests_down(monkeypatch):
    """Patch requests.get to raise RequestException (service unreachable).

    :param monkeypatch: pytest monkeypatch fixture
    """
    import requests as _requests

    monkeypatch.setattr(
        "wattnet.api.routers.v1.status.requests.get",
        MagicMock(side_effect=_requests.RequestException("unreachable")),
    )


def test_status_all_up(client, mock_requests_up) -> None:
    """When all services are reachable, /status returns all 'up'.

    :return: None
    :rtype: None
    """
    r = client.get(_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["storage"] == "up"
    assert body["entso-e"] == "up"
    assert body["elexon"] == "up"
    assert body["epias"] == "up"


def test_status_all_down(client, mock_requests_down) -> None:
    """When all services are unreachable, /status returns all 'down'.

    :return: None
    :rtype: None
    """
    r = client.get(_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["storage"] == "down"
    assert body["entso-e"] == "down"
    assert body["elexon"] == "down"
    assert body["epias"] == "down"


def test_status_storage_up(client, mock_requests_up) -> None:
    """GET /v1/status/storage returns storage status.

    :return: None
    :rtype: None
    """
    r = client.get(f"{_URL}/storage")
    assert r.status_code == 200
    assert r.json()["storage"] == "up"


def test_status_entsoe_up(client, mock_requests_up) -> None:
    """GET /v1/status/entso-e returns entso-e status.

    :return: None
    :rtype: None
    """
    r = client.get(f"{_URL}/entso-e")
    assert r.status_code == 200
    assert r.json()["entso-e"] == "up"


def test_status_elexon_up(client, mock_requests_up) -> None:
    """GET /v1/status/elexon returns elexon status.

    :return: None
    :rtype: None
    """
    r = client.get(f"{_URL}/elexon")
    assert r.status_code == 200
    assert r.json()["elexon"] == "up"


def test_status_epias_up(client, mock_requests_up) -> None:
    """GET /v1/status/epias returns epias status.

    :return: None
    :rtype: None
    """
    r = client.get(f"{_URL}/epias")
    assert r.status_code == 200
    assert r.json()["epias"] == "up"
