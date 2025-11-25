from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field

ZoneStatus = Literal["complete", "preview", "missing"]
DataState = Literal["official", "estimated", "missing"]
DataSource = Literal["ENTSO-E"]
Unit = Literal["MW"]


class ImportBlock(BaseModel):
    source: str = Field(..., description="Origin zone of the import")
    data_state: DataState = Field(..., description="official/estimated/missing")
    unit: Unit = Field(..., description="Energy unit for the values")
    values: List[tuple[datetime, float]] = Field(
        ..., description="Time series of imported energy values"
    )


class ImportSeries(BaseModel):
    valid: bool = Field(..., description="Validity of this series for the zone")
    zone_status: ZoneStatus = Field(..., description="Zone status for this series")
    imports: List[ImportBlock] = Field(
        ..., description="List of import blocks for different sources"
    )


class Import(BaseModel):
    zone: str = Field(..., description="Wattnet zone code")
    unit: Unit = Field(..., description="Unit of energy (constant per zone)")
    datasource: DataSource = Field(..., description="Data provider (constant per zone)")
    series: List[ImportSeries] = Field(
        ..., description="Multiple series grouped by valid/zone_status"
    )
