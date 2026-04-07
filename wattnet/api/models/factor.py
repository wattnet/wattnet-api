"""Models for representing factor data in the API responses."""

from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Literal

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
    """Base model for factors, containing common fields for both series & aggregates."""

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


class FactorSeries(BaseModel):
    """Represents a time series of factor values.

    Represents a time series of factor values for a specific production type and scope,
    including validity, zone status, and list of (timestamp, value) tuples.
    """

    values: List[Tuple[datetime, float]] = Field(
        default_factory=list, description="List of (timestamp, value) tuples"
    )


class Factor(FactorBase):
    """Represents factor data for a specific production type & scope.

    Represents factor data for a specific production type and scope, including multiple
    series grouped by validity and zone status.
    """

    series: List[FactorSeries] = Field(
        default_factory=list, description="Series grouped by production_type/scope etc."
    )


class FactorAggregate(FactorBase):
    """Represents an aggregated factor value over a specified time period.

    Represents an aggregated factor value over a specified time period, including
    aggregation method and validity.
    """

    start: datetime = Field(..., description="Start datetime of the aggregation period")
    end: datetime = Field(..., description="End datetime of the aggregation period")
    value: float = Field(..., description="Aggregated factor value over the period")
    aggregation_method: AggregationMethod = Field(
        "time-weighted-average", description="Method used for aggregation"
    )
