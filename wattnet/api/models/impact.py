"""Data models for impact endpoints in the wattnet API application."""

from datetime import datetime
from typing import List, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Literal

ZoneStatus = Literal["complete", "preview", "missing"]
ImpactType = Literal["water"]
ImpactScope = Literal["operational"]
AggregationMethod = Literal["time-weighted-average"]
ImpactUnit = Literal["stress-l/kWh"]
CoverageType = Literal["global", "local"]


class ImpactBase(BaseModel):
    """Base model for impact data, containing common fields."""

    impact_type: ImpactType = Field(..., description="Type of impact (water)")
    scope: ImpactScope = Field(..., description="Scope of the impact (operational)")
    zone: str = Field(..., description="wattnet zone code")
    unit: ImpactUnit = Field(..., description="Unit of the impact value (stress-l/kWh)")
    coverage: CoverageType = Field(
        ..., description="Coverage type of the impact (global or local)"
    )


class ImpactSeries(BaseModel):
    """Represents a series of impact data grouped by validity and zone status."""

    valid: bool = Field(
        ..., description="Indicates if the data points are valid and immutable"
    )
    zone_status: ZoneStatus = Field(
        ..., description="Status of the zone for this series"
    )
    values: List[Tuple[datetime, float]] = Field(
        ..., description="List of (timestamp, value) tuples"
    )


class Impact(ImpactBase):
    """Represents impact data for a specific zone with multiple series."""

    series: List[ImpactSeries] = Field(
        ..., description="Series grouped by status and validity"
    )


class ImpactAggregate(ImpactBase):
    """Represents aggregated impact data for a specific zone."""

    start: datetime = Field(..., description="Start datetime of the aggregation period")
    end: datetime = Field(..., description="End datetime of the aggregation period")
    value: float = Field(..., description="Aggregated impact value over the period")
    valid: bool = Field(
        ..., description="Indicates if the aggregated data is valid and immutable"
    )
    zone_status: ZoneStatus = Field(
        ..., description="Status of the zone for the aggregated impact"
    )
    aggregation_method: AggregationMethod = Field(
        "time-weighted-average", description="Method used for aggregation"
    )
