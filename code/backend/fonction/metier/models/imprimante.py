from pydantic import BaseModel
from typing import Optional


class ImprimanteResponse(BaseModel):
    id: int
    vid: Optional[int] = None
    pid: Optional[int] = None
    vendor: Optional[str] = None
    nom: Optional[str] = None