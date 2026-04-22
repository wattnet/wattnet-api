"""Settings management for the wattnet API application."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Determine the environment and load corresponding .env file
ENVIRONMENT = os.getenv("WATTNET_ENV", "development")
env_file = BASE_DIR / "config" / f".env.{ENVIRONMENT}"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Server Settings
    api_host: str = "localhost"
    api_port: int = 8000
    api_debug: bool = True

    # GeoJSON File Paths
    geojson_path: Path = BASE_DIR / "data" / "zones.geojson"

    # Zone YAML File Paths (required)
    zones_file_path: Path
    crossborders_file_path: Path

    # Logging Settings
    log_level: str = "INFO"
    log_handlers: list[str] = ["console"]  # Possible values: "console", "file"
    log_file: Path = BASE_DIR / "logs" / "wattnet-api.log"

    # Status Check Endpoint Settings
    storage_db_url: str = (
        "http://localhost:8123"  # URL for the wattnet-storage service (required)
    )
    entsoe_url: str = "https://web-api.tp.entsoe.eu/api"  # ENTSO-E API (required)
    elexon_url: str = "https://data.elexon.co.uk/bmrs/api/v1"  # ELEXON API (required)
    epias_url: str = (
        "https://seffaflik.epias.com.tr/electricity-service/v1"  # EPIAS API (required)
    )

    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Singleton instance of Settings
settings = Settings()
