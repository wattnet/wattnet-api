"""
Unit tests for wattnet.api.utils.geo module.

These tests validate:
- GeoJSON filtering logic
- Point containment detection
- Async concurrency behavior
- Integration with settings and trio runtime
"""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

import pytest
from shapely.geometry import Point

import wattnet.api.service.geo as geo

# ============================================================
# Helpers
# ============================================================


class FakeGeoDataFrame:
    """
    Minimal mock of a GeoDataFrame object.

    :param contains_result: Whether the mocked geometry contains the point
    :type contains_result: bool
    """

    def __init__(self, contains_result: bool) -> None:
        """Initialize with specified containment result.

        :param contains_result: Whether the mocked geometry contains the point
        :type contains_result: bool
        """
        self._contains_result: bool = contains_result

    def contains(self, point: Point) -> object:
        """Check if the geometry contains the point.

        :param point: Shapely point
        :type point: Point
        :return: Object with an .any() method
        :rtype: object
        """

        class Result:
            def __init__(self, value: bool) -> None:
                self._value: bool = value

            def any(self) -> bool:
                """
                Return containment result.

                :return: True if contained
                :rtype: bool
                """
                return self._value

        return Result(self._contains_result)


# ============================================================
# check_file_contains_point
# ============================================================


@pytest.mark.trio
async def test_check_file_contains_point_not_geojson(
    tmp_path: Path,
) -> None:
    """
    Ensure non-GeoJSON files are ignored.

    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    point: Point = Point(0.0, 0.0)

    result: Optional[str] = await geo.check_file_contains_point(
        "file.txt",
        tmp_path,
        point,
    )

    assert result is None


@pytest.mark.trio
async def test_check_file_contains_point_contains(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Ensure zone code is returned when point is contained.

    :param monkeypatch: Pytest monkeypatch fixture
    :type monkeypatch: pytest.MonkeyPatch
    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """

    def fake_read_file(path: Path) -> FakeGeoDataFrame:
        return FakeGeoDataFrame(True)

    monkeypatch.setattr(geo.gpd, "read_file", fake_read_file)

    point: Point = Point(1.0, 1.0)

    result: Optional[str] = await geo.check_file_contains_point(
        "ZONE.geojson",
        tmp_path,
        point,
    )

    assert result == "ZONE"


@pytest.mark.trio
async def test_check_file_contains_point_not_contains(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Ensure None is returned when point is not contained.

    :param monkeypatch: Pytest monkeypatch fixture
    :type monkeypatch: pytest.MonkeyPatch
    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """

    def fake_read_file(path: Path) -> FakeGeoDataFrame:
        return FakeGeoDataFrame(False)

    monkeypatch.setattr(geo.gpd, "read_file", fake_read_file)

    point: Point = Point(1.0, 1.0)

    result: Optional[str] = await geo.check_file_contains_point(
        "ZONE.geojson",
        tmp_path,
        point,
    )

    assert result is None


@pytest.mark.trio
async def test_check_file_contains_point_exception(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Ensure exceptions during file reading return None.

    :param monkeypatch: Pytest monkeypatch fixture
    :type monkeypatch: pytest.MonkeyPatch
    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """

    def fake_read_file(path: Path) -> FakeGeoDataFrame:
        raise RuntimeError("boom")

    monkeypatch.setattr(geo.gpd, "read_file", fake_read_file)

    point: Point = Point(1.0, 1.0)

    result: Optional[str] = await geo.check_file_contains_point(
        "ZONE.geojson",
        tmp_path,
        point,
    )

    assert result is None


# ============================================================
# find_zone_async
# ============================================================


@pytest.mark.trio
async def test_find_zone_async_found(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Ensure first matching zone is returned.

    :param monkeypatch: Pytest monkeypatch fixture
    :type monkeypatch: pytest.MonkeyPatch
    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    files: list[str] = ["A.geojson", "B.geojson", "C.geojson"]

    monkeypatch.setattr(os, "listdir", lambda folder: files)

    async def fake_check(
        filename: str,
        folder: Path,
        point: Point,
    ) -> Optional[str]:
        if filename == "B.geojson":
            return "B"
        return None

    monkeypatch.setattr(geo, "check_file_contains_point", fake_check)

    result: Optional[str] = await geo.find_zone_async(
        lat=10.0,
        lon=20.0,
        geojson_folder=tmp_path,
    )

    assert result == "B"


@pytest.mark.trio
async def test_find_zone_async_not_found(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Ensure None is returned when no zone matches.

    :param monkeypatch: Pytest monkeypatch fixture
    :type monkeypatch: pytest.MonkeyPatch
    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    files: list[str] = ["A.geojson", "B.geojson"]

    monkeypatch.setattr(os, "listdir", lambda folder: files)

    async def fake_check(
        filename: str,
        folder: Path,
        point: Point,
    ) -> Optional[str]:
        return None

    monkeypatch.setattr(geo, "check_file_contains_point", fake_check)

    result: Optional[str] = await geo.find_zone_async(
        lat=0.0,
        lon=0.0,
        geojson_folder=tmp_path,
    )

    assert result is None


# ============================================================
# get_zone_code
# ============================================================


def test_get_zone_code(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Ensure get_zone_code returns expected zone.

    :param monkeypatch: Pytest monkeypatch fixture
    :type monkeypatch: pytest.MonkeyPatch
    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    monkeypatch.setattr(
        geo,
        "settings",
        SimpleNamespace(geojson_path=str(tmp_path)),
    )

    async def fake_find(
        lat: float,
        lon: float,
        folder: Path,
    ) -> Optional[str]:
        return "TEST_ZONE"

    monkeypatch.setattr(geo, "find_zone_async", fake_find)

    result: Optional[str] = geo.get_zone_code(1.0, 2.0)

    assert result == "TEST_ZONE"
