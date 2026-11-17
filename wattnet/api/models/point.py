"""A point of a time series, as an object that can grow without breaking its readers."""

from datetime import datetime

from pydantic import BaseModel, Field


class Point(BaseModel):
    """One value of a time series, with the moment it was last written."""

    timestamp: datetime = Field(..., description="Moment the value refers to (UTC)")
    value: float = Field(..., description="Value, rounded as in `values`")
    updated_at: datetime = Field(
        ..., description="Moment this version of the value was stored (UTC)"
    )
