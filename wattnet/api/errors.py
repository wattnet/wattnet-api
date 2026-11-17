"""Errors of the API: the ``detail`` of always and a stable ``code`` next to it.

``detail`` is a sentence for a person and can be reworded; ``code`` is for programs and
does not change. A client that handles errors should read ``code`` and show ``detail``.
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, StarletteHTTPException
from fastapi.responses import JSONResponse

# For the errors that FastAPI itself raises (an unknown route, a method not allowed...).
_DEFAULT_CODES = {
    404: "not_found",
    405: "method_not_allowed",
    500: "internal_error",
}


class ApiError(HTTPException):
    """An HTTP error with a stable ``code``."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Create the error.

        :param status_code: HTTP status of the answer
        :param detail: Sentence that says what is wrong
        :param code: Stable identifier of the error, in lower snake case
        :param headers: Extra headers of the answer
        """
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code


async def _http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Answer with the ``detail`` of always and the ``code``."""
    code = getattr(exc, "code", None) or _DEFAULT_CODES.get(exc.status_code, "error")
    body: Dict[str, Any] = {"detail": exc.detail, "code": code}
    return JSONResponse(body, status_code=exc.status_code, headers=exc.headers)


async def _validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Answer 422 with the list of ``detail`` of FastAPI and the ``code``."""
    body = {"detail": jsonable_encoder(exc.errors()), "code": "validation_error"}
    return JSONResponse(body, status_code=422)


def install_error_handlers(app: FastAPI) -> None:
    """Make an app answer its errors with the ``code``.

    :param app: App to change. The versioned apps that ``VersionedFastAPI`` mounts do
        not inherit the handlers of the parent, so each one needs it.
    """
    app.add_exception_handler(StarletteHTTPException, _http_error)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validation_error)  # type: ignore[arg-type]
