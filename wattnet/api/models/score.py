"""Data models for score endpoints in the wattnet API application."""

from datetime import datetime
from typing import List, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Literal

ZoneStatus = Literal["complete", "preview", "missing"]
ScoreScope = Literal["operational"]
AggregationMethod = Literal["time-weighted-average"]
CoverageType = Literal["global", "local"]


class ScoreBase(BaseModel):
    """Base model for EnvironmentalScore data, containing common fields."""

    scope: ScoreScope = Field(..., description="Scope of the score (operational)")
    zone: str = Field(..., description="wattnet zone code")
    coverage: CoverageType = Field(
        ..., description="Coverage type of the score (global or local)"
    )


class EnvironmentalScoreSeries(BaseModel):
    """Represents a series of EnvironmentalScore data grouped by validity and zone."""

    valid: bool = Field(
        ..., description="Indicates if the data points are valid and immutable"
    )
    zone_status: ZoneStatus = Field(
        ..., description="Status of the zone for this series"
    )
    values: List[Tuple[datetime, float]] = Field(
        ..., description="List of (timestamp, value) tuples in range [0, 100]"
    )


class EnvironmentalScore(ScoreBase):
    """Represents EnvironmentalScore data for a specific zone with multiple series."""

    series: List[EnvironmentalScoreSeries] = Field(
        ..., description="Series grouped by status and validity"
    )


class EnvironmentalScoreAggregate(ScoreBase):
    """Represents aggregated EnvironmentalScore data for a specific zone."""

    start: datetime = Field(..., description="Start datetime of the aggregation period")
    end: datetime = Field(..., description="End datetime of the aggregation period")
    value: float = Field(
        ..., description="Aggregated score value over the period, in range [0, 100]"
    )
    valid: bool = Field(
        ..., description="Indicates if the aggregated data is valid and immutable"
    )
    zone_status: ZoneStatus = Field(
        ..., description="Status of the zone for the aggregated score"
    )
    aggregation_method: AggregationMethod = Field(
        "time-weighted-average", description="Method used for aggregation"
    )
