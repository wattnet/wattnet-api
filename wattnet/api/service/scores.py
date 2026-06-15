"""Service layer for handling score metrics in the wattnet API application."""

from datetime import datetime
from typing import List, Optional, cast

from wattnet.api.models.score import GreenScore, GreenScoreAggregate, GreenScoreSeries
from wattnet.api.service.operations import (
    ZoneStatus,
    build_time_series,
    compute_time_weighted_average,
    group_metrics_by_metadata,
    is_valid_agg,
    resolve_zone_status,
)
from wattnet.api.utils import log
from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

LOG = log.get(__name__)


class ScoreService:
    """Service to handle GreenScore metrics for wattnet."""

    def __init__(self, metrics_repo: MetricsRepository):
        """Initialize the ScoreService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing ScoreService")
        self.repo = metrics_repo

    def get_scores(
        self,
        zone: Optional[str] = None,
        scope: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        aggregate: bool = False,
        use_global: bool = True,
    ) -> List:
        """Retrieve GreenScore metrics filtered by zone, scope, and time range.

        :param zone: Optional zone code to filter metrics.
        :type zone: str, optional

        :param scope: Optional scope — 'operational'.
        :type scope: str, optional

        :param start: Optional start datetime.
        :type start: datetime, optional

        :param end: Optional end datetime.
        :type end: datetime, optional

        :param aggregate: Whether to return aggregated values or time series.
        :type aggregate: bool

        :param use_global: Whether to query global or local score metrics.
        :type use_global: bool

        :return: List of GreenScore or GreenScoreAggregate objects.
        :rtype: List
        """
        metric_name = "global_score" if use_global else "local_score"

        labels = {}
        if zone:
            labels["zone"] = zone
        if scope:
            labels["scope"] = scope

        metrics = self.repo.query_metrics(
            metric_name=metric_name, start=start, end=end, labels=labels
        )
        metrics = [m for m in metrics if m.value is not None and m.value >= 0]

        if not metrics:
            return []

        if aggregate and start and end:
            return self._aggregate_metrics(metrics, start, end, use_global)
        return self._group_metrics_series(metrics, use_global)

    # ── Builders ──────────────────────────────────────────────────────────────

    def _aggregate_metrics(
        self,
        metrics: List[Metric],
        start: datetime,
        end: datetime,
        use_global: bool,
    ) -> List[GreenScoreAggregate]:
        """Aggregate raw GreenScore metrics into GreenScoreAggregate objects."""
        grouped = group_metrics_by_metadata(metrics, ["scope", "zone"])
        aggregates = []

        for (scope, zone), mlist in grouped.items():
            value_agg = compute_time_weighted_average(mlist, start, end)
            valid_agg = is_valid_agg(mlist)
            zone_status = resolve_zone_status(mlist)

            aggregates.append(
                GreenScoreAggregate(
                    scope=scope,
                    zone=zone,
                    start=start,
                    end=end,
                    value=value_agg,
                    valid=valid_agg,
                    zone_status=zone_status,
                    aggregation_method="time-weighted-average",
                    coverage="global" if use_global else "local",
                )
            )

        return aggregates

    def _group_metrics_series(
        self,
        metrics: List[Metric],
        use_global: bool,
    ) -> List[GreenScore]:
        """Group raw GreenScore metrics into GreenScore objects with time series."""
        grouped = group_metrics_by_metadata(metrics, ["scope", "zone"])
        scores = []

        for (scope, zone), mlist in grouped.items():
            validity_subgroup: dict[tuple, list[Metric]] = {}
            for m in mlist:
                key = (
                    m.metadata.get("valid", "true").lower() == "true",
                    cast(ZoneStatus, m.metadata.get("zone_status", "missing")),
                )
                validity_subgroup.setdefault(key, []).append(m)

            series_list = []
            for (valid, zone_status), smetrics in validity_subgroup.items():
                series_list.append(
                    GreenScoreSeries(
                        valid=valid,
                        zone_status=zone_status,
                        values=build_time_series(smetrics),
                    )
                )

            scores.append(
                GreenScore(
                    scope=scope,
                    zone=zone,
                    series=series_list,
                    coverage="global" if use_global else "local",
                )
            )

        return scores
