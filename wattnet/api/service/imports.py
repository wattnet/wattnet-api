"""Service layer for handling import metrics in the wattnet API application."""

from datetime import datetime
from typing import List, Optional

from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.imports import Import, ImportBlock, ImportSeries
from wattnet.api.service.operations import group_metrics_by_metadata
from wattnet.api.utils import log

LOG = log.get(__name__)


class ImportService:
    """Service to handle import metrics for wattnet."""

    def __init__(self, metrics_repo: Optional[MetricsRepository] = None):
        """Initialize the ImportService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
        If not provided, a new instance will be created.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing ImportService")
        self.repo = metrics_repo or MetricsRepository()

    def get_imports(
        self,
        zone: Optional[str] = None,
        source: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Import]:
        """Retrieve import metrics filtered by zone, source, and time range.

        :param zone: Optional zone code to filter metrics by destination zone.
        :type zone: str, optional

        :param source: Optional origin zone code to filter metrics by source zone.
        :type source: str, optional

        :param start: Optional start datetime to filter metrics.
        If provided, end must also be provided.
        :type start: datetime, optional

        :param end: Optional end datetime to filter metrics.
        If provided, start must also be provided.
        :type end: datetime, optional

        :return: List of Import objects matching the filters.
        :rtype: List[Import]
        """
        labels = {"app": "wattnet"}
        if zone:
            labels["zone"] = zone
        if source:
            labels["from"] = source

        metrics = self.repo.query_metrics(
            metric_name="zone_import",
            start=start,
            end=end,
            labels=labels,
        )

        metrics = [m for m in metrics if m.value is not None and m.value >= 0]

        if not metrics:
            return []

        return self._group_metrics(metrics)

    # ------------------------------------------------------------------------------

    def _group_metrics(self, metrics: List[Metric]) -> List[Import]:
        """Group raw import metrics into structured Import objects.

        :param metrics: List of raw Metric objects to group.
        :type metrics: List[Metric]

        :return: List of grouped Import objects.
        :rtype: List[Import]
        """
        # 1) Group by zone, unit, datasource
        zone_groups = group_metrics_by_metadata(
            metrics,
            ["zone", "unit", "datasource"],
        )

        results = []

        for (zone, unit, datasource), zone_metrics in zone_groups.items():

            # 2) Group by (valid, zone_status) => ImportSeries
            series_groups = group_metrics_by_metadata(
                zone_metrics,
                ["valid", "zone_status"],
            )

            series_list: List[ImportSeries] = []

            for (valid, zone_status), series_metrics in series_groups.items():

                # 3) Group by source + data_state => ImportBlock
                block_groups = group_metrics_by_metadata(
                    series_metrics,
                    ["from", "data_state"],
                )

                block_list: List[ImportBlock] = []

                for (source_from, data_state), block_metrics in block_groups.items():

                    values = sorted(
                        [(m.timestamp, m.value) for m in block_metrics],
                        key=lambda x: x[0],
                    )

                    block = ImportBlock(
                        source=source_from,
                        data_state=data_state,
                        unit=unit,
                        values=values,
                    )

                    block_list.append(block)

                import_series = ImportSeries(
                    valid=valid,
                    zone_status=zone_status,
                    imports=block_list,  # note: field name is 'imports' in the model
                )

                series_list.append(import_series)

            import_obj = Import(
                zone=zone,
                unit=unit,
                datasource=datasource,
                series=series_list,
            )

            results.append(import_obj)

        return results
