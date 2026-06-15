import logging
from unittest.mock import patch

import pytest

from wattnet.api.utils.log import CustomFormatter, _get_level, get, setup_logging


@pytest.fixture(autouse=True)
def reset_wattnet_logger():
    """Remove all handlers from 'wattnet' logger between tests."""
    logger = logging.getLogger("wattnet")
    yield
    logger.handlers.clear()
    logger.propagate = True


class TestGetLevel:
    def test_debug(self):
        assert _get_level("debug") == logging.DEBUG

    def test_info(self):
        assert _get_level("info") == logging.INFO

    def test_warning(self):
        assert _get_level("warning") == logging.WARNING

    def test_error(self):
        assert _get_level("error") == logging.ERROR

    def test_critical(self):
        assert _get_level("critical") == logging.CRITICAL

    def test_uppercase_input(self):
        assert _get_level("DEBUG") == logging.DEBUG

    def test_mixed_case_input(self):
        assert _get_level("Warning") == logging.WARNING

    def test_invalid_string_returns_info(self):
        assert _get_level("not_a_level") == logging.INFO

    def test_empty_string_returns_info(self):
        assert _get_level("") == logging.INFO


class TestCustomFormatter:
    def _record(self, level=logging.INFO, msg="hello"):
        return logging.LogRecord(
            name="test", level=level, pathname="", lineno=0,
            msg=msg, args=(), exc_info=None,
        )

    def test_format_returns_string(self):
        result = CustomFormatter("%(message)s").format(self._record())
        assert isinstance(result, str)

    def test_format_contains_message(self):
        result = CustomFormatter("%(message)s").format(self._record(msg="hello world"))
        assert "hello world" in result

    def test_format_contains_ansi_color(self):
        result = CustomFormatter("%(message)s").format(self._record(level=logging.DEBUG))
        assert "\x1b[" in result

    def test_format_contains_reset(self):
        result = CustomFormatter("%(message)s").format(self._record())
        assert "\x1b[0m" in result

    def test_debug_and_error_have_different_colors(self):
        fmt = CustomFormatter("%(message)s")
        debug = fmt.format(self._record(level=logging.DEBUG))
        error = fmt.format(self._record(level=logging.ERROR))
        assert debug != error

    def test_all_standard_levels_produce_colored_output(self):
        fmt = CustomFormatter("%(levelname)s")
        for level in (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL):
            result = fmt.format(self._record(level=level))
            assert "\x1b[" in result, f"No ANSI code for level {level}"


class TestGet:
    def test_returns_logger_instance(self):
        assert isinstance(get("test.logger"), logging.Logger)

    def test_logger_name_matches(self):
        assert get("my.module.name").name == "my.module.name"

    def test_get_triggers_setup_logging(self):
        with patch("wattnet.api.utils.log.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_handlers = ["console"]
            mock_settings.log_file = None
            get("some.module")
        assert logging.getLogger("wattnet").handlers


class TestSetupLogging:
    def test_configures_wattnet_logger(self):
        with patch("wattnet.api.utils.log.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_handlers = ["console"]
            mock_settings.log_file = None
            setup_logging()
        assert logging.getLogger("wattnet").handlers

    def test_console_handler_added(self):
        with patch("wattnet.api.utils.log.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_handlers = ["console"]
            mock_settings.log_file = None
            setup_logging()
        handler_types = [type(h) for h in logging.getLogger("wattnet").handlers]
        assert logging.StreamHandler in handler_types

    def test_no_file_handler_without_file_setting(self):
        with patch("wattnet.api.utils.log.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_handlers = ["console", "file"]
            mock_settings.log_file = None
            setup_logging()
        handler_types = [type(h) for h in logging.getLogger("wattnet").handlers]
        assert logging.FileHandler not in handler_types

    def test_propagate_disabled(self):
        with patch("wattnet.api.utils.log.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_handlers = ["console"]
            mock_settings.log_file = None
            setup_logging()
        assert logging.getLogger("wattnet").propagate is False

    def test_idempotent(self):
        with patch("wattnet.api.utils.log.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_handlers = ["console"]
            mock_settings.log_file = None
            setup_logging()
            setup_logging()
        assert len(logging.getLogger("wattnet").handlers) == 1

    def test_storage_loggers_reach_wattnet_handler(self):
        records = []

        class CapturingHandler(logging.Handler):
            def emit(self, record):
                records.append(record)

        wattnet_logger = logging.getLogger("wattnet")
        wattnet_logger.setLevel(logging.DEBUG)
        wattnet_logger.propagate = False
        wattnet_logger.addHandler(CapturingHandler())

        logging.getLogger("wattnet.storage.clients.manager").info("from storage")
        assert any("from storage" in r.getMessage() for r in records)
