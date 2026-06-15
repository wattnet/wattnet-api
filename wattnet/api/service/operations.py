"""Service operations for processing and analyzing metrics data."""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Iterable, List, Optional, Tuple, cast

from typing_extensions import Literal

from wattnet.storage.models import Metric

ZoneStatus = Literal["complete", "preview", "missing"]

_PRIORITY_MAP: Dict[str, int] = {
    "missing": 0,
    "preview": 1,
    "complete": 2,
}


def resolve_zone_status(metrics: List[Metric]) -> ZoneStatus:
    """Return the minimum-priority zone_status across a list of metrics."""
    if not metrics:
        return "missing"
    zone_statuses = [m.metadata.get("zone_status", "missing") for m in metrics]
    min_priority = min(_PRIORITY_MAP.get(zs, 0) for zs in zone_statuses)
    result = [k for k, v in _PRIORITY_MAP.items() if v == min_priority][0]
    return cast(ZoneStatus, result)


def is_valid_agg(metrics: List[Metric]) -> bool:
    """Return True if all metrics have valid='true' (absent key treated as valid)."""
    return all(m.metadata.get("valid", "true").lower() == "true" for m in metrics)


def group_metrics_by_metadata(
    metrics: Iterable[Metric],
    key_fields: List[str],
) -> Dict[Tuple, List[Metric]]:
    """Group metrics by specified metadata fields.

    :param metrics: Iterable of Metric objects to group
    :type metrics: Iterable[Metric]

    :param key_fields: List of metadata field names to group by
    (e.g., ["zone", "production_type"])
    :type key_fields: List[str]

    :return: Dictionary mapping tuples of metadata values to lists of Metric objects
    :rtype: Dict[Tuple, List[Metric]]
    """
    grouped: Dict[Tuple, List[Metric]] = {}
    for m in metrics:
        key = tuple(m.metadata.get(field) for field in key_fields)
        grouped.setdefault(key, []).append(m)
    return grouped


def compute_time_weighted_average(
    metrics: List[Metric],
    start: datetime,
    end: datetime,
) -> float:
    """Compute the time-weighted average of metric values over a given time range.

    :param metrics: List of Metric objects sorted by timestamp
    :type metrics: List[Metric]

    :param start: Start datetime of the time range
    :type start: datetime

    :param end: End datetime of the time range
    :type end: datetime

    :return: Time-weighted average value over the time range
    :rtype: float
    """
    if not metrics:
        return 0.0

    metrics = sorted(metrics, key=lambda x: x.timestamp)

    # Pre-convert to Decimal once; derive precision in the same pass
    dvals: List[Optional[Decimal]] = []
    precision = 0
    for m in metrics:
        if m.value is not None:
            v = Decimal(str(m.value))
            precision = max(precision, abs(int(v.as_tuple().exponent)))
            dvals.append(v)
        else:
            dvals.append(None)

    total_weighted = Decimal("0")
    total_duration = Decimal("0")

    # Integrate all but last segment
    for (m0, v0), (m1, _) in zip(zip(metrics, dvals), zip(metrics[1:], dvals[1:])):
        t0 = max(m0.timestamp, start)
        t1 = min(m1.timestamp, end)
        duration = Decimal((t1 - t0).total_seconds())
        if duration > 0 and v0 is not None:
            total_weighted += v0 * duration
            total_duration += duration

    # Extend last metric until the end
    last = metrics[-1]
    v_last = dvals[-1]
    if last.timestamp < end and v_last is not None:
        t0 = max(last.timestamp, start)
        duration = Decimal((end - t0).total_seconds())
        if duration > 0:
            total_weighted += v_last * duration
            total_duration += duration

    if total_duration > 0:
        return float(round(total_weighted / total_duration, precision))

    # Fallback: single metric at/after end boundary — return its value.
    # Use first non-None decimal; return 0.0 only when all values are absent.
    v_first = next((v for v in dvals if v is not None), None)
    return float(round(v_first, precision)) if v_first is not None else 0.0


def build_time_series(
    metrics: List[Metric],
) -> List[Tuple[datetime, float]]:
    """Convert metrics to a sorted time series of (timestamp, float(value)).

    :param metrics: List of Metric objects to convert
    :type metrics: List[Metric]

    :return: List of tuples (timestamp, value) sorted by timestamp
    :rtype: List[Tuple[datetime, float]]
    """
    values = [
        (m.timestamp, float(Decimal(str(m.value))))
        for m in metrics
        if m.value is not None
    ]
    values.sort(key=lambda x: x[0])
    return values
