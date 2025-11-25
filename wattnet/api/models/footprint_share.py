from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field

ZoneStatus = Literal["complete", "preview", "missing"]
FootprintType = Literal["carbon", "water"]
FootprintScope = Literal["operational", "life-cycle"]
FootprintUnit = Literal["gCO2/kWh", "l/kWh"]


class FootprintShareBlock(BaseModel):
    source: str = Field(..., description="Origin zone contributing to the footprint")
    values: List[tuple[datetime, float]] = Field(
        ..., description="Time series of footprint values for this source"
    )


class FootprintShareSeries(BaseModel):
    valid: bool = Field(..., description="Validity of the series for the zone")
    zone_status: ZoneStatus = Field(..., description="Zone status for this series")
    blocks: List[FootprintShareBlock] = Field(
        ..., description="List of origin zones contributing to the footprint"
    )


class FootprintShare(BaseModel):
    zone: str = Field(..., description="Destination zone for the footprint")
    footprint_type: FootprintType = Field(
        ..., description="Type of footprint (carbon or water)"
    )
    scope: FootprintScope = Field(
        ..., description="Scope of footprint (operational or life-cycle)"
    )
    unit: FootprintUnit = Field(..., description="Unit of the footprint value")
    series: List[FootprintShareSeries] = Field(
        ..., description="Series grouped by valid/zone_status"
    )
