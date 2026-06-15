"""Service layer for handling factor metrics."""

from datetime import datetime
from typing import List, Optional, Union

from wattnet.api.models.factor import Factor, FactorAggregate, FactorSeries
from wattnet.api.service.operations import (
    build_time_series,
    compute_time_weighted_average,
    group_metrics_by_metadata,
)
from wattnet.api.utils import log
from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

LOG = log.get(__name__)


class FactorService:
    """Service to handle factor metrics."""

    def __init__(self, metrics_repo: MetricsRepository):
        """Initialize the FactorService with a MetricsRepository.

        :param metrics_repo: Optional MetricsRepository instance.
        If not provided, a new instance will be created.
        :type metrics_repo: MetricsRepository, optional
        """
        LOG.info("Initializing FactorService...")
        self.repo = metrics_repo

    def get_factors(
        self,
        factor_type: Optional[str] = None,
        scope: Optional[str] = None,
        production_type: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        aggregate: bool = False,
    ) -> Union[List[FactorAggregate], List[Factor]]:
        """Retrieve factor metrics filtered.

        :param factor_type: Optional factor type to filter metrics.
        :type factor_type: str, optional

        :param scope: Optional scope to filter metrics
        (e.g., "production", "consumption").
        :type scope: str, optional

        :param production_type: Optional production type to filter metrics.
        :type production_type: str, optional

        :param start: Optional start datetime to filter metrics.
        If provided, end must also be provided.
        :type start: datetime, optional

        :param end: Optional end datetime to filter metrics.
        If provided, start must also be provided.
        :type end: datetime, optional

        :param aggregate: Whether to return aggregated metrics (time-weighted average)
        or time series. Defaults to False (return time series).
        :type aggregate: bool, optional

        :return: List of FactorAggregate or Factor objects matching the filters.
        :rtype: Union[List[FactorAggregate], List[Factor]]
        """
        metric_name = "factor"

        labels = {}
        if production_type:
            labels["production_type"] = production_type
        if factor_type:
            labels["factor_type"] = factor_type
        if scope:
            labels["scope"] = scope

        metrics = self.repo.query_metrics(
            metric_name=metric_name,
            start=start,
            end=end,
            labels=labels,
        )

        metrics = [m for m in metrics if m.value is not None and m.value >= 0]

        if not metrics:
            return []

        if aggregate and start and end:
            return self._aggregate_metrics(metrics, start, end)
        else:
            return self._group_metrics_series(metrics)

    def _aggregate_metrics(
        self,
        metrics: List[Metric],
        start: datetime,
        end: datetime,
    ) -> List[FactorAggregate]:
        """Aggregate raw factor metrics into structured FactorAggregate objects.

        :param metrics: List of raw Metric objects to aggregate.
        :type metrics: List[Metric]

        :param start: Start datetime for the aggregation period.
        :type start: datetime

        :param end: End datetime for the aggregation period.
        :type end: datetime

        :return: List of aggregated FactorAggregate objects.
        :rtype: List[FactorAggregate]
        """
        if not metrics:
            return []

        grouped = group_metrics_by_metadata(
            metrics,
            [
                "factor_type",
                "production_type",
                "scope",
                "unit",
                "source",
                "year",
                "source_link",
            ],
        )

        results = []

        for key, mlist in grouped.items():
            (
                factor_type,
                production_type,
                scope,
                unit,
                source,
                year,
                source_link,
            ) = key

            value_agg = compute_time_weighted_average(mlist, start, end)

            results.append(
                FactorAggregate(
                    factor_type=factor_type,
                    production_type=production_type,
                    scope=scope,
                    unit=unit,
                    source=source,
                    year=year,
                    source_link=source_link,
                    start=start,
                    end=end,
                    value=value_agg,
                    aggregation_method="time-weighted-average",
                )
            )

        return results

    def _group_metrics_series(
        self,
        metrics: List[Metric],
    ) -> List[Factor]:
        """Group raw factor metrics into structured Factor objects with time series.

        :param metrics: List of raw Metric objects to group.
        :type metrics: List[Metric]

        :return: List of grouped Factor objects with time series.
        :rtype: List[Factor]
        """
        if not metrics:
            return []

        grouped = group_metrics_by_metadata(
            metrics,
            [
                "factor_type",
                "production_type",
                "scope",
                "unit",
                "source",
                "year",
                "source_link",
            ],
        )

        results = []

        for (
            factor_type,
            production_type,
            scope,
            unit,
            source,
            year,
            source_link,
        ), mlist in grouped.items():

            values = build_time_series(mlist)

            results.append(
                Factor(
                    factor_type=factor_type,
                    production_type=production_type,
                    scope=scope,
                    unit=unit,
                    source=source,
                    year=year,
                    source_link=source_link,
                    series=[FactorSeries(values=values)],
                )
            )

        return results
