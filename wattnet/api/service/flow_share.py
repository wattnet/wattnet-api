"""Service layer for handling flow share metrics."""

from datetime import datetime
from typing import List, Optional

from wattnet.api.models.flow_share import FlowShare, FlowShareBlock, FlowShareSeries
from wattnet.api.service.operations import build_time_series, group_metrics_by_metadata
from wattnet.api.utils import log
from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

LOG = log.get(__name__)


class FlowShareService:
    """Service to handle flow share metrics."""

    def __init__(self, metrics_repo: MetricsRepository):
        """Initialize the FlowShareService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
        If not provided, a new instance will be created.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing FlowShareService")
        self.repo = metrics_repo

    def get_flow_share(
        self,
        zone: Optional[str] = None,
        destination: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[FlowShare]:
        """
        Retrieve flow share metrics filtered by zone, destination, and time range.

        :param zone: Optional zone code to filter metrics by destination zone.
        :type zone: str, optional

        :param destination: Optional destination zone code to filter metrics
        by target zone.
        :type destination: str, optional

        :param start: Optional start datetime to filter metrics.
        If provided, end must also be provided.
        :type start: datetime, optional

        :param end: Optional end datetime to filter metrics.
        If provided, start must also be provided.
        :type end: datetime, optional

        :return: List of FlowShare objects matching the filters.
        :rtype: List[FlowShare]
        """
        labels = {}
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
        """Group raw flow share metrics into structured FlowShare objects.

        :param metrics: List of raw Metric objects to group.
        :type metrics: List[Metric]

        :return: List of grouped FlowShare objects.
        :rtype: List[FlowShare]
        """
        # 1) Group by zone (origin)
        zone_groups = group_metrics_by_metadata(metrics, ["zone"])

        results = []

        for (zone_str,), zone_metrics in zone_groups.items():

            # 2) Group by (valid, zone_status) => FlowShareSeries
            series_groups = group_metrics_by_metadata(
                zone_metrics, ["valid", "zone_status"]
            )

            series_list: List[FlowShareSeries] = []

            for (valid, zone_status), series_metrics in series_groups.items():

                # 3) Group by destination ('target' in DB)
                block_groups = group_metrics_by_metadata(series_metrics, ["target"])

                block_list: List[FlowShareBlock] = []

                for (destination,), block_metrics in block_groups.items():
                    block_list.append(
                        FlowShareBlock(
                            destination=(
                                destination if destination is not None else "unknown"
                            ),
                            values=build_time_series(block_metrics),
                        )
                    )

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
