"""Data models for generation endpoints in the wattnet API application."""

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
ProductionType = Literal[
    "biomass",
    "coal",
    "gas",
    "geothermal",
    "marine",
    "hydro_reservoir",
    "hydro_river",
    "hydro_pumped_storage",
    "nuclear",
    "oil",
    "other",
    "other_renewable",
    "solar",
    "waste",
    "wind_offshore",
    "wind_onshore",
]
Unit = Literal["MW"]


class ProductionBlock(BaseModel):
    """Represents generation data for a specific production type.

    Represents generation data for a specific production type,
    including time series of values.
    """

    production_type: ProductionType = Field(..., description="Energy source type")
    data_state: DataState = Field(..., description="official/estimated/missing")
    datasource: DataSource = Field(..., description="Data provider for this block")

    values: List[Tuple[datetime, float]] = Field(
        ..., description="Time series: (timestamp, generation_value)"
    )


class GenerationSeries(BaseModel):
    """Represents a series of generation data for a specific zone.

    Represents a series of generation data for a specific zone, including validity,
    zone status, and list of production blocks grouped by production type.
    """

    valid: bool = Field(..., description="Validity of this version of zone data")
    zone_status: ZoneStatus = Field(..., description="Status of the zone data")

    production: List[ProductionBlock] = Field(
        ..., description="Generation blocks grouped by production type"
    )


class Generation(BaseModel):
    """Represents generation data for a specific zone.

    Represents generation data for a specific zone, including multiple series
    grouped by validity and zone status.
    """

    zone: str = Field(..., description="wattnet zone code")
    unit: Unit = Field(..., description="Energy unit (fixed per zone)")

    series: List[GenerationSeries] = Field(
        ..., description="Multiple versions of the zone data grouped by status"
    )
