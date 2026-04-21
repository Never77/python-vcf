from enum import Enum
from pydantic import BaseModel, Field


class AdrType(str, Enum):
    HOME = "HOME"
    WORK = "WORK"
    POSTAL = "POSTAL"
    PARCEL = "PARCEL"
    DOM = "DOM"
    INTL = "INTL"
    PREF = "PREF"


class Address(BaseModel):
    post_office_box: str = ""
    extended_address: str = ""
    street: str = ""
    localcity: str = ""
    region: str = ""
    postal_code: str = ""
    country: str = ""
    types: list[AdrType] = Field(default_factory=list)

    def to_vcard(self) -> str:
        types_str = ",".join([t.value for t in self.types]) if self.types else ""
        adr_parts = [
            self.post_office_box,
            self.extended_address,
            self.street,
            self.localcity,
            self.region,
            self.postal_code,
            self.country,
        ]
        adr_value = ";".join(adr_parts)
        type_part = f";TYPE={types_str}" if types_str else ""
        return f"ADR{type_part}:{adr_value}"
