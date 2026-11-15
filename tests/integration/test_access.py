"""Integration tests for the access tiers on the data endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from wattnet.api import access
from wattnet.api.access import PolicyFile
from tests.unit.test_access import POLICY


def _range(days: float, ago: float = 1) -> str:
    end = datetime.now(timezone.utc) - timedelta(days=ago)
    start = end - timedelta(days=days)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return f"start={start.strftime(fmt)}&end={end.strftime(fmt)}"


@pytest.fixture
def with_policy(monkeypatch, tmp_path: Path) -> None:
    """Put the access policy in force for the test."""
    path = tmp_path / "access-policy.yaml"
    path.write_text(POLICY)
    monkeypatch.setattr(access, "policy", PolicyFile(path))


def _get(client, url: str, tier: str | None):
    return client.get(url, headers={"X-Wattnet-Tier": tier} if tier else {})


def test_a_request_without_tier_is_refused(client, with_policy, mock_db) -> None:
    """Without the header of the gate there is no access level: 403."""
    mock_db([])
    assert _get(client, "/v1/mix?zone=ES", None).status_code == 403
    assert _get(client, "/v1/mix?zone=ES", "nobody").status_code == 403


def test_a_tier_reaches_the_groups_it_has(client, with_policy, mock_db) -> None:
    """Free reaches the energy metrics and not the shares; research reaches both."""
    mock_db([])
    assert _get(client, "/v1/mix?zone=ES", "free").status_code == 200
    assert _get(client, "/v1/mix-share?zone=ES", "free").status_code == 403
    assert _get(client, "/v1/mix-share?zone=ES", "research").status_code == 200
    assert _get(client, "/v1/factors", "free").status_code == 403


def test_free_must_say_the_zone(client, with_policy, mock_db) -> None:
    """Without a zone a query is every zone, which free (one zone) cannot ask."""
    mock_db([])
    assert _get(client, "/v1/mix", "free").status_code == 403
    assert _get(client, "/v1/mix?zone=ES", "free").status_code == 200
    assert _get(client, "/v1/mix", "research").status_code == 200


def test_free_range_history_and_forecast(client, with_policy, mock_db) -> None:
    """Free reaches 7 days of range and of history and no forecast."""
    mock_db([])
    assert _get(client, f"/v1/mix?zone=ES&{_range(3)}", "free").status_code == 200
    assert _get(client, f"/v1/mix?zone=ES&{_range(10)}", "free").status_code == 403
    assert _get(client, f"/v1/mix?zone=ES&{_range(2, ago=20)}", "free").status_code == 403
    future = (datetime.now(timezone.utc) + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    later = (datetime.now(timezone.utc) + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert _get(client, f"/v1/mix?zone=ES&start={future}&end={later}", "free").status_code == 403
    assert _get(client, f"/v1/mix?zone=ES&start={future}&end={later}", "research").status_code == 200


def test_the_size_cap_applies_to_every_tier(client, with_policy, mock_db) -> None:
    """Even a tier with no limit cannot ask more than the server allows."""
    mock_db([])
    assert _get(client, f"/v1/mix?zone=ES&{_range(300)}", "internal").status_code == 200
    r = _get(client, f"/v1/mix?zone=ES&{_range(500)}", "internal")
    assert r.status_code == 400 and "too big" in r.json()["detail"]
    assert _get(client, f"/v1/mix?{_range(31)}", "research").status_code == 400


def test_without_a_policy_the_tiers_are_not_checked(client, mock_db, monkeypatch) -> None:
    """With no policy file, as in development, any request passes, but the cap stays."""
    mock_db([])
    monkeypatch.setattr(access, "policy", None)
    assert _get(client, "/v1/mix", None).status_code == 200
    assert _get(client, f"/v1/mix?zone=ES&{_range(500)}", None).status_code == 400


def test_status_and_the_probes_need_no_tier(client, with_policy, monkeypatch) -> None:
    """The status endpoints and the probes are not part of the groups."""
    from unittest.mock import MagicMock

    monkeypatch.setattr(
        "wattnet.api.routers.v1.status.metrics_repo", MagicMock(ping=lambda: True)
    )
    assert client.get("/v1/status/storage").status_code == 200
    assert client.get("/healthz").status_code == 200



def test_the_list_of_zones_needs_no_zone(client, with_policy) -> None:
    """Free (one zone per query) can list the zones: that endpoint has no zone to ask."""
    assert _get(client, "/v1/zones", "free").status_code == 200
