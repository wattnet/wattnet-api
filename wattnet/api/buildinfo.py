"""The version of the service, for the documentation and for the MCP server."""

import os
import re
from importlib.metadata import version as package_version


def build_version() -> str:
    """Return the version that the documentation shows.

    A snapshot image is built with the commit in ``BUILD_COMMIT`` and shows it; a
    release has none and shows the version of the package.

    :return: the commit when ``BUILD_COMMIT`` is a hexadecimal id, else the version
    """
    commit = os.environ.get("BUILD_COMMIT", "")
    if re.fullmatch(r"[0-9a-f]{7,40}", commit):
        return commit
    return package_version("wattnet-api")
