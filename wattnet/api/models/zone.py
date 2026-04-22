"""Data models for zones endpoints in the wattnet API application."""

from typing import List

from pydantic import BaseModel, Field
from typing_extensions import Literal

Provider = Literal["ENTSO-E", "Elexon", "EPIAS"]


class Zone(BaseModel):
    """Represents zone metadata enriched with electrical neighbours."""

    zone_id: str = Field(..., description="Zone area display name")
    full_name: str = Field(..., description="Full descriptive name of the zone")
    eic_code: str = Field(..., description="Energy Identification Code (EIC)")
    country_code: str = Field(..., description="ISO 3166-1 alpha-3 country code")
    country_name: str = Field(..., description="Country name")
    provider: Provider = Field(..., description="Normalized data provider")
    neighbours: List[str] = Field(
        ..., description="Connected cross-border zones for this zone"
    )
