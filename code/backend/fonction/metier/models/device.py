from typing import Optional
from pydantic import BaseModel

class Device(BaseModel):
    id_device: str
    serial_number: str
    modele: str
    id_type_appareil: int
    id_utilisateur: int
    chromeos_version: Optional[str] = None
    chrome_version: Optional[str] = None
    ip_adress: Optional[str] = None
    mac_adress: Optional[str] = None

class DeviceResponses(BaseModel):
    id: int
    id_device: str
    serial_number: str
    modele: str
    id_type_appareil: int
    id_utilisateur: int
    chromeos_version: Optional[str] = None
    chrome_version: Optional[str] = None
    date: Optional[str] = None
    ip_adress: Optional[str] = None
    mac_adress: Optional[str] = None
    status: Optional[str] = None
    utilisateur_email: Optional[str] = None
    utilisateurs_recents: Optional[list[str]] = []