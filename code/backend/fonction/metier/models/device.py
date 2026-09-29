from typing import Dict, Optional
from pydantic import BaseModel

class Device(BaseModel):
    id_device: str
    serial_number: str
    modele: str
    id_type_appareil: Optional[int] = None
    id_utilisateur: Optional[int] = None
    chromeos_version: Optional[str] = None
    chrome_version: Optional[str] = None
    ip_adress: Optional[str] = None
    mac_adress: Optional[str] = None

class DeviceResponses(BaseModel):
    id: int
    id_device: str
    serial_number: str
    modele: str
    id_type_appareil: Optional[int] = None
    type_appareil: Optional[str] = None
    id_utilisateur: Optional[int] = None
    chromeos_version: Optional[str] = None
    chrome_version: Optional[str] = None
    date: Optional[str] = None
    ip_adress: Optional[str] = None
    mac_adress: Optional[str] = None
    status: Optional[str] = None
    utilisateur_email: Optional[str] = None
    utilisateurs_recents: Optional[list[str]] = []
    filiale: Optional[str] = None

class StatistiquesResponse(BaseModel):
    total: int
    par_statut: Dict[str,int]
    par_type: Dict[str,int]