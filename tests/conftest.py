"""
Shared pytest configuration for the wattnet-api test suite.

Patches the ClickHouse storage manager initialisation so that unit tests can
import any wattnet.api.* module without requiring a live ClickHouse instance.
The patch is installed in pytest_configure, which runs before test collection,
so the mock is in place when test files (and their imports) are first loaded.
"""

from __future__ import annotations

from unittest.mock import patch


def pytest_configure(config: object) -> None:
    """Prevent ClickHouse connection attempts during module import.

    :param config: pytest config object (unused)
    :return: None
    :rtype: None
    """
    patch(
        "wattnet.storage.clients.manager.StorageClientsManager.__init__",
        return_value=None,
    ).start()
