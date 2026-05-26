"""Router for status endpoints to check health of storage and external APIs."""

import requests
from fastapi import APIRouter
from fastapi_versioning import version

from wattnet.api.settings import settings
from wattnet.api.utils import log

LOG = log.get(__name__)

router = APIRouter()


def check_storage_system() -> bool:
    """Check if the storage system is reachable.

    :return: True if the storage system is reachable, False otherwise
    :rtype: bool
    """
    storage_url = settings.storage_db_url
    LOG.debug(f"Storage URL: {storage_url}")
    if not storage_url:
        LOG.error("Storage system URL missing in config")
        return False
    try:
        requests.get(storage_url, timeout=5)
        return True
    except requests.RequestException as e:
        LOG.error(f"Storage system check failed: {e}")
        return False


def check_entsoe_api() -> bool:
    """Check if the ENTSOE API is reachable.

    :return: True if the ENTSOE API is reachable, False otherwise
    :rtype: bool
    """
    entsoe_url = settings.entsoe_url
    if not entsoe_url:
        LOG.error("ENTSOE API URL missing in config")
        return False
    try:
        requests.get(entsoe_url, timeout=5)
        return True  # If the request succeeds, we assume the API is reachable
    except requests.RequestException as e:
        LOG.error(f"ENTSOE API check failed: {e}")
        return False


def check_elexon_api() -> bool:
    """Check if the Elexon API is reachable.

    :return: True if the Elexon API is reachable, False otherwise
    :rtype: bool
    """
    elexon_url = settings.elexon_url
    if not elexon_url:
        LOG.error("Elexon API URL missing in config")
        return False
    try:
        requests.get(elexon_url, timeout=5)
        return True  # If the request succeeds, we assume the API is reachable
    except requests.RequestException as e:
        LOG.error(f"Elexon API check failed: {e}")
        return False


def check_epias_api() -> bool:
    """Check if the EPIAS API is reachable.

    :return: True if the EPIAS API is reachable, False otherwise
    :rtype: bool
    """
    epias_url = settings.epias_url
    if not epias_url:
        LOG.error("EPIAS API URL missing in config")
        return False
    try:
        requests.get(epias_url, timeout=5)
        return True  # If the request succeeds, we assume the API is reachable
    except requests.RequestException as e:
        LOG.error(f"EPIAS API check failed: {e}")
        return False


def check_storage() -> str:
    """Check the health of the storage system.

    :return: "up" if the storage system is healthy, "down" otherwise
    :rtype: str
    """
    try:
        if not check_storage_system():
            raise RuntimeError("Storage system is down")
        return "up"
    except RuntimeError:
        return "down"


def check_entsoe() -> str:
    """Check the health of the ENTSOE API.

    :return: "up" if the ENTSOE API is healthy, "down" otherwise
    :rtype: str
    """
    try:
        if not check_entsoe_api():
            raise RuntimeError("ENTSOE API is down")
        return "up"
    except RuntimeError:
        return "down"


def check_elexon() -> str:
    """Check the health of the Elexon API.

    :return: "up" if the Elexon API is healthy, "down" otherwise
    :rtype: str
    """
    try:
        if not check_elexon_api():
            raise RuntimeError("Elexon API is down")
        return "up"
    except RuntimeError:
        return "down"


def check_epias() -> str:
    """Check the health of the EPIAS API.

    :return: "up" if the EPIAS API is healthy, "down" otherwise
    :rtype: str
    """
    try:
        if not check_epias_api():
            raise RuntimeError("EPIAS API is down")
        return "up"
    except RuntimeError:
        return "down"


@router.get("")
@version(1)
async def status() -> dict:
    """Check the health of the storage system and external APIs.

    :return: Dictionary with the status of storage, ENTSOE API, and Elexon API
    :rtype: dict
    """
    return {
        "storage": check_storage(),
        "entso-e": check_entsoe(),
        "elexon": check_elexon(),
        "epias": check_epias(),
    }


@router.get("/storage")
@version(1)
async def status_storage() -> dict:
    """Check the health of the storage system.

    :return: Dictionary with the status of the storage system
    :rtype: dict
    """
    return {"storage": check_storage()}


@router.get("/entso-e")
@version(1)
async def status_entsoe() -> dict:
    """Check the health of the ENTSOE API.

    :return: Dictionary with the status of the ENTSOE API
    :rtype: dict
    """
    return {"entso-e": check_entsoe()}


@router.get("/elexon")
@version(1)
async def status_elexon() -> dict:
    """Check the health of the Elexon API.

    :return: Dictionary with the status of the Elexon API
    :rtype: dict
    """
    return {"elexon": check_elexon()}


@router.get("/epias")
@version(1)
async def status_epias() -> dict:
    """Check the health of the EPIAS API.

    :return: Dictionary with the status of the EPIAS API
    :rtype: dict
    """
    return {"epias": check_epias()}
