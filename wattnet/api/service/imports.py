from datetime import datetime
from typing import List

from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.imports import Import, ImportBlock, ImportSeries
from wattnet.api.service.operations import group_metrics_by_metadata
from wattnet.api.utils import log

LOG = log.get(__name__)


class ImportService:
    def __init__(self, metrics_repo: MetricsRepository = None):
        LOG.info("Initializing ImportService")
        self.repo = metrics_repo or MetricsRepository()

    def get_imports(
        self,
        zone: str = None,
        source: str = None,
        start: datetime = None,
        end: datetime = None,
    ) -> List[Import]:
        """
        Fetch import metrics and return hierarchical structure:
        Import -> ImportSeries -> ImportBlock
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

        if not metrics:
            return []

        return self._group_metrics(metrics)

    # ------------------------------------------------------------------------------

    def _group_metrics(self, metrics: List[Metric]) -> List[Import]:
        """
        Organize flat metrics into Import -> ImportSeries -> ImportBlock.
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
