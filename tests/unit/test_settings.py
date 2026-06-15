"""Unit tests for wattnet.api.settings."""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Marker: skip existence tests when data is not available at the configured path
# ---------------------------------------------------------------------------


def _data_present() -> bool:
    try:
        from wattnet.api.settings import settings

        return settings.geojson_path.is_dir() and any(settings.geojson_path.iterdir())
    except Exception:
        return False


DATA_PRESENT = pytest.mark.skipif(
    not _data_present(),
    reason="data not available at settings.geojson_path (check env or git submodule)",
)


# ---------------------------------------------------------------------------
# BASE_DIR structural tests (no data required)
# ---------------------------------------------------------------------------


def test_base_dir_is_three_parents_above_settings() -> None:
    """Test that BASE_DIR is correctly set to the parent of the parent of the parent of settings.py."""
    from wattnet.api import settings as m

    settings_file = (
        Path(__file__).resolve().parents[2] / "wattnet" / "api" / "settings.py"
    )
    assert m.BASE_DIR == settings_file.parent.parent.parent


def test_base_dir_exists() -> None:
    """Test that BASE_DIR exists and is a directory."""
    from wattnet.api.settings import BASE_DIR

    assert BASE_DIR.is_dir(), f"BASE_DIR does not exist: {BASE_DIR}"


# ---------------------------------------------------------------------------
# Default field value tests — use model_fields, not the runtime singleton
# (the singleton may be overridden by .env files in development)
# ---------------------------------------------------------------------------


def test_default_paths_are_under_base_dir() -> None:
    """Test that default paths are under BASE_DIR, ensuring they are relative to the project root."""
    from wattnet.api.settings import BASE_DIR, Settings

    fields = Settings.model_fields
    base = str(BASE_DIR)
    assert str(fields["geojson_path"].default).startswith(base)
    assert str(fields["zones_file_path"].default).startswith(base)
    assert str(fields["crossborders_file_path"].default).startswith(base)


def test_default_geojson_path_shape() -> None:
    """Test that the default geojson_path is set to BASE_DIR / 'data' / 'geojson'."""
    from wattnet.api.settings import BASE_DIR, Settings

    default: Path = Settings.model_fields["geojson_path"].default
    assert default == BASE_DIR / "data" / "geojson"


def test_default_zones_file_path_shape() -> None:
    """Test that the default zones_file_path is set to correct path under BASE_DIR."""
    from wattnet.api.settings import BASE_DIR, Settings

    default: Path = Settings.model_fields["zones_file_path"].default
    assert default == BASE_DIR / "data" / "zones" / "entsoe_full_zones.yaml"


def test_default_crossborders_file_path_shape() -> None:
    """Test that the default crossborders_file_path is set to correct path under BASE_DIR."""
    from wattnet.api.settings import BASE_DIR, Settings

    default: Path = Settings.model_fields["crossborders_file_path"].default
    assert default == (
        BASE_DIR / "data" / "zones" / "entsoe_full_crossborders.yaml"
    )


def test_default_server_fields() -> None:
    """Test that default server fields are set to expected values."""
    from wattnet.api.settings import Settings

    fields = Settings.model_fields
    assert fields["host"].default == "0.0.0.0"
    assert fields["port"].default == 8000
    assert fields["debug"].default is False


def test_default_storage_fields() -> None:
    """Test that default storage fields are set to expected values."""
    from wattnet.api.settings import Settings

    fields = Settings.model_fields
    assert fields["timeseries_step_minutes"].default == 15
    assert fields["storage_clients"].default == ["clickhouse"]


# ---------------------------------------------------------------------------
# Existence tests — use the runtime singleton (respects env overrides)
# ---------------------------------------------------------------------------


@DATA_PRESENT
def test_geojson_path_exists() -> None:
    """Test that the geojson_path directory exists."""
    from wattnet.api.settings import settings

    assert (
        settings.geojson_path.is_dir()
    ), f"geojson_path does not exist: {settings.geojson_path}"


@DATA_PRESENT
def test_geojson_path_contains_geojson_files() -> None:
    """Test that the geojson_path directory contains at least one .geojson file."""
    from wattnet.api.settings import settings

    files = list(settings.geojson_path.glob("*.geojson"))
    assert files, f"No .geojson files found in {settings.geojson_path}"


@DATA_PRESENT
def test_zones_file_path_exists() -> None:
    """Test that the zones_file_path file exists."""
    from wattnet.api.settings import settings

    assert (
        settings.zones_file_path.is_file()
    ), f"zones_file_path does not exist: {settings.zones_file_path}"


@DATA_PRESENT
def test_crossborders_file_path_exists() -> None:
    """Test that the crossborders_file_path file exists."""
    from wattnet.api.settings import settings

    assert (
        settings.crossborders_file_path.is_file()
    ), f"crossborders_file_path does not exist: {settings.crossborders_file_path}"


# ---------------------------------------------------------------------------
# Environment-variable override tests (use WATTNET_API_ prefix)
# ---------------------------------------------------------------------------


def test_geojson_path_overridable_via_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test that geojson_path can be overridden via environment variable."""
    monkeypatch.setenv("WATTNET_API_GEOJSON_PATH", str(tmp_path))

    from wattnet.api.settings import Settings

    s = Settings()  # type: ignore[call-arg]
    assert s.geojson_path == tmp_path


def test_zones_file_path_overridable_via_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test that zones_file_path can be overridden via environment variable."""
    fake = tmp_path / "zones.yaml"
    monkeypatch.setenv("WATTNET_API_ZONES_FILE_PATH", str(fake))

    from wattnet.api.settings import Settings

    s = Settings()  # type: ignore[call-arg]
    assert s.zones_file_path == fake


def test_crossborders_file_path_overridable_via_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test that crossborders_file_path can be overridden via environment variable."""
    fake = tmp_path / "crossborders.yaml"
    monkeypatch.setenv("WATTNET_API_CROSSBORDERS_FILE_PATH", str(fake))

    from wattnet.api.settings import Settings

    s = Settings()  # type: ignore[call-arg]
    assert s.crossborders_file_path == fake


def test_timeseries_step_minutes_overridable_via_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that timeseries_step_minutes can be overridden via environment variable."""
    monkeypatch.setenv("WATTNET_API_TIMESERIES_STEP_MINUTES", "30")

    from wattnet.api.settings import Settings

    s = Settings()  # type: ignore[call-arg]
    assert s.timeseries_step_minutes == 30


def test_storage_clients_overridable_via_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that storage_clients can be overridden via environment variable."""
    monkeypatch.setenv("WATTNET_API_STORAGE_CLIENTS", '["clickhouse"]')

    from wattnet.api.settings import Settings

    s = Settings()  # type: ignore[call-arg]
    assert s.storage_clients == ["clickhouse"]
