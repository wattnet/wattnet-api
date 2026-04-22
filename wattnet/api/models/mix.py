"""Data models for mix endpoints in the wattnet API application."""

from datetime import datetime
from typing import List, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Literal

DataState = Literal["official", "estimated", "missing"]
ZoneStatus = Literal["complete", "preview", "missing"]
DataSource = Literal["flow_tracing"]
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


class MixBlock(BaseModel):
    """Represents mix generation data for a production type."""

    production_type: ProductionType = Field(..., description="Energy source type")
    data_state: DataState = Field(..., description="official/estimated/missing")
    datasource: DataSource = Field(..., description="Data provider for this block")
    values: List[Tuple[datetime, float]] = Field(
        ..., description="Time series: (timestamp, mix_generation_value)"
    )


class MixSeries(BaseModel):
    """Represents a series of mix data for a specific zone."""

    valid: bool = Field(..., description="Validity of this version of zone data")
    zone_status: ZoneStatus = Field(..., description="Status of the zone data")
    production: List[MixBlock] = Field(
        ..., description="Mix blocks grouped by production type"
    )


class Mix(BaseModel):
    """Represents mix generation data for a specific zone."""

    zone: str = Field(..., description="wattnet zone code")
    unit: Unit = Field(..., description="Energy unit (fixed per zone)")
    series: List[MixSeries] = Field(
        ..., description="Multiple versions of the zone data grouped by status"
    )
