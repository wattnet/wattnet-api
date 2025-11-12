from typing import List, Optional


class ZoneService:
    """Service to query zones from the metrics storage."""

    def __init__(self, storage):
        self.storage = storage

    def get_zones(self, zone_id: Optional[int] = None) -> List[dict]:
        """Get all zones or a specific zone by ID."""
        if zone_id:
            return self.storage.get_zone(zone_id)
        return self.storage.get_zones()

    def get_zone(self, zone_id: int) -> dict:
        """Get a zone by ID."""
        return self.storage.get_zone(zone_id)
