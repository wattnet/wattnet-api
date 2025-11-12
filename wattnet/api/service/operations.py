from datetime import datetime
from typing import List


def time_weighted_average(data: List[List], start: str, end: str) -> float:
    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))

    total_duration = 0
    weighted_sum = 0

    for i, (ts_str, value) in enumerate(data):
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))

        # Skip if before start or beyond end
        if ts >= end_dt:
            break
        if i + 1 >= len(data):
            break  # no next point to define duration

        next_ts = datetime.fromisoformat(data[i + 1][0].replace("Z", "+00:00"))

        # Clamp to the interval [start, end]
        interval_start = max(ts, start_dt)
        interval_end = min(next_ts, end_dt)

        duration = (interval_end - interval_start).total_seconds()
        if duration <= 0:
            continue

        weighted_sum += value * duration
        total_duration += duration

    if total_duration == 0:
        return None  # or raise ValueError("No overlapping data in the time interval")

    return weighted_sum / total_duration
