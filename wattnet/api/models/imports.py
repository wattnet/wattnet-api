"""Data models for import endpoints in the wattnet API application."""

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


class ImportBlock(BaseModel):
    """Represents import data for a specific source zone.

    Represents import data for a specific source zone contributing to the imports
    of a destination zone, including time series of values.
    """

    source: str = Field(..., description="Origin zone of the import")
    data_state: DataState = Field(..., description="official/estimated/missing")
    datasource: DataSource = Field(..., description="Data provider for this block")
    values: List[tuple[datetime, float]] = Field(
        ..., description="Time series of imported energy values"
    )


class ImportSeries(BaseModel):
    """Represents a series of import data for a specific destination zone.

    Represents a series of import data for a specific destination zone,
    including validity, zone status, and list of source zones
    contributing to the imports.
    """

    valid: bool = Field(..., description="Validity of this series for the zone")
    zone_status: ZoneStatus = Field(..., description="Zone status for this series")
    imports: List[ImportBlock] = Field(
        ..., description="List of import blocks for different sources"
    )


class Import(BaseModel):
    """Represents import data for a specific destination zone.

    Represents import data for a specific destination zone, including multiple
    series grouped by validity and zone status.
    """

    zone: str = Field(..., description="Wattnet zone code")
    unit: Unit = Field(..., description="Unit of energy (constant per zone)")
    series: List[ImportSeries] = Field(
        ..., description="Multiple series grouped by valid/zone_status"
    )
