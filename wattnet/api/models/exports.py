from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field

ZoneStatus = Literal["complete", "preview", "missing"]
DataState = Literal["official", "estimated", "missing"]
DataSource = Literal["ENTSO-E"]
Unit = Literal["MW"]


class ExportBlock(BaseModel):
    destination: str = Field(..., description="Destination zone code")
    data_state: DataState = Field(..., description="official/estimated/missing")
    unit: Unit = Field(..., description="Unit of exported energy")
    values: List[tuple[datetime, float]] = Field(
        ..., description="Time series of exported energy values"
    )


class ExportSeries(BaseModel):
    valid: bool = Field(..., description="Validity of the series for the zone")
    zone_status: ZoneStatus = Field(..., description="Zone status for this series")
    exports: List[ExportBlock] = Field(
        ..., description="List of export blocks per destination"
    )


class Export(BaseModel):
    zone: str = Field(..., description="Origin zone code")
    unit: Unit = Field(..., description="Unit of energy (constant per zone)")
    datasource: DataSource = Field(..., description="Data provider (constant per zone)")
    series: List[ExportSeries] = Field(
        ..., description="Multiple series grouped by valid/zone_status"
    )
