"""Service layer for handling load metrics in the wattnet API application."""

from datetime import datetime
from typing import List, Optional

from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.load import Load, LoadBlock, LoadSeries
from wattnet.api.service.operations import group_metrics_by_metadata
from wattnet.api.utils import log

LOG = log.get(__name__)


class LoadService:
    """Service to handle load (total electricity demand) metrics for wattnet."""

    def __init__(self, metrics_repo: Optional[MetricsRepository] = None):
        """Initialize the LoadService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
            If not provided, a new instance will be created.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing LoadService")
        self.repo = metrics_repo or MetricsRepository()

    def get_load(
        self,
        zone: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Load]:
        """Retrieve load metrics filtered by zone and time range.

        :param zone: Optional zone code to filter metrics.
        :type zone: str, optional

        :param start: Optional start datetime to filter metrics.
            If provided, end must also be provided.
        :type start: datetime, optional

        :param end: Optional end datetime to filter metrics.
            If provided, start must also be provided.
        :type end: datetime, optional

        :return: List of Load objects matching the filters.
        :rtype: List[Load]
        """
        labels = {}
        if zone:
            labels["zone"] = zone

        metrics = self.repo.query_metrics(
            metric_name="zone_load", start=start, end=end, labels=labels
        )

        metrics = [m for m in metrics if m.value is not None and m.value >= 0]

        if not metrics:
            return []

        return self._group_metrics(metrics)

    def _group_metrics(self, metrics: List[Metric]) -> List[Load]:
        """Organise flat metrics into Load → LoadSeries.

        :param metrics: List of raw Metric objects to group.
        :type metrics: List[Metric]

        :return: List of grouped Load objects.
        :rtype: List[Load]
        """
        # Group by zone, unit (datasource can vary over time)
        zone_groups = group_metrics_by_metadata(metrics, ["zone", "unit"])

        results = []

        for (zone, unit), zone_metrics in zone_groups.items():

            # Subgroup by (valid, zone_status)
            series_groups = group_metrics_by_metadata(
                zone_metrics, ["valid", "zone_status"]
            )

            series_list: List[LoadSeries] = []

            for (valid, zone_status), series_metrics in series_groups.items():
                block_groups = group_metrics_by_metadata(
                    series_metrics,
                    ["data_state", "datasource"],
                )

                blocks: List[LoadBlock] = []

                for (data_state, datasource), block_metrics in block_groups.items():
                    values = sorted(
                        [(m.timestamp, m.value) for m in block_metrics],
                        key=lambda x: x[0],
                    )

                    blocks.append(
                        LoadBlock(
                            data_state=data_state,
                            datasource=datasource,
                            values=values,
                        )
                    )

                series_list.append(
                    LoadSeries(
                        valid=valid,
                        zone_status=zone_status,
                        blocks=blocks,
                    )
                )

            results.append(
                Load(
                    zone=zone,
                    unit=unit,
                    series=series_list,
                )
            )

        return results
