from datetime import datetime
from typing import List

from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.mix_share import MixShare, MixShareBlock, MixShareSeries
from wattnet.api.service.operations import group_metrics_by_metadata
from wattnet.api.utils import log

LOG = log.get(__name__)


class MixShareService:
    """Service to handle mix share metrics for Wattnet."""

    def __init__(self, metrics_repo: MetricsRepository = None):
        LOG.info("Initializing MixShareService")
        self.repo = metrics_repo or MetricsRepository()

    def get_mix_share(
        self,
        zone: str = None,
        origin: str = None,
        start: datetime = None,
        end: datetime = None,
    ) -> List[MixShare]:

        labels = {"app": "wattnet"}
        if zone:
            labels["zone"] = zone
        if origin:
            labels["source"] = origin  # DB column for origin

        metrics = self.repo.query_metrics(
            metric_name="mix_share",
            start=start,
            end=end,
            labels=labels,
        )

        if not metrics:
            return []

        return self._group_metrics(metrics)

    def _group_metrics(self, metrics: List[Metric]) -> List[MixShare]:
        results = []

        # Group by destination zone
        zone_groups = group_metrics_by_metadata(metrics, ["zone"])

        for zone_key, zone_metrics in zone_groups.items():
            zone_str = zone_key[0] if isinstance(zone_key, tuple) else zone_key

            # Group by series attributes (valid + zone_status)
            series_groups = group_metrics_by_metadata(
                zone_metrics, ["valid", "zone_status"]
            )
            series_list: List[MixShareSeries] = []

            for (valid, zone_status), series_metrics in series_groups.items():

                # Group by origin zone
                block_groups = group_metrics_by_metadata(series_metrics, ["source"])
                block_list: List[MixShareBlock] = []

                for origin_key, block_metrics in block_groups.items():
                    origin_str = (
                        origin_key[0] if isinstance(origin_key, tuple) else origin_key
                    )

                    values = sorted(
                        [(m.timestamp, m.value) for m in block_metrics],
                        key=lambda x: x[0],
                    )

                    block_list.append(MixShareBlock(origin=origin_str, values=values))

                series_list.append(
                    MixShareSeries(
                        valid=valid,
                        zone_status=zone_status,
                        shares=block_list,
                    )
                )

            results.append(
                MixShare(
                    zone=zone_str,
                    unit="%",
                    series=series_list,
                )
            )

        return results
