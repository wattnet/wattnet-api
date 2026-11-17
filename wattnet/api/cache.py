"""``Cache-Control`` of the answers that carry data.

The data of the API changes every 15 minutes, so a client that asks the same thing twice
in a minute gets the same answer. The header lets a browser or a client reuse it. It is
``private`` because the answer depends on the access level of who asks: the same URL
may be a 200 for one tier and a 403 for another, and a shared cache must not mix them.
"""

from typing import Awaitable, Callable, MutableMapping

Scope = MutableMapping[str, object]
Message = MutableMapping[str, object]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]

_DATA_PREFIXES = ("/v1/", "/latest/")
# What is not data, or must be seen as it is now: the status checks, the documents.
_NOT_DATA = ("/status", "/docs", "/openapi.json")


def _is_data(path: str) -> bool:
    if not path.startswith(_DATA_PREFIXES):
        return False
    rest = path.split("/", 2)[2]
    return not any(f"/{rest}".startswith(p) for p in _NOT_DATA)


class CacheControlMiddleware:
    """Add ``Cache-Control: private, max-age=N`` to the 200 answers of the data."""

    def __init__(self, app: Callable, max_age: int) -> None:
        """Wrap an ASGI app.

        :param app: The ASGI app to wrap
        :param max_age: Seconds a client may reuse an answer; 0 adds nothing
        """
        self.app = app
        self.value = f"private, max-age={max_age}".encode()
        self.enabled = max_age > 0

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Pass the request on and add the header to the start of the answer."""
        if not (
            self.enabled
            and scope["type"] == "http"
            and scope["method"] == "GET"
            and _is_data(str(scope["path"]))
        ):
            await self.app(scope, receive, send)
            return

        async def with_header(message: Message) -> None:
            if message["type"] == "http.response.start" and message["status"] == 200:
                headers = list(message.get("headers", []))  # type: ignore[call-overload]
                if not any(k.lower() == b"cache-control" for k, _ in headers):
                    headers.append((b"cache-control", self.value))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, with_header)
