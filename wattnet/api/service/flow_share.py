from datetime import datetime
from typing import List

from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.flow_share import FlowShare, FlowShareBlock, FlowShareSeries
from wattnet.api.service.operations import group_metrics_by_metadata
from wattnet.api.utils import log

LOG = log.get(__name__)


class FlowShareService:
    def __init__(self, metrics_repo: MetricsRepository = None):
        LOG.info("Initializing FlowShareService")
        self.repo = metrics_repo or MetricsRepository()

    def get_flow_share(
        self,
        zone: str = None,
        destination: str = None,
        start: datetime = None,
        end: datetime = None,
    ) -> List[FlowShare]:
        """
        Fetch flow share metrics and return hierarchical structure:
        FlowShare -> FlowShareSeries -> FlowShareBlock
        """
        labels = {"app": "wattnet"}
        if zone:
            labels["zone"] = zone
        if destination:
            labels["target"] = destination  # DB uses 'target'

        metrics = self.repo.query_metrics(
            metric_name="flow_share",
            start=start,
            end=end,
            labels=labels,
        )

        if not metrics:
            return []

        return self._group_metrics(metrics)

    def _group_metrics(self, metrics: List[Metric]) -> List[FlowShare]:
        # 1) Group by zone (origin)
        zone_groups = group_metrics_by_metadata(metrics, ["zone"])

        results = []

        for zone_key, zone_metrics in zone_groups.items():
            # Convert tuple to string if needed
            zone_str = zone_key[0] if isinstance(zone_key, tuple) else zone_key

            # 2) Group by (valid, zone_status) => FlowShareSeries
            series_groups = group_metrics_by_metadata(
                zone_metrics, ["valid", "zone_status"]
            )

            series_list: List[FlowShareSeries] = []

            for (valid, zone_status), series_metrics in series_groups.items():

                # 3) Group by destination ('target' in DB)
                block_groups = group_metrics_by_metadata(series_metrics, ["target"])

                block_list: List[FlowShareBlock] = []

                for destination_key, block_metrics in block_groups.items():
                    # Convert tuple to string if needed
                    destination_str = (
                        destination_key[0]
                        if isinstance(destination_key, tuple)
                        else destination_key
                    )

                    values = sorted(
                        [(m.timestamp, m.value) for m in block_metrics],
                        key=lambda x: x[0],
                    )

                    block = FlowShareBlock(
                        destination=destination_str,
                        values=values,
                    )

                    block_list.append(block)

                flow_series = FlowShareSeries(
                    valid=valid,
                    zone_status=zone_status,
                    flows=block_list,
                )

                series_list.append(flow_series)

            flow_obj = FlowShare(
                zone=zone_str,
                unit="%",
                series=series_list,
            )

            results.append(flow_obj)

        return results
