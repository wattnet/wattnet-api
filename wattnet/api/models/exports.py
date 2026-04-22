"""Models for representing export data in the API responses."""

from datetime import datetime
from typing import List

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


class ExportBlock(BaseModel):
    """Represents export data for a specific destination zone."""

    destination: str = Field(..., description="Destination zone code")
    data_state: DataState = Field(..., description="official/estimated/missing")
    datasource: DataSource = Field(..., description="Data provider for this block")
    values: List[tuple[datetime, float]] = Field(
        ..., description="Time series of exported energy values"
    )


class ExportSeries(BaseModel):
    """Represents a series of export data for a zone.

    Represents a series of export data for a specific zone, including validity,
    zone status, and list of destination zones contributing to the exports.
    """

    valid: bool = Field(..., description="Validity of the series for the zone")
    zone_status: ZoneStatus = Field(..., description="Zone status for this series")
    exports: List[ExportBlock] = Field(
        ..., description="List of export blocks per destination"
    )


class Export(BaseModel):
    """Represents export data for a specific zone, including multiple series."""

    zone: str = Field(..., description="Origin zone code")
    unit: Unit = Field(..., description="Unit of energy (constant per zone)")
    series: List[ExportSeries] = Field(
        ..., description="Multiple series grouped by valid/zone_status"
    )
