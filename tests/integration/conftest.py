"""
Shared fixtures for integration tests of the wattnet API.

Integration tests use the real versioned FastAPI application with a single
mock boundary: MetricsRepository.query_metrics. This lets tests exercise the
full router → validation → service → model-serialisation pipeline without
requiring a live ClickHouse instance.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.unit.service.helpers import FakeMetric  # noqa: F401 – re-exported for tests


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Return a TestClient for the full versioned FastAPI application.

    All v1 endpoints are reachable at /v1/<path>.

    The import is deferred to fixture time so that the StorageClientsManager
    patch from tests/conftest.py pytest_configure has already been applied
    before the app module is loaded.

    :return: TestClient bound to versioned_app
    :rtype: TestClient
    """
    from wattnet.api.app import versioned_app

    return TestClient(versioned_app)


@pytest.fixture
def mock_db(monkeypatch):
    """Return a callable that configures what MetricsRepository.query_metrics returns.

    Usage::

        def test_something(client, mock_db):
            mock_db([metric1, metric2])
            r = client.get("/v1/generation")
            assert r.status_code == 200

    The patch applies to the MetricsRepository *class*, so all service
    singletons (which share the same repo instance) use the mocked version.

    :param monkeypatch: pytest monkeypatch fixture
    :return: callable(metrics) that sets the return value for query_metrics
    """

    def _configure(metrics):
        monkeypatch.setattr(
            "wattnet.storage.repository.MetricsRepository.query_metrics",
            lambda self, *args, **kwargs: metrics,
        )

    return _configure


@pytest.fixture
def mock_geo(monkeypatch):
    """Return a callable that configures what geo.get_zone_code returns.

    Usage::

        def test_latlon(client, mock_db, mock_geo):
            mock_geo("ES")          # zone found
            mock_db([])
            r = client.get("/v1/generation?lat=40&lon=-3")
            assert r.status_code == 200

        def test_latlon_notfound(client, mock_db, mock_geo):
            mock_geo(None)          # no zone
            mock_db([])
            r = client.get("/v1/generation?lat=0&lon=0")
            assert r.status_code == 404

    :param monkeypatch: pytest monkeypatch fixture
    :return: callable(zone_or_none) that sets the return value for get_zone_code
    """

    def _configure(zone):
        monkeypatch.setattr(
            "wattnet.api.utils.validation.geo.get_zone_code",
            lambda lat, lon: zone,
        )

    return _configure
