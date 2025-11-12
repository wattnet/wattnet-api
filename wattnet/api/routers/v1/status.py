from datetime import datetime

import requests
from fastapi import APIRouter
from fastapi_versioning import version
from prometheus_api_client import PrometheusConnect

from wattnet.api.settings import settings
from wattnet.api.utils import log

# Get logger
LOG = log.get(__name__)

# Create API router
router = APIRouter()


# Helper function to check if ENTSOE API is available
def check_entsoe_api() -> bool:
    """Check if ENTSOE API is available"""

    # Get ENTSOE API URL
    entsoe_api_url = settings.entsoe_base_url
    print(f"ENTSOE API URL: {entsoe_api_url}")
    # Get ENTSOE API token
    entsoe_api_key = settings.entsoe_api_key
    print(f"ENTSOE API Key: {entsoe_api_key}")

    # Check if ENTSOE API URL and key are present
    if not entsoe_api_url or not entsoe_api_key:
        LOG.error("Missing ENTSOE API URL or API Key")
        return False

    # Get the current time in the required format for the 'interval' parameter
    # For example, 'interval' could be the current date in 'YYYY-MM-DD' format
    now = datetime.now()
    now1h = now.replace(hour=now.hour - 1, minute=0, second=0, microsecond=0)
    periodStart = now1h.strftime("%Y%m%d%H%M")
    periodEnd = now.strftime("%Y%m%d%H%M")
    documenType = "A73"
    processType = "A16"
    in_Domain = "10YBE----------2"

    try:

        # Perform the GET request with interval
        response = requests.get(
            entsoe_api_url,
            params={
                "securityToken": entsoe_api_key,
                "periodStart": periodStart,
                "periodEnd": periodEnd,
                "documentType": documenType,
                "processType": processType,
                "in_Domain": in_Domain,
            },
            timeout=5,
        )

        # Check if the response is OK
        if response.status_code == 200:
            LOG.info("ENTSOE API is available")
            return True
        else:
            LOG.error(
                f"ENTSOE API returned an error: {response.status_code} - {response.text}"
            )
            return False

    except requests.RequestException as e:
        # Catch network errors, timeouts, etc.
        LOG.error(f"Error checking ENTSOE API: {e}")
        return False


# Helper function to check if wattnet storage system is available
def check_storage_system() -> bool:
    """Check if the storage system is available"""

    # Get the storage URL
    storage_db_url = settings.storage_db_url
    LOG.debug(f"Storage URL: {storage_db_url}")

    # Initialize the storage connection
    storage = PrometheusConnect(
        url=storage_db_url,
        disable_ssl=True,
    )

    try:
        # Check if the storage is reachable
        storage.custom_query(query="up")
        LOG.info("Storage connection is healthy.")
        return True
    except Exception as e:
        LOG.error(f"Storage connection failed: {e}")
        return False


# Service status endpoint
@router.get("")
@version(1)
def get_status():
    """Get status"""
    status = {
        "entsoe": "ok" if check_entsoe_api() else "error",
        "storage": "ok" if check_storage_system() else "error",
    }

    return status


# ENTSOE API status endpoint
@router.get("/entsoe")
@version(1)
def get_entsoe_status():
    """Get ENTSOE API status"""
    if check_entsoe_api():
        return {"status": "ok", "message": "ENTSOE API is available"}
    else:
        return {"status": "error", "message": "ENTSOE API is not available"}


# Storage system status endpoint
@router.get("/storage")
@version(1)
def get_storage_status():
    """Get storage system status"""
    if check_storage_system():
        return {"status": "ok", "message": "wattnet storage system is available"}
    else:
        return {
            "status": "error",
            "message": "wattnet storage system is not available",
        }
