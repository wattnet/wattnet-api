"""Access tiers: what each tier of the access policy may ask of the API.

The access policy (a YAML file, a ConfigMap in the cluster) is the source of truth for
the groups of endpoints and the limits of data and query of each tier. The gate in
front of the API validates the token and sends the tier in ``X-Wattnet-Tier``; the API
only trusts that header because it is reachable from the gate alone.

Without a policy file (``WATTNET_API_ACCESS_POLICY_PATH`` empty) the tiers are not
checked, as in a development or an open installation. The cap on the size of a query
(``max_query_zone_days``) applies in both cases.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

import yaml
from fastapi import HTTPException, Request
from pydantic import TypeAdapter, ValidationError

from wattnet.api.settings import settings
from wattnet.api.utils import log
from wattnet.api.utils.validation import make_utc_aware

LOG = log.get(__name__)

TIER_HEADER = "x-wattnet-tier"
# Query parameters that say where: a zone or the coordinates of one.
_LOCATION_PARAMS = {
    f"{prefix}{name}"
    for prefix in ("", "source_", "destination_", "origin_")
    for name in ("zone", "lat", "lon")
}
_LIMIT_KEYS = (
    "max_zones_per_query",
    "max_query_range_days",
    "history_days",
    "forecast",
)
_datetime = TypeAdapter(datetime)


@dataclass(frozen=True)
class Limits:
    """What a tier may ask: ``None`` in a number means no limit."""

    groups: frozenset[str]
    max_zones_per_query: Optional[int]
    max_query_range_days: Optional[int]
    history_days: Optional[int]
    forecast: bool


def parse_policy(text: str) -> dict[str, Limits]:
    """Return the limits of every tier of the policy that makes requests.

    A tier without ``limits`` (``public``, ``custom``) does not make requests and is
    left out. A tier that has them writes all of them.

    :param text: Content of the access policy file
    :raises ValueError: If the policy is not valid
    """
    data = yaml.safe_load(text)
    tiers = data.get("tiers") if isinstance(data, dict) else None
    if not isinstance(tiers, dict):
        raise ValueError("the access policy has no tiers")
    result: dict[str, Limits] = {}
    for name, tier in tiers.items():
        limits = tier.get("limits") if isinstance(tier, dict) else None
        if limits is None:
            continue
        missing = [k for k in _LIMIT_KEYS if k not in limits]
        groups = (tier.get("access") or {}).get("endpoint_groups")
        if missing or not isinstance(groups, list):
            raise ValueError(f"the tier {name!r} lacks {missing or 'endpoint_groups'}")
        result[name] = Limits(
            groups=frozenset(groups),
            max_zones_per_query=limits["max_zones_per_query"],
            max_query_range_days=limits["max_query_range_days"],
            history_days=limits["history_days"],
            forecast=bool(limits["forecast"]),
        )
    return result


class PolicyFile:
    """The policy read from a file and read again when the file changes.

    A version that is not valid is not applied: the last good one stays. The first
    one has to be valid, so a bad policy stops the start instead of denying everything.
    """

    def __init__(self, path: Path):
        """Read the policy for the first time."""
        self.path = path
        self._tiers = parse_policy(path.read_text())
        self._mtime = path.stat().st_mtime_ns

    def tiers(self) -> dict[str, Limits]:
        """Return the limits of the tiers, reading the file again if it changed."""
        try:
            mtime = self.path.stat().st_mtime_ns
            if mtime != self._mtime:
                self._mtime = mtime  # one try per change, not one per request
                self._tiers = parse_policy(self.path.read_text())
                LOG.info(f"Access policy read again from {self.path}")
        except (OSError, ValueError, yaml.YAMLError) as e:
            LOG.error(f"Access policy not applied, the last good one stays: {e}")
        return self._tiers


# The policy in use; the tests replace it.
policy: Optional[PolicyFile] = (
    PolicyFile(settings.access_policy_path) if settings.access_policy_path else None
)


def _parse(value: Optional[str]) -> Optional[datetime]:
    """Return a datetime of the query, or None if it is missing or not a datetime."""
    if not value:
        return None
    try:
        return make_utc_aware(_datetime.validate_python(value))
    except ValidationError:
        return None  # the endpoint answers 422 for it


def _zones_requested(params: Mapping[str, Any]) -> int:
    """Count the zones a query asks: one if it says where, every zone if not."""
    if any(p in params for p in _LOCATION_PARAMS):
        return 1
    from wattnet.api.dependencies import zone_service

    return len(zone_service.get_zones())


def _forbid(detail: str) -> HTTPException:
    return HTTPException(status_code=403, detail=detail)


def check_query(limits: Limits, params: Mapping[str, Any], now: datetime) -> None:
    """Raise a 403 if a query asks more than the limits allow."""
    zones = _zones_requested(params)
    if limits.max_zones_per_query is not None and zones > limits.max_zones_per_query:
        raise _forbid(
            f"This access level allows {limits.max_zones_per_query} zone per query: "
            "say it with zone, or with lat and lon."
        )
    start, end = _parse(params.get("start")), _parse(params.get("end"))
    if not (start and end):
        return  # without both, the query is one interval: nothing to limit
    if limits.max_query_range_days is not None and end - start > timedelta(
        days=limits.max_query_range_days
    ):
        raise _forbid(
            f"This access level allows a range of {limits.max_query_range_days} days "
            "per query."
        )
    if limits.history_days is not None and start < now - timedelta(
        days=limits.history_days
    ):
        raise _forbid(
            f"This access level reaches {limits.history_days} days back from today."
        )
    horizon = now + timedelta(minutes=settings.timeseries_step_minutes)
    if not limits.forecast and end > horizon:
        raise _forbid("This access level does not include forecast data.")


def check_size(params: Mapping[str, Any]) -> None:
    """Raise a 400 if a query is too big for the server, whatever the tier.

    The size is the zones it asks times the days of its range: a year of one zone is
    365 and every zone for a month is more, and what a query costs in memory grows
    with that.
    """
    start, end = _parse(params.get("start")), _parse(params.get("end"))
    if not (start and end) or start >= end:
        return
    cost = _zones_requested(params) * (end - start).total_seconds() / 86400
    if cost > settings.max_query_zone_days:
        raise HTTPException(
            status_code=400,
            detail=(
                f"The query is too big: a zone for a day counts 1 and a query may have "
                f"up to {settings.max_query_zone_days}. Ask a zone (zone, or lat and "
                "lon) or a shorter range, and join the answers."
            ),
        )


def guard(group: str) -> Callable[[Request], None]:
    """Return the dependency of the endpoints of a group of the access policy."""

    def dependency(request: Request) -> None:
        params = request.query_params
        if policy is not None:
            tier = request.headers.get(TIER_HEADER)
            limits = policy.tiers().get(tier) if tier else None
            if limits is None:
                raise _forbid("The request carries no known access level.")
            if group not in limits.groups:
                raise _forbid("This access level does not include these endpoints.")
            check_query(limits, params, datetime.now(timezone.utc))
        check_size(params)

    return dependency
