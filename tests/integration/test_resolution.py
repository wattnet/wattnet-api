"""The ``resolution`` of the series: a resampled read, off by default."""

from __future__ import annotations

import pytest

_RANGE = "start=2025-06-01T00:00:00Z&end=2025-06-02T00:00:00Z"
_SERIES = [
    "/v1/load",
    "/v1/generation",
    "/v1/imports",
    "/v1/exports",
    "/v1/mix",
    "/v1/footprints",
    "/v1/impacts",
    "/v1/environmental-score",
]
_AGGREGABLE = ["/v1/footprints", "/v1/impacts", "/v1/environmental-score"]
_NO_RESOLUTION = [
    "/v1/factors",
    "/v1/flow-share",
    "/v1/mix-share",
    "/v1/footprint-share",
    "/v1/impact-share",
]


@pytest.fixture
def calls(monkeypatch):
    """Record the arguments the storage is asked with, and return no data."""
    seen: list[dict] = []

    def query_metrics(self, *args, **kwargs):
        seen.append(kwargs)
        return []

    monkeypatch.setattr(
        "wattnet.storage.repository.MetricsRepository.query_metrics", query_metrics
    )
    return seen


@pytest.mark.parametrize("url", _SERIES)
@pytest.mark.parametrize("resolution,minutes", [("1h", 60), ("1d", 1440)])
def test_the_resolution_reaches_the_storage(client, calls, url, resolution, minutes):
    """A coarser resolution is asked of the storage in minutes."""
    r = client.get(f"{url}?{_RANGE}&resolution={resolution}")
    assert r.status_code == 200
    assert calls and all(c["resolution_minutes"] == minutes for c in calls)
    # the negatives are dropped before the average, as the services do after reading
    assert all(c["min_value"] == 0 for c in calls)


@pytest.mark.parametrize("url", _SERIES)
@pytest.mark.parametrize("query", ["", "&resolution=15m"])
def test_without_resolution_or_with_15m_the_call_is_the_one_of_always(
    client, calls, url, query
):
    """The series as it is: the storage is not asked for anything new."""
    assert client.get(f"{url}?{_RANGE}{query}").status_code == 200
    assert calls and all(
        "resolution_minutes" not in c and "min_value" not in c for c in calls
    )


@pytest.mark.parametrize("url", _SERIES)
def test_an_unknown_resolution_is_refused(client, calls, url):
    """Only 15m, 1h and 1d."""
    r = client.get(f"{url}?{_RANGE}&resolution=7m")
    assert r.status_code == 400
    assert "Invalid resolution" in r.json()["detail"]
    assert not calls


@pytest.mark.parametrize("url", _AGGREGABLE)
def test_the_aggregate_has_no_resolution(client, calls, url):
    """aggregate=true is already one value."""
    r = client.get(f"{url}?{_RANGE}&aggregate=true&resolution=1h")
    assert r.status_code == 400
    assert "aggregate=true" in r.json()["detail"]
    assert not calls


@pytest.mark.parametrize("url", _NO_RESOLUTION)
def test_the_endpoints_that_are_not_averaged_do_not_take_it(client, calls, url):
    """A share or a factor is not averaged, so the parameter is not theirs."""
    assert client.get(f"{url}?resolution=1h").status_code == 400
    assert not calls


def test_the_refusals_have_a_code(client, calls):
    """The errors of the resolution say their code, as the others do."""
    r = client.get(f"/v1/load?{_RANGE}&resolution=7m")
    assert (r.status_code, r.json()["code"]) == (400, "invalid_resolution")
    r = client.get(f"/v1/footprints?{_RANGE}&aggregate=true&resolution=1h")
    assert (r.status_code, r.json()["code"]) == (400, "resolution_with_aggregate")
