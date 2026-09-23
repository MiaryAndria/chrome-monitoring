from typing import Optional
from pydantic import BaseModel

class Filiale(BaseModel):
    org_unit_path: str

class FilialeResponse(BaseModel):
    id: int
    org_unit_path: str

class FilialeWithDevicesResponse(BaseModel):
    id: int
    org_unit_path: str
    nombre_devices: Optional[int] = 0