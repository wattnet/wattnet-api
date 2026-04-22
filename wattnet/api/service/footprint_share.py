"""Service layer for handling footprint share metrics."""

from datetime import datetime
from typing import List, Optional

from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.footprint_share import (
    FootprintShare,
    FootprintShareBlock,
    FootprintShareSeries,
)
from wattnet.api.service.operations import group_metrics_by_metadata
from wattnet.api.utils import log

LOG = log.get(__name__)


class FootprintShareService:
    """Service to handle footprint share metrics."""

    def __init__(self, metrics_repo: Optional[MetricsRepository] = None):
        """Initialize the FootprintShareService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
        If not provided, a new instance will be created.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing FootprintShareService")
        self.repo = metrics_repo or MetricsRepository()

    def get_footprint_share(
        self,
        zone: Optional[str] = None,
        source: Optional[str] = None,
        footprint_type: Optional[str] = None,
        scope: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[FootprintShare]:
        """Retrieve footprint share metrics filtered.

        :param zone: Optional zone code to filter metrics by destination zone.
        :type zone: str, optional

        :param source: Optional origin zone code to filter metrics by source zone.
        :type source: str, optional

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

        :return: List of FootprintShare objects matching the filters.
        :rtype: List[FootprintShare]
        """
        labels = {}
        if zone:
            labels["zone"] = zone
        if source:
            labels["source"] = source
        if footprint_type:
            labels["footprint_type"] = footprint_type
        if scope:
            labels["scope"] = scope

        metrics = self.repo.query_metrics(
            metric_name="footprint_share",
            start=start,
            end=end,
            labels=labels,
        )

        if not metrics:
            return []

        return self._group_metrics(metrics)

    def _group_metrics(self, metrics: List[Metric]) -> List[FootprintShare]:
        """Group raw footprint share metrics into structured FootprintShare objects.

        :param metrics: List of raw Metric objects to group.
        :type metrics: List[Metric]

        :return: List of grouped FootprintShare objects.
        :rtype: List[FootprintShare]
        """
        results = []

        # Group by destination zone, footprint_type, scope, unit
        zone_groups = group_metrics_by_metadata(
            metrics, ["zone", "footprint_type", "scope", "unit"]
        )

        for (zone, footprint_type, scope, unit), zone_metrics in zone_groups.items():
            series_groups = group_metrics_by_metadata(
                zone_metrics, ["valid", "zone_status"]
            )
            series_list: List[FootprintShareSeries] = []

            for (valid, zone_status), series_metrics in series_groups.items():
                block_groups = group_metrics_by_metadata(series_metrics, ["source"])
                block_list: List[FootprintShareBlock] = []

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
                        FootprintShareBlock(source=source_str, values=values)
                    )

                series_list.append(
                    FootprintShareSeries(
                        valid=valid, zone_status=zone_status, blocks=block_list
                    )
                )

            results.append(
                FootprintShare(
                    zone=zone,
                    footprint_type=footprint_type,
                    scope=scope,
                    unit=unit,
                    series=series_list,
                )
            )

        return results
