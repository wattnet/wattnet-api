"""Integration tests for the top-level versioned app (favicon, main)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


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
    from wattnet.api.app import main

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
        "wattnet.api.routers.v1.status.metrics_repo", MagicMock(ping=lambda: True)
    )
    assert client.get("/readyz").status_code == 200


def test_readyz_is_503_when_the_storage_does_not_answer(client, monkeypatch) -> None:
    """The readiness probe is 503 when the storage does not answer.

    :return: None
    :rtype: None
    """
    monkeypatch.setattr(
        "wattnet.api.routers.v1.status.metrics_repo", MagicMock(ping=lambda: False)
    )
    assert client.get("/readyz").status_code == 503
