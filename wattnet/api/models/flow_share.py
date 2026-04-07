"""Models for representing flow share data in the API responses."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from typing_extensions import Literal

ZoneStatus = Literal["complete", "preview", "missing"]


class FlowShareBlock(BaseModel):
    """Represents flow share data for a specific destination zone.

    Represents flow share data for a specific destination zone,
    including time series of values.
    """

    destination: str = Field(..., description="Destination zone code")
    values: List[tuple[datetime, float]] = Field(
        ..., description="Time series of flow share values (%)"
    )


class FlowShareSeries(BaseModel):
    """Represents a series of flow share data for a specific origin zone.

    Represents a series of flow share data for a specific origin zone,
    including validity, zone status, and list of destination zones
    contributing to the flow share.
    """

    valid: bool = Field(..., description="Validity of the series for the zone")
    zone_status: ZoneStatus = Field(..., description="Zone status for this series")
    flows: List[FlowShareBlock] = Field(
        ..., description="List of flow share blocks per destination"
    )


class FlowShare(BaseModel):
    """Represents flow share data for a specific origin zone.

    Represents flow share data for a specific origin zone, including multiple series
    grouped by validity and zone status.
    """

    zone: str = Field(..., description="Origin zone code")
    unit: Literal["%"] = Field("%", description="Unit of flow share (always %)")
    series: List[FlowShareSeries] = Field(
        ..., description="Multiple series grouped by valid/zone_status"
    )
