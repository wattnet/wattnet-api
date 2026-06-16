"""Service layer for handling mix generation metrics in the wattnet API."""

from datetime import datetime
from typing import List, Optional

from wattnet.api.models.mix import Mix, MixBlock, MixSeries
from wattnet.api.service.operations import group_metrics_by_metadata
from wattnet.api.utils import log
from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

LOG = log.get(__name__)


class MixService:
    """Service to handle mix generation metrics for wattnet."""

    def __init__(self, metrics_repo: MetricsRepository):
        """Initialize the MixService with a MetricsRepository."""
        LOG.info("Initializing MixService")
        self.repo = metrics_repo

    def get_mix(
        self,
        zone: Optional[str] = None,
        production_type: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Mix]:
        """Retrieve mix generation metrics filtered by zone, type, and time."""
        labels = {}
        if zone:
            labels["zone"] = zone
        if production_type:
            labels["production_type"] = production_type

        metrics = self.repo.query_metrics(
            metric_name="zone_mix_generation",
            start=start,
            end=end,
            labels=labels,
        )

        metrics = [m for m in metrics if m.value is not None and m.value >= 0]

        if not metrics:
            return []

        return self._group_metrics(metrics)

    def _group_metrics(self, metrics: List[Metric]) -> List[Mix]:
        """Organize flat metrics into Mix -> MixSeries -> MixBlock."""
        zone_groups = group_metrics_by_metadata(
            metrics,
            ["zone", "unit"],
        )

        results: List[Mix] = []

        for (zone, unit), zone_metrics in zone_groups.items():
            series_groups = group_metrics_by_metadata(
                zone_metrics,
                ["valid", "zone_status"],
            )

            series_list: List[MixSeries] = []

            for (valid, zone_status), series_metrics in series_groups.items():
                block_groups = group_metrics_by_metadata(
                    series_metrics,
                    ["production_type", "data_state", "datasource"],
                )

                blocks: List[MixBlock] = []

                for (
                    production_type,
                    data_state,
                    datasource,
                ), block_metrics in block_groups.items():

                    values = sorted(
                        [(m.timestamp, m.value) for m in block_metrics],
                        key=lambda x: x[0],
                    )

                    blocks.append(
                        MixBlock(
                            production_type=production_type,
                            data_state=data_state,
                            datasource=datasource,
                            values=values,
                        )
                    )

                series_list.append(
                    MixSeries(
                        valid=valid,
                        zone_status=zone_status,
                        production=blocks,
                    )
                )

            series_list = [s for s in series_list if s.production]

            results.append(
                Mix(
                    zone=zone,
                    unit=unit,
                    series=series_list,
                )
            )

        results = [r for r in results if r.series]

        return results
