from datetime import datetime
from typing import List, Literal, Tuple

from pydantic import BaseModel, Field

ZoneStatus = Literal["complete", "preview", "missing"]
FootprintType = Literal["carbon", "water"]
FootprintScope = Literal["operational", "life-cycle"]
AggregationMethod = Literal["time-weighted-average"]
FootprintUnit = Literal["gCO2/kWh", "l/kWh"]
CoverageType = Literal["global", "local"]


class FootprintBase(BaseModel):
    footprint_type: FootprintType = Field(
        ..., description="Type of footprint (e.g., carbon, water)"
    )
    scope: FootprintScope = Field(
        ..., description="Scope of the footprint (e.g., operational, life-cycle)"
    )
    zone: str = Field(..., description="wattnet zone code")
    unit: FootprintUnit = Field(
        ..., description="Unit of the footprint value (e.g., gCO2/kWh, l/kWh)"
    )
    coverage: CoverageType = Field(
        ..., description="Coverage type of the footprint (global or local)"
    )


class FootprintSeries(BaseModel):
    valid: bool = Field(
        ..., description="Indicates if the data points are valid and inmutable"
    )
    zone_status: ZoneStatus = Field(
        ..., description="Status of the zone for this series"
    )
    values: List[Tuple[datetime, float]] = Field(
        ..., description="List of (timestamp, value) tuples"
    )


class Footprint(FootprintBase):
    series: List[FootprintSeries] = Field(
        ..., description="Series grouped by status and validity"
    )


class FootprintAggregate(FootprintBase):
    start: datetime = Field(..., description="Start datetime of the aggregation period")
    end: datetime = Field(..., description="End datetime of the aggregation period")
    value: float = Field(..., description="Aggregated footprint value over the period")
    valid: bool = Field(
        ..., description="Indicates if the aggregated data is valid and inmutable"
    )
    zone_status: ZoneStatus = Field(
        ..., description="Status of the zone for the aggregated footprint"
    )
    aggregation_method: AggregationMethod = Field(
        "time-weighted-average", description="Method used for aggregation"
    )
