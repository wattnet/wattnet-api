from datetime import datetime
from typing import List

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


class FootprintService:
    def __init__(self, metrics_repo: MetricsRepository = None):
        LOG.info("Initializing FootprintService")
        self.repo = metrics_repo or MetricsRepository()

    def get_footprints(
        self,
        zone: str = None,
        footprint_type: str = None,
        scope: str = None,
        start: datetime = None,
        end: datetime = None,
        aggregate: bool = False,
        use_global: bool = True,
    ) -> List:

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

        metrics = [m for m in metrics if m.value is not None and m.value > 0]

        if not metrics:
            return []

        if aggregate:
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

        if not metrics:
            return []

        grouped = group_metrics_by_metadata(
            metrics,
            ["footprint_type", "scope", "zone"],
        )

        aggregates = []

        for (footprint_type, scope, zone), mlist in grouped.items():
            value_agg = compute_time_weighted_average(mlist, start, end)

            valid_agg = all(m.metadata.get("valid", True) for m in mlist)
            min_priority = min(m.metadata.get("zone_status", "missing") for m in mlist)

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
                    zone_status=min_priority,
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

        if not metrics:
            return []

        grouped = group_metrics_by_metadata(
            metrics,
            ["footprint_type", "scope", "zone", "unit"],
        )

        footprints = []

        for (footprint_type, scope, zone, unit), mlist in grouped.items():

            # Subgroup by (valid, zone_status)
            validity_subgroup = {}
            for m in mlist:
                key = (
                    m.metadata.get("valid", True),
                    m.metadata.get("zone_status", "missing"),
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
