"""Every error carries a stable ``code`` next to the ``detail`` it always had."""

from __future__ import annotations

import pytest


@pytest.mark.parametrize("prefix", ["/v1", "/latest"])
def test_a_validation_error_of_the_api_has_a_code(client, mock_db, prefix) -> None:
    """A 400 raised by the API says its code and keeps the detail.

    :return: None
    :rtype: None
    """
    mock_db([])
    r = client.get(f"{prefix}/generation?zone=ES&lat=40&lon=-3")
    assert r.status_code == 400
    assert r.json()["code"] == "zone_and_coordinates_conflict"
    assert "must NOT be provided" in r.json()["detail"]


def test_a_404_for_coordinates_has_a_code(client, mock_db, mock_geo) -> None:
    """A 404 raised by the API has its code.

    :return: None
    :rtype: None
    """
    mock_geo(None)
    mock_db([])
    r = client.get("/v1/generation?lat=0&lon=0")
    assert (r.status_code, r.json()["code"]) == (404, "zone_not_found_for_coordinates")


def test_an_unknown_parameter_has_a_code(client) -> None:
    """The validator of the query parameters says its code.

    :return: None
    :rtype: None
    """
    r = client.get("/v1/zones?nope=1")
    assert (r.status_code, r.json()["code"]) == (400, "unknown_parameter")


def test_fastapi_validation_keeps_its_detail_list_and_adds_a_code(client) -> None:
    """A 422 keeps the list of FastAPI in ``detail`` and adds ``code``.

    :return: None
    :rtype: None
    """
    r = client.get("/v1/generation?lat=abc&lon=-3")
    assert r.status_code == 422
    assert r.json()["code"] == "validation_error"
    assert isinstance(r.json()["detail"], list) and r.json()["detail"][0]["loc"]


def test_an_unknown_route_has_a_code(client) -> None:
    """The errors that FastAPI raises get a code too.

    :return: None
    :rtype: None
    """
    r = client.get("/v1/not-a-route")
    assert (r.status_code, r.json()) == (
        404,
        {"detail": "Not Found", "code": "not_found"},
    )
