import requests
from fastapi import APIRouter
from fastapi_versioning import version

from wattnet.api.settings import settings
from wattnet.api.utils import log

LOG = log.get(__name__)

router = APIRouter()


def check_storage_system() -> bool:
    storage_url = settings.storage_db_url
    LOG.debug(f"Storage URL: {storage_url}")
    if not storage_url:
        LOG.error("Storage system URL missing in config")
        return False
    try:
        r = requests.get(storage_url, timeout=5)
        return r.status_code == 200
    except requests.RequestException as e:
        LOG.error(f"Storage system check failed: {e}")
        return False


def check_entsoe_api() -> bool:
    entsoe_url = settings.entsoe_url
    if not entsoe_url:
        LOG.error("ENTSOE API URL missing in config")
        return False
    try:
        r = requests.get(entsoe_url, timeout=5)
        print(r.status_code)
        return True  # If the request succeeds, we assume the API is reachable
    except requests.RequestException as e:
        LOG.error(f"ENTSOE API check failed: {e}")
        return False


def check_elexon_api() -> bool:
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


def check_storage():
    try:
        if not check_storage_system():
            raise Exception("Storage system is down")
        return "up"
    except Exception:
        return "down"


def check_entsoe():
    try:
        if not check_entsoe_api():
            raise Exception("ENTSOE API is down")
        return "up"
    except Exception:
        return "down"


def check_elexon():
    try:
        if not check_elexon_api():
            raise Exception("Elexon API is down")
        return "up"
    except Exception:
        return "down"


@router.get("/status")
@version(1)
async def status():
    return {
        "storage": check_storage(),
        "entso-e": check_entsoe(),
        "elexon": check_elexon(),
    }


@router.get("/status/storage")
@version(1)
async def status_storage():
    return {"storage": check_storage()}


@router.get("/status/entso-e")
@version(1)
async def status_entsoe():
    return {"entso-e": check_entsoe()}


@router.get("/status/elexon")
@version(1)
async def status_elexon():
    return {"elexon": check_elexon()}
