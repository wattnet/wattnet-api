"""Data models for footprint endpoints in the wattnet API application."""

from datetime import datetime
from typing import List, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Literal

ZoneStatus = Literal["complete", "preview", "missing"]
FootprintType = Literal["carbon", "water"]
FootprintScope = Literal["operational", "life-cycle"]
AggregationMethod = Literal["time-weighted-average"]
FootprintUnit = Literal["gCO2/kWh", "l/kWh"]
CoverageType = Literal["global", "local"]


class FootprintBase(BaseModel):
    """Base model for footprint data, containing common fields.

    Contains common fields for both footprint series and aggregate models, such as
    footprint type, scope, zone, unit, and coverage.
    """

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
    """Represents a series of footprint data for a specific destination zone.

    Represents a series of footprint data for a specific destination zone, including
    validity, zone status, and list of origin zones contributing to the footprint.
    """

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
    """Represents footprint data for a specific destination zone.

    Represents footprint data for a specific destination zone, including multiple
    series grouped by validity and zone status.
    """

    series: List[FootprintSeries] = Field(
        ..., description="Series grouped by status and validity"
    )


class FootprintAggregate(FootprintBase):
    """Represents aggregated footprint data for a specific destination zone.

    Represents aggregated footprint data for a specific destination zone, including
    aggregation period, method, validity, and zone status.
    """

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
