"""Data models for mix share endpoints in the wattnet API application."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from typing_extensions import Literal

ZoneStatus = Literal["complete", "preview", "missing"]


class MixShareBlock(BaseModel):
    """Represents mix share data for a specific origin zone.

    Represents mix share data for a specific origin zone contributing to the mix
    of a destination zone, including time series of values.
    """

    origin: str = Field(..., description="Origin zone contributing to the mix")
    values: List[tuple[datetime, float]] = Field(
        ..., description="Time series of mix share values (%)"
    )


class MixShareSeries(BaseModel):
    """Represents a series of mix share data for a specific destination zone.

    Represents a series of mix share data for a specific destination zone,
    including validity, zone status, and list of origin zones contributing to
    the mix.
    """

    valid: bool = Field(..., description="Validity of the series for the zone")
    zone_status: ZoneStatus = Field(..., description="Zone status for this series")
    shares: List[MixShareBlock] = Field(
        ..., description="List of origin zones contributing to the mix"
    )


class MixShare(BaseModel):
    """Represents mix share data for a specific destination zone.

    Represents mix share data for a specific destination zone, including multiple
    series grouped by validity and zone status.
    """

    zone: str = Field(..., description="Destination zone where mix is measured")
    unit: Literal["%"] = Field("%", description="Unit of mix share (always %)")
    series: List[MixShareSeries] = Field(
        ..., description="Multiple series grouped by valid/zone_status"
    )
