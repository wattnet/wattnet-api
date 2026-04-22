"""Service layer for handling impact metrics in the wattnet API application."""

from datetime import datetime
from typing import List, Optional, cast

from typing_extensions import Literal
from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.impact import Impact, ImpactAggregate, ImpactSeries
from wattnet.api.service.operations import (
    build_time_series,
    compute_time_weighted_average,
    group_metrics_by_metadata,
)
from wattnet.api.utils import log

LOG = log.get(__name__)

ZoneStatus = Literal["complete", "preview", "missing"]

# Carbon impact is stored as carbon footprint — unit is remapped at the API layer.
_CARBON_IMPACT_UNIT = "stress-gCO2eq/kWh"

priority_map = {
    "missing": 0,
    "preview": 1,
    "complete": 2,
}


class ImpactService:
    """Service to handle environmental impact metrics for wattnet.

    Carbon impact is identical to carbon footprint and is resolved by querying
    the footprint tables directly, then remapping the unit to stress-gCO2eq/kWh.
    Water impact is read from the dedicated impact tables.
    """

    def __init__(self, metrics_repo: Optional[MetricsRepository] = None):
        """Initialize the ImpactService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing ImpactService")
        self.repo = metrics_repo or MetricsRepository()

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

        Carbon impact is served from footprint storage with a remapped unit.
        Water impact is served from the dedicated impact storage.

        :param zone: Optional zone code to filter metrics.
        :type zone: str, optional

        :param impact_type: Optional impact type — 'carbon' or 'water'.
            If not provided, both types are returned.
        :type impact_type: str, optional

        :param scope: Optional scope — 'operational' or 'life-cycle'.
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

        # Determine which types to fetch
        fetch_carbon = impact_type is None or impact_type == "carbon"
        fetch_water = impact_type is None or impact_type == "water"

        if fetch_carbon:
            results.extend(
                self._get_carbon_impacts(zone, scope, start, end, aggregate, use_global)
            )

        if fetch_water:
            results.extend(
                self._get_water_impacts(zone, scope, start, end, aggregate, use_global)
            )

        return results

    # ── Carbon ────────────────────────────────────────────────────────────────

    def _get_carbon_impacts(
        self,
        zone: Optional[str],
        scope: Optional[str],
        start: Optional[datetime],
        end: Optional[datetime],
        aggregate: bool,
        use_global: bool,
    ) -> List:
        """Fetch carbon footprint metrics and remap unit to stress-gCO2eq/kWh."""
        metric_name = "global_footprint" if use_global else "local_footprint"

        labels = {"footprint_type": "carbon"}
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

        # Remap unit and footprint_type → impact_type in metadata
        for m in metrics:
            m.metadata["unit"] = _CARBON_IMPACT_UNIT
            m.metadata["impact_type"] = m.metadata.pop("footprint_type", "carbon")

        if aggregate and start and end:
            return self._aggregate_metrics(metrics, start, end, use_global, "carbon")
        return self._group_metrics_series(metrics, use_global, "carbon")

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
            valid_agg = all(
                m.metadata.get("valid", "").lower() == "true" for m in mlist
            )
            zone_status_values = [
                m.metadata.get("zone_status", "missing") for m in mlist
            ]
            min_priority_value = min(
                priority_map.get(zs, 0) for zs in zone_status_values
            )
            zone_status: ZoneStatus = cast(
                ZoneStatus,
                [k for k, v in priority_map.items() if v == min_priority_value][0],
            )

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
                    m.metadata.get("valid", True),
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
