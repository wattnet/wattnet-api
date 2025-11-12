import os

import geopandas as gpd
import trio
from shapely.geometry import Point

from wattnet.api.settings import settings
from wattnet.api.utils import log

# Get logger
LOG = log.get(__name__)


async def check_file_contains_point(filename, folder, point):
    if not filename.endswith(".geojson"):
        return None
    path = os.path.join(folder, filename)
    try:

        def read_and_check():
            gdf = gpd.read_file(path)
            if gdf.contains(point).any():
                return os.path.splitext(filename)[0]
            return None

        return await trio.to_thread.run_sync(read_and_check)
    except Exception as e:
        LOG.error(f"Error reading {filename}: {e}")
        return None


async def find_zone_async(lat, lon, geojson_folder):
    point = Point(lon, lat)
    filenames = os.listdir(geojson_folder)
    semaphore = trio.Semaphore(10)  # Cap concurrency
    result_holder = {"zone": None}

    async with trio.open_nursery() as nursery:

        async def worker(f):
            async with semaphore:
                result = await check_file_contains_point(f, geojson_folder, point)
                if result and result_holder["zone"] is None:
                    result_holder["zone"] = result
                    nursery.cancel_scope.cancel()

        for filename in filenames:
            nursery.start_soon(worker, filename)

    return result_holder["zone"]


def get_zone_code(lat: float, lon: float) -> str | None:
    """Return the zone code (filename without extension) that contains the coordinate."""
    # Get folder path from configuration
    geojson_folder = settings.geojson_path
    zone_code = trio.run(find_zone_async, lat, lon, geojson_folder)
    LOG.debug(f"Zone code for ({lat}, {lon}): {zone_code}")
    return zone_code
