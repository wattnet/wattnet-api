"""LatestPointRepository: a query with no range gets the latest point before now."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from wattnet.api.repository import LATEST_LOOKBACK, LatestPointRepository
from wattnet.storage import StorageConfig

LATEST = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def repo():
    """A repository over a mocked storage manager (15-minute intervals)."""
    with patch("wattnet.storage.repository.metrics_repository.StorageClientsManager"):
        repository = LatestPointRepository(StorageConfig(timeseries_step_minutes=15))
    repository.storage_manager = MagicMock()
    repository.storage_manager.read_metrics.return_value = []
    return repository


def test_no_range_reads_the_interval_of_the_latest_point(repo):
    repo.storage_manager.latest_timestamp.return_value = LATEST
    labels = {"zone": "ES"}
    repo.query_metrics("zone_load", labels=labels)

    name, before, asked_labels, after = repo.storage_manager.latest_timestamp.call_args.args
    assert (name, asked_labels) == ("zone_load", labels)
    assert before.tzinfo is not None and before - after == LATEST_LOOKBACK
    read = repo.storage_manager.read_metrics.call_args.kwargs
    assert read["start"] == LATEST
    assert read["end"] == LATEST + timedelta(minutes=15)
    assert read["labels"] == labels


def test_no_point_in_the_lookback_answers_nothing(repo):
    repo.storage_manager.latest_timestamp.return_value = None
    assert repo.query_metrics("factor", labels={"factor_type": "carbon"}) == []
    repo.storage_manager.read_metrics.assert_not_called()


def test_a_range_is_read_as_given(repo):
    start = datetime(2026, 7, 15, tzinfo=timezone.utc)
    end = start + timedelta(hours=6)
    repo.query_metrics("zone_load", start=start, end=end, labels={"zone": "ES"})
    repo.storage_manager.latest_timestamp.assert_not_called()
    read = repo.storage_manager.read_metrics.call_args.kwargs
    assert (read["start"], read["end"]) == (start, end)


def test_other_options_are_passed_on(repo):
    repo.storage_manager.latest_timestamp.return_value = LATEST
    repo.query_metrics("zone_load", labels={"zone": "ES"}, resolution_minutes=60)
    read = repo.storage_manager.read_metrics.call_args.kwargs
    assert read["params"] == {"resolution_minutes": 60}
