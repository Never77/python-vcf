from pydantic import Field
from .kind import KindType
from .gender import GenderType
from .related import Related
from python_vcf.rfc2426 import VCard3
from .pid import ClientPidMap
import base64

__all__ = ("ClientPidMap", "GenderType", "KindType", "Related", "VCard4")


class VCard4(VCard3):
    """
    Implementation of vCard 4.0 as specified in RFC 6350
    """

    version: str = "4.0"
    kind: KindType | None = None
    gender: GenderType | None = None
    related: list[Related] = Field(default_factory=list)
    member: list[str] = Field(default_factory=list)
    client_pid_maps: list[ClientPidMap] = Field(default_factory=list)

    def to_vcard(self) -> str:
        """
        Convert the model to vCard 4.0 format
        """
        lines = super().to_vcard().split("\n")
        lines.pop()

        version_index = next(
            (i for i, line in enumerate(lines) if line.startswith("VERSION:")), None
        )
        if version_index:
            lines[version_index] = f"VERSION:{self.version}"

        # Add vCard 4.0 specific fields
        if self.kind:
            lines.append(f"KIND:{self.kind.value}")

        if self.gender:
            lines.append(f"GENDER:{self.gender.value}")

        for rel in self.related:
            lines.append(rel.to_vcard())

        for pid_map in self.client_pid_maps:
            lines.append(pid_map.to_vcard())

        # Update PHOTO format to vCard 4.0
        photo_index = next(
            (i for i, line in enumerate(lines) if line.startswith("PHOTO;")), None
        )
        if photo_index and self.photo:
            encoded_data = base64.b64encode(self.photo.data).decode("ascii")
            lines[photo_index] = (
                f"PHOTO:data:image/{self.photo.image_type.lower()};base64,{encoded_data}"
            )

        # Add END:VCARD
        lines.append("END:VCARD")

        return "\n".join(lines)
