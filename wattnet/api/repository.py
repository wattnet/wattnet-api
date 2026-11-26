"""The repository of metrics the services of the API read from."""

from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

from wattnet.storage import MetricsRepository
from wattnet.storage.models import Metric

# How far back a query with no range looks for the latest point. Recent data comes
# within the hour; this only bounds the read when a series has stopped.
LATEST_LOOKBACK = timedelta(days=7)


class LatestPointRepository(MetricsRepository):
    """A ``MetricsRepository`` whose queries with no range get the latest point.

    The storage resolves a query with neither ``start`` nor ``end`` to the interval
    of the current moment, which is empty until that interval is published (the first
    minutes of each interval, or longer when the data is late). Here such a query asks
    first for the timestamp of the latest point before now with the same labels (one
    query, within ``LATEST_LOOKBACK``) and then reads that interval, so the answer is
    always the last data available. A range given by the caller is read as it is.
    """

    def query_metrics(
        self,
        metric_name: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        labels: Optional[dict] = None,
        **kwargs: Any,
    ) -> List[Metric]:
        """Query metrics; with no range, the interval of the latest point before now."""
        if start is None and end is None:
            now = datetime.now(timezone.utc)
            latest = self.latest_timestamp(
                metric_name, now, labels, after=now - LATEST_LOOKBACK
            )
            if latest is None:
                return []
            start, end = latest, latest + timedelta(seconds=self.step)
        metrics: List[Metric] = super().query_metrics(
            metric_name, start=start, end=end, labels=labels, **kwargs
        )
        return metrics
