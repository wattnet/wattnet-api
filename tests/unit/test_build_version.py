"""The version that the documentation shows."""

import pytest

from wattnet.api import __version__
from wattnet.api.app import build_version


def test_release_shows_the_package_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BUILD_COMMIT", raising=False)
    assert build_version() == __version__


def test_snapshot_shows_the_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BUILD_COMMIT", "6bc3875")
    assert build_version() == "6bc3875"


@pytest.mark.parametrize("value", ["", "main", "6BC3875", "abc"])
def test_anything_else_is_ignored(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("BUILD_COMMIT", value)
    assert build_version() == __version__
