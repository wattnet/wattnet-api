"""Service layer for handling impact metrics in the wattnet API application."""

from datetime import datetime
from typing import List, Optional, cast

from wattnet.api.models.impact import Impact, ImpactAggregate, ImpactSeries
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


class ImpactService:
    """Service to handle environmental impact metrics for wattnet.

    Water impact is read from the dedicated impact tables.
    """

    def __init__(self, metrics_repo: MetricsRepository):
        """Initialize the ImpactService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing ImpactService")
        self.repo = metrics_repo

    def get_impacts(
        self,
        zone: Optional[str] = None,
        impact_type: Optional[str] = None,
        scope: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        aggregate: bool = False,
        use_global: bool = True,
    ) -> List:
        """Retrieve impact metrics filtered by zone, type, scope, and time range.

        :param zone: Optional zone code to filter metrics.
        :type zone: str, optional

        :param impact_type: Optional impact type — 'water'.
            If not provided, water is returned.
        :type impact_type: str, optional

        :param scope: Optional scope — 'operational'.
        :type scope: str, optional

        :param start: Optional start datetime.
        :type start: datetime, optional

        :param end: Optional end datetime.
        :type end: datetime, optional

        :param aggregate: Whether to return aggregated values or time series.
        :type aggregate: bool

        :param use_global: Whether to query global or local metrics.
        :type use_global: bool

        :return: List of Impact or ImpactAggregate objects.
        :rtype: List
        """
        results = []
        normalized_type = impact_type.lower() if impact_type else None

        if normalized_type in (None, "water"):
            results.extend(
                self._get_water_impacts(zone, scope, start, end, aggregate, use_global)
            )

        return results

    # ── Water ─────────────────────────────────────────────────────────────────

    def _get_water_impacts(
        self,
        zone: Optional[str],
        scope: Optional[str],
        start: Optional[datetime],
        end: Optional[datetime],
        aggregate: bool,
        use_global: bool,
    ) -> List:
        """Fetch water impact metrics from the dedicated impact tables."""
        metric_name = "global_impact" if use_global else "local_impact"

        labels = {"impact_type": "water"}
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
            return self._aggregate_metrics(metrics, start, end, use_global, "water")
        return self._group_metrics_series(metrics, use_global, "water")

    # ── Shared builders ───────────────────────────────────────────────────────

    def _aggregate_metrics(
        self,
        metrics: List[Metric],
        start: datetime,
        end: datetime,
        use_global: bool,
        impact_type: str,
    ) -> List[ImpactAggregate]:
        """Aggregate raw impact metrics into ImpactAggregate objects."""
        grouped = group_metrics_by_metadata(metrics, ["impact_type", "scope", "zone"])
        aggregates = []

        for (i_type, scope, zone), mlist in grouped.items():
            value_agg = compute_time_weighted_average(mlist, start, end)
            valid_agg = is_valid_agg(mlist)
            zone_status = resolve_zone_status(mlist)

            unit = mlist[0].metadata.get("unit", "unknown")

            aggregates.append(
                ImpactAggregate(
                    impact_type=i_type,
                    scope=scope,
                    zone=zone,
                    unit=unit,
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
        impact_type: str,
    ) -> List[Impact]:
        """Group raw impact metrics into Impact objects with time series."""
        grouped = group_metrics_by_metadata(
            metrics, ["impact_type", "scope", "zone", "unit"]
        )
        impacts = []

        for (i_type, scope, zone, unit), mlist in grouped.items():
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
                    ImpactSeries(
                        valid=valid,
                        zone_status=zone_status,
                        values=build_time_series(smetrics),
                    )
                )

            impacts.append(
                Impact(
                    impact_type=i_type,
                    scope=scope,
                    zone=zone,
                    unit=unit,
                    series=series_list,
                    coverage="global" if use_global else "local",
                )
            )

        return impacts
