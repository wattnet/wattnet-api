"""Integration tests for the top-level versioned app (favicon, main)."""

from __future__ import annotations

from unittest.mock import patch


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
