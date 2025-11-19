from datetime import datetime
from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, Field

FactorType = Literal["carbon", "water"]
FactorScope = Literal["operational", "life-cycle"]
ProductionType = Literal[
    "biomass",
    "coal",
    "gas",
    "geothermal",
    "marine",
    "hydro_reservoir",
    "hydro_river",
    "nuclear",
    "oil",
    "other",
    "other_renewable",
    "solar",
    "waste",
    "wind_offshore",
    "wind_onshore",
]
FactorUnit = Literal["gCO2/kWh", "l/kWh"]
AggregationMethod = Literal["time-weighted-average"]


class FactorBase(BaseModel):
    factor_type: FactorType = Field(
        ..., description="Type of factor (e.g., carbon, water)"
    )
    production_type: ProductionType = Field(
        ..., description="Type of production (e.g., solar, wind, coal)"
    )
    scope: FactorScope = Field(
        ..., description="Scope of the factor (e.g., operational, life-cycle)"
    )
    unit: FactorUnit = Field(
        ..., description="Unit of the factor value (e.g., gCO2/kWh, l/kWh)"
    )
    source: str = Field(..., description="Source of the factor data")
    year: Optional[int] = Field(
        None, description="Year of the factor data (if applicable)"
    )
    source_link: Optional[str] = Field(
        None, description="Link to the source of the factor data"
    )


# Serie de valores de un factor (igual que tu Factor original, pero como serie)
class FactorSeries(BaseModel):
    values: List[Tuple[datetime, float]] = Field(
        default_factory=list, description="List of (timestamp, value) tuples"
    )


# Factor completo con series
class Factor(FactorBase):
    series: List[FactorSeries] = Field(
        default_factory=list, description="Series grouped by production_type/scope etc."
    )


# Factor agregado
class FactorAggregate(FactorBase):
    start: datetime = Field(..., description="Start datetime of the aggregation period")
    end: datetime = Field(..., description="End datetime of the aggregation period")
    value: float = Field(..., description="Aggregated factor value over the period")
    aggregation_method: AggregationMethod = Field(
        "time-weighted-average", description="Method used for aggregation"
    )
