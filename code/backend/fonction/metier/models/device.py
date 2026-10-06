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
    utilisateurs_recents: Optional[list[str]] = None
    filiale: Optional[str] = None

    ram_total: Optional[int] = None
    ram_total_label: Optional[str] = None
    disk_total: Optional[int] = None
    disk_total_label: Optional[str] = None
    disk_free: Optional[int] = None
    disk_free_label: Optional[str] = None
    disk_used: Optional[int] = None
    disk_used_label: Optional[str] = None
    disk_model: Optional[str] = None
    disk_type: Optional[str] = None
    cpu_model: Optional[str] = None
    cpu_freq_max: Optional[int] = None
    cpu_freq_max_label: Optional[str] = None
    cpu_architecture: Optional[str] = None

class StatistiquesResponse(BaseModel):
    total: int
    par_statut: Dict[str,int]
    par_type: Dict[str,int]