from enum import Enum
from pydantic import BaseModel


class RelatedType(str, Enum):
    CONTACT = "contact"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    MET = "met"
    CO_WORKER = "co-worker"
    COLLEAGUE = "colleague"
    CO_RESIDENT = "co-resident"
    NEIGHBOR = "neighbor"
    CHILD = "child"
    PARENT = "parent"
    SIBLING = "sibling"
    SPOUSE = "spouse"
    KIN = "kin"
    MUSE = "muse"
    CRUSH = "crush"
    DATE = "date"
    SWEETHEART = "sweetheart"
    ME = "me"
    AGENT = "agent"
    EMERGENCY = "emergency"


class Related(BaseModel):
    value: str
    types: list[RelatedType]

    def to_vcard(self) -> str:
        types_str = ",".join([t.value for t in self.types])
        return f"RELATED;TYPE={types_str}:{self.value}"
