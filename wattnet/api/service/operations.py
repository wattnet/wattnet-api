"""Service operations for processing and analyzing metrics data."""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Iterable, List, Tuple

from wattnet.storage.models import Metric


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

    total_weighted = Decimal("0")
    total_duration = Decimal("0")

    # Integrate all but last segment
    for m0, m1 in zip(metrics, metrics[1:]):
        t0 = max(m0.timestamp, start)
        t1 = min(m1.timestamp, end)
        duration = Decimal((t1 - t0).total_seconds())

        if duration > 0:
            total_weighted += Decimal(str(m0.value)) * duration
            total_duration += duration

    # Extend last metric until the end
    last = metrics[-1]
    if last.timestamp < end:
        t0 = max(last.timestamp, start)
        duration = Decimal((end - t0).total_seconds())
        if duration > 0:
            total_weighted += Decimal(str(last.value)) * duration
            total_duration += duration

    if total_duration > 0:
        return float(total_weighted / total_duration)

    return float(metrics[0].value)


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
