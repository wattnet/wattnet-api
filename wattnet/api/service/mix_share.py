"""Service layer for handling mix share metrics in the wattnet API application."""

from datetime import datetime
from typing import List, Optional

from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.mix_share import MixShare, MixShareBlock, MixShareSeries
from wattnet.api.service.operations import group_metrics_by_metadata
from wattnet.api.utils import log

LOG = log.get(__name__)


class MixShareService:
    """Service to handle mix share metrics for Wattnet."""

    def __init__(self, metrics_repo: Optional[MetricsRepository] = None):
        """Initialize the MixShareService with a metrics repository.

        :param metrics_repo: Optional MetricsRepository instance for database access.
        If not provided, a new instance will be created.
        :type metrics_repo: MetricsRepository, optional
        """
        self.repo = metrics_repo or MetricsRepository()

    def get_mix_share(
        self,
        zone: Optional[str] = None,
        origin: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[MixShare]:
        """Retrieve mix share metrics filtered by zone, origin, and time range.

        :param zone: Optional zone code to filter metrics by destination zone.
        :type zone: str, optional

        :param origin: Optional origin zone code to filter metrics by source zone.
        :type origin: str, optional

        :param start: Optional start datetime to filter metrics.
        If provided, end must also be provided.
        :type start: datetime, optional

        :param end: Optional end datetime to filter metrics.
        If provided, start must also be provided.
        :type end: datetime, optional

        :return: List of MixShare objects matching the filters.
        :rtype: List[MixShare]
        """
        labels = {}
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
        """Group raw mix share metrics into structured MixShare objects.

        :param metrics: List of raw Metric objects to group.
        :type metrics: List[Metric]

        :return: List of grouped MixShare objects.
        :rtype: List[MixShare]
        """
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
