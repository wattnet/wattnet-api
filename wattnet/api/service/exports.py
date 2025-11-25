from datetime import datetime
from typing import List

from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.exports import Export, ExportBlock, ExportSeries
from wattnet.api.service.operations import group_metrics_by_metadata
from wattnet.api.utils import log

LOG = log.get(__name__)


class ExportService:
    def __init__(self, metrics_repo: MetricsRepository = None):
        LOG.info("Initializing ExportService")
        self.repo = metrics_repo or MetricsRepository()

    def get_exports(
        self,
        zone: str = None,
        destination: str = None,
        start: datetime = None,
        end: datetime = None,
    ) -> List[Export]:
        """
        Fetch export metrics and return hierarchical structure:
        Export -> ExportSeries -> ExportBlock
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

        if not metrics:
            return []

        return self._group_metrics(metrics)

    # ------------------------------------------------------------------------------

    def _group_metrics(self, metrics: List[Metric]) -> List[Export]:
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
