"""Integration tests for the top-level versioned app (favicon, main)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def test_favicon_returns_200(client) -> None:
    """GET /favicon.ico must return 200.

    :return: None
    :rtype: None
    """
    r = client.get("/favicon.ico")
    assert r.status_code == 200


def test_main_calls_uvicorn_run() -> None:
    """main() must invoke uvicorn.run once.

    :return: None
    :rtype: None
    """
    from wattnet.api.main import main

    with patch("uvicorn.run") as mock_run:
        main()

    mock_run.assert_called_once()


def test_healthz_answers_without_asking_anything(client) -> None:
    """The liveness probe answers 200 and is not part of the public docs.

    :return: None
    :rtype: None
    """
    r = client.get("/healthz")
    assert r.status_code == 200
    assert "/healthz" not in client.get("/v1/openapi.json").json()["paths"]


def test_readyz_is_200_when_the_storage_answers(client, monkeypatch) -> None:
    """The readiness probe is 200 when the storage answers.

    :return: None
    :rtype: None
    """
    monkeypatch.setattr(
        "wattnet.api.rest.v1.status.metrics_repo", MagicMock(ping=lambda: True)
    )
    assert client.get("/readyz").status_code == 200


def test_readyz_is_503_when_the_storage_does_not_answer(client, monkeypatch) -> None:
    """The readiness probe is 503 when the storage does not answer.

    :return: None
    :rtype: None
    """
    monkeypatch.setattr(
        "wattnet.api.rest.v1.status.metrics_repo", MagicMock(ping=lambda: False)
    )
    assert client.get("/readyz").status_code == 503


@pytest.mark.parametrize(
    ("query", "fragment"),
    [
        ("zone=ES&zone=FR", "'zone' is repeated"),
        ("zone=", "'zone' is empty"),
    ],
)
@pytest.mark.parametrize("path", ["/v1/generation", "/v1/mix-share"])
def test_a_repeated_or_empty_parameter_is_refused(
    client, mock_db, path: str, query: str, fragment: str
) -> None:
    """A repeated or empty parameter is a 400, not a silently different query."""
    mock_db([])
    r = client.get(f"{path}?{query}")
    assert r.status_code == 400
    assert fragment in r.json()["detail"]


@pytest.mark.parametrize(
    "path", ["/v1/generation", "/v1/mix-share", "/v1/zones", "/v1/status"]
)
def test_an_unknown_parameter_is_refused(client, mock_db, path: str) -> None:
    """A misspelt name is a 400 that lists what the endpoint accepts."""
    mock_db([])
    r = client.get(f"{path}?zon=ES")
    assert r.status_code == 400
    assert "Unknown query parameter 'zon'" in r.json()["detail"]


def test_a_known_query_string_is_accepted(client, mock_db) -> None:
    """The parameters of the endpoint still go through."""
    mock_db([])
    assert client.get("/v1/generation?zone=ES&production_type=solar").status_code == 200
