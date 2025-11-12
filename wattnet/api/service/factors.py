from datetime import datetime, timezone

from wattnet.api.models.factor import Factor
from wattnet.api.service.storage_client import StorageClient
from wattnet.api.utils import log

# Get logger
LOG = log.get(__name__)


class FactorService:

    def __init__(self):
        """Service to configure queries to the storage."""

        LOG.info("Initializing FactorService...")

        # Get the storage client
        self.storage = StorageClient()

    def get_factors(
        self, factor_type=None, scope=None, production_type=None, start=None, end=None
    ):
        """Get all factors or a specific factor by ID."""

        factors = []

        # Build the query based on the parameters if provided (can be both)
        query = "factor{app='wattnet'"
        if factor_type:
            query += f", factor_type='{factor_type}'"
        if scope:
            query += f", scope='{scope}'"
        if production_type:
            query += f", production_type='{production_type}'"
        query += "}"
        LOG.debug(f"Query: {query}")

        # Get all factors from the storage
        response = self.storage.get_metrics(query=query, start=start, end=end)

        for factor in enumerate(response):
            # Convert the metric to a factor
            factor = self._metric2factor(factor[1])
            factors.append(factor)

        LOG.debug(f"Found {len(factors)} factors.")

        # Return the factors
        return factors

    def _metric2factor(self, metric: str) -> Factor:
        """Convert a metric to a factor."""

        # Get the labels
        labels = metric.get("metric", {}) if isinstance(metric, dict) else {}

        # Get the value list
        value_list = metric.get("values", []) if isinstance(metric, dict) else []

        # Convert the value list to a list of tuples (datetime with UTC (convert from timestamp), float)
        value_list = [
            (datetime.fromtimestamp(float(value[0]), tz=timezone.utc), float(value[1]))
            for value in value_list
        ]

        # Convert year to int if not none
        if labels["year"] != "None":
            labels["year"] = int(labels["year"])
        else:
            labels["year"] = None
        # Convert source_link to str if not none
        if labels["source_link"] != "None":
            labels["source_link"] = str(labels["source_link"])
        else:
            labels["source_link"] = None

        # Create the factor
        factor = Factor(
            factor_type=labels["factor_type"],
            scope=labels["scope"],
            production_type=labels["production_type"],
            values=value_list,
            unit=labels["unit"],
            source=labels["source"],
            year=labels["year"],
            source_link=labels["source_link"],
        )

        return factor
