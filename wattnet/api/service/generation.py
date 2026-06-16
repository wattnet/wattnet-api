"""Service layer for handling generation metrics in the wattnet API application."""

from datetime import datetime
from typing import List, Optional

from wattnet.api.models.generation import Generation, GenerationSeries, ProductionBlock
from wattnet.api.service.operations import build_time_series, group_metrics_by_metadata
from wattnet.api.utils import log
from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

LOG = log.get(__name__)


class GenerationService:
    """Service to handle generation metrics for wattnet."""

    def __init__(self, metrics_repo: MetricsRepository):
        """Initialize the GenerationService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
        If not provided, a new instance will be created.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing GenerationService")
        self.repo = metrics_repo

    def get_generation(
        self,
        zone: Optional[str] = None,
        production_type: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Generation]:
        """Retrieve generation metrics filtered by zone, production type, and time.

        :param zone: Optional zone code to filter metrics by zone.
        :type zone: str, optional

        :param production_type: Optional production type to filter metrics.
        :type production_type: str, optional

        :param start: Optional start datetime to filter metrics.
        If provided, end must also be provided.
        :type start: datetime, optional

        :param end: Optional end datetime to filter metrics.
        If provided, start must also be provided.
        :type end: datetime, optional

        :return: List of Generation objects matching the filters.
        :rtype: List[Generation]
        """
        labels = {}
        if zone:
            labels["zone"] = zone
        if production_type:
            labels["production_type"] = production_type

        metrics = self.repo.query_metrics(
            metric_name="zone_generation", start=start, end=end, labels=labels
        )

        metrics = [m for m in metrics if m.value is not None and m.value >= 0]

        if not metrics:
            return []

        return self._group_metrics(metrics)

    def _group_metrics(self, metrics: List[Metric]) -> List[Generation]:
        """Organize flat metrics into Generation -> GenerationSeries -> ProductionBlock.

        :param metrics: List of raw Metric objects to group.
        :type metrics: List[Metric]

        :return: List of grouped Generation objects.
        :rtype: List[Generation]
        """
        # 1) Group by zone, unit (datasource can vary over time)
        zone_groups = group_metrics_by_metadata(
            metrics,
            ["zone", "unit"],
        )

        results = []

        for (zone, unit), zone_metrics in zone_groups.items():

            # 2) Group by (valid, zone_status) to produce GenerationSeries
            series_groups = group_metrics_by_metadata(
                zone_metrics,
                ["valid", "zone_status"],
            )

            series_list: List[GenerationSeries] = []

            for (valid, zone_status), series_metrics in series_groups.items():

                # 3) Group metrics by (production_type, data_state, datasource)
                block_groups = group_metrics_by_metadata(
                    series_metrics,
                    ["production_type", "data_state", "datasource"],
                )

                blocks = []

                for (
                    production_type,
                    data_state,
                    datasource,
                ), block_metrics in block_groups.items():
                    blocks.append(
                        ProductionBlock(
                            production_type=production_type,
                            data_state=data_state,
                            datasource=datasource,
                            values=build_time_series(block_metrics),
                        )
                    )

                generation_series = GenerationSeries(
                    valid=valid,
                    zone_status=zone_status,
                    production=blocks,
                )

                series_list.append(generation_series)

            generation = Generation(
                zone=zone,
                unit=unit,
                series=series_list,
            )

            results.append(generation)

        return results
