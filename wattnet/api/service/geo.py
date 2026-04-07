"""Geospatial utilities for the wattnet API application."""

import os
from pathlib import Path
from typing import Optional

import geopandas as gpd
import trio
from shapely.geometry import Point

from wattnet.api.settings import settings
from wattnet.api.utils import log

# Get logger
LOG = log.get(__name__)


async def check_file_contains_point(
    filename: str, folder: Path, point: Point
) -> Optional[str]:
    """Check if the GeoJSON file contains the given point.

    :param filename: Name of the GeoJSON file to check
    :type filename: str

    :param folder: Path to the folder containing the GeoJSON files
    :type folder: str

    :param point: Shapely Point object representing the coordinate to check
    :type point: Point

    :return: Zone code (filename without extension) if the point is contained, else None
    :rtype: str | None
    """
    if not filename.endswith(".geojson"):
        return None
    path = folder / filename
    try:

        def read_and_check() -> Optional[str]:
            gdf = gpd.read_file(path)
            if gdf.contains(point).any():
                return filename.rsplit(".", 1)[0]
            return None

        return await trio.to_thread.run_sync(read_and_check)
    except Exception as e:
        LOG.error(f"Error reading {filename}: {e}")
        return None


async def find_zone_async(
    lat: float, lon: float, geojson_folder: Path
) -> Optional[str]:
    """Find the zone code for the given lat and lon by checking GeoJSON files.

    :param lat: Latitude in decimal degrees (DD)
    :type lat: float

    :param lon: Longitude in decimal degrees (DD)
    :type lon: float

    :param geojson_folder: Path to the folder containing the GeoJSON files
    :type geojson_folder: str

    :return: Zone code if a containing zone is found, else None
    :rtype: str | None
    """
    point = Point(lon, lat)
    filenames = os.listdir(geojson_folder)
    semaphore = trio.Semaphore(10)  # Cap concurrency
    result_holder: dict[str, Optional[str]] = {"zone": None}

    async with trio.open_nursery() as nursery:

        async def worker(f: str) -> None:
            async with semaphore:
                result = await check_file_contains_point(f, geojson_folder, point)
                if result and result_holder["zone"] is None:
                    result_holder["zone"] = result
                    nursery.cancel_scope.cancel()

        for filename in filenames:
            nursery.start_soon(worker, filename)

    return result_holder["zone"]


def get_zone_code(lat: float, lon: float) -> Optional[str]:
    """Get the zone code for the given latitude and longitude.

    :param lat: Latitude in decimal degrees (DD)
    :type lat: float

    :param lon: Longitude in decimal degrees (DD)
    :type lon: float

    :return: Zone code if a containing zone is found, else None
    :rtype: str | None
    """
    geojson_folder = Path(settings.geojson_path)  # <- Path en vez de str
    zone_code = trio.run(find_zone_async, lat, lon, geojson_folder)
    LOG.debug(f"Zone code for ({lat}, {lon}): {zone_code}")
    return zone_code
