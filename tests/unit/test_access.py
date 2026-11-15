"""Unit tests for the access tiers: the policy, its reading and the limits."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi import HTTPException

from wattnet.api import access
from wattnet.api.access import Limits, PolicyFile, check_query, check_size, parse_policy

NOW = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)

POLICY = """
version: 1
tiers:
  public:
    access: {endpoint_groups: [status]}
  free:
    access: {endpoint_groups: [zones, energy_metrics]}
    limits:
      max_zones_per_query: 1
      max_query_range_days: 7
      history_days: 7
      forecast: false
  research:
    access: {endpoint_groups: [zones, energy_metrics, shares_metrics]}
    limits:
      max_zones_per_query: null
      max_query_range_days: 31
      history_days: null
      forecast: true
  internal:
    access: {endpoint_groups: [zones, energy_metrics]}
    limits:
      max_zones_per_query: null
      max_query_range_days: null
      history_days: null
      forecast: true
  custom:
    by_agreement: true
"""


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _query(start: datetime, end: datetime, **extra: str) -> dict:
    return {"start": _iso(start), "end": _iso(end), **extra}


def _denied(limits: Limits, params: dict) -> str:
    with pytest.raises(HTTPException) as e:
        check_query(limits, params, NOW)
    assert e.value.status_code == 403
    return str(e.value.detail)


# ── parse_policy ─────────────────────────────────────────────────────────────


def test_parse_policy_keeps_the_tiers_that_make_requests() -> None:
    """The tiers with limits are read; public and custom have none."""
    tiers = parse_policy(POLICY)
    assert set(tiers) == {"free", "research", "internal"}
    free = tiers["free"]
    assert free.groups == {"zones", "energy_metrics"}
    assert (free.max_zones_per_query, free.max_query_range_days) == (1, 7)
    assert free.history_days == 7 and free.forecast is False
    assert tiers["research"].max_zones_per_query is None
    assert tiers["research"].forecast is True


_LIMITS = (
    "{max_zones_per_query: 1, max_query_range_days: 1, history_days: 1, forecast: true}"
)


@pytest.mark.parametrize(
    "text",
    [
        "just text",
        "tiers: []",
        "tiers: {free: {access: {endpoint_groups: [zones]}, limits: {forecast: true}}}",
        f"tiers: {{free: {{limits: {_LIMITS}}}}}",  # all the limits, no groups
    ],
)
def test_parse_policy_rejects_an_invalid_policy(text: str) -> None:
    """A policy without tiers, with a limit missing or without groups is invalid."""
    with pytest.raises(ValueError):
        parse_policy(text)


# ── PolicyFile ───────────────────────────────────────────────────────────────


def _write(path: Path, text: str, mtime: int) -> None:
    path.write_text(text)
    os.utime(path, ns=(mtime, mtime))


def test_policy_file_reads_again_when_the_file_changes(tmp_path: Path) -> None:
    """A new version of the file is applied without restarting."""
    path = tmp_path / "access-policy.yaml"
    _write(path, POLICY, 1_000_000_000)
    file = PolicyFile(path)
    assert file.tiers()["free"].max_zones_per_query == 1

    _write(path, POLICY.replace("max_zones_per_query: 1", "max_zones_per_query: 2"), 2)
    assert file.tiers()["free"].max_zones_per_query == 2


def test_policy_file_keeps_the_last_good_one(tmp_path: Path) -> None:
    """A version that is not valid is not applied, and it is not tried again."""
    path = tmp_path / "access-policy.yaml"
    _write(path, POLICY, 1_000_000_000)
    file = PolicyFile(path)

    _write(path, "tiers: []", 2_000_000_000)
    assert "free" in file.tiers()
    assert "free" in file.tiers()


def test_policy_file_keeps_the_last_good_one_if_the_file_is_gone(
    tmp_path: Path,
) -> None:
    """A file that cannot be read leaves the last good policy in place."""
    path = tmp_path / "access-policy.yaml"
    _write(path, POLICY, 1_000_000_000)
    file = PolicyFile(path)
    path.unlink()
    assert "free" in file.tiers()


def test_policy_file_refuses_a_bad_first_policy(tmp_path: Path) -> None:
    """The first policy has to be valid: the start fails, nothing is denied by mistake."""
    path = tmp_path / "access-policy.yaml"
    path.write_text("tiers: []")
    with pytest.raises(ValueError):
        PolicyFile(path)


# ── check_query ──────────────────────────────────────────────────────────────

FREE = parse_policy(POLICY)["free"]
RESEARCH = parse_policy(POLICY)["research"]
INTERNAL = parse_policy(POLICY)["internal"]


@pytest.fixture
def three_zones(monkeypatch) -> None:
    """The service has three zones, so a query without a zone asks three."""
    monkeypatch.setattr(
        "wattnet.api.dependencies.zone_service.get_zones", lambda: ["ES", "FR", "DE"]
    )


def test_a_zone_or_coordinates_count_as_one(three_zones) -> None:
    """With zone, or lat and lon, or a source zone, a query asks one zone."""
    for where in ({"zone": "ES"}, {"lat": "1", "lon": "2"}, {"source_zone": "FR"}):
        check_query(FREE, where, NOW)


def test_no_zone_is_every_zone(three_zones) -> None:
    """Without a zone a query asks every zone, which a limit of one refuses."""
    assert "1 zone per query" in _denied(FREE, {})
    check_query(RESEARCH, {}, NOW)


def test_a_limit_of_two_zones_refuses_every_zone(three_zones) -> None:
    """A tier with a number of zones refuses the query of all of them."""
    two = Limits(frozenset(), 2, None, None, True)
    _denied(two, {})
    check_query(two, {"zone": "ES"}, NOW)


def test_an_endpoint_without_a_zone_to_ask_asks_one(three_zones) -> None:
    """The list of zones and the factors are not about one zone, so no zone is not all of them."""
    check_query(FREE, {}, NOW, zoned=False)
    _denied(FREE, {})  # a data endpoint without zone is every zone


def test_the_range_is_limited() -> None:
    """A range wider than the tier allows is refused, and the limit itself passes."""
    where = {"zone": "ES"}
    check_query(FREE, _query(NOW - timedelta(days=7), NOW, **where), NOW)
    assert "7 days" in _denied(
        FREE, _query(NOW - timedelta(days=8), NOW - timedelta(minutes=1), **where)
    )


def test_the_history_is_limited() -> None:
    """A start older than the history of the tier is refused."""
    where = {"zone": "ES"}
    check_query(RESEARCH, _query(NOW - timedelta(days=900), NOW - timedelta(days=890), **where), NOW)
    assert "days back" in _denied(
        FREE, _query(NOW - timedelta(days=30), NOW - timedelta(days=29), **where)
    )


def test_forecast_is_what_comes_after_now() -> None:
    """A tier without forecast cannot ask for the future; the current interval is not."""
    where = {"zone": "ES"}
    check_query(FREE, _query(NOW - timedelta(days=1), NOW + timedelta(minutes=15), **where), NOW)
    assert "forecast" in _denied(
        FREE, _query(NOW - timedelta(days=1), NOW + timedelta(hours=1), **where)
    )
    check_query(RESEARCH, _query(NOW, NOW + timedelta(hours=20), **where), NOW)


def test_without_start_and_end_there_is_no_range_to_limit() -> None:
    """Without both bounds the query is one interval and passes."""
    check_query(FREE, {"zone": "ES", "start": "2026-01-01T00:00:00Z"}, NOW)


def test_a_start_that_is_not_a_date_is_left_to_the_endpoint() -> None:
    """The endpoint answers 422 for a bad date; the guard does not."""
    check_query(FREE, {"zone": "ES", "start": "yesterday", "end": "today"}, NOW)


def test_internal_has_no_limits() -> None:
    """A tier with every limit null asks anything."""
    check_query(INTERNAL, _query(NOW - timedelta(days=900), NOW + timedelta(days=9), zone="ES"), NOW)


# ── check_size ───────────────────────────────────────────────────────────────


def test_size_counts_zones_times_days(three_zones, monkeypatch) -> None:
    """The cap is zones times days: three zones for 200 days is 600."""
    monkeypatch.setattr(access.settings, "max_query_zone_days", 400)
    start = NOW - timedelta(days=200)
    check_size(_query(start, NOW, zone="ES"))
    with pytest.raises(HTTPException) as e:
        check_size(_query(start, NOW))
    assert e.value.status_code == 400
    assert "too big" in e.value.detail


def test_size_ignores_a_query_without_a_range(three_zones) -> None:
    """Without both bounds, or with the start after the end, there is no size."""
    check_size({})
    check_size(_query(NOW, NOW - timedelta(days=1)))
