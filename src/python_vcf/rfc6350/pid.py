from pydantic import BaseModel


class ClientPidMap(BaseModel):
    pid: int
    uri: str

    def to_vcard(self) -> str:
        return f"CLIENTPIDMAP:{self.pid}:{self.uri}"
