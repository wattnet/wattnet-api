"""Router for status endpoints to check health of storage and external APIs."""

import time
from collections.abc import Callable

import requests
from fastapi import APIRouter
from fastapi_versioning import version

from wattnet.api.dependencies import metrics_repo
from wattnet.api.settings import settings
from wattnet.api.utils import log

LOG = log.get(__name__)

router = APIRouter()

# The status endpoints are public and each call reaches a third party (ENTSO-E, Elexon,
# EPIAS), so the answer of a provider is kept for a few seconds.
# shortcut: not thread-safe, two calls at once may both ask the provider; fine here.
_CACHE_SECONDS = 30
_states: list[dict] = []


def _cached(check: Callable[[], bool]) -> Callable[[], bool]:
    """Return ``check`` remembering its answer for ``_CACHE_SECONDS`` seconds."""
    state = {"at": float("-inf"), "value": False}
    _states.append(state)

    def cached() -> bool:
        now = time.monotonic()
        if now - state["at"] >= _CACHE_SECONDS:
            state["value"], state["at"] = check(), now
        return bool(state["value"])

    cached.__name__ = check.__name__
    cached.__doc__ = check.__doc__
    return cached


def clear_cache() -> None:
    """Forget the remembered answers of the providers (for the tests)."""
    for state in _states:
        state["at"] = float("-inf")


def check_storage_system() -> bool:
    """Check if the storage system answers, through the connection the queries use.

    :return: True if the storage system answers, False otherwise
    :rtype: bool
    """
    try:
        return bool(metrics_repo.ping())
    except Exception as e:  # the check must never break the status endpoints
        LOG.error(f"Storage system check failed: {e}")
        return False


@_cached
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
        requests.get(entsoe_url, timeout=settings.external_timeout_seconds)
        return True  # If the request succeeds, we assume the API is reachable
    except requests.RequestException as e:
        LOG.error(f"ENTSOE API check failed: {e}")
        return False


@_cached
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
        requests.get(elexon_url, timeout=settings.external_timeout_seconds)
        return True  # If the request succeeds, we assume the API is reachable
    except requests.RequestException as e:
        LOG.error(f"Elexon API check failed: {e}")
        return False


@_cached
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
        requests.get(epias_url, timeout=settings.external_timeout_seconds)
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
def status() -> dict:
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
def status_storage() -> dict:
    """Check the health of the storage system.

    :return: Dictionary with the status of the storage system
    :rtype: dict
    """
    return {"storage": check_storage()}


@router.get("/entso-e")
@version(1)
def status_entsoe() -> dict:
    """Check the health of the ENTSOE API.

    :return: Dictionary with the status of the ENTSOE API
    :rtype: dict
    """
    return {"entso-e": check_entsoe()}


@router.get("/elexon")
@version(1)
def status_elexon() -> dict:
    """Check the health of the Elexon API.

    :return: Dictionary with the status of the Elexon API
    :rtype: dict
    """
    return {"elexon": check_elexon()}


@router.get("/epias")
@version(1)
def status_epias() -> dict:
    """Check the health of the EPIAS API.

    :return: Dictionary with the status of the EPIAS API
    :rtype: dict
    """
    return {"epias": check_epias()}
