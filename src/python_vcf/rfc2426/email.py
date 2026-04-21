from enum import Enum

from pydantic import BaseModel


class EmailType(str, Enum):
    HOME = "HOME"
    WORK = "WORK"
    INTERNET = "INTERNET"
    PREF = "PREF"
    X400 = "X400"


class Email(BaseModel):
    value: str
    types: list[EmailType] = [EmailType.INTERNET]

    def to_vcard(self) -> str:
        types_str = ",".join([t.value for t in self.types])
        return f"EMAIL;TYPE={types_str}:{self.value}"
