from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from wattnet.api.models.footprint import Footprint, FootprintAggregate, FootprintSeries
from wattnet.api.service.storage_client import StorageClient
from wattnet.api.utils import log

# Get logger
LOG = log.get(__name__)


# Priority for zone_status: higher number means higher priority
ZONE_STATUS_PRIORITY = {"missing": 0, "preview": 1, "complete": 2}


class FootprintService:
    def __init__(self):
        """Service to configure queries to the storage."""
        LOG.info("Initializing FootprintService")
        self.storage = StorageClient()

    def get_footprints(
        self,
        zone=None,
        footprint_type=None,
        scope=None,
        start=None,
        end=None,
        aggregate=False,
        use_global=True,
    ):
        """Get footprints, aggregated or as series grouped by state."""

        # Compose the query based on provided parameters
        if use_global:
            query = "global_footprint"  # Metric name if global
        else:
            query = "local_footprint"  # Metric name if local
        query += "{app='wattnet'"  # Start of label selectors
        if zone:
            query += f", zone='{zone}'"
        if footprint_type:
            query += f", footprint_type='{footprint_type}'"
        if scope:
            query += f", scope='{scope}'"
        query += "} > 0"  # Only positive values

        print("Footprint query:", query)

        # Query the storage for metrics
        response = self.storage.get_metrics(query=query, start=start, end=end)

        if not response:
            return []

        # Parse response into a list of raw points with states per timestamp
        raw_points = self._parse_metrics(response)

        # Filter points to keep only those with highest priority per unique key
        best_points = self._filter_best_points(raw_points)

        if aggregate:
            # Calculate aggregated footprint
            return self._aggregate_points(best_points, start, end, use_global)
        else:
            # Group series by (valid, zone_status)
            return self._group_points_by_status(best_points, use_global)

    def _parse_metrics(
        self, response
    ) -> List[Tuple[datetime, bool, str, float, str, str, str]]:
        """
        Parse response JSON into list of tuples:
        (timestamp, valid, zone_status, value, footprint_type, zone, unit)
        """
        points = []
        for metric in response:
            labels = metric.get("metric", {})
            values = metric.get("values", [])
            footprint_type = labels.get("footprint_type", "unknown")
            scope = labels.get("scope", "unknown")
            zone = labels.get("zone", "unknown")
            unit = labels.get("unit", "unknown")
            valid = labels.get("valid", "false").lower() == "true"
            zone_status = labels.get("zone_status", "missing")

            for ts_str, val_str in values:
                ts = datetime.fromtimestamp(float(ts_str), tz=timezone.utc)
                val = float(val_str)
                points.append(
                    (ts, valid, zone_status, val, footprint_type, scope, zone, unit)
                )

        return points

    def _filter_best_points(
        self, points: List[Tuple[datetime, bool, str, float, str, str, str]]
    ) -> List[Tuple[datetime, bool, str, float, str, str, str]]:
        """
        For each unique combination of (timestamp, footprint_type, scope, zone, unit)
        keep only points with highest priority:
        - valid=True preferred over valid=False
        - zone_status priority: complete > preview > missing
        """

        # Group points by (timestamp, footprint_type, scope, zone, unit)
        points_by_key: Dict[Tuple[datetime, str, str, str, str], List[Tuple]] = {}

        for p in points:
            key = (
                p[0],
                p[4],
                p[5],
                p[6],
                p[7],
            )  # timestamp, footprint_type, scope zone, unit
            points_by_key.setdefault(key, []).append(p)

        filtered_points = []

        for key, pts in points_by_key.items():
            # Prefer valid=True if any
            valid_true_pts = [p for p in pts if p[1] is True]
            if valid_true_pts:
                pts = valid_true_pts

            # Get max zone_status priority
            max_priority = max(ZONE_STATUS_PRIORITY[p[2]] for p in pts)
            best_pts = [p for p in pts if ZONE_STATUS_PRIORITY[p[2]] == max_priority]

            filtered_points.extend(best_pts)

        return filtered_points

    def _aggregate_points(
        self,
        points: List[Tuple[datetime, bool, str, float, str, str, str, str]],
        start: datetime,
        end: datetime,
        use_global: bool,
    ) -> List[FootprintAggregate]:
        """
        Compute time-weighted averages over [start, end) for each (footprint_type, scope, zone).
        Each point is valid from its timestamp until the next one,
        and the last point is valid until `end`.
        """

        if not points:
            return []

        # Group points by (footprint_type, scope, zone)
        grouped = defaultdict(list)
        for p in points:
            grouped[(p[4], p[5], p[6])].append(p)  # footprint_type, scope, zone

        aggregates = []

        for (footprint_type, scope, zone), pts in grouped.items():
            pts.sort(key=lambda x: x[0])

            total_weighted_value = 0.0
            total_duration = 0.0

            # Intermediate intervals
            for (t0, _, _, val0, *_), (t1, *_rest) in zip(pts, pts[1:]):
                effective_start = max(t0, start)
                effective_end = min(t1, end)
                duration = (effective_end - effective_start).total_seconds()
                if duration > 0:
                    total_weighted_value += val0 * duration
                    total_duration += duration

            # Last point until end
            last_ts, _, _, last_val, *_ = pts[-1]
            if last_ts < end:
                effective_start = max(last_ts, start)
                duration = (end - effective_start).total_seconds()
                if duration > 0:
                    total_weighted_value += last_val * duration
                    total_duration += duration

            value_agg = (
                total_weighted_value / total_duration
                if total_duration > 0
                else pts[0][3]
            )

            valid_agg = all(p[1] for p in pts)
            min_priority = min(ZONE_STATUS_PRIORITY[p[2]] for p in pts)
            zone_status_agg = next(
                status
                for status, prio in ZONE_STATUS_PRIORITY.items()
                if prio == min_priority
            )

            aggregates.append(
                FootprintAggregate(
                    footprint_type=footprint_type,
                    scope=scope,
                    zone=zone,
                    unit=pts[0][7],  # For now, we assume all points have the same unit
                    start=start,
                    end=end,
                    value=value_agg,
                    valid=valid_agg,
                    zone_status=zone_status_agg,
                    aggregation_method="time-weighted-average",
                    coverage="global" if use_global else "local",
                )
            )

        return aggregates

    def _group_points_by_status(
        self,
        points: List[Tuple[datetime, bool, str, float, str, str, str, str]],
        use_global: bool,
    ) -> List[Footprint]:
        """
        Agrupa los puntos en FootprintSeries agrupados por (valid, zone_status),
        y además separa por footprint_type, scope, zone y unit para no mezclar tipos diferentes.
        """

        if not points:
            return []

        # Group points by (footprint_type, scope, zone, unit)
        # key = (footprint_type, scope,  zone, unit)
        # value = dict {(valid, zone_status): list[(ts, val)]}
        grouped: Dict[
            Tuple[str, str, str, str],
            Dict[Tuple[bool, str], List[Tuple[datetime, float]]],
        ] = {}

        for ts, valid, zone_status, val, footprint_type, scope, zone, unit in points:
            key = (footprint_type, scope, zone, unit)
            if key not in grouped:
                grouped[key] = {}
            series_key = (valid, zone_status)
            grouped[key].setdefault(series_key, []).append((ts, val))

        footprints = []

        for (footprint_type, scope, zone, unit), series_map in grouped.items():
            footprint_series = []
            for (valid, zone_status), values in series_map.items():
                values.sort(key=lambda x: x[0])
                footprint_series.append(
                    FootprintSeries(valid=valid, zone_status=zone_status, values=values)
                )
            footprints.append(
                Footprint(
                    footprint_type=footprint_type,
                    scope=scope,
                    zone=zone,
                    unit=unit,
                    series=footprint_series,
                    coverage="global" if use_global else "local",
                )
            )

        return footprints
