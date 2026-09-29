from typing import Any, Dict, List
from datetime import datetime
from pydantic import BaseModel

class Rapport(BaseModel):
    id: int
    id_device: int
    id_type_rapport: int
    report_time: datetime
    donnees: Dict[str, Any]


class RapportResponse(BaseModel):
    cpu: List[Rapport]
    ram: List[Rapport]
    stockage: List[Rapport]
    batterie: List[Rapport]
    reseau: List[Rapport]
    peripheriques: List[Rapport]
    
class RapportDeviceResponse(BaseModel):
    id: int
    id_device: int
    id_type_rapport: int
    report_time: datetime
    donnees: Any   
    
    
class TypeRapportIdResponse(BaseModel):
    id: int | None = None