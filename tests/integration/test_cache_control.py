"""The answers that carry data say how long a client may reuse them."""

from __future__ import annotations

import asyncio

from tests.integration.test_load import _URL, _m
from wattnet.api.cache import CacheControlMiddleware, _is_data


def test_data_answer_is_private_and_reusable_for_a_minute(client, mock_db) -> None:
    """A 200 of a data endpoint carries ``Cache-Control: private, max-age=60``.

    :return: None
    :rtype: None
    """
    mock_db([_m()])
    for url in (_URL, _URL.replace("/v1", "/latest")):
        assert client.get(url).headers["cache-control"] == "private, max-age=60"


def test_what_is_not_data_or_not_a_200_has_no_header(client, mock_db) -> None:
    """The status checks, the documents, the errors and the probes carry none.

    :return: None
    :rtype: None
    """
    mock_db([])
    assert "cache-control" not in client.get("/v1/status").headers
    assert "cache-control" not in client.get("/v1/docs").headers
    assert "cache-control" not in client.get("/v1/openapi.json").headers
    assert "cache-control" not in client.get("/healthz").headers
    assert "cache-control" not in client.get(f"{_URL}?nope=1").headers  # a 400
    assert "cache-control" not in client.post(_URL).headers  # a 405


def test_paths_that_are_data() -> None:
    """Only /v1 and /latest paths outside the status checks and the documents.

    :return: None
    :rtype: None
    """
    assert _is_data("/v1/load") and _is_data("/latest/zones")
    assert not _is_data("/v1/status/storage") and not _is_data("/v1/docs")
    assert not _is_data("/static/images/a.png") and not _is_data("/healthz")


def test_zero_sends_nothing_and_an_existing_header_is_kept() -> None:
    """With 0 the app adds nothing, and a header that is already there stays.

    :return: None
    :rtype: None
    """
    sent: list = []

    async def app(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"cache-control", b"no-store")],
            }
        )

    async def send(message):
        sent.append(message)

    async def run(scope, max_age):
        sent.clear()
        await CacheControlMiddleware(app, max_age)(scope, None, send)

    scope = {"type": "http", "method": "GET", "path": "/v1/load"}
    asyncio.run(run(scope, 60))
    assert sent[0]["headers"] == [(b"cache-control", b"no-store")]
    asyncio.run(run(scope, 0))
    assert sent[0]["headers"] == [(b"cache-control", b"no-store")]
    asyncio.run(run({"type": "lifespan"}, 60))
    assert len(sent) == 1
