import base64

from pydantic import BaseModel


class Photo(BaseModel):
    data: bytes
    image_type: str = "JPEG"  # JPEG, GIF, PNG, etc.

    def to_vcard(self) -> str:
        encoded_data = base64.b64encode(self.data).decode("ascii")
        return f"PHOTO;ENCODING=b;TYPE={self.image_type}:{encoded_data}"
