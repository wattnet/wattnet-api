"""Service layer for handling impact share metrics in the wattnet API application."""

from datetime import datetime
from typing import List, Optional

from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.impact_share import (
    ImpactShare,
    ImpactShareBlock,
    ImpactShareSeries,
)
from wattnet.api.service.operations import group_metrics_by_metadata
from wattnet.api.utils import log

LOG = log.get(__name__)

# Carbon impact share is identical to carbon footprint share — unit remapped here.
_CARBON_FOOTPRINT_UNIT = "gCO2/kWh"
_CARBON_IMPACT_UNIT = "stress-gCO2eq/kWh"


class ImpactShareService:
    """Service to handle impact share metrics for wattnet.

    Carbon impact share is served from the footprint_share table with a
    remapped unit. Water impact share is served from the impact_share table.
    """

    def __init__(self, metrics_repo: Optional[MetricsRepository] = None):
        """Initialize the ImpactShareService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing ImpactShareService")
        self.repo = metrics_repo or MetricsRepository()

    def get_impact_share(
        self,
        zone: Optional[str] = None,
        source: Optional[str] = None,
        impact_type: Optional[str] = None,
        scope: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[ImpactShare]:
        """Retrieve impact share metrics filtered by zone, source, type, and scope.

        :param zone: Optional destination zone code.
        :type zone: str, optional

        :param source: Optional origin zone code.
        :type source: str, optional

        :param impact_type: Optional impact type — 'carbon' or 'water'.
            If not provided, both types are returned.
        :type impact_type: str, optional

        :param scope: Optional scope — 'operational' or 'life-cycle'.
        :type scope: str, optional

        :param start: Optional start datetime.
        :type start: datetime, optional

        :param end: Optional end datetime.
        :type end: datetime, optional

        :return: List of ImpactShare objects matching the filters.
        :rtype: List[ImpactShare]
        """
        results = []

        fetch_carbon = impact_type is None or impact_type == "carbon"
        fetch_water = impact_type is None or impact_type == "water"

        if fetch_carbon:
            results.extend(
                self._get_carbon_impact_share(zone, source, scope, start, end)
            )
        if fetch_water:
            results.extend(
                self._get_water_impact_share(zone, source, scope, start, end)
            )

        return results

    # ── Carbon ────────────────────────────────────────────────────────────────

    def _get_carbon_impact_share(
        self,
        zone: Optional[str],
        source: Optional[str],
        scope: Optional[str],
        start: Optional[datetime],
        end: Optional[datetime],
    ) -> List[ImpactShare]:
        """Fetch carbon footprint share and remap to carbon impact share."""
        labels = {"app": "wattnet", "footprint_type": "carbon"}
        if zone:
            labels["zone"] = zone
        if source:
            labels["source"] = source
        if scope:
            labels["scope"] = scope

        metrics = self.repo.query_metrics(
            metric_name="footprint_share", start=start, end=end, labels=labels
        )

        if not metrics:
            return []

        # Remap unit and key field
        for m in metrics:
            m.metadata["unit"] = _CARBON_IMPACT_UNIT
            m.metadata["impact_type"] = m.metadata.pop("footprint_type", "carbon")

        return self._group_metrics(metrics)

    # ── Water ─────────────────────────────────────────────────────────────────

    def _get_water_impact_share(
        self,
        zone: Optional[str],
        source: Optional[str],
        scope: Optional[str],
        start: Optional[datetime],
        end: Optional[datetime],
    ) -> List[ImpactShare]:
        """Fetch water impact share from the dedicated impact_share table."""
        labels = {"app": "wattnet", "impact_type": "water"}
        if zone:
            labels["zone"] = zone
        if source:
            labels["source"] = source
        if scope:
            labels["scope"] = scope

        metrics = self.repo.query_metrics(
            metric_name="impact_share", start=start, end=end, labels=labels
        )

        if not metrics:
            return []

        return self._group_metrics(metrics)

    # ── Builder ───────────────────────────────────────────────────────────────

    def _group_metrics(self, metrics: List[Metric]) -> List[ImpactShare]:
        """Group raw impact share metrics into ImpactShare objects."""
        results = []

        zone_groups = group_metrics_by_metadata(
            metrics, ["zone", "impact_type", "scope", "unit"]
        )

        for (zone, impact_type, scope, unit), zone_metrics in zone_groups.items():
            series_groups = group_metrics_by_metadata(
                zone_metrics, ["valid", "zone_status"]
            )
            series_list: List[ImpactShareSeries] = []

            for (valid, zone_status), series_metrics in series_groups.items():
                block_groups = group_metrics_by_metadata(series_metrics, ["source"])
                block_list: List[ImpactShareBlock] = []

                for source_key, block_metrics in block_groups.items():
                    source_str = (
                        source_key[0] if isinstance(source_key, tuple) else source_key
                    )
                    if source_str is None:
                        source_str = "unknown"

                    values = sorted(
                        [(m.timestamp, m.value) for m in block_metrics],
                        key=lambda x: x[0],
                    )
                    block_list.append(
                        ImpactShareBlock(source=source_str, values=values)
                    )

                series_list.append(
                    ImpactShareSeries(
                        valid=valid, zone_status=zone_status, blocks=block_list
                    )
                )

            results.append(
                ImpactShare(
                    zone=zone,
                    impact_type=impact_type,
                    scope=scope,
                    unit=unit,
                    series=series_list,
                )
            )

        return results
