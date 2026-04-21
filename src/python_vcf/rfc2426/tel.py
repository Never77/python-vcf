from pydantic import BaseModel, Field
from enum import Enum


class TelType(str, Enum):
    HOME = "HOME"
    WORK = "WORK"
    CELL = "CELL"
    VOICE = "VOICE"
    FAX = "FAX"
    PAGER = "PAGER"
    MSG = "MSG"
    BBS = "BBS"
    MODEM = "MODEM"
    CAR = "CAR"
    ISDN = "ISDN"
    VIDEO = "VIDEO"
    PCS = "PCS"


class Telephone(BaseModel):
    value: str
    types: list[TelType] = Field(default_factory=lambda: [TelType.VOICE])

    def to_vcard(self) -> str:
        types_str = ",".join([t.value for t in self.types])
        return f"TEL;TYPE={types_str}:{self.value}"
