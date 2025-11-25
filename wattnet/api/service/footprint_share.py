from datetime import datetime
from typing import List

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

    def __init__(self, metrics_repo: MetricsRepository = None):
        LOG.info("Initializing FootprintShareService")
        self.repo = metrics_repo or MetricsRepository()

    def get_footprint_share(
        self,
        zone: str = None,
        source: str = None,
        footprint_type: str = None,
        scope: str = None,
        start: datetime = None,
        end: datetime = None,
    ) -> List[FootprintShare]:

        labels = {"app": "wattnet"}
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
