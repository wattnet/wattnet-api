"""Integration tests for GET /v1/factors."""

from __future__ import annotations

from datetime import UTC, datetime

from tests.unit.service.helpers import FakeMetric

_NOW = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)
_URL = "/v1/factors"


def _m(**kw) -> FakeMetric:
    d = {"factor_type": "carbon", "production_type": "solar",
         "scope": "operational", "unit": "gCO2/kWh",
         "source": "IPCC", "year": 2023, "source_link": "https://ipcc.ch"}
    d.update(kw)
    return FakeMetric(_NOW, 25.0, d)


def test_200_empty(client, mock_db) -> None:
    """Empty DB returns 200 with empty list.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(_URL).status_code == 200
    assert client.get(_URL).json() == []


def test_returns_factor_structure(client, mock_db) -> None:
    """Valid metric produces a correctly nested Factor object.

    :return: None
    :rtype: None
    """
    mock_db([_m()])
    body = client.get(_URL).json()
    assert body[0]["factor_type"] == "carbon"
    assert body[0]["production_type"] == "solar"
    assert body[0]["scope"] == "operational"


def test_invalid_factor_type_returns_400(client, mock_db) -> None:
    """Unknown factor_type must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?factor_type=electric").status_code == 400


def test_valid_factor_type_passes(client, mock_db) -> None:
    """Known factor_type must be accepted.

    :return: None
    :rtype: None
    """
    mock_db([_m(factor_type="water")])
    assert client.get(f"{_URL}?factor_type=water").status_code == 200


def test_invalid_scope_returns_400(client, mock_db) -> None:
    """Unknown scope must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?scope=political").status_code == 400


def test_valid_scope_passes(client, mock_db) -> None:
    """Known scope must be accepted.

    :return: None
    :rtype: None
    """
    mock_db([_m(scope="life-cycle")])
    assert client.get(f"{_URL}?scope=life-cycle").status_code == 200


def test_invalid_production_type_returns_400(client, mock_db) -> None:
    """Unknown production_type must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?production_type=fusion").status_code == 400


def test_valid_production_type_passes(client, mock_db) -> None:
    """Known production_type must be accepted.

    :return: None
    :rtype: None
    """
    mock_db([_m(production_type="wind_onshore")])
    assert client.get(f"{_URL}?production_type=wind_onshore").status_code == 200


def test_aggregate_with_dates_returns_200(client, mock_db) -> None:
    """aggregate=true with start/end must return 200.

    :return: None
    :rtype: None
    """
    mock_db([_m()])
    r = client.get(
        f"{_URL}?aggregate=true"
        "&start=2025-06-01T00:00:00Z&end=2025-06-02T00:00:00Z"
    )
    assert r.status_code == 200


def test_start_without_end_returns_400(client, mock_db) -> None:
    """start without end must return 400.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert client.get(f"{_URL}?start=2025-01-01T00:00:00Z").status_code == 400
