from typing import List, Optional
from pydantic import BaseModel

class Filiale(BaseModel):
    org_unit_path: str

class FilialeResponse(BaseModel):
    id: int
    org_unit_path: str

class FilialePageResponse(BaseModel):
    items: List[FilialeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# class FilialeWithDevicesResponse(BaseModel):
#     id: int
#     org_unit_path: str
#     nombre_devices: Optional[int] = 0