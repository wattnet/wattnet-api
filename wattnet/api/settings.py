"""Settings management for wattnet-api."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from wattnet.storage.utils.plugin_loader import get_storage_clients_extensions

BASE_DIR = Path(__file__).resolve().parent.parent.parent

_ENV_FILES: list[str] = ["/etc/wattnet/api.env", ".env"]

plugin_settings: dict[str, BaseSettings] = {
    name: cls.config_class(_env_file=_ENV_FILES)
    for name, cls in get_storage_clients_extensions().items()
    if hasattr(cls, "config_class")
}


class Settings(BaseSettings):
    """Application settings for wattnet-api.

    Configuration sources (highest to lowest priority):
    1. Process environment variables (prefixed WATTNET_API_)
    2. /etc/wattnet/api.env  (production)
    3. .env at project root  (local development, gitignored)
    4. Defaults defined here
    """

    # Server
    host: str = "0.0.0.0"  # nosec B104
    port: int = 8000
    workers: int = 1
    debug: bool = False

    # GeoJSON
    geojson_path: Path = BASE_DIR / "data" / "geojson"

    # Zones (by default, use all ENTSO-E defined zones and crossborders)
    zones_file_path: Path = BASE_DIR / "data" / "zones" / "entsoe_full_zones.yaml"
    crossborders_file_path: Path = (
        BASE_DIR / "data" / "zones" / "entsoe_full_crossborders.yaml"
    )

    # Storage
    timeseries_step_minutes: int = 15
    storage_clients: list[str] = ["clickhouse"]

    # External services
    storage_db_url: str = "http://localhost:8123"
    entsoe_url: str = "https://web-api.tp.entsoe.eu/api"
    elexon_url: str = "https://data.elexon.co.uk/bmrs/api/v1"
    epias_url: str = "https://seffaflik.epias.com.tr/electricity-service/v1"

    # Logging
    log_level: str = "INFO"
    log_handlers: list[str] = ["console"]
    log_file: Path = BASE_DIR / "logs" / "wattnet-api.log"

    model_config = SettingsConfigDict(
        env_prefix="WATTNET_API_",
        env_file=["/etc/wattnet/api.env", ".env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
