"""Logging utilities for wattnet API."""

import logging

from wattnet.api.settings import settings


class CustomFormatter(logging.Formatter):
    """Custom colorized formatter for console output."""

    COLORS = {
        logging.DEBUG: "\x1b[38;5;10m",  # green
        logging.INFO: "\x1b[38;5;39m",  # blue
        logging.WARNING: "\x1b[38;5;226m",  # yellow
        logging.ERROR: "\x1b[31;1m",  # bold red
        logging.CRITICAL: "\x1b[38;5;196m",  # red
    }
    RESET = "\x1b[0m"

    def __init__(self, fmt: str):
        """Initialize the formatter with a format string.

        :param fmt: Log message format string
        :type fmt: str
        (e.g., "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        """
        super().__init__()
        self.fmt = fmt

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with color based on the log level.

        :param record: Log record to format
        :type record: logging.LogRecord

        :return: Formatted log message with color
        :rtype: str
        """
        color = self.COLORS.get(record.levelno, self.RESET)
        formatter = logging.Formatter(
            color + self.fmt + self.RESET, datefmt="%d-%m-%Y %H:%M:%S"
        )
        return formatter.format(record)


def _get_level(level: str) -> int:
    """Return a logging level constant from string.

    :param level: Log level as a string
    (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    :type level: str

    :return: Corresponding logging level constant (e.g., logging.DEBUG)
    :rtype: int
    """
    return getattr(logging, level.upper(), logging.INFO)


def setup_logging() -> None:
    """Configure logging once for all wattnet.* loggers (api + storage).

    Must be called once at application startup before any loggers are used.
    Configures the ``wattnet`` namespace logger so that both
    ``wattnet.api.*`` and ``wattnet.storage.*`` loggers write to the same
    handlers (console and/or file) as defined in settings.

    Idempotent: repeated calls are no-ops.
    """
    wattnet_logger = logging.getLogger("wattnet")

    if wattnet_logger.handlers:
        return

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    level = _get_level(getattr(settings, "log_level", "INFO"))
    handlers = getattr(settings, "log_handlers", ["console"])

    wattnet_logger.setLevel(level)
    # Prevent double-logging: wattnet.* logs are handled here
    # not by uvicorn's root handler.
    wattnet_logger.propagate = False

    if "console" in handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(CustomFormatter(fmt))
        wattnet_logger.addHandler(console_handler)

    if "file" in handlers and getattr(settings, "log_file", None):
        log_file = settings.log_file
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(fmt, datefmt="%d-%m-%Y %H:%M:%S"))
        wattnet_logger.addHandler(file_handler)


def get(name: str) -> logging.Logger:
    """Return a logger for the given name.

    Calls :func:`setup_logging` on first use so that any module importing
    this function before ``app.py`` runs still gets a configured logger.

    :param name: Name of the logger (e.g., module or component name)
    :type name: str

    :return: Logger instance
    :rtype: logging.Logger
    """
    setup_logging()
    return logging.getLogger(name)
