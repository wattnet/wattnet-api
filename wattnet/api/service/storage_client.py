from datetime import datetime, timedelta

from prometheus_api_client import PrometheusConnect

from wattnet.api.settings import settings
from wattnet.api.utils import log

# Get logger
LOG = log.get(__name__)

# Maximum number of points per query (VictoriaMetrics default is 30000)
MAX_POINTS = 30000


class StorageClient:
    """
    A class to interact with the Prometheus API for storage metrics.
    """

    def __init__(self):
        """
        Initializes the StorageClient with Prometheus connection details.
        """

        LOG.info("Initializing StorageClient...")

        # Get the storage URL
        self.storage_db_url = settings.storage_db_url
        LOG.debug(f"Storage URL: {self.storage_db_url}")

        # Initialize the storage connection
        self.storage = PrometheusConnect(
            url=self.storage_db_url,
            disable_ssl=True,
        )

        if not self.check_connection():
            LOG.error("Failed to connect to storage")
            raise ConnectionError("Failed to connect to storage")
        else:
            LOG.info("Connected to storage")

        self.step = settings.timeseries_step_minutes
        # Convert step to seconds if it's in minutes
        self.step = int(self.step) * 60

    def check_connection(self) -> bool:
        """
        Check the connection to the storage.
        """

        try:
            # Check if the storage is reachable
            self.storage.custom_query(query="up")
            LOG.info("Storage connection is healthy.")
            return True
        except Exception as e:
            LOG.error(f"Storage connection failed: {e}")
            return False

    def get_metrics(self, query, start=None, end=None, params=None):
        """
        Get metrics from the storage. If the interval is too large, split the query.
        """
        original_start = start
        start = self._align_start(start)
        print(f"Adjusted start time: {start}")

        query = self._add_step_to_query(query)
        params = self._prepare_query_params(params)

        if start and end:
            if self._needs_splitting(start, end):
                return self._query_in_chunks(query, start, end, original_start, params)
            return self._query_single_range(query, start, end, original_start, params)

        return self.storage.custom_query(query=query, params=params)

    # ---------- Auxiliary methods ----------

    def _align_start(self, start: datetime) -> datetime | None:
        if not start:
            return None

        step_seconds = self.step  # e.g., 900 for 15 minutes
        timestamp = start.timestamp()
        aligned_timestamp = (timestamp // step_seconds) * step_seconds
        return datetime.fromtimestamp(aligned_timestamp, tz=start.tzinfo)

    def _add_step_to_query(self, query):
        return f"{query}[{self.step}s]"

    def _prepare_query_params(self, params):
        params = params or {}
        params.update(
            {
                "dedup": "false",
                "downsampling": "0",
                "maxPoints": "0",
            }
        )
        return params

    def _needs_splitting(self, start, end):
        interval = (end - start).total_seconds()
        return interval / self.step > MAX_POINTS

    def _adjust_first_timestamp(self, result, new_timestamp):
        if not result:
            return result

        try:
            if isinstance(result, dict):
                series_list = result["data"]["result"]
            if isinstance(result, list):
                series_list = result
            else:
                return result

            for series in series_list:
                if series.get("values"):
                    series["values"][0][0] = new_timestamp.timestamp()

            return result
        except (KeyError, TypeError, IndexError):
            return result

    def _query_single_range(self, query, start, end, original_start, params):
        result = self.storage.custom_query_range(
            query=query,
            start_time=start,
            end_time=end,
            step=self.step,
            params=params,
        )
        return self._adjust_first_timestamp(result, original_start)

    def _query_in_chunks(self, query, start, end, original_start, params):
        LOG.warning(
            f"Query interval exceeds maximum points limit ({MAX_POINTS}). "
            "Splitting the query into smaller intervals."
        )
        results = []
        max_chunk = timedelta(seconds=self.step * MAX_POINTS)
        current_start = start

        while current_start < end:
            current_end = min(current_start + max_chunk, end)

            partial_result = self.storage.custom_query_range(
                query=query,
                start_time=current_start,
                end_time=current_end,
                step=self.step,
                params=params,
            )

            if current_start == start:
                partial_result = self._adjust_first_timestamp(
                    partial_result, original_start
                )

            results.append(partial_result)
            current_start = current_end

        return self._merge_results(results)

    def _merge_results(self, results):
        if not results:
            return []

        merged = {}
        for result in results:
            for series in result:
                key = (series["metric"].get("__name__", ""),) + tuple(
                    sorted(series["metric"].items())
                )
                if key not in merged:
                    merged[key] = {
                        "metric": series["metric"],
                        "values": [],
                    }
                merged[key]["values"].extend(series["values"])

        return list(merged.values())
