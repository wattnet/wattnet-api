from pydantic import BaseModel


class ZoneInfo(BaseModel):

    code: str
    name: str
    eic_code: str | None = None
    country: str
    country_code: str


class Zone(ZoneInfo):
    """
    Represents a zone with its details.
    """
