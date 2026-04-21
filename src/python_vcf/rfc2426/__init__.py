from pydantic import BaseModel, HttpUrl
from .name import Name
from .tel import Telephone, TelType
from .email import Email, EmailType
from .address import Address, AdrType
from .org import Organization
from .photo import Photo
from datetime import date, datetime
from pathlib import Path

__all__ = (
    "Address",
    "AdrType",
    "Email",
    "EmailType",
    "Name",
    "Organization",
    "Photo",
    "TelType",
    "Telephone",
    "VCard3",
)


class VCard3(BaseModel):
    """
    Implementation of vCard 3.0 as specified in RFC 2426
    """

    version: str = "3.0"
    name: Name | None = None
    formatted_name: str
    nickname: str | None = None
    telephones: list[Telephone] = []
    emails: list[Email] = []
    addresses: list[Address] = []
    organization: Organization | None = None
    title: str | None = None
    role: str | None = None
    photo: Photo | None = None
    birthday: date | datetime | None = None
    url: list[HttpUrl] = []
    note: str | None = None
    categories: list[str] = []
    revision: datetime | None = None
    uid: str | None = None

    class Config:
        arbitrary_types_allowed = True

    def to_vcard(self) -> str:
        """
        Convert the model to vCard 3.0 format
        """
        lines = [
            "BEGIN:VCARD",
            f"VERSION:{self.version}",
        ]

        # Add name fields
        if self.name:
            lines.append(self.name.to_vcard())
        lines.append(f"FN:{self.formatted_name}")
        if self.nickname:
            lines.append(f"NICKNAME:{self.nickname}")
            lines.append(
                f"X-ANDROID-CUSTOM;vnd.android.cursor.item/nickname;{self.nickname};1;;;;;;;;;;;;;"
            )  # Support for Android

        # Add contact fields
        for tel in self.telephones:
            lines.append(tel.to_vcard())
        for email in self.emails:
            lines.append(email.to_vcard())
        for address in self.addresses:
            lines.append(address.to_vcard())

        # Add organization fields
        if self.organization:
            lines.append(self.organization.to_vcard())
        if self.title:
            lines.append(f"TITLE:{self.title}")
        if self.role:
            lines.append(f"ROLE:{self.role}")

        # Add media
        if self.photo:
            lines.append(self.photo.to_vcard())

        # Add other fields
        if self.birthday:
            if isinstance(self.birthday, datetime):
                birthday_str = self.birthday.strftime("%Y%m%dT%H%M%SZ")
            else:
                birthday_str = self.birthday.strftime("%Y%m%d")
            lines.append(f"BDAY:{birthday_str}")

        for url in self.url:
            lines.append(f"URL:{url.unicode_string()}")

        if self.note:
            lines.append(f"NOTE:{self.note}")

        if self.categories:
            categories_str = ",".join(self.categories)
            lines.append(f"CATEGORIES:{categories_str}")

        if self.revision:
            rev_str = self.revision.strftime("%Y%m%dT%H%M%SZ")
        else:
            rev_str = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        lines.append(f"REV:{rev_str}")

        if self.uid:
            lines.append(f"UID:{self.uid}")

        lines.append("END:VCARD")

        return "\n".join(lines)

    def to_file(self, path: Path) -> None:
        """
        Save the vCard to a file
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_vcard())
