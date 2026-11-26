"""Integration tests for GET /v1/status endpoints."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from wattnet.api.rest.v1.status import (
    check_elexon_api,
    check_entsoe_api,
    check_epias_api,
    check_storage_system,
    clear_cache,
)

_URL = "/v1/status"


@pytest.fixture(autouse=True)
def _no_cache() -> None:
    """Start every test with no answer of a provider remembered."""
    clear_cache()


@pytest.fixture
def mock_requests_up(monkeypatch):
    """Patch requests.get to simulate all external services reachable.

    :param monkeypatch: pytest monkeypatch fixture
    """
    mock = MagicMock()
    mock.return_value.status_code = 200
    monkeypatch.setattr("wattnet.api.rest.v1.status.requests.get", mock)
    monkeypatch.setattr(
        "wattnet.api.rest.v1.status.metrics_repo", MagicMock(ping=lambda: True)
    )


@pytest.fixture
def mock_requests_down(monkeypatch):
    """Patch requests.get to raise RequestException (service unreachable).

    :param monkeypatch: pytest monkeypatch fixture
    """
    import requests as _requests

    monkeypatch.setattr(
        "wattnet.api.rest.v1.status.requests.get",
        MagicMock(side_effect=_requests.RequestException("unreachable")),
    )
    monkeypatch.setattr(
        "wattnet.api.rest.v1.status.metrics_repo", MagicMock(ping=lambda: False)
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


# ── Missing URL branches ──────────────────────────────────────────────────────


def test_check_storage_system_ping_false_returns_false(monkeypatch) -> None:
    """check_storage_system() must return False when the storage does not answer.

    :return: None
    :rtype: None
    """
    monkeypatch.setattr(
        "wattnet.api.rest.v1.status.metrics_repo", MagicMock(ping=lambda: False)
    )
    assert check_storage_system() is False


def test_check_storage_system_ping_error_returns_false(monkeypatch) -> None:
    """check_storage_system() must return False, not raise, when ping() fails.

    :return: None
    :rtype: None
    """
    repo = MagicMock()
    repo.ping.side_effect = RuntimeError("no client")
    monkeypatch.setattr("wattnet.api.rest.v1.status.metrics_repo", repo)
    assert check_storage_system() is False


def test_check_entsoe_api_missing_url_returns_false(monkeypatch) -> None:
    """check_entsoe_api() must return False when entsoe_url is empty.

    :return: None
    :rtype: None
    """
    monkeypatch.setattr(
        "wattnet.api.rest.v1.status.settings",
        MagicMock(entsoe_url=""),
    )
    assert check_entsoe_api() is False


def test_check_elexon_api_missing_url_returns_false(monkeypatch) -> None:
    """check_elexon_api() must return False when elexon_url is empty.

    :return: None
    :rtype: None
    """
    monkeypatch.setattr(
        "wattnet.api.rest.v1.status.settings",
        MagicMock(elexon_url=""),
    )
    assert check_elexon_api() is False


def test_check_epias_api_missing_url_returns_false(monkeypatch) -> None:
    """check_epias_api() must return False when epias_url is empty.

    :return: None
    :rtype: None
    """
    monkeypatch.setattr(
        "wattnet.api.rest.v1.status.settings",
        MagicMock(epias_url=""),
    )
    assert check_epias_api() is False


def test_provider_answer_is_kept_for_a_few_seconds(monkeypatch) -> None:
    """The third party is asked once in the cache time, and again after it.

    :return: None
    :rtype: None
    """
    clock = [100.0]
    monkeypatch.setattr("wattnet.api.rest.v1.status.time.monotonic", lambda: clock[0])
    mock = MagicMock()
    monkeypatch.setattr("wattnet.api.rest.v1.status.requests.get", mock)

    assert check_entsoe_api() is True
    assert check_entsoe_api() is True
    assert mock.call_count == 1

    clock[0] += 31
    assert check_entsoe_api() is True
    assert mock.call_count == 2


def test_status_asks_the_providers_at_the_same_time(client, monkeypatch) -> None:
    """The three providers are asked at the same time, not one after the other.

    Each call waits for the other two at a barrier: asked one by one, the first
    call would wait alone until the barrier gives up.

    :return: None
    :rtype: None
    """
    import threading

    barrier = threading.Barrier(3, timeout=5)

    def get(*_args, **_kwargs) -> MagicMock:
        barrier.wait()
        return MagicMock(status_code=200)

    monkeypatch.setattr("wattnet.api.rest.v1.status.requests.get", get)
    monkeypatch.setattr(
        "wattnet.api.rest.v1.status.metrics_repo", MagicMock(ping=lambda: True)
    )
    r = client.get(_URL)
    assert r.status_code == 200
    assert r.json() == {"storage": "up", "entso-e": "up", "elexon": "up", "epias": "up"}
