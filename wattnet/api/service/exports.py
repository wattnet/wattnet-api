"""Service layer for handling export metrics."""

from datetime import datetime
from typing import List, Optional

from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.exports import Export, ExportBlock, ExportSeries
from wattnet.api.service.operations import group_metrics_by_metadata
from wattnet.api.utils import log

LOG = log.get(__name__)


class ExportService:
    """Service to handle export metrics."""

    def __init__(self, metrics_repo: Optional[MetricsRepository] = None):
        """Initialize the ExportService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
        If not provided, a new instance will be created.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing ExportService")
        self.repo = metrics_repo or MetricsRepository()

    def get_exports(
        self,
        zone: Optional[str] = None,
        destination: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Export]:
        """Retrieve export metrics filtered by zone, destination, and time range.

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

        :return: List of Export objects matching the filters.
        :rtype: List[Export]
        """
        labels = {"app": "wattnet"}
        if zone:
            labels["zone"] = zone
        if destination:
            labels["to"] = destination  # DB label is "to"

        metrics = self.repo.query_metrics(
            metric_name="zone_export",
            start=start,
            end=end,
            labels=labels,
        )

        metrics = [m for m in metrics if m.value is not None and m.value >= 0]

        if not metrics:
            return []

        return self._group_metrics(metrics)

    # ------------------------------------------------------------------------------

    def _group_metrics(self, metrics: List[Metric]) -> List[Export]:
        """Group raw export metrics into structured Export objects.

        :param metrics: List of raw Metric objects to group.
        :type metrics: List[Metric]

        :return: List of grouped Export objects.
        :rtype: List[Export]
        """
        # 1) Group by zone, unit, datasource
        zone_groups = group_metrics_by_metadata(
            metrics,
            ["zone", "unit", "datasource"],
        )

        results = []

        for (zone, unit, datasource), zone_metrics in zone_groups.items():

            # 2) Group by (valid, zone_status) => ExportSeries
            series_groups = group_metrics_by_metadata(
                zone_metrics,
                ["valid", "zone_status"],
            )

            series_list: List[ExportSeries] = []

            for (valid, zone_status), series_metrics in series_groups.items():

                # 3) Group by "to" + data_state => ExportBlock
                block_groups = group_metrics_by_metadata(
                    series_metrics,
                    ["to", "data_state"],  # DB uses 'to'
                )

                block_list: List[ExportBlock] = []

                for (destination_to, data_state), block_metrics in block_groups.items():

                    values = sorted(
                        [(m.timestamp, m.value) for m in block_metrics],
                        key=lambda x: x[0],
                    )

                    block = ExportBlock(
                        destination=destination_to,  # Pydantic field
                        data_state=data_state,
                        unit=unit,
                        values=values,
                    )

                    block_list.append(block)

                export_series = ExportSeries(
                    valid=valid,
                    zone_status=zone_status,
                    exports=block_list,
                )

                series_list.append(export_series)

            export_obj = Export(
                zone=zone,
                unit=unit,
                datasource=datasource,
                series=series_list,
            )

            results.append(export_obj)

        return results
