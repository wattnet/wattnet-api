"""The OpenAPI document declares the bearer scheme, for the docs only."""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def schema(client) -> dict:
    """Return the OpenAPI document of version 1."""
    return client.get("/v1/openapi.json").json()


def test_declares_only_the_bearer_scheme(schema) -> None:
    """Declare HTTPBearer as the only scheme, so Swagger UI offers Authorize."""
    assert schema["components"]["securitySchemes"] == {
        "HTTPBearer": {"type": "http", "scheme": "bearer"}
    }


@pytest.mark.parametrize(
    "path",
    ["/zones", "/generation", "/footprints", "/factors", "/status/storage"],
)
def test_authenticated_endpoints_require_the_scheme(schema, path) -> None:
    """Authenticated endpoints show the lock in the docs."""
    assert schema["paths"][path]["get"]["security"] == [{"HTTPBearer": []}]


def test_the_aggregate_status_stays_public(schema) -> None:
    """The aggregate status has no lock in the docs."""
    assert "security" not in schema["paths"]["/status"]["get"]


def test_the_app_itself_never_rejects_a_missing_token(client) -> None:
    """The gateway enforces the token, so a request without one reaches the API."""
    assert client.get("/v1/status/storage").status_code != 401
