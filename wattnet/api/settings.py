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

    # Storage Database Settings
    storage_db_url: str = "http://localhost:8428"
    timeseries_step_minutes: int = 15  # minutes between data points

    # GeoJSON File Paths
    geojson_path: Path  # Path to GeoJSON file (required)

    # Logging Settings
    log_level: str = "INFO"
    log_handlers: list[str] = ["console"]  # Possible values: "console", "file"
    log_file: Path = BASE_DIR / "logs" / "wattnet-api.log"

    # ENTSOE API Settings
    entsoe_api_key: str  # ENTSOE API key (required)
    entsoe_base_url: str = "https://web-api.tp.entsoe.eu/api"

    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Singleton instance of Settings
settings = Settings()
