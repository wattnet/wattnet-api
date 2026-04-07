"""Service layer for handling footprint metrics in the wattnet API application."""

from datetime import datetime
from typing import List, Optional, cast

from typing_extensions import Literal
from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.footprint import Footprint, FootprintAggregate, FootprintSeries
from wattnet.api.service.operations import (
    build_time_series,
    compute_time_weighted_average,
    group_metrics_by_metadata,
)
from wattnet.api.utils import log

LOG = log.get(__name__)

ZoneStatus = Literal["complete", "preview", "missing"]

priority_map = {
    "missing": 0,
    "preview": 1,
    "complete": 2,
}


class FootprintService:
    """Service to handle footprint metrics for wattnet."""

    def __init__(self, metrics_repo: Optional[MetricsRepository] = None):
        """Initialize the FootprintService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
        If not provided, a new instance will be created.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing FootprintService")
        self.repo = metrics_repo or MetricsRepository()

    def get_footprints(
        self,
        zone: Optional[str] = None,
        footprint_type: Optional[str] = None,
        scope: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        aggregate: bool = False,
        use_global: bool = True,
    ) -> List:
        """Retrieve footprint metrics filtered by zone, type, scope, and time range.

        :param zone: Optional zone code to filter metrics by zone.
        :type zone: str, optional

        :param footprint_type: Optional footprint type to filter metrics.
        :type footprint_type: str, optional

        :param scope: Optional scope to filter metrics
        (e.g., "production", "consumption").
        :type scope: str, optional

        :param start: Optional start datetime to filter metrics.
        If provided, end must also be provided.
        :type start: datetime, optional

        :param end: Optional end datetime to filter metrics.
        If provided, start must also be provided.
        :type end: datetime, optional

        :param aggregate: Whether to return aggregated metrics
        (FootprintAggregate) or time series (Footprint).
        :type aggregate: bool, optional (default: False for time series)

        :param use_global: Whether to query global_footprint or local_footprint metrics.
        :type use_global: bool, optional (default: True for global_footprint)

        :return: List of Footprint or FootprintAggregate objects matching the filters.
        :rtype: List[Footprint] or List[FootprintAggregate]
        """
        metric_name = "global_footprint" if use_global else "local_footprint"

        labels = {"app": "wattnet"}
        if zone:
            labels["zone"] = zone
        if footprint_type:
            labels["footprint_type"] = footprint_type
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
        else:
            return self._group_metrics_series(metrics, use_global)

    def _aggregate_metrics(
        self,
        metrics: List[Metric],
        start: datetime,
        end: datetime,
        use_global: bool,
    ) -> List[FootprintAggregate]:
        """Aggregate raw footprint metrics into structured FootprintAggregate objects.

        :param metrics: List of raw Metric objects to aggregate.
        :type metrics: List[Metric]

        :param start: Start datetime for the aggregation period.
        :type start: datetime

        :param end: End datetime for the aggregation period.
        :type end: datetime

        :param use_global: Whether the metrics are from
        global_footprint or local_footprint.
        :type use_global: bool

        :return: List of aggregated FootprintAggregate objects.
        :rtype: List[FootprintAggregate]
        """
        if not metrics:
            return []

        grouped = group_metrics_by_metadata(
            metrics,
            ["footprint_type", "scope", "zone"],
        )

        aggregates = []

        for (footprint_type, scope, zone), mlist in grouped.items():
            value_agg = compute_time_weighted_average(mlist, start, end)

            valid_agg = all(
                m.metadata.get("valid", "").lower() == "true" for m in mlist
            )
            zone_status_values = [
                m.metadata.get("zone_status", "missing") for m in mlist
            ]
            min_priority_value = min(
                priority_map.get(zs, 0) for zs in zone_status_values
            )
            min_priority = [
                k for k, v in priority_map.items() if v == min_priority_value
            ][0]

            zone_status: ZoneStatus = cast(ZoneStatus, min_priority)

            aggregates.append(
                FootprintAggregate(
                    footprint_type=footprint_type,
                    scope=scope,
                    zone=zone,
                    unit=mlist[0].metadata.get("unit", "unknown"),
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
    ) -> List[Footprint]:
        """Group raw footprint metrics into structured Footprint objects.

        :param metrics: List of raw Metric objects to group.
        :type metrics: List[Metric]

        :param use_global: Whether the metrics are
        from global_footprint or local_footprint.
        :type use_global: bool

        :return: List of grouped Footprint objects with time series.
        :rtype: List[Footprint]
        """
        if not metrics:
            return []

        grouped = group_metrics_by_metadata(
            metrics,
            ["footprint_type", "scope", "zone", "unit"],
        )

        footprints = []

        for (footprint_type, scope, zone, unit), mlist in grouped.items():

            # Subgroup by (valid, zone_status)
            validity_subgroup: dict[tuple[bool, ZoneStatus], list[Metric]] = {}
            for m in mlist:
                key = (
                    m.metadata.get("valid", True),
                    cast(ZoneStatus, m.metadata.get("zone_status", "missing")),
                )
                validity_subgroup.setdefault(key, []).append(m)
            series_list = []

            for (valid, zone_status), smetrics in validity_subgroup.items():
                values = build_time_series(smetrics)
                series_list.append(
                    FootprintSeries(
                        valid=valid,
                        zone_status=zone_status,
                        values=values,
                    )
                )

            footprints.append(
                Footprint(
                    footprint_type=footprint_type,
                    scope=scope,
                    zone=zone,
                    unit=unit,
                    series=series_list,
                    coverage="global" if use_global else "local",
                )
            )

        return footprints
