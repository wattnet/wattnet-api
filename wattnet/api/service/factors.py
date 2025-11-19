from datetime import datetime
from typing import List, Optional, Union

from wattnet.storage.models import Metric
from wattnet.storage.repository import MetricsRepository

from wattnet.api.models.factor import Factor, FactorAggregate, FactorSeries
from wattnet.api.service.operations import (
    build_time_series,
    compute_time_weighted_average,
    group_metrics_by_metadata,
)
from wattnet.api.utils import log

LOG = log.get(__name__)


class FactorService:
    def __init__(self, metrics_repo: MetricsRepository = None):
        LOG.info("Initializing FactorService...")
        self.repo = metrics_repo or MetricsRepository()

    def get_factors(
        self,
        factor_type: Optional[str] = None,
        scope: Optional[str] = None,
        production_type: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        aggregate: bool = False,
    ) -> List[Union[Factor, FactorAggregate]]:

        metric_name = "factor"

        labels = {"app": "wattnet"}
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

        metrics = [m for m in metrics if m.value is not None]

        if not metrics:
            return []

        if aggregate:
            return self._aggregate_metrics(metrics, start, end)
        else:
            return self._group_metrics_series(metrics)

    def _aggregate_metrics(
        self,
        metrics: List[Metric],
        start: datetime,
        end: datetime,
    ) -> List[FactorAggregate]:

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
