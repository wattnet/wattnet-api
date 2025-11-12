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


class Factor(BaseModel):
    factor_type: FactorType
    production_type: ProductionType
    scope: FactorScope
    values: List[Tuple[datetime, float]] = Field(
        default_factory=list, description="List of tuples containing datetime and value"
    )
    unit: FactorUnit
    source: str
    year: Optional[int] = None
    source_link: Optional[str] = None
