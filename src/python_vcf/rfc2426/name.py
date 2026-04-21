from pydantic import BaseModel


class Name(BaseModel):
    family_name: str = ""
    given_name: str = ""
    additional_names: str = ""
    honorific_prefixes: str = ""
    honorific_suffixes: str = ""

    def to_vcard(self) -> str:
        name_parts = [
            self.family_name,
            self.given_name,
            self.additional_names,
            self.honorific_prefixes,
            self.honorific_suffixes,
        ]
        return f"N:{';'.join(name_parts)}"
