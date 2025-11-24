from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field

ZoneStatus = Literal["complete", "preview", "missing"]


class MixShareBlock(BaseModel):
    origin: str = Field(..., description="Origin zone contributing to the mix")
    values: List[tuple[datetime, float]] = Field(
        ..., description="Time series of mix share values (%)"
    )


class MixShareSeries(BaseModel):
    valid: bool = Field(..., description="Validity of the series for the zone")
    zone_status: ZoneStatus = Field(..., description="Zone status for this series")
    shares: List[MixShareBlock] = Field(
        ..., description="List of origin zones contributing to the mix"
    )


class MixShare(BaseModel):
    zone: str = Field(..., description="Destination zone where mix is measured")
    unit: Literal["%"] = Field("%", description="Unit of mix share (always %)")
    series: List[MixShareSeries] = Field(
        ..., description="Multiple series grouped by valid/zone_status"
    )
