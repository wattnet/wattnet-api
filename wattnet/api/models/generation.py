from datetime import datetime
from typing import List, Literal, Tuple

from pydantic import BaseModel, Field

DataState = Literal["official"]
ZoneStatus = Literal["complete", "preview", "missing"]
DataSource = Literal["ENTSO-E", "ELEXON"]
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
    production_type: ProductionType = Field(..., description="Energy source type")
    data_state: DataState = Field(..., description="official/estimated/missing")

    values: List[Tuple[datetime, float]] = Field(
        ..., description="Time series: (timestamp, generation_value)"
    )


class GenerationSeries(BaseModel):
    valid: bool = Field(..., description="Validity of this version of zone data")
    zone_status: ZoneStatus = Field(..., description="Status of the zone data")

    production: List[ProductionBlock] = Field(
        ..., description="Generation blocks grouped by production type"
    )


class Generation(BaseModel):
    zone: str = Field(..., description="wattnet zone code")
    unit: Unit = Field(..., description="Energy unit (fixed per zone)")
    datasource: DataSource = Field(..., description="Data provider (fixed per zone)")

    series: List[GenerationSeries] = Field(
        ..., description="Multiple versions of the zone data grouped by status"
    )
