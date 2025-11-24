from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field

ZoneStatus = Literal["complete", "preview", "missing"]


class FlowShareBlock(BaseModel):
    destination: str = Field(..., description="Destination zone code")
    values: List[tuple[datetime, float]] = Field(
        ..., description="Time series of flow share values (%)"
    )


class FlowShareSeries(BaseModel):
    valid: bool = Field(..., description="Validity of the series for the zone")
    zone_status: ZoneStatus = Field(..., description="Zone status for this series")
    flows: List[FlowShareBlock] = Field(
        ..., description="List of flow share blocks per destination"
    )


class FlowShare(BaseModel):
    zone: str = Field(..., description="Origin zone code")
    unit: Literal["%"] = Field("%", description="Unit of flow share (always %)")
    series: List[FlowShareSeries] = Field(
        ..., description="Multiple series grouped by valid/zone_status"
    )
