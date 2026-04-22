"""Data models for load endpoints in the wattnet API application."""

from datetime import datetime
from typing import List, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal, Union

HybridEstimationSource = Annotated[
    str, Field(pattern=r"^wattnet-hybrid-estimation:.*$")
]

DataState = Literal["official", "estimated", "missing"]
ZoneStatus = Literal["complete", "preview", "missing"]
DataSource = Union[
    Literal["ENTSO-E", "Elexon", "EPIAS"],
    HybridEstimationSource,
]
Unit = Literal["MW"]


class LoadSeries(BaseModel):
    """Represents a series of load data for a specific zone.

    Groups load values by validity and zone status, analogous to
    GenerationSeries but without production type breakdown.
    """

    valid: bool = Field(..., description="Validity of this version of zone data")
    zone_status: ZoneStatus = Field(..., description="Status of the zone data")
    blocks: List["LoadBlock"] = Field(..., description="Load blocks grouped by source")


class LoadBlock(BaseModel):
    """Represents load data for a specific state/source combination."""

    data_state: DataState = Field(..., description="official/estimated/missing")
    datasource: DataSource = Field(..., description="Data provider for this block")
    values: List[Tuple[datetime, float]] = Field(
        ..., description="Time series: (timestamp, load_value)"
    )


class Load(BaseModel):
    """Represents total electricity demand data for a specific zone."""

    zone: str = Field(..., description="wattnet zone code")
    unit: Unit = Field(..., description="Energy unit (fixed per zone)")
    series: List[LoadSeries] = Field(
        ..., description="Multiple versions of the zone data grouped by status"
    )
