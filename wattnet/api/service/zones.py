"""Service layer for handling zone metadata and neighbours."""

from pathlib import Path
from typing import Dict, List

import yaml

from wattnet.api.models.zone import Provider, Zone
from wattnet.api.utils import log

LOG = log.get(__name__)

_PROVIDER_MAP: Dict[str, Provider] = {
    "entsoe": "ENTSO-E",
    "elexon": "Elexon",
    "epias": "EPIAS",
}


class ZoneService:
    """Service to load and merge zone metadata with cross-border neighbours."""

    def __init__(
        self,
        zones_file_path: Path,
        crossborders_file_path: Path,
    ):
        """Initialize the ZoneService with mandatory YAML data files."""
        self.zones_file_path = zones_file_path
        self.crossborders_file_path = crossborders_file_path
        LOG.info(
            "Initialized ZoneService with zones file: %s and crossborders file: %s",
            zones_file_path,
            crossborders_file_path,
        )

    def get_zones(self) -> List[Zone]:
        """Return merged zones list including neighbours."""
        zones_raw = self._read_yaml_list(self.zones_file_path)
        crossborders_raw = self._read_yaml_list(self.crossborders_file_path)

        neighbours_by_zone: Dict[str, List[str]] = {}
        for item in crossborders_raw:
            zone_id = item["zone_id"]
            neighbours_by_zone[zone_id] = list(item.get("neighbours", []))

        zones: List[Zone] = []
        for item in zones_raw:
            zone_id = item["zone_id"]
            provider = self._normalize_provider(item["provider"])
            zones.append(
                Zone(
                    zone=zone_id,
                    full_name=item["full_name"],
                    eic_code=item["eic_code"],
                    country_code=item["country_code"],
                    country_name=item["country_name"],
                    provider=provider,
                    neighbours=neighbours_by_zone.get(zone_id, []),
                )
            )

        return sorted(zones, key=lambda x: x.zone)

    @staticmethod
    def _read_yaml_list(path: Path) -> List[dict]:
        """Read and validate a YAML file expected to contain a list."""
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, list):
            raise ValueError(f"YAML file must contain a list: {path}")

        return data

    @staticmethod
    def _normalize_provider(provider: str) -> Provider:
        """Normalize provider naming to API output conventions."""
        if provider not in _PROVIDER_MAP:
            raise ValueError(f"Unsupported provider '{provider}'")
        return _PROVIDER_MAP[provider]
