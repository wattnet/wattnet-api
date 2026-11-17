"""Shared test doubles for unit tests of the service layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class FakeMetric:
    """Minimal Metric test double.

    :param timestamp: Metric timestamp
    :type timestamp: datetime
    :param value: Metric value (None means missing)
    :type value: float | None
    :param metadata: Metadata dictionary
    :type metadata: Dict[str, object]
    :param updated_at: When the value was stored
    :type updated_at: datetime
    """

    timestamp: datetime
    value: Optional[float]
    metadata: Dict[str, object]
    updated_at: datetime = datetime(2025, 6, 2, tzinfo=timezone.utc)


class FakeRepo:
    """Configurable MetricsRepository stub.

    :param metrics: Metrics returned by every query_metrics call
    :type metrics: List[FakeMetric]
    """

    def __init__(self, metrics: List[FakeMetric]) -> None:
        """Initialise with a fixed list of metrics.

        :param metrics: Metrics to return
        :type metrics: List[FakeMetric]
        """
        self._metrics = metrics

    def query_metrics(
        self,
        metric_name: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        labels: Optional[Dict] = None,
    ) -> List[FakeMetric]:
        """Return the preconfigured metric list, ignoring all filters.

        :param metric_name: Ignored
        :param start: Ignored
        :param end: Ignored
        :param labels: Ignored
        :return: Preconfigured metric list
        :rtype: List[FakeMetric]
        """
        return self._metrics
