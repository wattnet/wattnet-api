"""API application for wattnet."""

from importlib.metadata import version

from wattnet.api.app import versioned_app as app

__version__ = version("wattnet-api")
__all__ = ["app", "__version__"]
