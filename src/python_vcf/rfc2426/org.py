from pydantic import BaseModel, Field


class Organization(BaseModel):
    name: str
    units: list[str] = Field(default_factory=list)

    def to_vcard(self) -> str:
        org_parts = [self.name] + self.units
        return f"ORG:{';'.join(org_parts)}"
