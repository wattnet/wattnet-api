"""Data models for impact share endpoints in the wattnet API application."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from typing_extensions import Literal

ZoneStatus = Literal["complete", "preview", "missing"]
ImpactType = Literal["carbon", "water"]
ImpactScope = Literal["operational", "life-cycle"]
ImpactUnit = Literal["stress-gCO2eq/kWh", "stress-l/kWh"]


class ImpactShareBlock(BaseModel):
    """Represents impact share data for a specific origin zone."""

    source: str = Field(..., description="Origin zone contributing to the impact")
    values: List[tuple[datetime, float]] = Field(
        ..., description="Time series of impact values for this source"
    )


class ImpactShareSeries(BaseModel):
    """Represents a series of impact share data grouped by validity and zone status."""

    valid: bool = Field(..., description="Validity of the series for the zone")
    zone_status: ZoneStatus = Field(..., description="Zone status for this series")
    blocks: List[ImpactShareBlock] = Field(
        ..., description="List of origin zones contributing to the impact"
    )


class ImpactShare(BaseModel):
    """Represents impact share data for a specific destination zone."""

    zone: str = Field(..., description="Destination zone for the impact")
    impact_type: ImpactType = Field(..., description="Type of impact (carbon or water)")
    scope: ImpactScope = Field(
        ..., description="Scope of impact (operational or life-cycle)"
    )
    unit: ImpactUnit = Field(..., description="Unit of the impact value")
    series: List[ImpactShareSeries] = Field(
        ..., description="Series grouped by valid/zone_status"
    )
