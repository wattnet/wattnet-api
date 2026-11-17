"""The aggregates say when the most recent value of the period was stored."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tests.integration import (
    test_factors,
    test_footprints,
    test_impacts,
    test_scores,
)
from tests.unit.service.helpers import FakeMetric

_QUERY = "aggregate=true&start=2025-06-01T00:00:00Z&end=2025-06-02T00:00:00Z"
_OLD = datetime(2025, 6, 2, 1, 0, tzinfo=timezone.utc)
_NEW = datetime(2025, 6, 3, 2, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "module,url",
    [
        (test_footprints, "/v1/footprints"),
        (test_impacts, "/v1/impacts"),
        (test_scores, "/v1/environmental-score"),
        (test_factors, "/v1/factors"),
    ],
)
def test_aggregate_has_the_latest_updated_at(client, mock_db, module, url) -> None:
    """The aggregate carries the most recent ``updated_at`` of its metrics.

    :return: None
    :rtype: None
    """
    first = module._m()
    second = FakeMetric(first.timestamp.replace(minute=15), 3.0, first.metadata, _NEW)
    mock_db([FakeMetric(first.timestamp, 1.0, first.metadata, _OLD), second])
    body = client.get(f"{url}?{_QUERY}").json()
    assert body[0]["updated_at"] == "2025-06-03T02:00:00Z"
